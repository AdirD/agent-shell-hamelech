#!/usr/bin/env python3
"""Validate and render a portable podcast edit plan with FFmpeg.

The helper deliberately uses only the Python standard library. It validates the
entire JSON plan and the referenced media before starting FFmpeg, builds one
filter graph for the ordered clip/card sequence, normalizes the concatenated
audio, and writes H.264/AAC MP4 output.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, NoReturn, Optional, Sequence, Set, Tuple


SCHEMA_VERSION = 1
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
BITRATE_RE = re.compile(r"^[1-9][0-9]*k$")
PRESETS = {
    "ultrafast",
    "superfast",
    "veryfast",
    "faster",
    "fast",
    "medium",
    "slow",
    "slower",
    "veryslow",
}
TOP_LEVEL_KEYS = {
    "version",
    "approval",
    "sources",
    "output",
    "canvas",
    "audio",
    "encoding",
    "speaker_crops",
    "sequence",
}


class PlanError(ValueError):
    """A user-correctable edit-plan or media validation error."""


@dataclass(frozen=True)
class SourceSpec:
    name: str
    path: Path
    video_stream: int
    audio_stream: int


@dataclass(frozen=True)
class CropSpec:
    name: str
    source: str
    x: int
    y: int
    width: int
    height: int
    fit: str
    anchor_x: float
    anchor_y: float


@dataclass(frozen=True)
class MediaInfo:
    width: int
    height: int
    duration: float


@dataclass(frozen=True)
class EditPlan:
    plan_path: Path
    approval_path: Path
    sources: Mapping[str, SourceSpec]
    output_path: Path
    width: int
    height: int
    fps: float
    canvas_background: str
    sample_rate: int
    channel_layout: str
    audio_bitrate: str
    integrated_lufs: float
    true_peak_db: float
    loudness_range_lu: float
    preset: str
    crf: int
    crops: Mapping[str, CropSpec]
    sequence: Sequence[Mapping[str, Any]]

    @property
    def channels(self) -> int:
        return 1 if self.channel_layout == "mono" else 2


class _DuplicateKeyError(PlanError):
    pass


def _reject_duplicate_keys(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> NoReturn:
    raise PlanError(f"non-finite JSON number {value!r} is not allowed")


def _object(value: Any, where: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise PlanError(f"{where} must be an object")
    return value


def _array(value: Any, where: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise PlanError(f"{where} must be an array")
    return value


def _keys(
    value: Mapping[str, Any],
    *,
    required: Set[str],
    optional: Set[str] = frozenset(),
    where: str,
) -> None:
    actual = set(value)
    missing = sorted(required - actual)
    unknown = sorted(actual - required - optional)
    if missing:
        raise PlanError(f"{where} is missing required field(s): {', '.join(missing)}")
    if unknown:
        raise PlanError(f"{where} has unknown field(s): {', '.join(unknown)}")


def _string(value: Any, where: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str):
        raise PlanError(f"{where} must be a string")
    if "\x00" in value:
        raise PlanError(f"{where} must not contain a NUL character")
    if nonempty and not value.strip():
        raise PlanError(f"{where} must not be empty")
    if nonempty and value != value.strip():
        raise PlanError(f"{where} must not have leading or trailing whitespace")
    return value


def _identifier(value: Any, where: str) -> str:
    result = _string(value, where)
    if not IDENTIFIER_RE.fullmatch(result):
        raise PlanError(
            f"{where} must start with a letter and contain only letters, digits, '_' or '-'"
        )
    return result


def _integer(
    value: Any,
    where: str,
    *,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PlanError(f"{where} must be an integer")
    if minimum is not None and value < minimum:
        raise PlanError(f"{where} must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise PlanError(f"{where} must be at most {maximum}")
    return value


def _number(
    value: Any,
    where: str,
    *,
    minimum: Optional[float] = None,
    maximum: Optional[float] = None,
    exclusive_minimum: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PlanError(f"{where} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise PlanError(f"{where} must be finite")
    if minimum is not None:
        invalid = result <= minimum if exclusive_minimum else result < minimum
        if invalid:
            comparator = "greater than" if exclusive_minimum else "at least"
            raise PlanError(f"{where} must be {comparator} {minimum}")
    if maximum is not None and result > maximum:
        raise PlanError(f"{where} must be at most {maximum}")
    return result


def _color(value: Any, where: str) -> str:
    result = _string(value, where)
    if not COLOR_RE.fullmatch(result):
        raise PlanError(f"{where} must be a color in #RRGGBB form")
    return result.upper()


def _resolve_path(raw: Any, where: str, base: Path) -> Path:
    text = _string(raw, where)
    candidate = Path(text)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve(strict=False)


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PlanError(f"cannot read plan {path}: {exc}") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant,
        )
    except _DuplicateKeyError:
        raise
    except PlanError:
        raise
    except json.JSONDecodeError as exc:
        raise PlanError(
            f"invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    return _object(value, "plan")


def load_plan(path: Path) -> EditPlan:
    """Parse and structurally validate a plan without invoking external tools."""
    plan_path = path.resolve(strict=False)
    raw = _load_json(plan_path)
    _keys(raw, required=TOP_LEVEL_KEYS, where="plan")
    base = plan_path.parent

    version = _integer(raw["version"], "plan.version", minimum=1)
    if version != SCHEMA_VERSION:
        raise PlanError(
            f"plan.version must be {SCHEMA_VERSION}; got {version}. "
            "Use the matching schema/reference before rendering."
        )

    approval = _object(raw["approval"], "plan.approval")
    _keys(approval, required={"status", "script_path"}, where="plan.approval")
    status = _string(approval["status"], "plan.approval.status")
    if status != "approved":
        raise PlanError("plan.approval.status must be exactly 'approved' before video editing")
    approval_path = _resolve_path(
        approval["script_path"], "plan.approval.script_path", base
    )

    sources_raw = _object(raw["sources"], "plan.sources")
    if not sources_raw:
        raise PlanError("plan.sources must contain at least one source")
    sources: Dict[str, SourceSpec] = {}
    for source_name, source_value in sources_raw.items():
        name = _identifier(source_name, f"plan.sources key {source_name!r}")
        source = _object(source_value, f"plan.sources.{name}")
        _keys(
            source,
            required={"path", "video_stream", "audio_stream"},
            where=f"plan.sources.{name}",
        )
        sources[name] = SourceSpec(
            name=name,
            path=_resolve_path(source["path"], f"plan.sources.{name}.path", base),
            video_stream=_integer(
                source["video_stream"],
                f"plan.sources.{name}.video_stream",
                minimum=0,
            ),
            audio_stream=_integer(
                source["audio_stream"],
                f"plan.sources.{name}.audio_stream",
                minimum=0,
            ),
        )

    output = _object(raw["output"], "plan.output")
    _keys(output, required={"path"}, where="plan.output")
    output_path = _resolve_path(output["path"], "plan.output.path", base)
    if output_path.suffix.lower() != ".mp4":
        raise PlanError("plan.output.path must end in .mp4")

    canvas = _object(raw["canvas"], "plan.canvas")
    _keys(
        canvas,
        required={"width", "height", "fps", "background"},
        where="plan.canvas",
    )
    width = _integer(canvas["width"], "plan.canvas.width", minimum=2, maximum=16384)
    height = _integer(canvas["height"], "plan.canvas.height", minimum=2, maximum=16384)
    if width % 2 or height % 2:
        raise PlanError("plan.canvas.width and height must be even for yuv420p output")
    fps = _number(
        canvas["fps"], "plan.canvas.fps", minimum=0, maximum=240, exclusive_minimum=True
    )
    canvas_background = _color(canvas["background"], "plan.canvas.background")

    audio = _object(raw["audio"], "plan.audio")
    _keys(
        audio,
        required={"sample_rate", "channel_layout", "bitrate", "loudness"},
        where="plan.audio",
    )
    sample_rate = _integer(
        audio["sample_rate"], "plan.audio.sample_rate", minimum=8000, maximum=192000
    )
    channel_layout = _string(audio["channel_layout"], "plan.audio.channel_layout")
    if channel_layout not in {"mono", "stereo"}:
        raise PlanError("plan.audio.channel_layout must be 'mono' or 'stereo'")
    audio_bitrate = _string(audio["bitrate"], "plan.audio.bitrate")
    if not BITRATE_RE.fullmatch(audio_bitrate):
        raise PlanError("plan.audio.bitrate must look like '192k'")
    loudness = _object(audio["loudness"], "plan.audio.loudness")
    _keys(
        loudness,
        required={"integrated_lufs", "true_peak_db", "range_lu"},
        where="plan.audio.loudness",
    )
    integrated_lufs = _number(
        loudness["integrated_lufs"],
        "plan.audio.loudness.integrated_lufs",
        minimum=-70,
        maximum=-5,
    )
    true_peak_db = _number(
        loudness["true_peak_db"],
        "plan.audio.loudness.true_peak_db",
        minimum=-9,
        maximum=0,
    )
    loudness_range_lu = _number(
        loudness["range_lu"],
        "plan.audio.loudness.range_lu",
        minimum=1,
        maximum=50,
    )

    encoding = _object(raw["encoding"], "plan.encoding")
    _keys(
        encoding,
        required={"video_codec", "audio_codec", "pixel_format", "preset", "crf"},
        where="plan.encoding",
    )
    if _string(encoding["video_codec"], "plan.encoding.video_codec") != "libx264":
        raise PlanError("plan.encoding.video_codec must be 'libx264'")
    if _string(encoding["audio_codec"], "plan.encoding.audio_codec") != "aac":
        raise PlanError("plan.encoding.audio_codec must be 'aac'")
    if _string(encoding["pixel_format"], "plan.encoding.pixel_format") != "yuv420p":
        raise PlanError("plan.encoding.pixel_format must be 'yuv420p'")
    preset = _string(encoding["preset"], "plan.encoding.preset")
    if preset not in PRESETS:
        raise PlanError(f"plan.encoding.preset must be one of: {', '.join(sorted(PRESETS))}")
    crf = _integer(encoding["crf"], "plan.encoding.crf", minimum=0, maximum=51)

    crops_raw = _object(raw["speaker_crops"], "plan.speaker_crops")
    if not crops_raw:
        raise PlanError("plan.speaker_crops must contain at least one named crop")
    crops: Dict[str, CropSpec] = {}
    for crop_name, crop_value in crops_raw.items():
        name = _identifier(crop_name, f"plan.speaker_crops key {crop_name!r}")
        crop = _object(crop_value, f"plan.speaker_crops.{name}")
        _keys(
            crop,
            required={
                "source",
                "x",
                "y",
                "width",
                "height",
                "fit",
                "anchor_x",
                "anchor_y",
            },
            where=f"plan.speaker_crops.{name}",
        )
        source_name = _identifier(crop["source"], f"plan.speaker_crops.{name}.source")
        if source_name not in sources:
            raise PlanError(
                f"plan.speaker_crops.{name}.source references unknown source {source_name!r}"
            )
        fit = _string(crop["fit"], f"plan.speaker_crops.{name}.fit")
        if fit not in {"cover", "contain"}:
            raise PlanError(f"plan.speaker_crops.{name}.fit must be 'cover' or 'contain'")
        crops[name] = CropSpec(
            name=name,
            source=source_name,
            x=_integer(crop["x"], f"plan.speaker_crops.{name}.x", minimum=0),
            y=_integer(crop["y"], f"plan.speaker_crops.{name}.y", minimum=0),
            width=_integer(crop["width"], f"plan.speaker_crops.{name}.width", minimum=1),
            height=_integer(crop["height"], f"plan.speaker_crops.{name}.height", minimum=1),
            fit=fit,
            anchor_x=_number(
                crop["anchor_x"],
                f"plan.speaker_crops.{name}.anchor_x",
                minimum=0,
                maximum=1,
            ),
            anchor_y=_number(
                crop["anchor_y"],
                f"plan.speaker_crops.{name}.anchor_y",
                minimum=0,
                maximum=1,
            ),
        )

    sequence_raw = _array(raw["sequence"], "plan.sequence")
    if not sequence_raw:
        raise PlanError("plan.sequence must contain at least one item")
    items: List[Mapping[str, Any]] = []
    item_ids: Set[str] = set()
    used_sources: Set[str] = set()
    used_crops: Set[str] = set()
    source_intervals: Dict[str, List[Tuple[float, float, str]]] = {}
    clip_count = 0

    for index, item_value in enumerate(sequence_raw):
        where = f"plan.sequence[{index}]"
        item = _object(item_value, where)
        item_type = _string(item.get("type"), f"{where}.type")
        if item_type == "clip":
            _keys(
                item,
                required={
                    "type",
                    "id",
                    "provenance",
                    "source",
                    "speaker_crop",
                    "start",
                    "end",
                    "verbatim",
                },
                where=where,
            )
            if _string(item["provenance"], f"{where}.provenance") != "verbatim":
                raise PlanError(f"{where}.provenance must be 'verbatim' for clip items")
            source_name = _identifier(item["source"], f"{where}.source")
            crop_name = _identifier(item["speaker_crop"], f"{where}.speaker_crop")
            if source_name not in sources:
                raise PlanError(f"{where}.source references unknown source {source_name!r}")
            if crop_name not in crops:
                raise PlanError(f"{where}.speaker_crop references unknown crop {crop_name!r}")
            if crops[crop_name].source != source_name:
                raise PlanError(
                    f"{where}.speaker_crop {crop_name!r} belongs to source "
                    f"{crops[crop_name].source!r}, not {source_name!r}"
                )
            start = _number(item["start"], f"{where}.start", minimum=0)
            end = _number(item["end"], f"{where}.end", minimum=0)
            if end <= start:
                raise PlanError(f"{where}.end must be greater than start")
            _string(item["verbatim"], f"{where}.verbatim")
            used_sources.add(source_name)
            used_crops.add(crop_name)
            source_intervals.setdefault(source_name, []).append((start, end, str(item["id"])))
            clip_count += 1
        elif item_type == "card":
            _keys(
                item,
                required={
                    "type",
                    "id",
                    "provenance",
                    "role",
                    "duration",
                    "title",
                    "background",
                    "text_color",
                    "title_size",
                    "subtitle_size",
                },
                optional={"subtitle", "font_file"},
                where=where,
            )
            if _string(item["provenance"], f"{where}.provenance") != "editorial":
                raise PlanError(f"{where}.provenance must be 'editorial' for card items")
            role = _string(item["role"], f"{where}.role")
            if role not in {"title", "editorial_summary", "interstitial", "outro"}:
                raise PlanError(
                    f"{where}.role must be title, editorial_summary, interstitial, or outro"
                )
            _number(item["duration"], f"{where}.duration", minimum=0, exclusive_minimum=True)
            _string(item["title"], f"{where}.title")
            if "subtitle" in item:
                _string(item["subtitle"], f"{where}.subtitle", nonempty=False)
            _color(item["background"], f"{where}.background")
            _color(item["text_color"], f"{where}.text_color")
            _integer(item["title_size"], f"{where}.title_size", minimum=8, maximum=512)
            _integer(item["subtitle_size"], f"{where}.subtitle_size", minimum=8, maximum=512)
            if "font_file" in item:
                _resolve_path(item["font_file"], f"{where}.font_file", base)
        else:
            raise PlanError(f"{where}.type must be 'clip' or 'card'")

        item_id = _identifier(item.get("id"), f"{where}.id")
        if item_id in item_ids:
            raise PlanError(f"duplicate sequence item id {item_id!r}")
        item_ids.add(item_id)
        items.append(dict(item))

    if not clip_count:
        raise PlanError("plan.sequence must contain at least one clip item")
    unused_sources = sorted(set(sources) - used_sources)
    if unused_sources:
        raise PlanError(f"plan.sources contains unused source(s): {', '.join(unused_sources)}")
    unused_crops = sorted(set(crops) - used_crops)
    if unused_crops:
        raise PlanError(
            f"plan.speaker_crops contains unused crop(s): {', '.join(unused_crops)}"
        )

    for source_name, intervals in source_intervals.items():
        ordered = sorted(intervals, key=lambda value: (value[0], value[1]))
        for previous, current in zip(ordered, ordered[1:]):
            if current[0] < previous[1] - 1e-6:
                raise PlanError(
                    f"clip intervals overlap in source {source_name!r}: "
                    f"{previous[2]} [{previous[0]:.6f}, {previous[1]:.6f}) and "
                    f"{current[2]} [{current[0]:.6f}, {current[1]:.6f}). "
                    "Overlaps can duplicate approved audio."
                )

    return EditPlan(
        plan_path=plan_path,
        approval_path=approval_path,
        sources=sources,
        output_path=output_path,
        width=width,
        height=height,
        fps=fps,
        canvas_background=canvas_background,
        sample_rate=sample_rate,
        channel_layout=channel_layout,
        audio_bitrate=audio_bitrate,
        integrated_lufs=integrated_lufs,
        true_peak_db=true_peak_db,
        loudness_range_lu=loudness_range_lu,
        preset=preset,
        crf=crf,
        crops=crops,
        sequence=items,
    )


def _require_file(path: Path, where: str) -> None:
    if not path.exists():
        raise PlanError(f"{where} does not exist: {path}")
    if not path.is_file():
        raise PlanError(f"{where} is not a regular file: {path}")


def validate_referenced_files(plan: EditPlan) -> None:
    """Validate every referenced path without creating or overwriting anything."""
    _require_file(plan.approval_path, "approved script")
    for source in plan.sources.values():
        _require_file(source.path, f"source {source.name!r}")
        if source.path == plan.output_path:
            raise PlanError(f"output path would overwrite source {source.name!r}")
    if plan.output_path == plan.approval_path:
        raise PlanError("output path would overwrite approved-script.md")
    for index, item in enumerate(plan.sequence):
        font_file = item.get("font_file")
        if font_file is not None:
            font_path = _resolve_path(
                font_file,
                f"plan.sequence[{index}].font_file",
                plan.plan_path.parent,
            )
            _require_file(font_path, f"plan.sequence[{index}].font_file")


def _resolve_executable(value: str, label: str) -> str:
    found = shutil.which(value)
    if found is None:
        raise PlanError(f"{label} executable not found: {value!r}")
    return found


def _parse_duration(value: Any) -> Optional[float]:
    if value in (None, "", "N/A"):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) and result > 0 else None


def probe_source(ffprobe: str, source: SourceSpec) -> MediaInfo:
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,width,height,duration",
        "-of",
        "json",
        str(source.path),
    ]
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        raise PlanError(f"could not run ffprobe for source {source.name!r}: {exc}") from exc
    if completed.returncode:
        detail = completed.stderr.strip() or f"exit status {completed.returncode}"
        raise PlanError(f"ffprobe failed for source {source.name!r}: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise PlanError(f"ffprobe returned invalid JSON for source {source.name!r}") from exc

    streams = payload.get("streams")
    if not isinstance(streams, list):
        raise PlanError(f"ffprobe found no streams in source {source.name!r}")
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
    if source.video_stream >= len(videos):
        raise PlanError(
            f"source {source.name!r} requests video_stream {source.video_stream}, "
            f"but only {len(videos)} video stream(s) exist"
        )
    if source.audio_stream >= len(audios):
        raise PlanError(
            f"source {source.name!r} requests audio_stream {source.audio_stream}, "
            f"but only {len(audios)} audio stream(s) exist"
        )
    selected_video = videos[source.video_stream]
    selected_audio = audios[source.audio_stream]
    width = selected_video.get("width")
    height = selected_video.get("height")
    if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
        raise PlanError(f"ffprobe returned no usable video width for source {source.name!r}")
    if isinstance(height, bool) or not isinstance(height, int) or height <= 0:
        raise PlanError(f"ffprobe returned no usable video height for source {source.name!r}")

    durations = [
        _parse_duration(selected_video.get("duration")),
        _parse_duration(selected_audio.get("duration")),
        _parse_duration((payload.get("format") or {}).get("duration")),
    ]
    usable_durations = [duration for duration in durations if duration is not None]
    if not usable_durations:
        raise PlanError(f"ffprobe returned no usable duration for source {source.name!r}")
    return MediaInfo(width=width, height=height, duration=min(usable_durations))


def validate_media(plan: EditPlan, ffprobe: str) -> Mapping[str, MediaInfo]:
    """Probe source streams, crop bounds, and every source-time interval."""
    media = {
        source_name: probe_source(ffprobe, plan.sources[source_name])
        for source_name in sorted(plan.sources)
    }
    for crop in plan.crops.values():
        info = media[crop.source]
        if crop.x + crop.width > info.width or crop.y + crop.height > info.height:
            raise PlanError(
                f"speaker crop {crop.name!r} ({crop.x},{crop.y},{crop.width},{crop.height}) "
                f"exceeds source {crop.source!r} dimensions {info.width}x{info.height}"
            )
    tolerance = max(0.05, 1.0 / plan.fps)
    for index, item in enumerate(plan.sequence):
        if item["type"] != "clip":
            continue
        end = float(item["end"])
        source_name = str(item["source"])
        if end > media[source_name].duration + tolerance:
            raise PlanError(
                f"plan.sequence[{index}].end ({end:.6f}) exceeds source {source_name!r} "
                f"duration ({media[source_name].duration:.6f})"
            )
    return media


def _decimal(value: Any) -> str:
    result = f"{float(value):.9f}".rstrip("0").rstrip(".")
    return "0" if result in {"", "-0"} else result


def _ff_color(value: str) -> str:
    return "0x" + value[1:].upper()


def _filter_quote(value: str) -> str:
    """Quote one FFmpeg filter option value, including drawtext text."""
    escaped = value.replace("\\", "\\\\")
    for character in ("'", ":", ",", ";", "[", "]"):
        escaped = escaped.replace(character, "\\" + character)
    escaped = escaped.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")
    return "'" + escaped + "'"


def _drawtext_filter(
    *,
    text: str,
    size: int,
    color: str,
    y: str,
    font_path: Optional[Path],
) -> str:
    options = [
        "expansion=none",
        f"text={_filter_quote(text)}",
        f"fontcolor={_ff_color(color)}",
        f"fontsize={size}",
        "x=(w-text_w)/2",
        f"y={y}",
        "fix_bounds=true",
    ]
    if font_path is not None:
        options.append(f"fontfile={_filter_quote(str(font_path))}")
    return "drawtext=" + ":".join(options)


def build_filter_graph(plan: EditPlan, source_order: Sequence[str]) -> str:
    """Build the complete deterministic FFmpeg filter graph."""
    source_indexes = {name: index for index, name in enumerate(source_order)}
    clip_indexes: Dict[str, List[int]] = {name: [] for name in source_order}
    for sequence_index, item in enumerate(plan.sequence):
        if item["type"] == "clip":
            clip_indexes[str(item["source"])].append(sequence_index)

    graph: List[str] = []
    clip_inputs: Dict[int, Tuple[str, str]] = {}
    for source_number, source_name in enumerate(source_order):
        source = plan.sources[source_name]
        indexes = clip_indexes[source_name]
        input_index = source_indexes[source_name]
        video_input = f"[{input_index}:v:{source.video_stream}]"
        audio_input = f"[{input_index}:a:{source.audio_stream}]"
        if len(indexes) == 1:
            clip_inputs[indexes[0]] = (video_input, audio_input)
            continue
        video_outputs = [f"[s{source_number}v{branch}]" for branch in range(len(indexes))]
        audio_outputs = [f"[s{source_number}a{branch}]" for branch in range(len(indexes))]
        graph.append(f"{video_input}split={len(indexes)}{''.join(video_outputs)}")
        graph.append(f"{audio_input}asplit={len(indexes)}{''.join(audio_outputs)}")
        for branch, sequence_index in enumerate(indexes):
            clip_inputs[sequence_index] = (video_outputs[branch], audio_outputs[branch])

    fps = _decimal(plan.fps)
    background = _ff_color(plan.canvas_background)
    for index, item in enumerate(plan.sequence):
        video_label = f"[v{index}]"
        audio_label = f"[a{index}]"
        if item["type"] == "clip":
            crop = plan.crops[str(item["speaker_crop"])]
            start = _decimal(item["start"])
            end = _decimal(item["end"])
            video_input, audio_input = clip_inputs[index]
            video_filters = [
                f"trim=start={start}:end={end}",
                "setpts=PTS-STARTPTS",
                f"crop=w={crop.width}:h={crop.height}:x={crop.x}:y={crop.y}",
            ]
            if crop.fit == "cover":
                video_filters.extend(
                    [
                        f"scale=w={plan.width}:h={plan.height}:"
                        "force_original_aspect_ratio=increase:flags=lanczos",
                        f"crop=w={plan.width}:h={plan.height}:"
                        f"x=(iw-{plan.width})*{_decimal(crop.anchor_x)}:"
                        f"y=(ih-{plan.height})*{_decimal(crop.anchor_y)}",
                    ]
                )
            else:
                video_filters.extend(
                    [
                        f"scale=w={plan.width}:h={plan.height}:"
                        "force_original_aspect_ratio=decrease:flags=lanczos",
                        f"pad=w={plan.width}:h={plan.height}:x=(ow-iw)/2:y=(oh-ih)/2:"
                        f"color={background}",
                    ]
                )
            video_filters.extend(
                [
                    f"fps=fps={fps}",
                    "setsar=1",
                    "settb=AVTB",
                    "format=pix_fmts=yuv420p",
                ]
            )
            graph.append(f"{video_input}{','.join(video_filters)}{video_label}")
            audio_filters = [
                f"atrim=start={start}:end={end}",
                "asetpts=PTS-STARTPTS",
                f"aresample={plan.sample_rate}",
                f"aformat=sample_fmts=fltp:sample_rates={plan.sample_rate}:"
                f"channel_layouts={plan.channel_layout}",
                f"asettb=expr=1/{plan.sample_rate}",
            ]
            graph.append(f"{audio_input}{','.join(audio_filters)}{audio_label}")
            continue

        duration = _decimal(item["duration"])
        card_background = _ff_color(_color(item["background"], "card.background"))
        text_color = _color(item["text_color"], "card.text_color")
        subtitle = str(item.get("subtitle", ""))
        font_path: Optional[Path] = None
        if item.get("font_file") is not None:
            font_path = _resolve_path(
                item["font_file"],
                f"plan.sequence[{index}].font_file",
                plan.plan_path.parent,
            )
        card_filters = [
            f"color=c={card_background}:s={plan.width}x{plan.height}:r={fps}:d={duration}",
            "format=pix_fmts=yuv420p",
            "setsar=1",
            "settb=AVTB",
        ]
        title_y = "h*0.43-text_h/2" if subtitle else "(h-text_h)/2"
        card_filters.append(
            _drawtext_filter(
                text=str(item["title"]),
                size=int(item["title_size"]),
                color=text_color,
                y=title_y,
                font_path=font_path,
            )
        )
        if subtitle:
            card_filters.append(
                _drawtext_filter(
                    text=subtitle,
                    size=int(item["subtitle_size"]),
                    color=text_color,
                    y="h*0.59-text_h/2",
                    font_path=font_path,
                )
            )
        graph.append(f"{','.join(card_filters)}{video_label}")
        graph.append(
            f"anullsrc=r={plan.sample_rate}:cl={plan.channel_layout}:d={duration},"
            f"atrim=duration={duration},asetpts=PTS-STARTPTS,"
            f"aformat=sample_fmts=fltp:sample_rates={plan.sample_rate}:"
            f"channel_layouts={plan.channel_layout},"
            f"asettb=expr=1/{plan.sample_rate}{audio_label}"
        )

    concat_inputs = "".join(f"[v{index}][a{index}]" for index in range(len(plan.sequence)))
    graph.append(
        f"{concat_inputs}concat=n={len(plan.sequence)}:v=1:a=1[vcat][acat]"
    )
    graph.append("[vcat]format=pix_fmts=yuv420p[vout]")
    loudnorm_options = [
        f"I={_decimal(plan.integrated_lufs)}",
        f"TP={_decimal(plan.true_peak_db)}",
        f"LRA={_decimal(plan.loudness_range_lu)}",
    ]
    if plan.channel_layout == "mono":
        loudnorm_options.append("dual_mono=true")
    graph.append(
        f"[acat]loudnorm={':'.join(loudnorm_options)},"
        f"aresample={plan.sample_rate},"
        f"aformat=sample_fmts=fltp:sample_rates={plan.sample_rate}:"
        f"channel_layouts={plan.channel_layout}[aout]"
    )
    return ";\n".join(graph)


def build_ffmpeg_command(
    plan: EditPlan,
    ffmpeg: str,
    source_order: Sequence[str],
    filter_graph: str,
    overwrite: bool,
) -> List[str]:
    command = [ffmpeg, "-hide_banner", "-nostdin", "-y" if overwrite else "-n"]
    for source_name in source_order:
        command.extend(["-i", str(plan.sources[source_name].path)])
    command.extend(
        [
            "-filter_complex",
            filter_graph,
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-map_metadata",
            "-1",
            "-map_chapters",
            "-1",
            "-c:v",
            "libx264",
            "-preset",
            plan.preset,
            "-crf",
            str(plan.crf),
            "-pix_fmt",
            "yuv420p",
            "-r",
            _decimal(plan.fps),
            "-c:a",
            "aac",
            "-b:a",
            plan.audio_bitrate,
            "-ar",
            str(plan.sample_rate),
            "-ac",
            str(plan.channels),
            "-movflags",
            "+faststart",
            str(plan.output_path),
        ]
    )
    return command


def _timeline_duration(plan: EditPlan) -> float:
    total = 0.0
    for item in plan.sequence:
        if item["type"] == "clip":
            total += float(item["end"]) - float(item["start"])
        else:
            total += float(item["duration"])
    return total


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a portable edit-plan.json, construct an FFmpeg filter graph, "
            "and render an H.264/AAC MP4. All plan and media checks finish before "
            "FFmpeg is started."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  render_video.py edit-plan.json --validate-only
  render_video.py edit-plan.json --dry-run --filtergraph-out build/filtergraph.txt
  render_video.py edit-plan.json --overwrite --print-command

Relative paths inside the plan are resolved from the plan file's directory.
The plan schema is in ../references/edit-plan.schema.json.
""",
    )
    parser.add_argument("plan", type=Path, help="path to portable edit-plan.json")
    parser.add_argument(
        "--ffmpeg", default="ffmpeg", help="FFmpeg executable name or path (default: ffmpeg)"
    )
    parser.add_argument(
        "--ffprobe", default="ffprobe", help="ffprobe executable name or path (default: ffprobe)"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="allow replacement of an existing output MP4"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--validate-only",
        action="store_true",
        help="validate JSON, paths, streams, crops, and intervals without rendering",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and print the exact FFmpeg command without rendering",
    )
    parser.add_argument(
        "--filtergraph-out",
        type=Path,
        help="also write the generated filter graph to this path",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="print the shell-quoted FFmpeg command before rendering",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    try:
        plan = load_plan(args.plan)
        validate_referenced_files(plan)
        ffprobe = _resolve_executable(args.ffprobe, "ffprobe")
        validate_media(plan, ffprobe)
        source_order = sorted(plan.sources)
        filter_graph = build_filter_graph(plan, source_order)

        if args.filtergraph_out is not None:
            graph_path = args.filtergraph_out.resolve(strict=False)
            graph_path.parent.mkdir(parents=True, exist_ok=True)
            graph_path.write_text(filter_graph + "\n", encoding="utf-8")

        if args.validate_only:
            print(
                f"valid: {len(plan.sequence)} item(s), {len(plan.sources)} source(s), "
                f"{_timeline_duration(plan):.3f}s timeline"
            )
            return 0

        ffmpeg = _resolve_executable(args.ffmpeg, "ffmpeg")
        if plan.output_path.exists() and not args.overwrite:
            raise PlanError(
                f"output already exists: {plan.output_path} "
                "(pass --overwrite to replace it)"
            )
        command = build_ffmpeg_command(
            plan, ffmpeg, source_order, filter_graph, args.overwrite
        )
        if args.dry_run or args.print_command:
            print(shlex.join(command))
        if args.dry_run:
            return 0

        plan.output_path.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(command, check=False)
        if completed.returncode:
            print(f"error: FFmpeg exited with status {completed.returncode}", file=sys.stderr)
            return completed.returncode
        print(f"rendered: {plan.output_path}")
        return 0
    except PlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
