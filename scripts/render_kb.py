#!/usr/bin/env python3
"""Render family markdown tables and README from data/loras.jsonl + rich records."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

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
    if u.get("huggingface"):
        parts.append(f"[HF]({u['huggingface']})")
    if u.get("civitai_skeleton") and not u.get("civitai"):
        parts.append(f"[skeleton]({u['civitai_skeleton']})")
    return ", ".join(parts) or "—"

def table(rows):
    lines = [
        "| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    for r in rows:
        slug = r.get("slug") or r["file"]
        purpose = esc(r.get("purpose") or r.get("civitai_name") or slug)[:90]
        inst = "installed" if r.get("installed") else "catalog"
        ver = "verified" if r.get("verified") else "unverified"
        if r.get("low_signal"):
            ver += ", low_signal"
        dl = r.get("downloads")
        dl_s = f"{int(dl):,}" if isinstance(dl, (int, float)) and dl is not None else "—"
        lines.append(
            f"| `{esc(slug)}` | {trig(r)} | {esc(r.get('strength') or 'not stated')} | "
            f"{esc(r.get('i2v_t2v') or 'not stated')} | {purpose} | {dl_s} | {inst}, {ver} | {links(r)} |"
        )
    return "\n".join(lines)

def sort_rows(rows):
    def key(r):
        inst = 0 if r.get("installed") else 1
        dl = r.get("downloads")
        dl = -(dl or 0)
        return (inst, dl, (r.get("slug") or r["file"]))
    return sorted(rows, key=key)

def counts(recs):
    out = {}
    for fam in ("H3", "Wan", "LTX2"):
        sub = [r for r in recs if r["family"] == fam]
        inst = [r for r in sub if r.get("installed")]
        out[fam] = {
            "total": len(sub),
            "installed": len(inst),
            "installed_verified": sum(1 for r in inst if r.get("verified")),
            "installed_unverified": sum(1 for r in inst if not r.get("verified")),
            "catalog_only": sum(1 for r in sub if not r.get("installed")),
            "verified": sum(1 for r in sub if r.get("verified")),
            "unverified": sum(1 for r in sub if not r.get("verified")),
            "cats": {c: sum(1 for r in sub if c in (r.get("categories") or [])) for c in CAT_FILE},
            "cats_inst": {c: sum(1 for r in inst if c in (r.get("categories") or [])) for c in CAT_FILE},
        }
    return out

def render_families(recs, rich_by_key):
    written = {}
    for fam, dname in FAM_DIR.items():
        dest = ROOT / "families" / dname
        # remove stale files then rewrite
        dest.mkdir(parents=True, exist_ok=True)
        for old in dest.glob("*.md"):
            old.unlink()
        sub = [r for r in recs if r["family"] == fam]
        written[fam] = []
        for cat, fname in CAT_FILE.items():
            rows = sort_rows([r for r in sub if cat in (r.get("categories") or [])])
            if not rows:
                continue
            inst_n = sum(1 for r in rows if r.get("installed"))
            parts = [
                f"# {fam}: {CAT_TITLE[cat]}",
                "",
                f"{len(rows)} LoRAs ({inst_n} installed on the 13 Nov 2026 RAID snapshot). "
                "Installed rows are listed first, then the rest by CivitAI/HF download count.",
                "",
                "Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.",
                "",
                table(rows),
                "",
            ]
            # rich details: installed with example/strength, plus a few popular catalog rows
            details = []
            popular_added = 0
            for r in rows:
                ex = (rich_by_key.get((r["family"], r["file"], r.get("civitai_model_id"))) or {}).get("example_prompt")
                if r.get("example_prompt"):
                    ex = r["example_prompt"]
                interesting = (r.get("strength") not in (None, "not stated")) or ex or r.get("installed") and r.get("triggers")
                if r.get("installed") and interesting:
                    details.append((r, ex))
                elif (not r.get("installed")) and ex and popular_added < 8:
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
                    if r.get("installed"):
                        meta.append("installed")
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
        written[fam].append(("unverified", "unverified.md", len(unver), sum(1 for r in unver if r.get("installed"))))
        # family index
        idx = [f"# {fam} LoRAs\n", "Installed rows are flagged in every table and sorted first.\n"]
        for cat, fname, n, inst_n in written[fam]:
            title = CAT_TITLE.get(cat, cat)
            idx.append(f"- [{title}]({fname}) — {n} ({inst_n} installed)")
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

def render_readme(recs, c, written):
    h, w, l = c["H3"], c["Wan"], c["LTX2"]
    def cat_table():
        lines = [
            "| Category | H3 total (installed) | Wan total (installed) | LTX total (installed) |",
            "|---|---:|---:|---:|",
        ]
        for cat, title in CAT_TITLE.items():
            lines.append(
                f"| {title} | {h['cats'][cat]} ({h['cats_inst'][cat]}) | "
                f"{w['cats'][cat]} ({w['cats_inst'][cat]}) | "
                f"{l['cats'][cat]} ({l['cats_inst'][cat]}) |"
            )
        return "\n".join(lines)
    return f"""# Video LoRA knowledge base

