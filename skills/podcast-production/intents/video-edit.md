# Podcast video editor

Convert an approved editorial handoff into a reproducible media edit without changing the story or inventing speech. The production boundary matters: source-window estimates help locate material, but only timestamped audio and direct listening establish cut points.

## Resources

| Read/use | Purpose |
|---|---|
| [`references/edit-plan.md`](../references/edit-plan.md) | Plan semantics, complete generic example, crop behavior, and render contract. Read before authoring a plan. |
| [`references/edit-plan.schema.json`](../references/edit-plan.schema.json) | Portable JSON Schema for tooling and editor validation. |
| [`scripts/render_video.py`](../scripts/render_video.py) | Stdlib-only validator and deterministic FFmpeg renderer. Run rather than rebuilding the filter graph by hand. |

`<skill-root>` means the parent `podcast-production/` directory containing `intents/`, `references/`, `templates/`, and `scripts/`.

## Non-negotiable production gate

Start video editing only when `approved-script.md` exists and its approval status is explicit. If the status is draft, pending, ambiguous, or changed by later feedback, stop at editorial iteration; do not create a production plan or render.

Treat the approved handoff as immutable input. It should provide:

- source inventory and paths;
- privacy, legal, employer, brand, or topic exclusions;
- target runtime and premise;
- ordered speaker turns with verbatim text and rough source windows;
- explicit omissions and rejected options;
- visual notes; and
- approval status.

Retain the editorial decision log when it explains exclusions or rejected endings. Apply legal/privacy exclusions to every candidate window and every usable option, not merely to obvious names. Never let excluded surrounding material leak through a generous audio handle, subtitle, card, filename, or metadata field.

## Truth and provenance rules

- A clip is recorded speech. Its `verbatim` value must be the complete phrase actually present in the selected audio.
- A rough source window in `approved-script.md` is an editorial estimate, never a frame-accurate claim.
- A card, summary, or other authored bridge is editorial. Label it as editorial in the plan and make any claim-summary status clear to viewers.
- Do not manufacture connective dialogue, join fragments into a sentence the speaker never said, or repair wording silently.
- If recording and approved text differ, show the discrepancy and return it for approval. Do not “close enough” the quote.
- Version 1 supports recorded clips and editorial cards, not narration. Never disguise generated narration as a clip.

## Workflow

### 1. Read the approved handoff and make a production checklist

Extract the ordered turn IDs, exact text, rough windows, speaker identities, target runtime, omissions, and visual direction. Build two small ledgers before touching timestamps:

1. **Eligibility ledger:** every approved turn and every exclusion that could affect its surrounding audio.
2. **Use ledger:** one row per approved turn with source, recovered interval, and final sequence position. This catches accidental duplicate quotes.

Do not defend or reinsert discarded material. The approved arc—not the available footage—sets the edit.

### 2. Inspect dependencies and media

Required tools:

```bash
ffmpeg -version
ffprobe -version
```

Probe every candidate source before choosing crops or times:

```bash
ffprobe -v error \
  -show_entries format=filename,duration,start_time:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channel_layout,duration \
  -of json path/to/source-media
```

Record the selected zero-based video/audio stream ordinals, frame dimensions, duration, frame rate, sample rate, and channel layout. Never assume source dimensions, split position, stream order, or a local font path.

### 3. Recover timestamps from the recording

Transcript-position guesses are unsafe. Speech rate, pauses, edits, questions, and transcript omissions are nonuniform, so “this quote is 40% through the text, therefore 40% through the video” can land minutes away or cut the wrong statement. Use rough windows only to narrow the search.

For each approved turn:

1. Expand its rough window enough to include natural phrase boundaries, while excluding prohibited neighboring material.
2. Extract or transcribe that candidate window. A mono 16 kHz WAV is a portable transcription input:

   ```bash
   ffmpeg -v error -ss <rough-start-seconds> -t <window-duration-seconds> \
     -i path/to/source-media -vn -ac 1 -ar 16000 candidate-turn.wav
   ```

3. If a Whisper-compatible tool is available, request word timestamps. Add the candidate window's source offset to local word times before writing source times.
4. Find the exact approved wording in the timestamped result, then listen across both edges. Automatic word times are candidates, not final authority.
5. Put the in-point before the first phoneme and the out-point after the complete final word/natural release. Do not cut breaths so tightly that a recorded phrase sounds synthetic, and do not include the first word of the next excluded sentence.
6. Re-listen to the isolated phrase and compare every word against the approved turn.

Parallelize independent candidate-window transcription when it saves time: create one immutable audio window and one timestamp output per turn, run disjoint windows concurrently, then merge results into the use ledger in approved reading order. Do not let workers edit one shared plan. Resolve overlaps, exclusions, discrepancies, and sequence order centrally before rendering.

If no word-timestamp transcriber is available, use repeated narrow audio extracts, waveform/spectrogram inspection, and listening. Never fall back to transcript-position arithmetic.

### 4. Confirm sentence boundaries and uniqueness

Before authoring JSON, review the recovered intervals as a set:

- each interval contains one complete recorded phrase;
- no same-source intervals overlap;
- no normalized approved quote or turn ID appears twice;
- speaker/source/crop identity is correct;
- the assembled clip durations plus cards fit the target runtime;
- excluded or rejected material does not appear inside cut handles; and
- the final turn lands on the approved ending rather than a previously discarded one.

A source can be edited out of chronology, but the final reading order must still preserve the approved meaning. Any material semantic change returns to editorial approval.

### 5. Design the visual treatment from probed dimensions

For split-screen media, define one named crop rectangle per used speaker/angle in `speaker_crops`. Preview representative frames before committing:

```bash
ffmpeg -v error -ss <source-seconds> -i path/to/source-media \
  -vf "crop=<width>:<height>:<x>:<y>,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720" \
  -frames:v 1 crop-preview.png
```

