# LTX2: Pose / control

10 LoRAs (0 installed on the 13 Nov 2026 RAID snapshot). Installed rows are listed first, then the rest by CivitAI/HF download count.

Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.

| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |
|---|---|---|---|---|---:|---|---|
| `bfs-best-face-swap` | `head_swap`, `head_swap: FACE: [Face Description]`, `head_swap: FACE: [describe the new face here] ACTION: [describe the action from original video here]` | not stated | not stated | BFS - Best Face Swap | 110,030 | catalog, verified | [CivitAI](https://civitai.com/models/2027766?modelVersionId=2783974) |
| `nsfw-posing-nude` | — | not stated | I2V | NSFW Posing Nude | 91,732 | catalog, verified | [CivitAI](https://civitai.com/models/1648982?modelVersionId=2949966) |
| `ltx-2-3-lora-pose-helper-i2v` | — | not stated | I2V and T2V | (LTX-2.3 Lora) - Pose Helper (I2V) | 6,240 | catalog, verified | [CivitAI](https://civitai.com/models/2402694?modelVersionId=2783626) |
| `ltx-2-3-lora-camera-zoom-out-i2v` | — | not stated | I2V | (LTX-2.3 Lora) - Camera Zoom Out (I2V) | 2,097 | catalog, verified | [CivitAI](https://civitai.com/models/2490345?modelVersionId=2799690) |
| `east-asian-facial-fidelity-ltx-2-3-i2v` | — | 1.0 | I2V | East Asian Facial Fidelity | 1,258 | catalog, verified | [CivitAI](https://civitai.com/models/2816700?modelVersionId=3176918) |
| `front-lat-spread-pose` | `FrontLatSpreadPose` | not stated | not stated | Front Lat Spread Pose | 937 | catalog, verified | [CivitAI](https://civitai.com/models/2010060?modelVersionId=2906922) |
| `evernightwiggle` | `A girl is dancing the Cry0EvernWig`, `Dancing the Cry0EvernWig.` | not stated | I2V and T2V | EvernightWiggle | 472 | catalog, verified | [CivitAI](https://civitai.com/models/2339706?modelVersionId=2631753) |
| `ltx-2-3-most-muscular-pose-lora` | `mm_pose` | not stated | not stated | LTX-2.3 Most Muscular Pose LoRA | 340 | catalog, verified | [CivitAI](https://civitai.com/models/2533614?modelVersionId=2847433) |
| `ltx-2-19b-ic-lora-depth-control` | — | not stated | not stated | LTX-2-19b-IC-LoRA-Depth-Control | 0 | catalog, verified | [HF](https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Depth-Control) |
| `ltx-2-19b-ic-lora-pose-control` | — | not stated | not stated | LTX-2-19b-IC-LoRA-Pose-Control | 0 | catalog, verified | [HF](https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Pose-Control) |

## Details

### `ltx23__demopose_d3m0p0s3.safetensors`

**(LTX-2.3 Lora) - Pose Helper (I2V)**
- base `LTXV2` · I2V and T2V · strength: not stated

Example prompt (from the images API, page, or sidecar; never invented):


```
`d3m0p0se.
A brunette woman wearing sunglasses mini jeans and a white top is saying (not singing) seductively to the viewer "Don't you like my outfit".
She then is happily posing on the street, touching her clothes and hair.
Pop music plays in the background`
```

Compatibility: mode: I2V and T2V; Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible

Source: [CivitAI](https://civitai.com/models/2402694?modelVersionId=2783626)

### `ltx23_zoomout_z00m047.safetensors`

**(LTX-2.3 Lora) - Camera Zoom Out (I2V)**
- base `LTXV2` · I2V · strength: not stated

Example prompt (from the images API, page, or sidecar; never invented):


```
`z00m047. a clean video of a closeup of a SINGLE blonde woman is posing and moving in a neon street. The camera zooms out, revealing a large cyberpunk like neon city street with shops, the SINGLE woman is barely visible in the distance`
```

Compatibility: mode: I2V; Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible

Source: [CivitAI](https://civitai.com/models/2490345?modelVersionId=2799690)

### `ltx-23-most-muscular-pose-lora-v10.safetensors`

**LTX-2.3 Most Muscular Pose LoRA**
- base `LTXV 2.3` · not stated · strength: not stated · triggers: `mm_pose`

Example prompt (from the images API, page, or sidecar; never invented):


```
"he stands up, does the mm_pose , then relaxes and waves hi".
```

Compatibility: Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible

Source: [CivitAI](https://civitai.com/models/2533614?modelVersionId=2847433)

