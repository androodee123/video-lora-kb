#!/usr/bin/env python3
"""Build a privacy-preserving share pack in dist/ from the knowledge base.

Produces a prompt-ready skill markdown, compact catalog JSON/CSV, a Claude
Agent Skill zip, and a combined share zip. Metadata only. Never invents
strengths or triggers. Never downloads weights.

Usage:
    python3 scripts/export_pack.py
"""
from __future__ import annotations

import csv
import io
import json
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_kb as R

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DATA = ROOT / "data" / "loras.jsonl"
SKILL_SRC = ROOT / "SKILL.md"
GUIDES = ROOT / "guides"
FAMILIES = ROOT / "families"

MAX_SKILL_BYTES = 150 * 1024
DEFAULT_PER_CAT = 15
MIN_PER_CAT = 6
PROMPT_TRUNCATE = 300
NAME_TRUNCATE = 72
TRIGGER_TRUNCATE = 60

FAMILY_ORDER = ("H3", "Wan", "LTX2")
FAMILY_LABEL = {"H3": "MiniMax H3", "Wan": "Wan 2.1 / 2.2", "LTX2": "LTX-2 / 2.3 / 2.5"}
# Fixed zip timestamps for deterministic archives (catalog snapshot date).
ZIP_DATE = (2026, 11, 13, 0, 0, 0)
# Derived from the repo so the pack keeps building as the catalog grows (update.py).
EXPECTED_COUNT = sum(1 for _l in DATA.read_text(encoding="utf-8").split("\n") if _l.strip())
EXPECTED_RECIPES = len(re.findall(r"^### \d+\. ", SKILL_SRC.read_text(encoding="utf-8"), re.M))

FRONTMATTER = """\
---
name: video-lora-kb
description: >-
  Choose and stack video LoRAs for MiniMax H3, Wan 2.1/2.2 (14B high/low and
  5B TI2V), and LTX-2/2.3/2.5 (T2V and I2V). Use when picking, comparing, or
  combining video LoRAs. Prefer LoRAs already on Graydient when they cover the goal; if a pick is still *to add to Graydient*, ingest it first;
  never invent triggers or strengths.
---
"""

INTRO = """\
# Skill: choose a video LoRA

Comprehensive goal→LoRA chooser for MiniMax H3, Wan 2.1 / 2.2 (14B high/low and 5B TI2V), and LTX-2 / 2.3 / 2.5. Prefer **available** Graydient LoRAs (already on Graydient, or *to add to Graydient* after civit-to-graydient ingest) when they cover the goal. Where a high-value candidate is not yet available, add a clearly labelled Suggest ingest line; never auto-download. Adult NSFW LoRAs are in scope — describe them factually.

This is a standalone, prompt-ready export of the private `video-lora-kb` knowledge base (390 video LoRAs; RAID snapshot 13 Nov 2026; Graydient source: Octavian123/civit, civit2, and private). It stores **metadata only** — no weights.

**Never invent a trigger or a strength.** If the catalog says a strength is blank / `not stated`, or a trigger cell is empty, say so and tune on a short test clip. A general H3 starting range of 0.6–0.9 is only a rule of thumb, not per-file data.

Names use catalog slugs. Compact top-N tables list available Graydient LoRAs (on Graydient first, then to add). Candidates that are not yet available appear only as Suggest ingest. The accessible catalog is in `video-lora-catalog.json` / `.csv` in the same share pack.

"""


def load_rows() -> list[dict[str, Any]]:
    rows = []
    with DATA.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if len(rows) != EXPECTED_COUNT:
        print(
            f"warning: catalog has {len(rows)} rows, expected {EXPECTED_COUNT}",
            file=sys.stderr,
        )
    return rows


def display_name(r: dict) -> str:
    return (r.get("civitai_name") or r.get("purpose") or r.get("slug") or r["file"] or "").strip()


def primary_url(r: dict) -> str:
    u = r.get("urls") or {}
    return u.get("civitai") or u.get("huggingface") or u.get("civitai_skeleton") or ""