Use `cover` for a full-bleed speaker shot and tune normalized anchors to keep eyes/faces framed. Use `contain` when the entire source rectangle must remain visible. Source and canvas dimensions belong in `edit-plan.json`; never patch interview-specific coordinates into the renderer.

Prefer restrained title/outro cards, readable typography, clean hard cuts, and the actual people. Do not add fake AI-HUD scans, synthetic dashboards, or decorative “analysis” graphics that imply capabilities or evidence not present in the interview. An optional font must be a plan-relative asset; otherwise let FFmpeg use its configured default and inspect the result.

### 6. Build the portable plan

Read [`references/edit-plan.md`](../references/edit-plan.md), then create `edit-plan.json` beside the handoff or in its production directory. Validate it against [`references/edit-plan.schema.json`](../references/edit-plan.schema.json) if a JSON Schema tool is available.

The plan must carry:

- `approval.status: "approved"` and the path to `approved-script.md`;
- named source and output paths, preferably relative to the plan;
- canvas width/height/fps/background;
- sample rate, channel layout, AAC bitrate, and loudness targets;
- explicit H.264/AAC encoding settings;
- source-pixel named speaker crops with fit/anchors; and
- an ordered `sequence` of `clip` and `card` items.

For every clip, copy the source-verified approved phrase into `verbatim` and use recovered source times—not the rough handoff window. Set clip provenance to `verbatim`. Set card provenance to `editorial` and choose a role (`title`, `editorial_summary`, `interstitial`, or `outro`). Keep authored cards out of quotation marks that could imply speech.

### 7. Validate, inspect the graph, and render

The helper is stdlib-only and performs strict plan validation before FFmpeg can run. It also probes media to reject missing streams, out-of-bounds crops, out-of-duration cuts, overlapping source intervals, unused declarations, unsafe output paths, and malformed/unknown fields.

```bash
python3 <skill-root>/scripts/render_video.py path/to/edit-plan.json --help
python3 <skill-root>/scripts/render_video.py path/to/edit-plan.json --validate-only
python3 <skill-root>/scripts/render_video.py path/to/edit-plan.json \
  --dry-run --filtergraph-out path/to/filtergraph.txt
python3 <skill-root>/scripts/render_video.py path/to/edit-plan.json \
  --overwrite --print-command
```

The generated graph trims/reset-timestamps each audio/video clip, applies its named crop and cover/contain treatment, creates silent cards, concatenates in array order, normalizes the completed audio program with `loudnorm`, and encodes H.264/AAC MP4 with `yuv420p` and `+faststart`.

Do not bypass a validation error with a hand-written FFmpeg command. Fix the source plan or return an editorial mismatch for approval.

## End-to-end verification

Rendering success is not completion. Set `OUT` to the output path and run every check below.

### 1. Container, streams, codecs, dimensions, fps, and duration

```bash
OUT="path/to/final.mp4"
ffprobe -v error \
  -show_entries format=filename,format_name,duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channel_layout \
  -of json "$OUT"
```

Confirm H.264 video, AAC audio, configured canvas/fps/pixel format/sample rate/layout, plausible duration, and exactly the intended streams.

### 2. Complete decode

```bash
ffmpeg -v error -i "$OUT" -map 0:v:0 -map 0:a:0 -f null -
```

Any output is a failure to investigate; a zero exit with no diagnostics proves the whole file decodes, not merely its header.

### 3. Contact sheet and representative visual inspection

```bash
# First set INTERVAL_SECONDS to output_duration / 16, as a numeric value.
ffmpeg -v error -i "$OUT" \
  -vf "fps=1/${INTERVAL_SECONDS},scale=320:-2,tile=4x4:padding=4:margin=4" \
  -frames:v 1 contact-sheet.jpg
```

Compute output-timeline midpoints from the ordered plan, then extract at least one title, each named speaker crop, and the outro:

```bash
ffmpeg -v error -ss <title-midpoint> -i "$OUT" -frames:v 1 title-check.png
ffmpeg -v error -ss <speaker-a-midpoint> -i "$OUT" -frames:v 1 speaker-a-check.png
ffmpeg -v error -ss <speaker-b-midpoint> -i "$OUT" -frames:v 1 speaker-b-check.png
ffmpeg -v error -ss <outro-midpoint> -i "$OUT" -frames:v 1 outro-check.png
```

Inspect actual images—not just command success—for crop identity, face framing, aspect ratio, card legibility, font fallback/glyphs, safe margins, cut order, and restrained treatment. For more than two speakers/angles, extract one still for each named crop.

### 4. Silence gaps

```bash
ffmpeg -hide_banner -nostats -i "$OUT" \
  -af "silencedetect=noise=-35dB:d=0.5" -f null - 2>silence.log
```

Review every detected interval against cumulative sequence times. Silence on title/outro cards is expected; unexplained silence inside or between speaker clips can indicate a bad boundary, missing channel, or concat error. Listen around every reported interior gap.

### 5. Black frames

```bash
ffmpeg -hide_banner -nostats -i "$OUT" \
  -vf "blackdetect=d=0.20:pix_th=0.10" -an -f null - 2>black.log
```

Reconcile every report with intentional dark cards. Unexplained black at clip boundaries, throughout a speaker item, or after the expected end is a render defect. Dark card designs still require direct image inspection because an intentional near-black background can trigger this detector.

### 6. Final human pass

Watch the output from start to finish with sound. Verify exact words and sentence boundaries against the use ledger; no duplicated approved quote; natural pacing; correct speaker crop on every turn; no legal/privacy leakage; reasonable loudness; and the approved ending. If any quote, omission, or story order must change, return to explicit approval before making the new render.
