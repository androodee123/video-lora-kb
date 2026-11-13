#!/usr/bin/env python3
"""Render family markdown tables and README from data/loras.jsonl + rich records."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import access_rules as R

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Africa/Johannesburg")
NOW = datetime.now(TZ)
DATE_LABEL = NOW.strftime("%-d %b %Y, %H:%M") + " Africa/Johannesburg (SAST)"

FAM_DIR = {"H3": "h3", "Wan": "wan", "LTX2": "ltx"}
CAT_FILE = {
    "motion": "motion.md",
    "camera": "camera.md",
    "audio": "audio.md",
    "style": "style.md",
    "enhancement": "enhancement.md",
    "identity": "identity.md",
    "effects": "effects.md",
    "transitions": "transitions.md",
    "lighting": "lighting.md",
    "physics": "physics.md",
    "nsfw-act": "nsfw-acts.md",
    "anime": "anime.md",
    "realism": "realism.md",
    "character_consistency": "character-consistency.md",
    "object_control": "object-control.md",
    "pose": "pose.md",
    "lipsync": "lipsync.md",
}
CAT_TITLE = {
    "motion": "Motion",
    "camera": "Camera",
    "audio": "Audio / voice",
    "style": "Style",
    "enhancement": "Enhancement / quality / speed",
    "identity": "Identity / character",
    "effects": "Effects / VFX",
    "transitions": "Transitions",
    "lighting": "Lighting",
    "physics": "Physics / cloth / hair",
    "nsfw-act": "NSFW acts and anatomy",
    "anime": "Anime / 2D",
    "realism": "Realism",
    "character_consistency": "Character consistency",
    "object_control": "Object control",
    "pose": "Pose / control",
    "lipsync": "Lipsync",
}

def esc(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()

def trig(r):
    t = r.get("triggers") or []
    return ", ".join(f"`{x}`" for x in t[:5]) if t else "—"

def links(r):
    u = r.get("urls") or {}
    parts = []
    if u.get("civitai"):
        parts.append(f"[CivitAI]({u['civitai']})")
    hf = u.get("huggingface")
    gd = u.get("graydient_hf")
    if hf:
        parts.append(f"[HF]({hf})")
    if gd and gd != hf:
        parts.append(f"[Graydient HF]({gd})")
    if u.get("civitai_skeleton") and not u.get("civitai"):
        parts.append(f"[skeleton]({u['civitai_skeleton']})")
    return ", ".join(parts) or "—"

def status_of(r):
    lab = R.access_label_pretty(r)
    ver = "verified" if r.get("verified") else "unverified"
    if r.get("low_signal"):
        ver += ", low_signal"
    return f"{lab}, {ver}"

def table(rows):
    lines = [
        "| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    for r in rows:
        slug = r.get("slug") or r["file"]
        purpose = esc(r.get("purpose") or r.get("civitai_name") or slug)[:90]
        dl = r.get("downloads")
        dl_s = f"{int(dl):,}" if isinstance(dl, (int, float)) and dl is not None else "—"
        lines.append(
            f"| `{esc(slug)}` | {trig(r)} | {esc(r.get('strength') or 'not stated')} | "
            f"{esc(r.get('i2v_t2v') or 'not stated')} | {purpose} | {dl_s} | {status_of(r)} | {links(r)} |"
        )
    return "\n".join(lines)

def sort_rows(rows):
    def key(r):
        dl = -(r.get("downloads") or 0)
        return (R.status_rank(r), dl, (r.get("slug") or r["file"]))
    return sorted(rows, key=key)

def counts(recs, cands=None):
    cands = cands or []
    out = {}
    for fam in ("H3", "Wan", "LTX2"):
        sub = [r for r in recs if r["family"] == fam]
        g = [r for r in sub if R.is_on_graydient(r)]
        to_add = [r for r in sub if R.is_to_add(r)]
        a = [r for r in sub if r.get("aiops") or r.get("installed")]
        inst = a
        out[fam] = {
            "total": len(sub),
            "on_graydient": len(g),
            "to_add": len(to_add),
            "graydient": len(g),
            "aiops": len(a),
            "installed": len(inst),
            "installed_verified": sum(1 for r in inst if r.get("verified")),
            "installed_unverified": sum(1 for r in inst if not r.get("verified")),
            "catalog_only": sum(1 for r in sub if not (r.get("aiops") or r.get("installed"))),
            "candidates": sum(1 for r in cands if r.get("family") == fam),
            "verified": sum(1 for r in sub if r.get("verified")),
            "unverified": sum(1 for r in sub if not r.get("verified")),
            "cats": {c: sum(1 for r in sub if c in (r.get("categories") or [])) for c in CAT_FILE},
            "cats_inst": {c: sum(1 for r in inst if c in (r.get("categories") or [])) for c in CAT_FILE},
            "cats_on": {c: sum(1 for r in g if c in (r.get("categories") or [])) for c in CAT_FILE},
            "cats_toadd": {c: sum(1 for r in to_add if c in (r.get("categories") or [])) for c in CAT_FILE},
        }
    return out

def suggest_why(c, accessible_rows):
    gap = len(accessible_rows) == 0
    max_dl = max((r.get("downloads") or 0) for r in accessible_rows) if accessible_rows else 0
    dl = c.get("downloads") or 0
    reasons = []
    if gap:
        reasons.append("no accessible LoRA in this category")
    elif dl >= R.SUGGEST_MIN_DOWNLOADS and dl >= R.SUGGEST_RATIO * max(max_dl, 1):
        reasons.append(f"high-value upgrade ({dl:,} downloads, ≥{R.SUGGEST_RATIO:g}× the top accessible)")
    if R.is_official_util(c) and not any(R.is_official_util(r) for r in accessible_rows):
        reasons.append("official utility pack with no accessible equivalent")
    return "; ".join(reasons) or "ranked ingest candidate"

def suggest_section(fam, cat, accessible_rows, all_candidates):
    cands = [r for r in all_candidates if r.get("family") == fam and cat in (r.get("categories") or [])]
    picked = R.pick_suggestions(cands, accessible_rows, limit=R.MAX_SUGGEST_PER_CATEGORY)
    if not picked:
        return []
    lines = [
        "## Suggest ingest",
        "",
        "These are **not** in the available Graydient set yet. Suggestion only — "
        "download and ingest them yourself with the civit-to-graydient pipeline if you want them. "
        "**Nothing here is auto-downloaded.**",
        "",
        "| slug / file | trigger | strength | downloads | ingest priority | why | links |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for r in picked:
        slug = r.get("slug") or r["file"]
        dl = r.get("downloads")
        dl_s = f"{int(dl):,}" if isinstance(dl, (int, float)) and dl is not None else "—"
        pri = r.get("ingest_priority")
        pri_s = f"{pri:.1f}" if isinstance(pri, (int, float)) else "—"
        lines.append(
            f"| `{esc(slug)}` | {trig(r)} | {esc(r.get('strength') or 'not stated')} | "
            f"{dl_s} | {pri_s} | {esc(suggest_why(r, accessible_rows))} | {links(r)} |"
        )
    lines.append("")
    return lines

def render_families(recs, rich_by_key, candidates=None):
    written = {}
    for fam, dname in FAM_DIR.items():
        dest = ROOT / "families" / dname
        # remove stale files then rewrite
        dest.mkdir(parents=True, exist_ok=True)
        for old in dest.glob("*.md"):
            old.unlink()
        sub = [r for r in recs if r["family"] == fam]
        candidates = candidates or []
        written[fam] = []
        for cat, fname in CAT_FILE.items():
            rows = sort_rows([r for r in sub if cat in (r.get("categories") or [])])
            suggest = suggest_section(fam, cat, rows, candidates)
            if not rows and not suggest:
                continue
            inst_n = sum(1 for r in rows if r.get("aiops") or r.get("installed"))
            gd_n = sum(1 for r in rows if R.is_on_graydient(r))
            to_add_n = sum(1 for r in rows if R.is_to_add(r))
            if rows:
                intro = (
                    f"{len(rows)} available Graydient LoRAs ({gd_n} already on Graydient, "
                    f"{to_add_n} still to add to Graydient). "
                    "Everything in this table is part of the Graydient set: files already in "
                    "`Octavian123/civit`, `Octavian123/civit2`, or `Octavian123/private` are listed first; "
                    "RAID files that still need ingest are labelled *to add to Graydient* "
                    "(or *to add to Graydient (no public source; needs local upload)* when there is no public URL) "
                    "and must be ingested before they appear in the concept browser. There is no AIOps-only category. "
                    "Nothing is auto-downloaded."
                )
            else:
                intro = (
                    "No LoRA in this category is in the available Graydient set yet. "
                    "See *Suggest ingest* below for high-value candidates. Nothing is auto-downloaded."
                )
            parts = [
                f"# {fam}: {CAT_TITLE[cat]}",
                "",
                intro,
                "",
                "Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.",
                "",
            ]
            if rows:
                parts += [table(rows), ""]
            parts.extend(suggest)
            # rich details: installed with example/strength, plus a few popular catalog rows
            details = []
            popular_added = 0
            for r in rows:
                ex = (rich_by_key.get((r["family"], r["file"], r.get("civitai_model_id"))) or {}).get("example_prompt")
                if r.get("example_prompt"):
                    ex = r["example_prompt"]
                interesting = (r.get("strength") not in (None, "not stated")) or ex or r.get("installed") and r.get("triggers")
                if (r.get("aiops") or r.get("installed") or r.get("graydient")) and interesting:
                    details.append((r, ex))
                elif (not (r.get("aiops") or r.get("installed"))) and ex and popular_added < 8:
                    details.append((r, ex))
                    popular_added += 1
            if details:
                parts.append("## Details")
                parts.append("")
                for r, ex in details[:40]:
                    title = r.get("civitai_name") or r.get("purpose") or r["file"]
                    parts.append(f"### `{r['file']}`")
                    parts.append("")
                    parts.append(f"**{esc(title)}**")
                    meta = []
                    if r.get("base"):
                        meta.append(f"base `{r['base']}`")
                    meta.append(r.get("i2v_t2v") or "I2V/T2V not stated")
                    if r.get("strength") and r["strength"] != "not stated":
                        meta.append(f"strength (stated): {r['strength']}")
                    else:
                        meta.append("strength: not stated")
                    if r.get("triggers"):
                        meta.append("triggers: " + ", ".join(f"`{t}`" for t in r["triggers"][:8]))
                    if r.get("graydient") or r.get("aiops") or r.get("installed"):
                        meta.append(R.access_label_pretty(r))
                    parts.append("- " + " · ".join(meta))
                    if not r.get("verified"):
                        parts.append("- **Unverified** — no confirmed live page, or the listed id 404'd.")
                    prompts = r.get("example_prompts") or ([ex] if ex else [])
                    if prompts:
                        parts.append("")
                        parts.append("Example prompt" + ("s" if len(prompts) > 1 else "") + " (from the images API, page, or sidecar; never invented):")
                        for i, pr in enumerate(prompts[:2], 1):
                            parts += ["", f"Example {i}:" if len(prompts) > 1 else "", "```", str(pr).strip()[:1200], "```"]
                    if r.get("compatibility"):
                        parts.append("")
                        parts.append("Compatibility: " + "; ".join(str(x) for x in r["compatibility"]))
                    if r.get("urls"):
                        parts.append(f"\nSource: {links(r)}")
                    parts.append("")
            (dest / fname).write_text("\n".join(parts) + "\n", encoding="utf-8")
            written[fam].append((cat, fname, len(rows), inst_n))
        unver = sort_rows([r for r in sub if not r.get("verified")])
        (dest / "unverified.md").write_text(
            f"# {fam}: Unverified stubs\n\n"
            "These could not be confirmed against a live CivitAI or Hugging Face page. "
            "Do not invent triggers or strengths for them.\n\n"
            + (table(unver) if unver else "None.\n")
            + "\n",
            encoding="utf-8",
        )
        written[fam].append(("unverified", "unverified.md", len(unver), sum(1 for r in unver if r.get("aiops") or r.get("installed"))))
        # family index
        idx = [f"# {fam} LoRAs\n",
               "Tables list **available** Graydient LoRAs only (already on Graydient, or still to add). "
               "A *Suggest ingest* block lists high-value candidates that are not yet available. "
               "Suggestions are not auto-downloaded.\n"]
        for cat, fname, n, inst_n in written[fam]:
            title = CAT_TITLE.get(cat, cat)
            if cat == "unverified":
                idx.append(f"- [{title}]({fname}) — {n}")
            else:
                idx.append(f"- [{title}]({fname}) — {n} accessible")
        (dest / "README.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
    return written

def coverage_block(recs):
    n = len(recs) or 1
    trig = sum(1 for r in recs if r.get("triggers"))
    strn = sum(1 for r in recs if r.get("strength") not in (None, "", "not stated"))
    ex = sum(1 for r in recs if r.get("example_prompts") or r.get("example_prompt"))
    low = sum(1 for r in recs if r.get("low_signal"))
    return (
        f"Of {len(recs)} rows: **{trig}** ({100*trig/n:.1f}%) have at least one recorded trigger, "
        f"**{strn}** ({100*strn/n:.1f}%) have a stated strength, "
        f"**{ex}** ({100*ex/n:.1f}%) have at least one example prompt (images API or page text). "
        f"**{low}** rows are flagged `low_signal`. Missing fields are recorded as `not stated` / empty — never invented."
    )

def render_readme(recs, c, written, cand_n=0):
    h, w, l = c["H3"], c["Wan"], c["LTX2"]
    def cat_table():
        lines = [
            "| Category | H3 available (on Graydient / to add) | Wan available (on Graydient / to add) | LTX available (on Graydient / to add) |",
            "|---|---:|---:|---:|",
        ]
        for cat, title in CAT_TITLE.items():
            lines.append(
                f"| {title} | {h['cats'][cat]} ({h['cats_on'][cat]}/{h['cats_toadd'][cat]}) | "
                f"{w['cats'][cat]} ({w['cats_on'][cat]}/{w['cats_toadd'][cat]}) | "
                f"{l['cats'][cat]} ({l['cats_on'][cat]}/{l['cats_toadd'][cat]}) |"
            )
        return "\n".join(lines)
    return f"""# Video LoRA knowledge base