def stated_strength(r: dict) -> str:
    s = (r.get("strength") or "").strip()
    if not s or s.lower() == "not stated":
        return ""
    return s


def trigger_text(r: dict, limit: int | None = None) -> str:
    t = r.get("triggers") or []
    if not t:
        return ""
    s = ", ".join(str(x) for x in t)
    if limit and len(s) > limit:
        s = s[: limit - 1].rstrip() + "…"
    return s


def categories_of(r: dict) -> list[str]:
    raw = r.get("categories") or []
    order = {c: i for i, c in enumerate(R.CAT_FILE)}
    return sorted(raw, key=lambda c: (order.get(c, 999), c))


def category_field(r: dict) -> str:
    return "|".join(categories_of(r))


def make_id(r: dict) -> str:
    fam = r["family"]
    slug = r.get("slug") or Path(str(r.get("file") or "unnamed")).stem
    fname = r.get("file") or slug
    if r.get("civitai_model_id") is not None:
        vid = r.get("version_id") if r.get("version_id") is not None else "v"
        return f"{fam}:civitai:{r['civitai_model_id']}:{vid}:{slug}:{fname}"
    if r.get("hf_id"):
        return f"{fam}:hf:{r['hf_id']}:{slug}:{fname}"
    return f"{fam}:local:{slug}:{fname}"