Private, comprehensive catalog of **useful video LoRAs** for MiniMax H3, Wan (2.1, 2.2 14B high/low and 5B TI2V), and LTX (LTXV, LTX-2, 2.3, 2.5).

Coverage is the full CivitAI inventory for the confirmed `baseModel` strings (paged to exhaustion, plus Most Downloaded / Highest Rated checks), Hugging Face official and community speed/control packs, and the [Fuzz Puppy directory](https://www.fuzzpuppy.com/lora-directory). LoRAs **installed** on the AIOps RAID (`/Volumes/RAID/Lora/{{H3,Wan,LTX2}}`, snapshot 13 Nov 2026) are flagged `installed=true` and sorted first in every table.

Research compiled **{DATE_LABEL}**. Many entries are adult NSFW and are documented factually. This repo stores **metadata only** — no weights. `scripts/harvest.py` and `scripts/check_new.py` must never download or ingest LoRA files.

## Counts

| Family | Total records | Installed | Installed verified | Installed unverified | Catalog-only (CivitAI/HF) | Verified |
|---|---:|---:|---:|---:|---:|---:|
| MiniMax H3 | {h['total']} | {h['installed']} | {h['installed_verified']} | {h['installed_unverified']} | {h['catalog_only']} | {h['verified']} |
| Wan (2.1 / 2.2) | {w['total']} | {w['installed']} | {w['installed_verified']} | {w['installed_unverified']} | {w['catalog_only']} | {w['verified']} |
| LTX-2 / 2.3 / 2.5 | {l['total']} | {l['installed']} | {l['installed_verified']} | {l['installed_unverified']} | {l['catalog_only']} | {l['verified']} |
| **Total** | **{h['total']+w['total']+l['total']}** | **{h['installed']+w['installed']+l['installed']}** | **{h['installed_verified']+w['installed_verified']+l['installed_verified']}** | **{h['installed_unverified']+w['installed_unverified']+l['installed_unverified']}** | **{h['catalog_only']+w['catalog_only']+l['catalog_only']}** | **{h['verified']+w['verified']+l['verified']}** |

Low-download CivitAI rows (under ~100 downloads and no thumbs-up) are kept and flagged `low_signal=true` rather than dropped, so niche but relevant LoRAs stay in the catalog.

### Counts by category

{cat_table()}

A LoRA may appear in more than one category.

{coverage_block(recs)}

## How to use this repo

1. Start with [`SKILL.md`](SKILL.md) — a goal→LoRA chooser with recipes across families, stacking, stated strengths, and known conflicts.
2. Open the family + category page under `families/`. Tables list **installed first**, then catalog entries by popularity (downloads).
3. For I2V / T2V prompting and Graydient workflow names, read [`guides/image-to-video.md`](guides/image-to-video.md). Per-family prompt templates and trigger usage: [`guides/prompt-patterns.md`](guides/prompt-patterns.md).
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
python3 scripts/harvest.py --full-sorts --period AllTime   # Newest + Most Downloaded + Highest Rated, all bases
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
"""

def main():
    recs = [json.loads(l) for l in (ROOT / "data" / "loras.jsonl").read_text().splitlines() if l.strip()]
    rich = {}
    rp = Path("/tmp/vlora-work/records-full.json")
    if rp.exists():
        for r in json.loads(rp.read_text()):
            rich[(r["family"], r["file"], r.get("civitai_model_id"))] = r
            if r.get("example_prompt") and not any(x.get("example_prompt") for x in [r]):
                pass
        # copy example prompts onto recs
        for r in recs:
            src = rich.get((r["family"], r["file"], r.get("civitai_model_id")))
            if src and src.get("example_prompt") and not r.get("example_prompt"):
                r["example_prompt"] = src["example_prompt"]
    c = counts(recs)
    written = render_families(recs, rich)
    (ROOT / "README.md").write_text(render_readme(recs, c, written), encoding="utf-8")
    print("rendered", json.dumps({k: v for k, v in written.items()}, indent=2)[:2000])
    print("counts", {k: {kk: vv for kk, vv in val.items() if kk not in ("cats", "cats_inst")} for k, val in c.items()})

if __name__ == "__main__":
    main()
