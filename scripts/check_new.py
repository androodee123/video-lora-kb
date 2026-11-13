#!/usr/bin/env python3
"""Propose new CivitAI video LoRAs that are not yet accessible.

Accessible LoRAs live in data/loras.jsonl (on Graydient via Hugging Face
Octavian123/civit, Octavian123/civit2, or Octavian123/private, or still
to add from the AIOps RAID). Already-known but not-yet-accessible rows
live in data/candidates.jsonl.
This script lists *new* CivitAI video LoRAs (LORA / LoCon / DoRA on confirmed
video baseModels) that are in neither file — ingest candidates for a person
to review and, if wanted, ingest with civit-to-graydient.

Writes proposals/YYYY-MM-DD.md. MUST NEVER download or ingest weights.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest as H
import video_lora as V

ROOT = H.ROOT
JSONL = ROOT / "data" / "loras.jsonl"
PROPOSALS = ROOT / "proposals"


CANDIDATES = ROOT / "data" / "candidates.jsonl"


def _ingest_row(r, ids, files, hf):
    if r.get("civitai_model_id"):
        try:
            ids.add(int(r["civitai_model_id"]))
        except (TypeError, ValueError):
            pass
    if r.get("file"):
        files.add(r["file"].lower())
    for n in r.get("files") or []:
        if n:
            files.add(n.lower())
    if r.get("hf_id"):
        hf.add(r["hf_id"])
    url = (r.get("urls") or {}).get("huggingface") or ""
    if "huggingface.co/" in url:
        hf.add(url.split("huggingface.co/")[-1].strip("/"))


def load_known():
    """Return ids/files already accessible or already listed as candidates."""
    ids, files, hf = set(), set(), set()
    n_acc = n_cand = 0
    for path, kind in ((JSONL, "accessible"), (CANDIDATES, "candidates")):
        if not path.exists():
            if kind == "accessible":
                sys.stderr.write(f"warning: {path} not found; every result will look new\n")
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            _ingest_row(r, ids, files, hf)
            if kind == "accessible":
                n_acc += 1
            else:
                n_cand += 1
    return ids, files, hf, n_acc, n_cand


def slim(it, queried_base: str):
    versions = []
    for v in it.get("modelVersions") or []:
        files = [{"name": f.get("name"), "sizeKB": f.get("sizeKB")} for f in (v.get("files") or [])]
        versions.append({
            "id": v.get("id"),
            "name": v.get("name"),
            "baseModel": v.get("baseModel"),
            "trainedWords": v.get("trainedWords") or [],
            "files": files,
        })
    st = it.get("stats") or {}
    return {
        "id": it.get("id"),
        "name": it.get("name"),
        "nsfw": it.get("nsfw"),
        "downloads": st.get("downloadCount") or 0,
        "thumbs_up": st.get("thumbsUpCount") or 0,
        "queried_base": queried_base,
        "url": f"https://civitai.com/models/{it.get('id')}",
        "versions": versions,
    }


def main():
    ap = argparse.ArgumentParser(description="Propose new CivitAI video LoRAs (metadata only).")
    ap.add_argument("--pages", type=int, default=2, help="pages per baseModel (default 2, Newest)")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--sort", default="newest", choices=list(H.SORTS))
    ap.add_argument("--refresh", action="store_true", help="re-fetch proposal pages")
    ap.add_argument("--date", help="proposal filename date (YYYY-MM-DD)")
    args = ap.parse_args()

    known_ids, known_files, _known_hf, n_acc, n_cand = load_known()
    seen = set()
    new = []
    already = 0
    for bm in H.BASE_MODELS:
        print(f"query {bm} ...", file=sys.stderr)
        n = 0
        for page in H.iter_civitai_pages(bm, args.sort, limit=args.limit, max_pages=args.pages,
                                          refresh=args.refresh, cache_name="check_new",
                                          types=["LORA", "LoCon", "DoRA"]):
            for it in page.get("items") or []:
                mid = it.get("id")
                if mid in seen:
                    continue
                seen.add(mid)
                # Video LoRA / LoCon / DoRA only, on a confirmed video base.
                typ = it.get("type") or ""
                if typ not in V.ADAPTER_TYPES:
                    continue
                if not V.civitai_has_video_base(it):
                    continue
                if mid in known_ids:
                    already += 1
                    continue
                names = [
                    (f.get("name") or "").lower()
                    for v in (it.get("modelVersions") or [])
                    for f in (v.get("files") or [])
                ]
                if names and all(n in known_files for n in names if n.endswith(".safetensors")):
                    already += 1
                    continue
                new.append(slim(it, bm))
            n += 1
        time.sleep(0.2)

    day = args.date or datetime.now().strftime("%Y-%m-%d")
    PROPOSALS.mkdir(parents=True, exist_ok=True)
    dest = PROPOSALS / f"{day}.md"

    lines = [
        f"# Ingest-candidate proposals — {day}",
        "",
        "Generated by `scripts/check_new.py` using `scripts/harvest.py` paging. "
        "These are **new CivitAI video LoRAs that are not yet in the available Graydient set**, "
        "and are not already listed in `data/candidates.jsonl`. "
        "Metadata only; **no weights were downloaded or ingested.** "
        "If you want one, download and ingest it yourself with the civit-to-graydient pipeline.",
        "",
        f"Already accessible (`data/loras.jsonl`): {n_acc} rows. "
        f"Already-known candidates (`data/candidates.jsonl`): {n_cand} rows. "
        f"Known model ids (both files): {len(known_ids)}. Window: {args.pages} page(s) of {args.limit} "
        f"`{H.SORTS[args.sort]}` LoRAs per baseModel, `nsfw=true`.",
        f"New ingest candidates in this window: **{len(new)}**. Already known (skipped): {already}.",
        "",
        "This file is a proposal list, not an ingest queue. Nothing is auto-downloaded.",
        "",
    ]
    if not new:
        lines.append("No new candidates in this window.")
    else:
        lines += [
            "| model id | name | downloads | baseModel | triggers | files | link |",
            "|---|---|---:|---|---|---|---|",
        ]
        for it in new:
            bases = sorted({v.get("baseModel") or "" for v in it["versions"] if v.get("baseModel")})
            words = []
            for v in it["versions"]:
                for w in v.get("trainedWords") or []:
                    if w and w not in words:
                        words.append(w)
            files = []
            for v in it["versions"]:
                for f in v.get("files") or []:
                    if f.get("name") and f["name"] not in files:
                        files.append(f["name"])
            trig = ", ".join(f"`{w}`" for w in words[:6]) or "—"
            fn = ", ".join(f"`{n}`" for n in files[:5]) or "—"
            name = (it.get("name") or "").replace("|", "\\|")
            lines.append(
                f"| {it['id']} | {name} | {it['downloads']:,} | {', '.join(bases) or it['queried_base']} "
                f"| {trig} | {fn} | [{it['id']}]({it['url']}) |"
            )
        lines += ["", "## Details", ""]
        for it in new:
            lines.append(f"### {it.get('name') or it['id']}")
            lines.append("")
            lines.append(f"- CivitAI: {it['url']} · downloads {it['downloads']:,} · thumbs {it['thumbs_up']}")
            for v in it["versions"]:
                fns = ", ".join(f.get("name") or "" for f in v.get("files") or [])
                words = ", ".join(v.get("trainedWords") or []) or "—"
                lines.append(
                    f"- version `{v.get('id')}` `{v.get('name')}` base `{v.get('baseModel')}` "
                    f"triggers: {words}. files: {fns or '—'}"
                )
            lines.append("")

    dest.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {dest} ({len(new)} new, {already} already known)", file=sys.stderr)


if __name__ == "__main__":
    main()
