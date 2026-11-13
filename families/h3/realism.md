# H3: Realism

11 accessible LoRAs (6 on both Graydient and AIOps, 1 Graydient-only, 4 AIOps-only). Accessible rows are listed first (both, then AIOps, then Graydient), then by download count. The 13 Nov 2026 RAID snapshot is the AIOps source.

Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.

| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |
|---|---|---|---|---|---:|---|---|
| `h3-ltx-2-3-ltx2-better-nsfw-motion-h3` | `h3 ltx 2 3 ltx2 better nsfw motion h3` | 0.8; 0.9; 1 | I2V | H3 - LTX 2.3 - LTX2 better NSFW motion | 40,210 | Graydient+AIOps, verified | [CivitAI](https://civitai.com/models/2344781?modelVersionId=2986751) |
| `amateur-pov-h3` | `zy_amateurpov` | 0.4–0.85 | not stated | Amateur POV ✨ KREA 2 + H3 | 12,200 | Graydient+AIOps, verified | [CivitAI](https://civitai.com/models/2776852?modelVersionId=3403798) |
| `mmh3-realism-slider-h3` | — | not stated | not stated | [MMH3] Realism Slider | 9,583 | Graydient+AIOps, verified | [CivitAI](https://civitai.com/models/3014078?modelVersionId=3421124) |
| `minimax-h3-2d-anime-realism-style-slider-h3` | — | not stated | T2V | MiniMax H3 — 2D Anime ↔ Realism Style Slider | 1,849 | Graydient+AIOps, verified | [CivitAI](https://civitai.com/models/2980230?modelVersionId=3378274) |
| `nsfw-only-fans-beauty-h3` | `onlyfansbeauty` | not stated | not stated | NSFW Only Fans Beauty | 894 | Graydient+AIOps, verified | [CivitAI](https://civitai.com/models/2811800?modelVersionId=3392828) |
| `minimax-h3-t2v-i2v-gpovxxx-h3` | `minimax h3 t2v i2v gpovxxx h3` | not stated | I2V and T2V | Minimax-H3-T2V_I2V-GPovxxx | 207 | Graydient+AIOps, verified | [CivitAI](https://civitai.com/models/2893972?modelVersionId=3272198) |
| `mmh3-realism-slider-v2-hyperflow-h3-flash-h3` | — | 0.65–0.85; 0.65–0.90 | I2V | MMH3 Realism Slider V2 — HyperFlow H3 Flash & MiniMax H3 | 2,395 | AIOps, verified | [CivitAI](https://civitai.com/models/3041489?modelVersionId=3463588) |
| `smart-glasses-pov-minimax-h3` | `povsint` | not stated | I2V and T2V | Smart Glasses POV - MiniMax H3 | 712 | AIOps, verified | [CivitAI](https://civitai.com/models/3040975?modelVersionId=3456452) |
| `friend-s-pov-minimax-h3` | `celsint` | not stated | I2V and T2V | Friend's POV - MiniMax H3 | 419 | AIOps, verified | [CivitAI](https://civitai.com/models/3040960?modelVersionId=3456437) |
| `earth-from-iss-low-earth-orbit-planetary-v-h3` | — | not stated | not stated | Earth from ISS | 164 | AIOps, verified | [CivitAI](https://civitai.com/models/3044877?modelVersionId=3461417) |
| `minimax-h3-tiddies-and-realism-slider` | — | 0.4–0.5 | I2V and T2V | Minimax H3 - Tiddies and Realism Slider | 16,493 | Graydient, verified | [CivitAI](https://civitai.com/models/2858760?modelVersionId=3229050) |

## Suggest ingest

These are **not** on Graydient or the AIOps RAID yet. Suggestion only — download and ingest them yourself with the civit-to-graydient pipeline if you want them. **Nothing here is auto-downloaded.**

| slug / file | trigger | strength | downloads | ingest priority | why | links |
|---|---|---|---:|---:|---|---|
| `hmnsfw-h3` | `hmmotion` | 0.6–1.0 | 88,223 | 212.6 | high-value upgrade (88,223 downloads, ≥2× the top accessible) | [CivitAI](https://civitai.com/models/2834417?modelVersionId=3206518) |
| `minimax-h3-realism-people-lora` | `r34l1sm` | 1.0 | 121,514 | 204.1 | high-value upgrade (121,514 downloads, ≥2× the top accessible) | [HF](https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA) |

## Details

### `h3-ltx-2-3-ltx2-better-nsfw-motion-h3.safetensors`

**H3 - LTX 2.3 - LTX2 better NSFW motion**
- base `LTXV 2.3` · I2V · strength (stated): 0.8; 0.9; 1 · triggers: `h3 ltx 2 3 ltx2 better nsfw motion h3` · Graydient+AIOps

Compatibility: mode: I2V; speed/distill LoRA — use on the few-step / turbo graph; do not treat as a style LoRA on a full-step pass; Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/2344781?modelVersionId=2986751)

### `amateur-pov-h3.safetensors`

**Amateur POV ✨ KREA 2 + H3**
- base `MiniMax H3` · not stated · strength (stated): 0.4–0.85 · triggers: `zy_amateurpov` · Graydient+AIOps

Example prompt (from the images API, page, or sidecar; never invented):


```
`integrated_multimodal_description: [Shot 1] zy_amateurpov, [detailed continuous scene description covering appearance, clothing/state of undress, body details, actions, facial expressions, camera angle, background, lighting]`
```

Compatibility: Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/2776852?modelVersionId=3403798)

### `nsfw-only-fans-beauty-h3.safetensors`

**NSFW Only Fans Beauty**
- base `MiniMax H3` · not stated · strength: not stated · triggers: `onlyfansbeauty` · Graydient+AIOps

Compatibility: Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/2811800?modelVersionId=3392828)

### `minimax-h3-t2v-i2v-gpovxxx-h3.safetensors`

**Minimax-H3-T2V_I2V-GPovxxx**
- base `MiniMax H3` · I2V and T2V · strength: not stated · triggers: `minimax h3 t2v i2v gpovxxx h3` · Graydient+AIOps

Compatibility: mode: I2V and T2V; Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/2893972?modelVersionId=3272198)

### `mmh3-realism-slider-v2-hyperflow-h3-flash-h3.safetensors`

**MMH3 Realism Slider V2 — HyperFlow H3 Flash & MiniMax H3**
- base `MiniMax H3` · I2V · strength (stated): 0.65–0.85; 0.65–0.90 · AIOps

Compatibility: mode: I2V; Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/3041489?modelVersionId=3463588)

### `smart-glasses-pov-minimax-h3.safetensors`

**Smart Glasses POV - MiniMax H3**
- base `MiniMax H3` · I2V and T2V · strength: not stated · triggers: `povsint` · AIOps

Compatibility: mode: I2V and T2V; Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/3040975?modelVersionId=3456452)

### `friend-s-pov-minimax-h3.safetensors`

**Friend's POV - MiniMax H3**
- base `MiniMax H3` · I2V and T2V · strength: not stated · triggers: `celsint` · AIOps

Compatibility: mode: I2V and T2V; Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/3040960?modelVersionId=3456437)

### `earth-from-iss-low-earth-orbit-planetary-v-h3.safetensors`

**Earth from ISS \| Low Earth Orbit \| Planetary view \| H3 Minimax LoRA**
- base `MiniMax H3` · not stated · strength: not stated · AIOps

Example prompt (from the images API, page, or sidecar; never invented):


```
" This is a high-resolution photograph of Earth from space, taken from a satellite or spacecraft. The image prominently features the curved horizon of the planet, showcasing a vivid blue ocean with scattered white clouds. The ocean occupies the lower half of the image, while the upper half is dominated by the cloud-covered atmosphere. The clouds are dense and fluffy, creating a textured pattern against the bright blue of the ocean. In the top right corner, parts of the spacecraft's structure are visible, including metallic components and a section of the satellite's arm. The background is the blackness of outer space, providing a stark contrast to the bright colors of Earth. The photograph captures the beauty and vastness of our planet, highlighting the interplay between the ocean and clou
```

Compatibility: Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/3044877?modelVersionId=3461417)

### `PlagueKind-tiddies-realismslider.safetensors`

**Minimax H3 - Tiddies and Realism Slider**
- base `MiniMax H3` · I2V and T2V · strength (stated): 0.4–0.5 · Graydient

Example prompt (from the images API, page, or sidecar; never invented):


```
`865BrcfWLdwELwuq5faV1uVTbh93zVK6AUYLY2c3mX6sFfAGRfS6axe1kBTYYKuM7ccN7zBZDAZvnT7E4NKmUazySdbpc7p`
```

Compatibility: mode: I2V and T2V; speed/distill LoRA — use on the few-step / turbo graph; do not treat as a style LoRA on a full-step pass; Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)

Source: [CivitAI](https://civitai.com/models/2858760?modelVersionId=3229050)

