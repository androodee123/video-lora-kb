# Video LoRA knowledge base

Private, comprehensive catalog of **video LoRAs only** for MiniMax H3, Wan (2.1 including 1.3B T2V, 2.2 14B high/low and 5B TI2V), and LTX (LTXV, LTX-2, 2.3, 2.5). Rows are LoRA / LoCon / DoRA adapters that can be stacked into T2V or I2V graphs. Speed and distill LoRAs (lightx2v, CausVid) stay in.

**Out of scope** (image LoRAs, checkpoints, finetunes, merges, full base-model repos, pure workflows, ControlNets that are not LoRAs, VAEs, text encoders, GGUF/quantised full models, and non-video families such as Hunyuan) are not in `data/loras.jsonl`. Installed RAID files that fail this test are moved to [`data/excluded.jsonl`](data/excluded.jsonl) with a reason — they are not deleted. Catalog-only drops are logged there too.

Coverage is the full CivitAI inventory for the confirmed `baseModel` strings (paged to exhaustion, plus Most Downloaded / Highest Rated checks; types `LORA`, `LoCon`, and `DoRA`), Hugging Face official and community speed/control packs, and the [Fuzz Puppy directory](https://www.fuzzpuppy.com/lora-directory). LoRAs **installed** on the AIOps RAID (`/Volumes/RAID/Lora/{H3,Wan,LTX2}`, snapshot 13 Nov 2026) are flagged `installed=true` and sorted first in every table.

Research compiled **13 Nov 2026, 20:19 Africa/Johannesburg (SAST)**. Many entries are adult NSFW and are documented factually. This repo stores **metadata only** — no weights. `scripts/harvest.py` and `scripts/check_new.py` must never download or ingest LoRA files.

## Counts

| Family | Total records | Installed | Installed verified | Installed unverified | Catalog-only (CivitAI/HF) | Verified |
|---|---:|---:|---:|---:|---:|---:|
| MiniMax H3 | 1249 | 241 | 201 | 40 | 1008 | 1209 |
| Wan (2.1 / 2.2) | 2778 | 54 | 47 | 7 | 2724 | 2771 |
| LTX-2 / 2.3 / 2.5 | 817 | 32 | 28 | 4 | 785 | 813 |
| **Total** | **4844** | **327** | **276** | **51** | **4517** | **4793** |

Low-download CivitAI rows (under ~100 downloads and no thumbs-up) are kept and flagged `low_signal=true` rather than dropped, so niche but relevant LoRAs stay in the catalog.

### Counts by category

| Category | H3 total (installed) | Wan total (installed) | LTX total (installed) |
|---|---:|---:|---:|
| Motion | 51 (14) | 66 (2) | 34 (4) |
| Camera | 61 (12) | 145 (4) | 44 (2) |
| Audio / voice | 41 (3) | 3 (0) | 16 (1) |
| Style | 310 (46) | 498 (1) | 175 (9) |
| Enhancement / quality / speed | 501 (140) | 981 (30) | 313 (13) |
| Identity / character | 299 (24) | 644 (0) | 148 (0) |
| Effects / VFX | 34 (9) | 117 (0) | 26 (1) |
| Transitions | 6 (2) | 9 (0) | 15 (0) |
| Lighting | 6 (1) | 10 (0) | 7 (0) |
| Physics / cloth / hair | 25 (12) | 19 (0) | 9 (0) |
| NSFW acts and anatomy | 234 (96) | 634 (34) | 121 (19) |
| Anime / 2D | 90 (15) | 373 (1) | 64 (4) |
| Realism | 76 (10) | 98 (0) | 21 (1) |
| Character consistency | 3 (0) | 6 (0) | 1 (0) |
| Object control | 3 (1) | 1 (0) | 0 (0) |
| Pose / control | 10 (1) | 32 (0) | 15 (0) |
| Lipsync | 2 (1) | 0 (0) | 2 (0) |

A LoRA may appear in more than one category.

Of 4844 rows: **3015** (62.2%) have at least one recorded trigger, **919** (19.0%) have a stated strength, **1317** (27.2%) have at least one example prompt (images API or page text). **39** rows are flagged `low_signal`. Missing fields are recorded as `not stated` / empty — never invented.

## How to use this repo

1. Start with [`SKILL.md`](SKILL.md) — a goal→LoRA chooser with recipes across families, stacking, stated strengths, and known conflicts.
2. Open the family + category page under `families/`. Tables list **installed first**, then catalog entries by popularity (downloads).
3. For I2V / T2V prompting and Graydient workflow names, read [`guides/image-to-video.md`](guides/image-to-video.md). Per-family prompt templates and trigger usage: [`guides/prompt-patterns.md`](guides/prompt-patterns.md).
4. Official / utility packs also appear in [`guides/fuzzpuppy-directory.md`](guides/fuzzpuppy-directory.md).
5. Machine-readable data: [`data/loras.jsonl`](data/loras.jsonl). Rows that were audited out of the catalog (including installed RAID files that are not video LoRAs) live in [`data/excluded.jsonl`](data/excluded.jsonl) with an `exclude_reason`.
6. Refresh CivitAI/HF metadata: `python3 scripts/harvest.py` (writes `data/raw/`, gitignored). Propose new video LoRAs since the last harvest: `python3 scripts/check_new.py` (LORA / LoCon / DoRA on confirmed video bases only).

## Strengths and triggers

If a page or sidecar does not state a strength or trigger, the catalog says **`not stated`** or leaves `triggers` empty. Do not invent either. A general MiniMax H3 starting range of 0.6–0.9 is a rule of thumb only, not per-LoRA data.

## Wan 2.2 high / low pairs

Wan 2.2 14B dual-KSampler graphs need **paired HIGH and LOW noise LoRAs** for the same concept when both were trained. Load the high-noise file on the high-noise sampler and the low-noise file on the low-noise sampler, usually at the same strength. Catalog rows for uninstalled models list both published filenames in `files` when present. The local `b7_test1` run is **high-noise only**.

## CivitAI `baseModel` strings (`scripts/harvest.py` / `check_new.py`)

- `MiniMax H3`
- `Wan Video`
- `Wan Video 14B i2v 480p`
- `Wan Video 14B i2v 720p`
- `Wan Video 14B t2v`
- `Wan Video 2.2 I2V-A14B`
- `Wan Video 2.2 T2V-A14B`
- `Wan Video 2.2 TI2V-5B`
- `Wan Video 1.3B t2v`
- `LTXV`
- `LTXV2`
- `LTXV 2.3`
- `LTXV 2.5`

High vs low noise is not a `baseModel` value.


## Share pack (for other AIs)

To attach this knowledge base to another chat or agent without opening the private repo, regenerate a local export:

```
python3 scripts/export_pack.py
```

`dist/` is gitignored. It contains a prompt-ready `video-lora-skill.md` (recipes, stacking, compact top-LoRA tables), compact catalog JSON/CSV, `HOW-TO-USE.md`, a Claude Agent Skill zip, and `video-lora-kb-share-pack.zip`. The script never downloads weights and never invents triggers or strengths.


## Reproducing the harvest

```
python3 scripts/harvest.py --full-sorts --period AllTime   # Newest + Most Downloaded + Highest Rated, all bases (types=LORA)
python3 scripts/harvest.py --full-sorts --period AllTime --types LoCon,DoRA   # LyCORIS adapters on the same video bases
python3 scripts/harvest.py --keywords                      # CivitAI keyword queries (video bases only)
python3 scripts/harvest.py --hf-expand                     # broader Hugging Face LoRA search
python3 scripts/harvest.py --hf-cards                      # README/model cards for Hugging Face rows
python3 scripts/harvest.py --enrich --enrich-images        # full /models/{id} + example-prompt images API
python3 scripts/harvest.py --full-sorts --bases 'Wan Video 1.3B t2v'
python3 scripts/build_kb.py && python3 scripts/render_kb.py
```

Raw API dumps live in `data/raw/` and are gitignored (tens of megabytes). See `data/raw/README.md`.

## Sources

- CivitAI public API, metadata only (every confirmed baseModel paged with Newest, Most Downloaded, and Highest Rated, including `period=AllTime`; keyword queries for camera/motion/audio/identity/control/etc.; full `/api/v1/models/{id}` descriptions and `/api/v1/images` example prompts when the public API returns `meta.prompt`).
- Hugging Face Hub search (author lists plus `models?search=` / pipeline tags for Wan-AI / Wan2.1 / Wan2.2, Lightricks / LTX, MiniMax, lightx2v, alibaba-pai, and related community packs).
- RAID inventory and sidecars, Sept 2026 catalog skeletons, curated MCB `h3-loras.md`.
- [fuzzpuppy.com/lora-directory](https://www.fuzzpuppy.com/lora-directory).
