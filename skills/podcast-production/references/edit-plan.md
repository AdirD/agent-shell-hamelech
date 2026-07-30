# Portable `edit-plan.json` reference

Read this when converting an approved editorial handoff into the renderer's strict JSON contract. The machine-readable companion is [`edit-plan.schema.json`](edit-plan.schema.json); `scripts/render_video.py` performs the same structural checks plus cross-field, filesystem, stream, crop-bound, duration, overlap, and output-safety checks.

## Boundary between editorial and production

`approved-script.md` remains the editorial source of truth. It must contain the source inventory, constraints, target runtime, premise, ordered speaker turns with verbatim text and rough source windows, explicit omissions, visual notes, and an explicit approval status. Those windows are search hints, not edit decisions.

Create `edit-plan.json` only after approval. Recover timestamps from the media, align each approved turn to complete recorded phrase boundaries, and put those recovered source times in clip items. If the approved wording cannot be found exactly, return to editorial review; do not rewrite, synthesize, or silently shorten the quote.

All relative paths are resolved from the directory containing `edit-plan.json`. Keep media, the approved handoff, optional fonts, and output paths relative when the project may move between machines. Environment-variable expansion is intentionally unsupported.

## Top-level fields

| Field | Meaning |
|---|---|
| `version` | Schema version; currently exactly `1`. |
| `approval` | Binds production to an explicitly approved handoff. The helper requires `status: "approved"` and an existing `script_path`. |
| `sources` | Named input media. Each entry declares a path and zero-based video/audio stream ordinals. |
| `output` | Destination `.mp4`; it may not overwrite a source or the approved handoff. |
| `canvas` | Even output width/height, positive fps, and the background used for `contain` padding. |
| `audio` | Sample rate, mono/stereo layout, AAC bitrate, and EBU R128 loudness targets. |
| `encoding` | Explicit fixed codecs (`libx264`, `aac`, `yuv420p`) plus x264 preset and CRF. |
| `speaker_crops` | Named source rectangles and how each rectangle fits the canvas. |
| `sequence` | The final reading order as clip and editorial-card items. Array order is output order. |

The helper rejects unknown fields rather than guessing what a misspelling meant. It also rejects declared sources or crops that are never used.

## Named speaker crops

A crop is a rectangle in source pixels:

```json
"guest": {
  "source": "call",
  "x": 1920,
  "y": 0,
  "width": 1920,
  "height": 1080,
  "fit": "cover",
  "anchor_x": 0.5,
  "anchor_y": 0.5
}
```

This is how a side-by-side recording is turned into full-frame speaker shots without embedding any interview-specific dimensions in the renderer. Inspect the actual source with `ffprobe`, then configure the correct rectangles.

- `cover` preserves aspect ratio, fills the canvas, then trims overflow around the normalized anchor.
- `contain` preserves the whole crop and pads it with `canvas.background`.
- `anchor_x` and `anchor_y` range from `0` to `1`; `0.5` centers the cover crop. They remain explicit for both fit modes so plans are self-describing.

Every clip names both its source and speaker crop. The crop must belong to that source, and its rectangle must fit within the probed source dimensions.

## Sequence items and provenance

### Clip

```json
{
  "type": "clip",
  "id": "guest-surprising-claim",
  "provenance": "verbatim",
  "source": "call",
  "speaker_crop": "guest",
  "start": 312.44,
  "end": 320.91,
  "verbatim": "<VERBATIM: copy the exact approved recorded phrase>"
}
```

`start` is inclusive and `end` is exclusive, in seconds on the named source. They must describe one complete recorded phrase: no clipped initial consonant, missing final word, or splice that changes meaning. The `verbatim` field is an audit field and is not drawn on screen. Copy the approved, source-verified words; do not put a paraphrase there.

Clip intervals from the same source may be reordered, but may not overlap. Overlap commonly repeats a word or breath at a cut and can duplicate an approved quote. The helper rejects it. Also compare normalized quote text and item IDs while building the plan so the same approved turn is not accidentally inserted twice at two different source locations.

### Card

```json
{
  "type": "card",
  "id": "title",
  "provenance": "editorial",
  "role": "title",
  "duration": 2.4,
  "title": "A concise episode title",
  "subtitle": "Edited interview excerpt",
  "background": "#111318",
  "text_color": "#F4F4F2",
  "title_size": 56,
  "subtitle_size": 28
}
```

Card roles are `title`, `editorial_summary`, `interstitial`, or `outro`. Card text is explicitly editorial, never represented as a speaker quote. If a card summarizes a claim, make that status visible in its wording (for example, “Editorial summary”) as well as in `provenance`. Cards carry silence so the clip/card sequence can be concatenated as a single audio/video timeline.