Private catalog of **available Graydient video LoRAs** for MiniMax H3, Wan (2.1 including 1.3B T2V, 2.2 14B high/low and 5B TI2V), and LTX (LTXV, LTX-2, 2.3, 2.5). Every row in `data/loras.jsonl` is a Graydient LoRA. `graydient_status` is **on Graydient** when a matching weight is already in Hugging Face `Octavian123/civit`, `Octavian123/civit2`, or `Octavian123/private`, or **to add to Graydient** (including **to add to Graydient (no public source; needs local upload)**) when the file is on the 13 Nov 2026 RAID snapshot (`/Volumes/RAID/Lora/{{H3,Wan,LTX2}}`, `aiops=true`) and still needs ingest before it appears in the concept browser. There is no “AIOps only” category — anything on the RAID must be added to Graydient.

Public CivitAI / Hugging Face video LoRAs that are not yet in this set live in [`data/candidates.jsonl`](data/candidates.jsonl) with an `ingest_priority` score. They are suggested for ingest when they fill a gap or clearly outrank what is already available — never auto-downloaded. The RAID files that still need ingest are listed in [`data/graydient_ingest_queue.md`](data/graydient_ingest_queue.md).

**Out of scope** (image LoRAs, checkpoints, finetunes, merges, full base-model repos, pure workflows, ControlNets that are not LoRAs, VAEs, text encoders, GGUF/quantised full models, and non-video families such as Hunyuan) are not in `data/loras.jsonl`. Installed RAID files that fail this test are in [`data/excluded.jsonl`](data/excluded.jsonl) with a reason. See [`data/accessibility_report.md`](data/accessibility_report.md) for the last accessibility filter.

