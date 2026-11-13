# Image-to-video and text-to-video

How the three families installed on AIOps are usually driven, including the Graydient workflow names Andrew already uses. This is usage guidance, not a substitute for a per-LoRA row in `families/`.


## Choosing LoRAs for a prompt upgrade

This guide is about prompt shape and Graydient workflow names. For *which* LoRA to hang on the graph, use [`SKILL.md`](../SKILL.md) (98 goal recipes) and [`prompt-patterns.md`](prompt-patterns.md) and the family tables. Installed LoRAs are listed first.

Official speed and control packs that are usually **not** on the RAID — LightX2V / CausVid distill LoRAs for Wan, Lightricks LTX-2/2.3/2.5 camera-control and IC-LoRAs, Pika H3 Flex, MiniMax H3 turbo and character-swap — are in the SKILL recipes and in `guides/fuzzpuppy-directory.md`. They are workflow-specific; do not treat an IC-LoRA as a drop-in I2V style adapter.

## MiniMax H3

H3 generates video **and** synchronized audio. LoRAs may be I2V, T2V, Ref2VA, or several of those; check the row.

### Graydient workflows

- **`omni-eros-new-h3`** — image-to-video from a still (`/image1:`). This is the current NSFW I2V path used with kromoss stills (the live workflow list also has the older slug `omni-eros-h3`). Observed working recipe from a Nov 2026 success run: `/size:640x640` `/length:200`, still attached as `/image1:`. That size/length is an observed recipe, not a universal default.
- **`extend-h3`** — extend an existing H3 clip with audio. The workflow conditions on the last few seconds of the source video.
- **`extendturbo-h3`** — the same job with a turbo / few-step H3 stack. Faster, usually less fidelity. Use the matching turbo LoRA only when the workflow expects it (`minimax-h3-turbo-loras-h3` is the verified installed turbo pack).

Other live H3 slugs (`animate-h3`, `video-h3`, `videoturbo-h3`, `animateturbo-h3`, Ref2VA editors) exist on Graydient; they are not the three named above.

### Prompt structure (I2V)

H3 responds well to a structured block rather than a single SD-style tag line. A working pattern:

```
subject_definitions:
<Subject 1> is the person in <Picture 1>, with [identity details you must keep].

summary:
[reference generation] The target video shows <Subject 1> [framing, action, and speech intent].

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - [list the features that must not drift from <Picture 1>].

detailed_description:
The target video is [camera, lighting, space].
[Shot 1] [Visible action, hands, props, one or two motions only.]
She speaks … </d\\> [language] DIALOGUE. </d\\> </d\\>
[Breaths, moans, Foley.]

overall_soundscape:
[Room tone, cloth/latex/skin, breathing.]

non_diegetic_music:
[Optional, keep it under the voice.]
```

For I2V, **retention** is the important part: name the features from the still that must stay (hair, face, wardrobe, anatomy, prop state). Keep the shot count low. Put LoRA trigger words in the prompt where the row says to; do not invent any.

T2V (no still) drops `retention_analysis` and `<Picture 1>`, and has to do more work in `subject_definitions`.

## Wan 2.2

Graydient: **`animate-wan22`** is the speed-optimized I2V graph (supports LoRAs). **`video-wan22`** is the T2V counterpart. Older `video-wan22-lora` is marked outdated in the live list.

Wan 2.2 14B I2V-A14B and T2V-A14B are **dual-noise** models:

- Use a **HIGH + LOW** LoRA pair for the same concept when both were trained.
- Same strength on both ends unless a page says otherwise (most pages here do not).
- Do not put a 5B TI2V LoRA (`Wan Video 2.2 TI2V-5B`) on a 14B graph, or a Wan 2.1 480p LoRA on a 2.2 sampler, without a reason.

Prompt style is natural language, usually with the trigger at the front:

```
<trigger>, [shot size and camera], [who is in frame], [the action in time order], [lighting]
```

The local `b7` test is T2V high-noise only, trigger `b7vhs`, trained around 17 frames / 480p / 16 fps. Example from its README:

```
b7vhs, three women in a dark brick dungeon, white lingerie, locked-off wide shot, they slowly move together
```

## LTX-2 / 2.3 / 2.5

Graydient: **`animate-ltx2`** / **`animate-ltx23`** / **`animate-ltx25`** are image-to-video with built-in audio. **`video-ltx2`** / **`video-ltx23`** / **`video-ltx25`** are text-to-video with built-in audio. `extend-ltx23` extends a clip.

The model is prompted in **natural language**. Describe the shot, the motion, and the sound in prose. Put the LoRA trigger in the prompt when the row has one (`taker pov`, `sexy`, `PENISLORA`, …).

A general LTX I2V shape:

```
<trigger if any>. A [camera] shot of [subject as they appear in the start frame].
[What moves, how fast, what stays still.]
Audio: [room, body, voice].
```

Match the LoRA's `base` (`LTXV2` vs `LTXV 2.3` vs `LTXV 2.5`) to the workflow when you can. Official Lightricks camera-control and IC-LoRAs are listed in `guides/fuzzpuppy-directory.md`; they are mostly not on the RAID snapshot this catalog starts from.

## Cross-family notes

- A still that already reads as the act often needs less LoRA than a still that does not.
- When a row says strength `not stated`, make a short test clip before a long one.
- H3 audio LoRAs will not fix Wan or LTX speech. Use them on H3.
