# LTX2: Motion

4 available Graydient LoRAs (4 already on Graydient, 0 still to add to Graydient). Everything in this table is part of the Graydient set: files already in `Octavian123/civit`, `Octavian123/civit2`, or `Octavian123/private` are listed first; RAID files that still need ingest are labelled *to add to Graydient* (or *to add to Graydient (no public source; needs local upload)* when there is no public URL) and must be ingested before they appear in the concept browser. There is no AIOps-only category. Nothing is auto-downloaded.

Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.

| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |
|---|---|---|---|---|---:|---|---|
| `ltx2-i2v-sexymove` | `LTX2-i2v-SexyMove`, `LTX2 i2v SexyMove`, `sexy` | 0.2–0.91 | I2V and T2V | LTX2 i2v - Sexy Move | 13,288 | on Graydient, verified | [CivitAI](https://civitai.com/models/2312166?modelVersionId=2621203), [HF](https://huggingface.co/Octavian123/civit2/blob/main/ltx2-i2v-sexymove.safetensors) |
| `ltx2-i2v-sexthrust` | `LTX2-i2v-SexThrust_1`, `LTX2 i2v SexThrust` | 0.8–1.0; 0.2–0.4 | I2V and T2V | LTX2 - Sex Thrust | 10,888 | on Graydient, verified | [CivitAI](https://civitai.com/models/2378690?modelVersionId=2674954), [HF](https://huggingface.co/Octavian123/civit2/blob/main/ltx2-i2v-sexthrust.safetensors) |
| `ltx23-i2v-swing-up-down-os` | `ltx23-i2v-swing-up-down`, `ltx23 i2v swing up down os` | not stated | I2V and T2V | Swing Up and Down Legs | 752 | on Graydient, verified | [CivitAI](https://civitai.com/models/2755595?modelVersionId=3100594), [HF](https://huggingface.co/Octavian123/civit/blob/main/ltx23-i2v-swing-up-down-os.safetensors) |
| `ltx23-i2v-swing-in-out-os` | `ltx23-i2v-swing-in-out2`, `ltx23 i2v swing in out os` | not stated | I2V and T2V | Swing In and Out Legs | 649 | on Graydient, verified | [CivitAI](https://civitai.com/models/2755583?modelVersionId=3100573), [HF](https://huggingface.co/Octavian123/civit/blob/main/ltx23-i2v-swing-in-out-os.safetensors) |

## Suggest ingest

These are **not** in the available Graydient set yet. Suggestion only — download and ingest them yourself with the civit-to-graydient pipeline if you want them. **Nothing here is auto-downloaded.**

| slug / file | trigger | strength | downloads | ingest priority | why | links |
|---|---|---|---:|---:|---|---|
| `h3-ltx-2-3-ltx2-better-nsfw-motion` | `g@n` | 0.8; 0.9; 1 | 40,210 | 200.4 | high-value upgrade (40,210 downloads, ≥2× the top accessible) | [CivitAI](https://civitai.com/models/2344781?modelVersionId=2986751) |
| `ltx-2-5-22b-lora-cinemagraph` | — | not stated | 6,116 | 156.7 | official utility pack with no accessible equivalent | [HF](https://huggingface.co/Lightricks/LTX-2.5-22b-LoRA-Cinemagraph) |
| `cameraman-ic-lora-for-ltx2-3-22b` | — | not stated | 3,213 | 151.6 | official utility pack with no accessible equivalent | [CivitAI](https://civitai.com/models/2525197?modelVersionId=3068448) |

## Details

### `LTX2-i2v-SexyMove.safetensors`

**LTX2 i2v - Sexy Move**
- base `LTXV2` · I2V and T2V · strength (stated): 0.2–0.91 · triggers: `LTX2-i2v-SexyMove`, `LTX2 i2v SexyMove`, `sexy` · on Graydient

Compatibility: mode: I2V and T2V; Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible

Source: [CivitAI](https://civitai.com/models/2312166?modelVersionId=2621203), [HF](https://huggingface.co/Octavian123/civit2/blob/main/ltx2-i2v-sexymove.safetensors)

### `LTX2-i2v-SexThrust.safetensors`

**LTX2 - Sex Thrust**
- base `LTXV2` · I2V and T2V · strength (stated): 0.8–1.0; 0.2–0.4 · triggers: `LTX2-i2v-SexThrust_1`, `LTX2 i2v SexThrust` · on Graydient

Compatibility: mode: I2V and T2V; speed/distill LoRA — use on the few-step / turbo graph; do not treat as a style LoRA on a full-step pass; Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible

Source: [CivitAI](https://civitai.com/models/2378690?modelVersionId=2674954), [HF](https://huggingface.co/Octavian123/civit2/blob/main/ltx2-i2v-sexthrust.safetensors)

### `ltx23-i2v-swing-up-down-os.safetensors`

**Swing Up and Down Legs**
- base `LTXV 2.3` · I2V and T2V · strength: not stated · triggers: `ltx23-i2v-swing-up-down`, `ltx23 i2v swing up down os` · on Graydient

Compatibility: mode: I2V and T2V; Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible

Source: [CivitAI](https://civitai.com/models/2755595?modelVersionId=3100594), [HF](https://huggingface.co/Octavian123/civit/blob/main/ltx23-i2v-swing-up-down-os.safetensors)

### `ltx23-i2v-swing-in-out-os.safetensors`

**Swing In and Out Legs**
- base `LTXV 2.3` · I2V and T2V · strength: not stated · triggers: `ltx23-i2v-swing-in-out2`, `ltx23 i2v swing in out os` · on Graydient

Compatibility: mode: I2V and T2V; Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible

Source: [CivitAI](https://civitai.com/models/2755583?modelVersionId=3100573), [HF](https://huggingface.co/Octavian123/civit/blob/main/ltx23-i2v-swing-in-out-os.safetensors)

