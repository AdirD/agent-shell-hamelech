---
name: podcast-production
description: Turn long interviews, meetings, webinars, panels, or recorded conversations into a short, user-approved podcast story and finished video. Use this skill whenever the user wants to find the best storyline, compare editorial angles, script a short cut, pull the strongest clips, iterate on an interview narrative, or edit/render/verify an approved podcast video—even if they ask for only one stage or never use the word podcast. It provides two intents: collaborative storyline development from raw media/transcripts, and source-faithful FFmpeg production from an approved script.
compatibility: Storyline work needs readable media/transcripts and standard research tools. Video production requires Python 3.9+, ffmpeg, and ffprobe; a Whisper-compatible word-timestamp transcriber is optional.
---

# Podcast production

Use one skill for the complete editorial-to-video workflow while keeping the two phases independently invokable.

## Select the intent

| User state or request | Intent to load |
|---|---|
| Raw recording/transcript; story is undecided; asks for themes, options, script, clips, or a shorter narrative | Read [intents/storyline.md](intents/storyline.md) |
| A named script/version is already locked and the user asks to cut, render, assemble, or verify video | Read [intents/video-edit.md](intents/video-edit.md) |
| End-to-end request from a long recording to a finished short | Run storyline first; after the user unequivocally selects a named version and authorizes production, continue with video edit |
| Existing `edit-plan.json` needs audit, rendering, or verification | Read [intents/video-edit.md](intents/video-edit.md) |

Do not load both intent files when only one phase is requested. The shared handoff is `approved-script.md`: storyline creates it after approval; video edit treats it as immutable editorial input.

## Shared invariants

1. Recorded media is the authority. Transcripts and rough windows are search aids.
2. Never invent, rewrite, or silently reconstruct spoken dialogue. Label authored cards or narration as editorial material.
3. Apply privacy, legal, employer, client, and confidentiality exclusions across every active option and production handle.
4. Preserve user agency. Storyline work presents genuinely distinct options and iterates; media production starts only after an unequivocal named selection.
5. Rough transcript-derived windows are never frame-accurate. The editor must recover timestamped audio and align complete recorded phrase boundaries.
6. If source audio contradicts the approved text, return the discrepancy for editorial review instead of substituting a nearby phrase.
7. Completion requires the phase-specific evidence: a complete approved handoff for storyline, or a fully decoded and visually inspected final media file for video edit.

## Resource map

- Story method: [references/editorial-method.md](references/editorial-method.md)
- Working options template: [templates/editorial-options.md](templates/editorial-options.md)
- Approved handoff template: [templates/approved-script.md](templates/approved-script.md)
- Edit-plan contract: [references/edit-plan.md](references/edit-plan.md)
- JSON Schema: [references/edit-plan.schema.json](references/edit-plan.schema.json)
- Deterministic renderer: [scripts/render_video.py](scripts/render_video.py)

## Handoff boundary

`approved-script.md` contains source inventory, constraints, runtime, premise, ordered verbatim turns with rough source windows, omissions, visual notes, and approval evidence. It deliberately does not claim exact cut points. The video intent aligns each approved turn to timestamped source audio, writes a portable `edit-plan.json`, renders it with the bundled helper, and verifies the output end to end.