def truncate_prompt(s: str | None, n: int = PROMPT_TRUNCATE) -> str:
    text = (s or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(text) <= n:
        return text
    cut = text[: n - 1].rstrip()
    return cut + "…"


def md_cell(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").replace("\r", " ").strip()


def sort_catalog(rows: list[dict]) -> list[dict]:
    fam_rank = {f: i for i, f in enumerate(FAMILY_ORDER)}

    def key(r):
        dl = r.get("downloads")
        dl = -(dl or 0)
        return (
            fam_rank.get(r.get("family"), 99),
            0 if (r.get("graydient_status") == "on Graydient" or r.get("graydient")) else 1,
            dl,
            (r.get("slug") or ""),
            (r.get("file") or ""),
            make_id(r),
        )

    return sorted(rows, key=key)


def compact_record(r: dict) -> dict[str, Any]:
    dl = r.get("downloads")
    if dl is None or dl == "":
        downloads = None
    else:
        downloads = int(dl)
    return {
        "id": make_id(r),
        "family": r.get("family") or "",
        "base": r.get("base") or "",
        "category": category_field(r),
        "name": display_name(r),
        "trigger": trigger_text(r),
        "strength": stated_strength(r),
        "graydient_status": r.get("graydient_status") or "",
        "graydient_slug": r.get("graydient_slug") or r.get("slug") or "",
        "graydient_hf": (r.get("urls") or {}).get("graydient_hf") or "",
        "aiops": bool(r.get("aiops")),
        "installed": bool(r.get("installed")),
        "url": primary_url(r),
        "downloads": downloads,
        "example_prompt": truncate_prompt(r.get("example_prompt")),
    }


def assert_unique_ids(rows: list[dict]) -> None:
    ids = [make_id(r) for r in rows]
    if len(set(ids)) != len(ids):
        seen = {}
        dups = []
        for i in ids:
            if i in seen:
                dups.append(i)
            seen[i] = True
        raise SystemExit(f"non-unique catalog ids, e.g. {dups[:5]}")


def extract_skill_sections(text: str) -> tuple[str, str]:
    """Return (stacking/selection body, recipes body) from SKILL.md."""
    # Drop the original H1 and the first intro paragraphs; we replace those.
    # Keep from "## How to stack" through the end of recipes, minus "Where to look next".
    m = re.search(r"^## How to stack \(read this first\)\s*$", text, re.M)
    if not m:
        raise SystemExit("SKILL.md missing 'How to stack' heading")
    rest = text[m.start() :]
    look = re.search(r"^## Where to look next\s*$", rest, re.M)
    if look:
        rest = rest[: look.start()].rstrip() + "\n"
    rec = re.search(r"^## Goal recipes\s*$", rest, re.M)
    if not rec:
        raise SystemExit("SKILL.md missing 'Goal recipes' heading")
    stacking = rest[: rec.start()].rstrip() + "\n"
    recipes = rest[rec.start() :].rstrip() + "\n"
    return stacking, recipes


def count_recipes(text: str) -> int:
    return len(re.findall(r"^### (\d+)\.\s", text, re.M))


def strip_guide_title(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip() + "\n"
    return text


def link_cell(r: dict) -> str:
    u = primary_url(r)
    if not u:
        return ""
    label = "HF" if "huggingface.co" in u else "CivitAI"
    return f"[{label}]({u})"


def top_table(rows: list[dict], n: int) -> str:
    chosen = R.sort_rows(rows)[:n]
    lines = [
        "| Name | Trigger | Strength | Installed | Link |",
        "|---|---|---|---|---|",
    ]
    for r in chosen:
        name = display_name(r)
        if len(name) > NAME_TRUNCATE:
            name = name[: NAME_TRUNCATE - 1].rstrip() + "…"
        inst = "yes" if r.get("installed") else ""
        lines.append(
            f"| {md_cell(name)} | {md_cell(trigger_text(r, TRIGGER_TRUNCATE))} | "
            f"{md_cell(stated_strength(r))} | {inst} | {link_cell(r)} |"
        )
    return "\n".join(lines)


def build_top_sections(rows: list[dict], per_cat: int) -> str:
    parts = [
        "## Top LoRAs per family and category",
        "",
        f"Up to {per_cat} LoRAs per category: **available first** (on Graydient, then to add to Graydient), then by download count. "
        "Trigger and strength are shown only when already recorded in the catalog — never invented. "
        "A blank trigger or strength means `not stated`. A LoRA may appear in more than one category. "
        f"Full catalog ({len(rows)} rows): `video-lora-catalog.json` / `video-lora-catalog.csv`.",
        "",
    ]
    for fam in FAMILY_ORDER:
        sub = [r for r in rows if r.get("family") == fam]
        inst_n = sum(1 for r in sub if r.get("installed"))
        parts.append(f"## {FAMILY_LABEL[fam]} (`{fam}`)")
        parts.append("")
        on_n = sum(1 for r in sub if (r.get("graydient_status")=="on Graydient" or r.get("graydient")))
        to_n = len(sub) - on_n
        parts.append(f"{len(sub)} available Graydient LoRAs in this family ({on_n} on Graydient, {to_n} to add).")
        parts.append("")
        for cat, _fname in R.CAT_FILE.items():
            cat_rows = [r for r in sub if cat in (r.get("categories") or [])]
            if not cat_rows:
                continue
            inst_c = sum(1 for r in cat_rows if r.get("installed"))
            shown = min(per_cat, len(cat_rows))
            title = R.CAT_TITLE[cat]
            parts.append(
                f"### {fam} — {title} ({len(cat_rows)} available; showing {shown})"
            )
            parts.append("")
            parts.append(top_table(cat_rows, per_cat))
            parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def build_skill_markdown(rows: list[dict], per_cat: int) -> str:
    skill_src = SKILL_SRC.read_text(encoding="utf-8")
    stacking, recipes = extract_skill_sections(skill_src)
    n_rec = count_recipes(recipes)
    if n_rec != EXPECTED_RECIPES:
        raise SystemExit(f"expected {EXPECTED_RECIPES} recipes, found {n_rec}")

    i2v = (GUIDES / "image-to-video.md").read_text(encoding="utf-8")
    patterns = (GUIDES / "prompt-patterns.md").read_text(encoding="utf-8")

    parts = [
        FRONTMATTER,
        INTRO,
        stacking,
        "\n## Image-to-video and text-to-video\n\n",
        strip_guide_title(i2v),
        "\n## Prompt patterns and trigger usage\n\n",
        strip_guide_title(patterns),
        "\n",
        recipes,
        "\n",
        build_top_sections(rows, per_cat),
    ]
    return "".join(parts)


def fit_skill_markdown(rows: list[dict]) -> tuple[str, int]:
    per_cat = DEFAULT_PER_CAT
    text = build_skill_markdown(rows, per_cat)
    while len(text.encode("utf-8")) > MAX_SKILL_BYTES and per_cat > MIN_PER_CAT:
        per_cat -= 1
        text = build_skill_markdown(rows, per_cat)
    size = len(text.encode("utf-8"))
    if size > MAX_SKILL_BYTES:
        print(
            f"warning: skill markdown is {size} bytes at {per_cat}/category "
            f"(target {MAX_SKILL_BYTES})",
            file=sys.stderr,
        )
    return text, per_cat


def write_json(path: Path, records: list[dict]) -> None:
    payload = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    path.write_text(payload + "\n", encoding="utf-8")


def write_csv(path: Path, records: list[dict]) -> None:
    fields = [
        "id",
        "family",
        "base",
        "category",
        "name",
        "trigger",
        "strength",
        "graydient_status",
        "graydient_slug",
        "graydient_hf",
        "aiops",
        "installed",
        "url",
        "downloads",
        "example_prompt",
    ]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for rec in records:
        row = dict(rec)
        if row.get("installed") is True:
            row["installed"] = "true"
        elif row.get("installed") is False:
            row["installed"] = "false"
        if row.get("aiops") is True:
            row["aiops"] = "true"
        elif row.get("aiops") is False:
            row["aiops"] = "false"
        if row.get("downloads") is None:
            row["downloads"] = ""
        w.writerow(row)
    path.write_text(buf.getvalue(), encoding="utf-8")


def how_to_use_md() -> str:
    return """\
# How to use the video LoRA share pack

This pack is a privacy-preserving export of the private `video-lora-kb` knowledge base (video LoRAs for MiniMax H3, Wan, and LTX). It contains **metadata only** — no LoRA weights. Triggers and strengths are copied from the catalog; blank means not stated. Do not invent either.

## Files

- `video-lora-skill.md` — single consolidated, prompt-ready skill (selection logic, stacking, I2V/T2V usage, prompt patterns, all 98 recipes, compact top LoRAs per family/category). Target size is under ~150 KB so it fits in an AI context window.
- `video-lora-catalog.json` / `video-lora-catalog.csv` — the full accessible-row catalog with useful fields only (id, family, base, category, name, trigger, strength, graydient_status, aiops, installed, url, downloads, short example prompt).
- `HOW-TO-USE.md` — this file.
- `video-lora-kb-claude-skill.zip` — Anthropic Agent Skills layout (`video-lora-kb/SKILL.md` plus `references/` guides and family category pages).

## Grok / ChatGPT / Gemini

Attach `video-lora-skill.md` to the chat, or add it to a Project / Gem / custom GPT knowledge file. For lookups beyond the compact tables, also attach `video-lora-catalog.json` (or the CSV). A typical starter instruction:

> Use the attached video LoRA skill to choose and stack LoRAs for MiniMax H3, Wan, and LTX. Prefer LoRAs already on Graydient. If a pick is *to add to Graydient*, ingest it with civit-to-graydient before use. Suggest ingest of a public candidate only when the documented rule says so, and never auto-download. Never invent a trigger or a strength; if the skill or catalog leaves them blank, say so and suggest a short test clip.

## Claude (Agent Skill)

Upload `video-lora-kb-claude-skill.zip` in Claude Settings → Capabilities → Skills (check your Claude app for the exact location; the labels move). After it is enabled, ask Claude to choose or stack video LoRAs for H3 / Wan / LTX. Full category tables live under `references/families/`.

## System prompt / custom instructions

Paste `video-lora-skill.md` into custom instructions, a system prompt, or a saved memory. If the tool has a size limit, paste the skill markdown first; keep the JSON/CSV as an on-demand attachment.

## Cursor and other coding agents

Drop the unzipped `video-lora-kb/` folder from the Claude skill zip into the agent's skills directory (for Cursor, a project or user `.cursor/skills/` or `.agents/skills/` folder, depending on the setup). Or add `video-lora-skill.md` to the repo and point the agent at it.

## Regenerating this pack

From the `video-lora-kb` repo (no network required for a local rebuild):

```
python3 scripts/export_pack.py
```

Output goes to `dist/` (gitignored). The script never downloads LoRA weights and never invents triggers or strengths.
"""


def reset_dist() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)


def copy_references(dest: Path) -> None:
    guides_dest = dest / "references" / "guides"
    guides_dest.mkdir(parents=True)
    for src in sorted(GUIDES.glob("*.md")):
        shutil.copy2(src, guides_dest / src.name)
    fam_dest = dest / "references" / "families"
    for fam_dir in ("h3", "wan", "ltx"):
        src_dir = FAMILIES / fam_dir
        if not src_dir.is_dir():
            continue
        out = fam_dest / fam_dir
        out.mkdir(parents=True, exist_ok=True)
        for src in sorted(src_dir.glob("*.md")):
            shutil.copy2(src, out / src.name)


def _zipinfo(arcname: str, data: bytes) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    # Regular file, rw-r--r--
    info.external_attr = (0o100644 & 0xFFFF) << 16
    info.create_system = 3
    return info


def write_deterministic_zip(path: Path, files: list[tuple[str, bytes]]) -> None:
    """Write a zip with sorted names and a fixed timestamp."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for arcname, data in sorted(files, key=lambda x: x[0]):
            # Zip directory entries for parents? Not required for extraction.
            zf.writestr(_zipinfo(arcname, data), data)


def collect_dir(root: Path, prefix: str = "") -> list[tuple[str, bytes]]:
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        arc = f"{prefix}{rel}" if not prefix else f"{prefix.rstrip('/')}/{rel}"
        out.append((arc, p.read_bytes()))
    return out


def write_claude_skill(skill_md: str) -> Path:
    skill_root = DIST / "claude-skill" / "video-lora-kb"
    if skill_root.exists():
        shutil.rmtree(skill_root)
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(skill_md, encoding="utf-8")
    copy_references(skill_root)
    zip_path = DIST / "video-lora-kb-claude-skill.zip"
    files = collect_dir(skill_root, "video-lora-kb/")
    write_deterministic_zip(zip_path, files)
    return zip_path


def write_share_pack() -> Path:
    zip_path = DIST / "video-lora-kb-share-pack.zip"
    names = [
        "video-lora-skill.md",
        "video-lora-catalog.json",
        "video-lora-catalog.csv",
        "HOW-TO-USE.md",
        "video-lora-kb-claude-skill.zip",
    ]
    files = []
    for name in names:
        p = DIST / name
        if not p.is_file():
            raise SystemExit(f"missing {p} when building share pack")
        files.append((name, p.read_bytes()))
    write_deterministic_zip(zip_path, files)
    return zip_path


def verify(skill_text: str, records: list[dict], per_cat: int) -> None:
    errors = []
    n = len(records)
    if n != EXPECTED_COUNT:
        errors.append(f"catalog records {n} != {EXPECTED_COUNT}")
    n_rec = count_recipes(skill_text)
    if n_rec != EXPECTED_RECIPES:
        errors.append(f"recipes in skill md {n_rec} != {EXPECTED_RECIPES}")
    skill_path = DIST / "video-lora-skill.md"
    size = skill_path.stat().st_size
    if size > MAX_SKILL_BYTES:
        errors.append(f"skill md {size} bytes exceeds {MAX_SKILL_BYTES}")
    if not skill_text.startswith("---\nname: video-lora-kb\n"):
        errors.append("skill md missing expected frontmatter")
    if "## How to stack (read this first)" not in skill_text:
        errors.append("skill md missing stacking section")
    if "## Image-to-video and text-to-video" not in skill_text:
        errors.append("skill md missing I2V/T2V section")
    if "## Prompt patterns and trigger usage" not in skill_text:
        errors.append("skill md missing prompt patterns")
    if "## Top LoRAs per family and category" not in skill_text:
        errors.append("skill md missing top LoRA tables")

    json_path = DIST / "video-lora-catalog.json"
    parsed = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(parsed, list):
        errors.append("catalog JSON is not a list")
    elif len(parsed) != EXPECTED_COUNT:
        errors.append(f"JSON length {len(parsed)} != {EXPECTED_COUNT}")
    else:
        ids = [r["id"] for r in parsed]
        if len(set(ids)) != len(ids):
            errors.append("JSON ids are not unique")
        required = {
            "id",
            "family",
            "base",
            "category",
            "name",
            "trigger",
            "strength",
            "installed",
            "url",
            "downloads",
            "example_prompt",
        }
        missing = required - set(parsed[0])
        if missing:
            errors.append(f"JSON missing fields {missing}")
        for rec in parsed:
            ep = rec.get("example_prompt") or ""
            if len(ep) > PROMPT_TRUNCATE:
                errors.append("example_prompt longer than 300")
                break
            if rec.get("strength") in ("not stated", "Not stated"):
                errors.append("JSON strength still says 'not stated' (should be blank)")
                break

    csv_path = DIST / "video-lora-catalog.csv"
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = list(csv.DictReader(f))
    if len(reader) != EXPECTED_COUNT:
        errors.append(f"CSV rows {len(reader)} != {EXPECTED_COUNT}")

    claude_skill = DIST / "claude-skill" / "video-lora-kb" / "SKILL.md"
    if not claude_skill.is_file():
        errors.append("Claude skill SKILL.md missing")
    for rel in (
        "references/guides/image-to-video.md",
        "references/guides/prompt-patterns.md",
        "references/guides/fuzzpuppy-directory.md",
        "references/families/h3/motion.md",
        "references/families/wan/motion.md",
        "references/families/ltx/motion.md",
    ):
        if not (DIST / "claude-skill" / "video-lora-kb" / rel).is_file():
            errors.append(f"Claude skill missing {rel}")

    for zname in ("video-lora-kb-claude-skill.zip", "video-lora-kb-share-pack.zip"):
        zp = DIST / zname
        if not zipfile.is_zipfile(zp):
            errors.append(f"{zname} is not a valid zip")
            continue
        with zipfile.ZipFile(zp) as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f"{zname} failed testzip on {bad}")
            if zname.endswith("claude-skill.zip") and "video-lora-kb/SKILL.md" not in zf.namelist():
                errors.append("claude skill zip missing video-lora-kb/SKILL.md")
            if zname.endswith("share-pack.zip"):
                names = set(zf.namelist())
                for need in (
                    "video-lora-skill.md",
                    "video-lora-catalog.json",
                    "video-lora-catalog.csv",
                    "HOW-TO-USE.md",
                    "video-lora-kb-claude-skill.zip",
                ):
                    if need not in names:
                        errors.append(f"share pack missing {need}")

    if errors:
        raise SystemExit("verification failed:\n- " + "\n- ".join(errors))

    print("Verification OK")
    print(f"  catalog rows:     {n}")
    print(f"  recipes:          {n_rec}")
    print(f"  per-category cap: {per_cat}")
    print(f"  video-lora-skill.md: {size:,} bytes ({size / 1024:.1f} KB)")
    for name in (
        "video-lora-skill.md",
        "video-lora-catalog.json",
        "video-lora-catalog.csv",
        "HOW-TO-USE.md",
        "video-lora-kb-claude-skill.zip",
        "video-lora-kb-share-pack.zip",
    ):
        p = DIST / name
        print(f"  dist/{name}: {p.stat().st_size:,} bytes")


def build() -> tuple[str, list[dict], int]:
    rows = load_rows()
    assert_unique_ids(rows)
    records = [compact_record(r) for r in sort_catalog(rows)]
    reset_dist()
    skill_text, per_cat = fit_skill_markdown(rows)
    (DIST / "video-lora-skill.md").write_text(skill_text, encoding="utf-8")
    write_json(DIST / "video-lora-catalog.json", records)
    write_csv(DIST / "video-lora-catalog.csv", records)
    (DIST / "HOW-TO-USE.md").write_text(how_to_use_md(), encoding="utf-8")
    write_claude_skill(skill_text)
    write_share_pack()
    verify(skill_text, records, per_cat)
    return skill_text, records, per_cat


def main() -> int:
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