Research compiled **{DATE_LABEL}**. Many entries are adult NSFW and are documented factually. This repo stores **metadata only** — no weights. `scripts/harvest.py`, `scripts/check_new.py`, and `scripts/filter_accessible.py` must never download or ingest LoRA files.

## Counts

| Family | On Graydient | To add to Graydient | Available total | Candidates |
|---|---:|---:|---:|---:|
| MiniMax H3 | {h['on_graydient']} | {h['to_add']} | {h['total']} | {h['candidates']} |
| Wan (2.1 / 2.2) | {w['on_graydient']} | {w['to_add']} | {w['total']} | {w['candidates']} |
| LTX-2 / 2.3 / 2.5 | {l['on_graydient']} | {l['to_add']} | {l['total']} | {l['candidates']} |
| **Total** | **{h['on_graydient']+w['on_graydient']+l['on_graydient']}** | **{h['to_add']+w['to_add']+l['to_add']}** | **{h['total']+w['total']+l['total']}** | **{h['candidates']+w['candidates']+l['candidates']}** |

Recommend a LoRA that is already on Graydient first. If the pick is labelled *to add to Graydient*, ingest it before using it in the concept browser (not auto-downloaded). RAID-only files with no public URL need a local upload. Suggest ingest of a public candidate when the category or goal has no available option, or when a candidate is clearly stronger (at least 2,000 downloads and at least 2× the top available download count in that category) or is an official utility pack with no available equivalent. The full rule is in [`SKILL.md`](SKILL.md).

