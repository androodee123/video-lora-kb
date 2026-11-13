# LTX2: Audio / voice

1 accessible LoRAs (0 on both Graydient and AIOps, 0 Graydient-only, 1 AIOps-only). Accessible rows are listed first (both, then AIOps, then Graydient), then by download count. The 13 Nov 2026 RAID snapshot is the AIOps source.

Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.

| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |
|---|---|---|---|---|---:|---|---|
| `ltx2-i2v-sexthrust` | `LTX2-i2v-SexThrust_1`, `LTX2 i2v SexThrust` | 0.8–1.0; 0.2–0.4 | I2V and T2V | LTX2 - Sex Thrust | 10,888 | AIOps, verified | [CivitAI](https://civitai.com/models/2378690?modelVersionId=2674954) |

## Suggest ingest

These are **not** on Graydient or the AIOps RAID yet. Suggestion only — download and ingest them yourself with the civit-to-graydient pipeline if you want them. **Nothing here is auto-downloaded.**

| slug / file | trigger | strength | downloads | ingest priority | why | links |
|---|---|---|---:|---:|---|---|
| `ltx-2-3-22b-lora-foley-v2a` | — | not stated | 824 | 134.6 | official utility pack with no accessible equivalent | [HF](https://huggingface.co/Lightricks/LTX-2.3-22b-LoRA-Foley-V2A) |

## Details

### `LTX2-i2v-SexThrust.safetensors`

**LTX2 - Sex Thrust**
- base `LTXV2` · I2V and T2V · strength (stated): 0.8–1.0; 0.2–0.4 · triggers: `LTX2-i2v-SexThrust_1`, `LTX2 i2v SexThrust` · AIOps

Compatibility: mode: I2V and T2V; speed/distill LoRA — use on the few-step / turbo graph; do not treat as a style LoRA on a full-step pass; Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible

Source: [CivitAI](https://civitai.com/models/2378690?modelVersionId=2674954)

