# Video LoRA knowledge base

Private catalog of **accessible video LoRAs** for MiniMax H3, Wan (2.1 including 1.3B T2V, 2.2 14B high/low and 5B TI2V), and LTX (LTXV, LTX-2, 2.3, 2.5). A LoRA is **accessible** when it is on **Graydient** (a matching `{slug}.safetensors` in the Hugging Face repo `Octavian123/civit`, which is what the civit-to-graydient pipeline registers as a private concept) or on **AIOps** (present on the 13 Nov 2026 RAID snapshot at `/Volumes/RAID/Lora/{H3,Wan,LTX2}`, flagged `aiops=true` / `installed=true`), or both.

`data/loras.jsonl` holds only accessible rows. Public CivitAI / Hugging Face video LoRAs that are not yet on Graydient or the RAID live in [`data/candidates.jsonl`](data/candidates.jsonl) with an `ingest_priority` score. They are suggested for ingest when they fill a gap or clearly outrank what is already available — never auto-downloaded.

**Out of scope** (image LoRAs, checkpoints, finetunes, merges, full base-model repos, pure workflows, ControlNets that are not LoRAs, VAEs, text encoders, GGUF/quantised full models, and non-video families such as Hunyuan) are not in `data/loras.jsonl`. Installed RAID files that fail this test are in [`data/excluded.jsonl`](data/excluded.jsonl) with a reason. See [`data/accessibility_report.md`](data/accessibility_report.md) for the last Graydient/AIOps filter.

Research compiled **13 Nov 2026, 22:08 Africa/Johannesburg (SAST)**. Many entries are adult NSFW and are documented factually. This repo stores **metadata only** — no weights. `scripts/harvest.py`, `scripts/check_new.py`, and `scripts/filter_accessible.py` must never download or ingest LoRA files.

## Counts

| Family | Accessible | Graydient only | AIOps only | Both | Candidates |
|---|---:|---:|---:|---:|---:|
| MiniMax H3 | 274 | 33 | 50 | 191 | 981 |
| Wan (2.1 / 2.2) | 73 | 19 | 19 | 35 | 2706 |
| LTX-2 / 2.3 / 2.5 | 44 | 12 | 17 | 15 | 774 |
| **Total** | **391** | **64** | **86** | **241** | **4461** |

Recommend available LoRAs first (Graydient, AIOps, or both). Suggest ingest of a candidate when the category or goal has no accessible option, or when a candidate is clearly stronger (at least 2,000 downloads and at least 2× the top accessible download count in that category) or is an official utility pack with no accessible equivalent. The full rule is in [`SKILL.md`](SKILL.md).

### Counts by category (accessible)

| Category | H3 accessible (AIOps) | Wan accessible (AIOps) | LTX accessible (AIOps) |
|---|---:|---:|---:|
| Motion | 15 (14) | 3 (2) | 4 (4) |
| Camera | 12 (12) | 7 (4) | 5 (2) |
| Audio / voice | 3 (3) | 0 (0) | 1 (1) |
| Style | 49 (46) | 1 (1) | 11 (9) |
| Enhancement / quality / speed | 153 (140) | 41 (30) | 17 (13) |
| Identity / character | 25 (24) | 2 (0) | 2 (0) |
| Effects / VFX | 9 (9) | 0 (0) | 2 (1) |
| Transitions | 2 (2) | 0 (0) | 0 (0) |
| Lighting | 1 (1) | 0 (0) | 0 (0) |
| Physics / cloth / hair | 14 (12) | 0 (0) | 0 (0) |
| NSFW acts and anatomy | 110 (96) | 39 (34) | 22 (19) |
| Anime / 2D | 17 (15) | 1 (1) | 5 (4) |
| Realism | 11 (10) | 0 (0) | 1 (1) |
| Character consistency | 0 (0) | 0 (0) | 0 (0) |
| Object control | 1 (1) | 0 (0) | 0 (0) |
| Pose / control | 2 (1) | 1 (0) | 0 (0) |
| Lipsync | 1 (1) | 0 (0) | 0 (0) |

A LoRA may appear in more than one category.