### Counts by category (available)

{cat_table()}

A LoRA may appear in more than one category.

{coverage_block(recs)}

## How to use this repo

1. Start with [`SKILL.md`](SKILL.md) — a goal→LoRA chooser. Recipes recommend available Graydient LoRAs first. Picks labelled *to add to Graydient* must be ingested (or locally uploaded if there is no public source) before use. When the rule says so, a *Suggest ingest* line points at a public candidate.
2. Open the family + category page under `families/`. Tables list available LoRAs (on Graydient first, then to add), then a *Suggest ingest* block when the rule fires.
3. For I2V / T2V prompting and Graydient workflow names, read [`guides/image-to-video.md`](guides/image-to-video.md). Per-family prompt templates and trigger usage: [`guides/prompt-patterns.md`](guides/prompt-patterns.md).
4. Official / utility packs also appear in [`guides/fuzzpuppy-directory.md`](guides/fuzzpuppy-directory.md). If they are not already on Graydient, treat them as ingest candidates.
5. Machine-readable data: [`data/loras.jsonl`](data/loras.jsonl) (available Graydient set), [`data/graydient_ingest_queue.md`](data/graydient_ingest_queue.md) (RAID files still to add), [`data/candidates.jsonl`](data/candidates.jsonl) (ranked public candidates), [`data/excluded.jsonl`](data/excluded.jsonl) (non-video or otherwise dropped, with a reason).
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
python3 scripts/harvest.py --enrich --enrich-images        # full /models/{{id}} + example-prompt images API
python3 scripts/harvest.py --full-sorts --bases 'Wan Video 1.3B t2v'
python3 scripts/build_kb.py
python3 scripts/filter_accessible.py    # rematch civit + civit2 + private; available set (on Graydient or to add); rest -> data/candidates.jsonl
python3 scripts/render_kb.py
python3 scripts/export_pack.py
```

Raw API dumps live in `data/raw/` and are gitignored (tens of megabytes). See `data/raw/README.md`.

## Sources

- Hugging Face `Octavian123/civit`, `Octavian123/civit2`, and `Octavian123/private` file listings (Graydient access). Metadata only — weights are never downloaded by these scripts.
- AIOps RAID inventory and sidecars (`/Volumes/RAID/Lora/{{H3,Wan,LTX2}}`, snapshot 13 Nov 2026).
- CivitAI public API, metadata only (every confirmed baseModel paged with Newest, Most Downloaded, and Highest Rated, including `period=AllTime`; keyword queries; full `/api/v1/models/{{id}}` descriptions and `/api/v1/images` example prompts when the public API returns `meta.prompt`).
- Hugging Face Hub search (author lists plus `models?search=` / pipeline tags for Wan-AI / Wan2.1 / Wan2.2, Lightricks / LTX, MiniMax, lightx2v, alibaba-pai, and related community packs).
- Sept 2026 catalog skeletons, curated MCB `h3-loras.md`.
- [fuzzpuppy.com/lora-directory](https://www.fuzzpuppy.com/lora-directory).
"""

def main():
    recs = [json.loads(l) for l in (ROOT / "data" / "loras.jsonl").read_text().splitlines() if l.strip()]
    cand_path = ROOT / "data" / "candidates.jsonl"
    candidates = []
    if cand_path.exists():
        candidates = [json.loads(l) for l in cand_path.read_text().splitlines() if l.strip()]
    rich = {}
    rp = Path("/tmp/vlora-work/records-full.json")
    if rp.exists():
        for r in json.loads(rp.read_text()):
            rich[(r["family"], r["file"], r.get("civitai_model_id"))] = r
        for r in recs:
            src = rich.get((r["family"], r["file"], r.get("civitai_model_id")))
            if src and src.get("example_prompt") and not r.get("example_prompt"):
                r["example_prompt"] = src["example_prompt"]
    c = counts(recs, candidates)
    written = render_families(recs, rich, candidates)
    (ROOT / "README.md").write_text(render_readme(recs, c, written, len(candidates)), encoding="utf-8")
    print("rendered", json.dumps({k: v for k, v in written.items()}, indent=2)[:2000])
    print("counts", {k: {kk: vv for kk, vv in val.items() if kk not in ("cats", "cats_inst")} for k, val in c.items()})

if __name__ == "__main__":
    main()
