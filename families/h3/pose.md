# H3: Pose / control

2 accessible LoRAs (1 on both Graydient and AIOps, 1 Graydient-only, 0 AIOps-only). Accessible rows are listed first (both, then AIOps, then Graydient), then by download count. The 13 Nov 2026 RAID snapshot is the AIOps source.

Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.

| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |
|---|---|---|---|---|---:|---|---|
| `jacko-pose-minimax-h3-v1-h3` | — | not stated | not stated | Jacko pose minimax h3 v1 | 2,301 | Graydient+AIOps, verified | [CivitAI](https://civitai.com/models/2961690?modelVersionId=3355328) |
| `zero-two-dance` | `doing the zero-two dance` | not stated | not stated | Zero-Two Dance | 5,226 | Graydient, verified | [CivitAI](https://civitai.com/models/1819613?modelVersionId=3264304) |

## Suggest ingest

These are **not** on Graydient or the AIOps RAID yet. Suggestion only — download and ingest them yourself with the civit-to-graydient pipeline if you want them. **Nothing here is auto-downloaded.**

| slug / file | trigger | strength | downloads | ingest priority | why | links |
|---|---|---|---:|---:|---|---|
| `bfs-best-face-swap` | `body_swap: subject_definitions: <Subject 1> is the {details} shown in <Picture 1>, whose identity, face, head, hair or fur, skin, body shape, proportions and clothing define the character in the target video. The guide video provides the scene and the performance: its background, environment, lighting, camera, framing, body pose, hand and arm movement, head rotation, gaze direction, lip movement and facial expression, frame by frame; only the main subject of the guide video is replaced: its face, hair, body and clothing become <Subject 1>.  summary: [video generation + reference] Replace the guide subject with <Subject 1>, keeping the scene, camera and the complete motion and performance of the guide video.  detailed_description: [Shot 1] <Subject 1> takes the exact place of the guide subject and moves with the same timing, body pose, gestures, head motion, gaze, speech and facial expressions, while keeping the complete identity from <Picture 1>: facial structure, hair or fur, skin, body shape and clothing stay stable in every frame. The background, lighting, colors and camera of the guide video are preserved. Prevent identity drift, clothing changes, texture crawling and flicker.`, `body_swap:  subject_definitions: <Subject 1> is the {details} shown in <Picture 1>, whose identity, face, head, hair or fur, skin, body shape, proportions and clothing define the character in the target video. The guide video provides the scene and the performance: its background, environment, lighting, camera, framing, body pose, hand and arm movement, head rotation, gaze direction, lip movement and facial expression, frame by frame; only the main subject of the guide video is replaced: its face, hair, body and clothing become <Subject 1>.  summary: [video generation + reference] Replace the guide subject with <Subject 1>, keeping the scene, camera and the complete motion and performance of the guide video.  detailed_description: [Shot 1] <Subject 1> takes the exact place of the guide subject and moves with the same timing, body pose, gestures, head motion, gaze, speech and facial expressions, while keeping the complete look from <Picture 1>: head, face, skin, hair or fur, body shape and clothing stay stable in every frame, with no trace of the original subject's face, hair or clothing. The background, lighting, colors and camera of the guide video are preserved. Prevent identity drift, clothing changes, texture crawling and flicker. The result is a real, photographic video.`, `body_swap:  subject_definitions: <Subject 1> is the {details} shown in <Picture 1>, whose identity, face, head, hair or fur, skin, body shape, proportions and clothing define the character in the target video. The guide video provides the scene and the performance: its background, environment, lighting, camera, framing, body pose, hand and arm movement, head rotation, gaze direction, lip movement and facial expression, frame by frame; only {target} is replaced: their face, hair, body and clothing become <Subject 1>.  summary: [video generation + reference] Replace {target} in the guide video with <Subject 1>, keeping the scene, camera and the complete motion and performance of the guide video.  detailed_description: [Shot 1] <Subject 1> takes the exact place of {target} and moves with the same timing, body pose, gestures, head motion, gaze, speech and facial expressions, while keeping the complete look from <Picture 1>: head, face, skin, hair or fur, body shape and clothing stay stable in every frame, with no trace of the original subject's face, hair or clothing. The background, lighting, colors and camera of the guide video are preserved. Prevent identity drift, clothing changes, texture crawling and flicker. The result is a real, photographic video.`, `Use the workflow auto-prompt.` | not stated | 110,030 | 220.4 | high-value upgrade (110,030 downloads, ≥2× the top accessible) | [CivitAI](https://civitai.com/models/2027766?modelVersionId=3412620) |
| `accelerator-loras` | — | not stated | 25,313 | 197.8 | high-value upgrade (25,313 downloads, ≥2× the top accessible); official utility pack with no accessible equivalent | [CivitAI](https://civitai.com/models/1063735?modelVersionId=3213016) |
| `redcraft-dark-beast-loras` | `Exploded View Diagram` | 0.7–1 | 11,358 | 188.1 | high-value upgrade (11,358 downloads, ≥2× the top accessible) | [CivitAI](https://civitai.com/models/964312?modelVersionId=3378342) |

## Details

### `zero-two-dance-mh3-e20-az420.safetensors`

**Zero-Two Dance**
- base `MiniMax H3` · not stated · strength: not stated · triggers: `doing the zero-two dance` · Graydient

Example prompt (from the images API, page, or sidecar; never invented):


```
`Front view of a beautiful {Russian|French|Swedish|Swiss|Latina|Austrian|Dutch|English|America|California} woman doing the zero-two dance. Her arms are up with her hands behind her head as she sways her hips from side the side.

She has {very long|long|medium length} {bright blonde|blonde|black|brown|dirty blond|bleach blonde} {straight|ponytailed|pigtailed|wavy|curly|braided|styled|tied} hair and a {slim|fit|perfect|curvy} body.

She is {naked|wearing a dress|wearing a bikini|wearing pyjamas|wearing jeans and a leather shirt}.

She is in a {night club|modern bedroom|kitchen|crowded subway train|classroom}.

Her oiled body glistens in the {bright|soft|dim} light.
realistic`
```

Compatibility: Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/1819613?modelVersionId=3264304)