Of 391 rows: **235** (60.1%) have at least one recorded trigger, **55** (14.1%) have a stated strength, **99** (25.3%) have at least one example prompt (images API or page text). **2** rows are flagged `low_signal`. Missing fields are recorded as `not stated` / empty — never invented.

## How to use this repo

1. Start with [`SKILL.md`](SKILL.md) — a goal→LoRA chooser. Recipes recommend accessible LoRAs first and, when the rule says so, add a clearly labelled *Suggest ingest* line with a CivitAI or Hugging Face link.
2. Open the family + category page under `families/`. Tables list accessible LoRAs (both, then AIOps, then Graydient), then a *Suggest ingest* block when the rule fires.
3. For I2V / T2V prompting and Graydient workflow names, read [`guides/image-to-video.md`](guides/image-to-video.md). Per-family prompt templates and trigger usage: [`guides/prompt-patterns.md`](guides/prompt-patterns.md).
4. Official / utility packs also appear in [`guides/fuzzpuppy-directory.md`](guides/fuzzpuppy-directory.md). If they are not on Graydient or the RAID, treat them as ingest candidates.
5. Machine-readable data: [`data/loras.jsonl`](data/loras.jsonl) (accessible), [`data/candidates.jsonl`](data/candidates.jsonl) (ranked ingest candidates), [`data/excluded.jsonl`](data/excluded.jsonl) (non-video or otherwise dropped, with a reason).
6. Refresh CivitAI/HF metadata: `python3 scripts/harvest.py` (writes `data/raw/`, gitignored). Re-filter accessibility: `python3 scripts/filter_accessible.py`. Propose new ingest candidates: `python3 scripts/check_new.py`.

## Share pack (for other AIs)

To attach this knowledge base to another chat or agent without opening the private repo, regenerate a local export:

```
python3 scripts/export_pack.py
```

`dist/` is gitignored. It contains a prompt-ready `video-lora-skill.md` (recipes, stacking, compact top-LoRA tables), compact catalog JSON/CSV, `HOW-TO-USE.md`, a Claude Agent Skill zip, and `video-lora-kb-share-pack.zip`. The script never downloads weights and never invents triggers or strengths.

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

## Reproducing the harvest

```
python3 scripts/harvest.py --full-sorts --period AllTime   # Newest + Most Downloaded + Highest Rated, all bases (types=LORA)
python3 scripts/harvest.py --full-sorts --period AllTime --types LoCon,DoRA   # LyCORIS adapters on the same video bases
python3 scripts/harvest.py --keywords                      # CivitAI keyword queries (video bases only)
python3 scripts/harvest.py --hf-expand                     # broader Hugging Face LoRA search
python3 scripts/harvest.py --hf-cards                      # README/model cards for Hugging Face rows
python3 scripts/harvest.py --enrich --enrich-images        # full /models/{id} + example-prompt images API
python3 scripts/harvest.py --full-sorts --bases 'Wan Video 1.3B t2v'
python3 scripts/build_kb.py
python3 scripts/filter_accessible.py    # keep only Graydient- or AIOps-accessible rows; rest -> data/candidates.jsonl
python3 scripts/render_kb.py
python3 scripts/export_pack.py
```

Raw API dumps live in `data/raw/` and are gitignored (tens of megabytes). See `data/raw/README.md`.

## Sources

- Hugging Face `Octavian123/civit` file listing (Graydient access). Metadata only — weights are never downloaded by these scripts.
- AIOps RAID inventory and sidecars (`/Volumes/RAID/Lora/{H3,Wan,LTX2}`, snapshot 13 Nov 2026).
- CivitAI public API, metadata only (every confirmed baseModel paged with Newest, Most Downloaded, and Highest Rated, including `period=AllTime`; keyword queries; full `/api/v1/models/{id}` descriptions and `/api/v1/images` example prompts when the public API returns `meta.prompt`).
- Hugging Face Hub search (author lists plus `models?search=` / pipeline tags for Wan-AI / Wan2.1 / Wan2.2, Lightricks / LTX, MiniMax, lightx2v, alibaba-pai, and related community packs).
- Sept 2026 catalog skeletons, curated MCB `h3-loras.md`.
- [fuzzpuppy.com/lora-directory](https://www.fuzzpuppy.com/lora-directory).
