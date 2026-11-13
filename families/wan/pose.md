# Wan: Pose / control

1 available Graydient LoRAs (1 already on Graydient, 0 to add to Graydient). Everything in this table is part of the Graydient set: files already in `Octavian123/civit` are listed first; RAID files that still need ingest are labelled *to add to Graydient* and must be run through civit-to-graydient before they appear in the concept browser. There is no AIOps-only category. Nothing is auto-downloaded.

Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.

| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |
|---|---|---|---|---|---:|---|---|
| `zero-two-dance` | `doing the zero-two dance`, `arms are up with her hands behind her head as she sways her hips from side the side` | not stated | T2V | Zero-Two Dance | 5,226 | on Graydient, verified | [CivitAI](https://civitai.com/models/1819613?modelVersionId=2412504) |

## Suggest ingest

These are **not** on Graydient or the AIOps RAID yet. Suggestion only — download and ingest them yourself with the civit-to-graydient pipeline if you want them. **Nothing here is auto-downloaded.**

| slug / file | trigger | strength | downloads | ingest priority | why | links |
|---|---|---|---:|---:|---|---|
| `bfs-best-face-swap` | `head_swap:` | 0.7–1.0 | 110,030 | 228.4 | high-value upgrade (110,030 downloads, ≥2× the top accessible) | [CivitAI](https://civitai.com/models/2027766?modelVersionId=3050039) |
| `nsfw-posing-nude` | — | not stated | 91,732 | 207.1 | high-value upgrade (91,732 downloads, ≥2× the top accessible) | [CivitAI](https://civitai.com/models/1648982?modelVersionId=2391828) |
| `pleasured-orgasm-pose-xl` | — | not stated | 24,041 | 204.5 | high-value upgrade (24,041 downloads, ≥2× the top accessible) | [CivitAI](https://civitai.com/models/721065?modelVersionId=2092191) |

## Details

### `zerto-two-dance-wan-one-e18-az420.safetensors`

**Zero-Two Dance**
- base `Wan Video 14B t2v` · T2V · strength: not stated · triggers: `doing the zero-two dance`, `arms are up with her hands behind her head as she sways her hips from side the side` · on Graydient

Example prompt (from the images API, page, or sidecar; never invented):


```
`Front view of a beautiful {Russian|French|Swedish|Swiss|Latina|Austrian|Dutch|English|America|California} woman doing the zero-two dance. Her arms are up with her hands behind her head as she sways her hips from side the side.

She has {very long|long|medium length} {bright blonde|blonde|black|brown|dirty blond|bleach blonde} {straight|ponytailed|pigtailed|wavy|curly|braided|styled|tied} hair and a {slim|fit|perfect|curvy} body.

She is {naked|wearing a dress|wearing a bikini|wearing pyjamas|wearing jeans and a leather shirt}.

She is in a {night club|modern bedroom|kitchen|crowded subway train|classroom}.

Her oiled body glistens in the {bright|soft|dim} light.
realistic`
```

Compatibility: mode: T2V; Wan 2.1 LoRA; do not assume it works on 2.2 high/low graphs; Graydient Wan workflows (family-level, not a per-LoRA install claim): animate-wan22, video-wan22

Source: [CivitAI](https://civitai.com/models/1819613?modelVersionId=2412504)

