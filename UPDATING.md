# Updating video-lora-kb

One command refreshes everything and publishes it:

```bash
cd /workspace/video-lora-kb && bash scripts/update.sh
```

It is idempotent: with nothing new it changes nothing and exits 0. The **last stdout line is one JSON summary** (counts, changes, runtime, commit SHA); progress goes to stderr.

## Flags

| flag | effect |
|---|---|
| `--dry-run` | do everything, print the summary, **do not commit/push**, and restore the working tree |
| `--no-civitai` | Graydient/HF rematch only (no CivitAI requests) |
| `--no-push` | commit locally, do not push |
| `--max-minutes N` | runtime budget (default 30; CivitAI paging is capped by `--pages`, default 3 per baseModel) |
| `--pages N` | CivitAI "Newest" pages per video baseModel |
| `--allow-dirty` | do not abort on uncommitted changes (the tree is then never auto-restored) |

## What it does (in order)

1. `git pull --rebase` (aborts if the tree is dirty).
2. **New CivitAI LoRAs** (`scripts/add_new_candidates.py`): reads the newest CivitAI pages for every video baseModel (MiniMax H3, Wan, LTXV/LTXV2/2.3/2.5), skips models already known, builds candidate rows with the same builders as `build_kb.py` (triggers, strength and example prompts only when the source states them, never invented) and appends them to `data/candidates.jsonl`. Minor-coded or forbidden-identity names/tags go to `data/excluded.jsonl` instead.
3. **Graydient rematch** (`scripts/filter_accessible.py --refresh-hf`): re-lists `Octavian123/civit`, `civit2` and `private` on Hugging Face (read-only metadata) and rematches. Candidates whose file is now on Graydient **move to available** automatically; candidate ingest priorities are recomputed. If a repo cannot be listed, the run aborts without changes.
4. **Rebuild**: family pages, README counts, the auto-updated "Live inventory" block in `SKILL.md`, `data/accessibility_report.md`, `data/graydient_ingest_queue.*`, and the export pack (`dist/`, copied to `/workspace/share/`).
5. **Proposals and changelog**: `proposals/YYYY-MM-DD.md` and a `CHANGELOG.md` entry listing moved / added / removed LoRAs and the new ingest candidates. Written only when something changed.
6. **Secret scan** of the staged changes (HF/GitHub/CivitAI tokens, bearer tokens, private keys, the Graydient login config key and login URLs, weight files). Any hit aborts the commit.
7. **Commit and push to `main`** only if something changed. GitHub account: `androodee123` only; `GITHUB_TOKEN`/`GH_TOKEN` are unset.

## Proposed vs applied

- **Applied automatically:** catalogs (`data/*.jsonl`), family pages, README, the SKILL.md live block, reports, the ingest queue and the export pack. Everything is metadata; the repo never holds weights.
- **Proposed only:** adding any weights to Graydient. `data/graydient_ingest_queue.md` and the *Suggest ingest* lines are proposals. Ingesting (civit-to-graydient, `ingest.py`) stays a manual step Andrew asks for. These scripts never download weights and never ingest.
- Curated SKILL.md recipes are not rewritten automatically; new LoRAs show up in the live block and the family pages until a recipe is edited by hand.

## Weekly routine

The weekly routine runs `bash scripts/update.sh` from this repo and reports the JSON summary line (counts, new/moved LoRAs, commit SHA, runtime). Run the same command by hand any time.

## Keeping forks and other AIs in sync

- Raw skill on main: `https://raw.githubusercontent.com/androodee123/video-lora-kb/main/SKILL.md`
- Clones: `git pull` (or `git pull --rebase`).
- Share pack for chat attachments: `python3 scripts/export_pack.py` (writes `dist/`).

## Requirements and caches

Python 3 with `huggingface_hub` (HF credentials come from the machine's normal HF login; nothing is stored in the repo) and `gh` logged in as `androodee123`. Raw caches live in `data/raw/` (gitignored). `scripts/check_new.py` remains a read-only preview of new CivitAI LoRAs.
