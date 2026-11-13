# Video LoRA knowledge base

Private, comprehensive catalog of **useful video LoRAs** for MiniMax H3, Wan (2.1, 2.2 14B high/low and 5B TI2V), and LTX (LTXV, LTX-2, 2.3, 2.5).

Coverage is the full CivitAI inventory for the confirmed `baseModel` strings (paged to exhaustion, plus Most Downloaded / Highest Rated checks), Hugging Face official and community speed/control packs, and the [Fuzz Puppy directory](https://www.fuzzpuppy.com/lora-directory). LoRAs **installed** on the AIOps RAID (`/Volumes/RAID/Lora/{H3,Wan,LTX2}`, snapshot 13 Nov 2026) are flagged `installed=true` and sorted first in every table.

Research compiled **13 Nov 2026, 18:37 Africa/Johannesburg (SAST)**. Many entries are adult NSFW and are documented factually. This repo stores **metadata only** — no weights. `scripts/harvest.py` and `scripts/check_new.py` must never download or ingest LoRA files.

## Counts

| Family | Total records | Installed | Installed verified | Installed unverified | Catalog-only (CivitAI/HF) | Verified |
|---|---:|---:|---:|---:|---:|---:|
| MiniMax H3 | 1183 | 244 | 203 | 41 | 939 | 1142 |
| Wan (2.1 / 2.2) | 2451 | 55 | 47 | 8 | 2396 | 2443 |
| LTX-2 / 2.3 / 2.5 | 668 | 32 | 28 | 4 | 636 | 664 |
| **Total** | **4302** | **331** | **278** | **53** | **3971** | **4249** |

Low-value CivitAI rows (under ~100 downloads and no thumbs-up) were dropped unless they were installed. 37 such models were excluded.

### Counts by category

| Category | H3 total (installed) | Wan total (installed) | LTX total (installed) |
|---|---:|---:|---:|
| Motion | 49 (14) | 55 (2) | 41 (4) |
| Camera | 55 (12) | 130 (4) | 43 (2) |
| Audio / voice | 37 (3) | 3 (0) | 12 (0) |
| Style | 298 (47) | 479 (1) | 169 (9) |
| Enhancement / quality / speed | 405 (131) | 768 (31) | 203 (10) |
| Identity / character | 293 (24) | 607 (0) | 147 (0) |
| Effects / VFX | 34 (9) | 112 (0) | 24 (1) |
| Transitions | 3 (2) | 7 (0) | 6 (0) |
| Lighting | 7 (1) | 9 (0) | 5 (0) |
| Physics / cloth / hair | 23 (10) | 17 (0) | 9 (0) |
| NSFW acts and anatomy | 235 (97) | 604 (34) | 112 (19) |
| Anime / 2D | 88 (15) | 348 (1) | 60 (4) |
| Realism | 75 (10) | 95 (0) | 20 (1) |

A LoRA may appear in more than one category.

## How to use this repo

1. Start with [`SKILL.md`](SKILL.md) — a goal→LoRA chooser with recipes across families, stacking, stated strengths, and known conflicts.
2. Open the family + category page under `families/`. Tables list **installed first**, then catalog entries by popularity (downloads).
3. For I2V / T2V prompting and Graydient workflow names, read [`guides/image-to-video.md`](guides/image-to-video.md).
4. Official / utility packs also appear in [`guides/fuzzpuppy-directory.md`](guides/fuzzpuppy-directory.md).
5. Machine-readable data: [`data/loras.jsonl`](data/loras.jsonl).
6. Refresh CivitAI/HF metadata: `python3 scripts/harvest.py` (writes `data/raw/`, gitignored). Propose new models since the last harvest: `python3 scripts/check_new.py`.

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
- `LTXV`
- `LTXV2`
- `LTXV 2.3`
- `LTXV 2.5`

High vs low noise is not a `baseModel` value.

## Reproducing the harvest

```
python3 scripts/harvest.py --sorts newest           # resume from data/raw cache
python3 scripts/harvest.py --verify-sorts           # first page of Most Downloaded / Highest Rated
python3 scripts/harvest.py --hf-only                # official HF org listings
python3 scripts/build_kb.py && python3 scripts/render_kb.py
```

Raw API dumps live in `data/raw/` and are gitignored (tens of megabytes). See `data/raw/README.md`.

## Sources

- CivitAI public API, metadata only (full Newest crawl of the base models above, plus Most Downloaded / Highest Rated first-page checks; two popular models missing from Newest were merged in).
- Hugging Face model listings (Lightricks, lightx2v, alibaba-pai, Kijai, Cseti, fal, Pika-Labs, FuzzPuppy, plus targeted searches for CausVid / self-forcing / distill / camera-control).
- RAID inventory and sidecars, Sept 2026 catalog skeletons, curated MCB `h3-loras.md`.
- [fuzzpuppy.com/lora-directory](https://www.fuzzpuppy.com/lora-directory).