`font_file` is optional and is resolved relative to the plan. When omitted, FFmpeg's configured default font is used. The helper never assumes a machine-specific font path. Keep title treatment restrained and verify glyph coverage, line length, and safe margins from rendered stills.

Narration is intentionally not a sequence type in version 1. Do not disguise generated or editorial narration as a `clip`. Either use a labeled card or revise the schema and renderer under explicit editorial approval.

## Complete generic example

The values below demonstrate a configurable 3840×1080 side-by-side source. The angle-bracketed `verbatim` values are instructions, not purported dialogue; replace them with exact phrases verified against the recording.

```json
{
  "version": 1,
  "approval": {
    "status": "approved",
    "script_path": "approved-script.md"
  },
  "sources": {
    "call": {
      "path": "media/interview.mp4",
      "video_stream": 0,
      "audio_stream": 0
    }
  },
  "output": {
    "path": "renders/short-podcast.mp4"
  },
  "canvas": {
    "width": 1280,
    "height": 720,
    "fps": 30,
    "background": "#111318"
  },
  "audio": {
    "sample_rate": 48000,
    "channel_layout": "stereo",
    "bitrate": "192k",
    "loudness": {
      "integrated_lufs": -16,
      "true_peak_db": -1.5,
      "range_lu": 11
    }
  },
  "encoding": {
    "video_codec": "libx264",
    "audio_codec": "aac",
    "pixel_format": "yuv420p",
    "preset": "medium",
    "crf": 18
  },
  "speaker_crops": {
    "host": {
      "source": "call",
      "x": 0,
      "y": 0,
      "width": 1920,
      "height": 1080,
      "fit": "cover",
      "anchor_x": 0.5,
      "anchor_y": 0.5
    },
    "guest": {
      "source": "call",
      "x": 1920,
      "y": 0,
      "width": 1920,
      "height": 1080,
      "fit": "cover",
      "anchor_x": 0.5,
      "anchor_y": 0.5
    }
  },
  "sequence": [
    {
      "type": "card",
      "id": "title",
      "provenance": "editorial",
      "role": "title",
      "duration": 2.4,
      "title": "A concise episode title",
      "subtitle": "Edited interview excerpt",
      "background": "#111318",
      "text_color": "#F4F4F2",
      "title_size": 56,
      "subtitle_size": 28
    },
    {
      "type": "clip",
      "id": "host-question",
      "provenance": "verbatim",
      "source": "call",
      "speaker_crop": "host",
      "start": 101.24,
      "end": 106.82,
      "verbatim": "<VERBATIM: exact complete recorded host question>"
    },
    {
      "type": "clip",
      "id": "guest-answer",
      "provenance": "verbatim",
      "source": "call",
      "speaker_crop": "guest",
      "start": 107.31,
      "end": 118.67,
      "verbatim": "<VERBATIM: exact complete recorded guest answer>"
    },
    {
      "type": "card",
      "id": "outro",
      "provenance": "editorial",
      "role": "outro",
      "duration": 2.0,
      "title": "End card",
      "subtitle": "",
      "background": "#111318",
      "text_color": "#F4F4F2",
      "title_size": 48,
      "subtitle_size": 28
    }
  ]
}
```

## Validation and render behavior

Run from any working directory; plan-relative paths remain stable. Here `<skill-root>` is the directory containing this module's `SKILL.md`, whether standalone or nested under a larger skill:

```bash
python3 <skill-root>/scripts/render_video.py path/to/edit-plan.json --validate-only
python3 <skill-root>/scripts/render_video.py path/to/edit-plan.json --dry-run --filtergraph-out path/to/filtergraph.txt
python3 <skill-root>/scripts/render_video.py path/to/edit-plan.json --overwrite --print-command
```

Validation is deliberately front-loaded:

1. Parse strict JSON, including rejection of duplicate keys and non-finite numbers.
2. Validate every field, type, enum, range, reference, item ID, interval, overlap, and unused declaration.
3. Confirm the approved handoff, sources, and optional fonts exist and output cannot overwrite an input.
4. Use `ffprobe` to confirm selected video/audio streams, dimensions, duration, crop bounds, and clip ends.
5. Only then resolve and invoke `ffmpeg` (unless validation or dry-run mode was selected).

The generated graph splits each source stream when several clips use it; trims audio and video at the same recovered source boundaries; resets timestamps; crops, scales, and pads each speaker shot; creates silent cards; concatenates the ordered items; and applies `loudnorm` to the complete program. Output is H.264 (`libx264`) plus AAC in an MP4 with `yuv420p` and `+faststart`.

Single-pass `loudnorm` makes the render repeatable and enforces the plan target, but it does not replace listening. Verify perceived level, clipping, and the transition between silent cards and speech in the final media.
