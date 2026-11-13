# Video LoRA knowledge base

Private catalog for Andrew (FormsXpress) of **video LoRAs already installed** on the AIOps RAID (`/Volumes/RAID/Lora/{H3,Wan,LTX2}`), plus a small curated set of MiniMax H3 motion/camera/realism and audio LoRAs from the Sept 2026 MCB grouping that were not in the 13 Nov 2026 inventory snapshot.

Inventory snapshot: **13 Nov 2026**. Research compiled **13 Nov 2026, 18:23 Africa/Johannesburg (SAST)**. Many entries are adult NSFW; they are documented factually like any other LoRA.

This repo stores **metadata only**. It does not contain weights, and `scripts/check_new.py` must never download or ingest LoRA files.

## Counts

| Family | Installed `.safetensors` | Installed verified | Installed unverified | Extra curated (not in snapshot) | Notes |
|---|---:|---:|---:|---:|---|
| MiniMax H3 | 244 | 203 | 41 | 12 | Curated extras are motion/camera/realism and audio picks from `h3-loras.md`. |
| Wan (2.1 / 2.2) | 55 | 47 | 8 | 0 | Includes 9 local `b7_test1` high-noise training checkpoints. |
| LTX-2 / 2.3 / 2.5 | 32 | 28 | 4 | 0 | Sidecar `.txt` files were the primary trigger source when present. |
| **Total records** | 331 | 278 | 53 | 12 | One JSONL row per file. |

Verified means a CivitAI (or local README, for the `b7` test) source was matched with reasonable confidence and the model metadata was fetched. Unverified rows are stubs: keep them, do not invent triggers or strengths.

## How to use this repo

1. Start with [`SKILL.md`](SKILL.md) if you are choosing LoRAs for a goal (realistic motion, breathy audio, camera orbit, identity, style, a specific act).
2. Then open the family + category page under `families/`. Each page is a table of slug/file, trigger, strength, I2V vs T2V, purpose, and links. Richer entries have a short details section with a source example prompt when one was published.
3. For I2V / T2V prompting and Graydient workflow names, read [`guides/image-to-video.md`](guides/image-to-video.md).
4. Machine-readable data is [`data/loras.jsonl`](data/loras.jsonl) — one record per LoRA file.
5. To see what is new on CivitAI since this catalog was built, run `python3 scripts/check_new.py`. It only writes a markdown proposal list; it never downloads weights.

## Layout

```
README.md
SKILL.md
guides/image-to-video.md
guides/fuzzpuppy-directory.md
families/h3/     motion, camera, audio, style, identity, enhancement, nsfw-acts, unverified
families/wan/    same category split
families/ltx/    same category split
data/loras.jsonl
scripts/check_new.py
```

## Strengths

If a page or sidecar does not state a strength, the catalog says **`not stated`**. Do not copy a family-wide rule of thumb into a per-LoRA field. A general MiniMax H3 starting range of 0.6–0.9 appears in older notes as a rule of thumb only — tune each LoRA yourself.

## Wan 2.2 high / low pairs

Wan 2.2 14B dual-KSampler graphs need **paired HIGH and LOW noise LoRAs** for the same concept when both were trained. Load the high-noise file on the high-noise sampler and the low-noise file on the low-noise sampler, usually at the same strength. The local `b7_test1` run is **high-noise only**; a matching low-noise LoRA was not trained.

## CivitAI `baseModel` strings used by `check_new.py`

These are the strings CivitAI's API actually returned and accepted as `baseModels` filters on 13 Nov 2026:

- `MiniMax H3`
- `Wan Video`
- `Wan Video 14B i2v 480p`
- `Wan Video 14B i2v 720p`
- `Wan Video 14B t2v`
- `Wan Video 2.2 I2V-A14B`
- `Wan Video 2.2 T2V-A14B`
- `Wan Video 2.2 TI2V-5B`
- `LTXV`
- `LTXV2`
- `LTXV 2.3`
- `LTXV 2.5`

High vs low noise is **not** a `baseModel` value; it lives in the version or filename.

## Sources

- RAID inventory TSVs and sidecars under `/Volumes/RAID/Lora/{H3,Wan,LTX2}` (snapshot copied to the box 13 Nov 2026).
- Sept 2026 H3 and Wan catalog skeletons, and the curated MCB-focused `h3-loras.md` grouping.
- CivitAI public API (`/api/v1/models` and `/api/v1/models/{id}`), metadata only.
- [Fuzz Puppy AI Video LoRA Directory](https://www.fuzzpuppy.com/lora-directory) (61 tracked utility/official LoRAs). See [`guides/fuzzpuppy-directory.md`](guides/fuzzpuppy-directory.md). Almost none of the installed NSFW act LoRAs appear there.

## Gaps worth knowing

- A cluster of Sept 2026 skeleton CivitAI ids now 404 on `civitai.com` (for example Disney Style, doggy-style sex, dildo masturbation, natural sagging breasts). Triggers from the skeleton are kept; rows stay unverified.
- `natural-face-speech-minimax-h3` is installed and is an audio pick, but no live page was found and no trigger was recorded.
- Several Wan 2.2 pairs (`Fondled_*`, `wan22_i2v_futa_missionary_*`, `xMilkDuctXrayx_*`) have sidecar triggers but no confirmed CivitAI/HF page.
- `LTX-2 - Orgasm v1`, `LTX-2 - Rubbing Her Pussy`, `PLORAV7_LTX_000010500`, and `tiny-breasts-flat-chest-ltx2` remain unverified. `LTX-2 - Better Female Nudity` was matched by exact file size and name to SexGod's LTX-2 Female Nudity pack; the other two same-size files were **not** assumed to be the same model.
- A few files sitting in the H3 folder are named for other families (`*-wan.safetensors`, `*-krea2*.safetensors`, `minigirl-onahole-xl.safetensors`). They are catalogued where they were found.
- Official Lightricks / Fuzz Puppy camera, restore, and IC-LoRAs are mostly **not** installed on the RAID snapshot.
