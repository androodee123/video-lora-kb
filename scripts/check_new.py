#!/usr/bin/env python3
"""List new CivitAI video LoRAs that are not already in data/loras.jsonl.

This script queries the CivitAI public API for LoRAs whose baseModel is one of
the MiniMax H3 / Wan / LTX strings confirmed against the API. It compares
model ids (and installed filenames) to data/loras.jsonl and writes
proposals/YYYY-MM-DD.md.

It MUST NEVER download, fetch, or ingest LoRA weight files, archives, or
images. Metadata (JSON) only.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# Exact CivitAI baseModel strings confirmed 2026-11-13 via
# GET /api/v1/models?types=LORA&baseModels=<value>&nsfw=true
BASE_MODELS = [
    "MiniMax H3",
    "Wan Video",
    "Wan Video 14B i2v 480p",
    "Wan Video 14B i2v 720p",
    "Wan Video 14B t2v",
    "Wan Video 2.2 I2V-A14B",
    "Wan Video 2.2 T2V-A14B",
    "Wan Video 2.2 TI2V-5B",
    "LTXV",
    "LTXV2",
    "LTXV 2.3",
    "LTXV 2.5",
]

API = "https://civitai.com/api/v1/models"
UA = "video-lora-kb/check_new.py (metadata only; never download weights)"
ROOT = Path(__file__).resolve().parents[1]
JSONL = ROOT / "data" / "loras.jsonl"
PROPOSALS = ROOT / "proposals"

def load_known():
    ids = set()
    files = set()
    if not JSONL.exists():
        sys.stderr.write(f"warning: {JSONL} not found; every result will look new\n")
        return ids, files
    for line in JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("civitai_model_id"):
            ids.add(int(r["civitai_model_id"]))
        if r.get("file"):
            files.add(r["file"].lower())
        for u in (r.get("urls") or {}).values():
            # also parse ids from urls
            pass
    return ids, files

def get_json(url: str, retries: int = 5):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 + i * 2)
                continue
            raise
        except Exception as e:
            last = e
            time.sleep(1 + i)
    raise RuntimeError(f"failed GET {url}: {last}")

def page_base(base_model: str, pages: int, limit: int):
    """Yield slim model dicts for one baseModel, newest first. Metadata only."""
    cursor = None
    for _ in range(pages):
        params = {
            "types": "LORA",
            "limit": limit,
            "baseModels": base_model,
            "nsfw": "true",
            "sort": "Newest",
        }
        if cursor:
            params["cursor"] = cursor
        url = API + "?" + urllib.parse.urlencode(params)
        data = get_json(url)
        items = data.get("items") or []
        if not items:
            break
        for it in items:
            yield it
        cursor = (data.get("metadata") or {}).get("nextCursor")
        if not cursor:
            break
        time.sleep(0.3)

def slim(it, queried_base: str):
    versions = []
    for v in it.get("modelVersions") or []:
        files = []
        for f in v.get("files") or []:
            name = f.get("name") or ""
            # Never record download URLs. Name and size only.
            files.append({"name": name, "sizeKB": f.get("sizeKB")})
        versions.append({
            "id": v.get("id"),
            "name": v.get("name"),
            "baseModel": v.get("baseModel"),
            "trainedWords": v.get("trainedWords") or [],
            "createdAt": v.get("createdAt") or v.get("publishedAt"),
            "files": files,
        })
    return {
        "id": it.get("id"),
        "name": it.get("name"),
        "nsfw": it.get("nsfw"),
        "queried_base": queried_base,
        "url": f"https://civitai.com/models/{it.get('id')}",
        "versions": versions,
    }

def main():
    ap = argparse.ArgumentParser(description="Propose new CivitAI video LoRAs (metadata only).")
    ap.add_argument("--pages", type=int, default=2, help="pages per baseModel (default 2)")
    ap.add_argument("--limit", type=int, default=50, help="page size (default 50)")
    ap.add_argument("--date", help="proposal filename date (YYYY-MM-DD), default today local")
    args = ap.parse_args()

    known_ids, known_files = load_known()
    seen = set()
    new = []
    already = 0
    for bm in BASE_MODELS:
        print(f"query {bm} ...", file=sys.stderr)
        for it in page_base(bm, args.pages, args.limit):
            mid = it.get("id")
            if mid in seen:
                continue
            seen.add(mid)
            if mid in known_ids:
                already += 1
                continue
            # also skip if every published safetensors name is already catalogued
            names = [
                (f.get("name") or "").lower()
                for v in (it.get("modelVersions") or [])
                for f in (v.get("files") or [])
            ]
            if names and all(n in known_files for n in names if n.endswith(".safetensors")):
                already += 1
                continue
            new.append(slim(it, bm))
        time.sleep(0.2)

    day = args.date or datetime.now().strftime("%Y-%m-%d")
    PROPOSALS.mkdir(parents=True, exist_ok=True)
    dest = PROPOSALS / f"{day}.md"

    lines = [
        f"# CivitAI video LoRA proposals — {day}",
        "",
        "Generated by `scripts/check_new.py`. Metadata only; **no weights were downloaded or ingested.**",
        "",
        f"Known catalog model ids: {len(known_ids)}. Query windows: {args.pages} page(s) of {args.limit} newest LoRAs per baseModel, `nsfw=true`.",
        f"New candidates: **{len(new)}**. Already in catalog (skipped): {already}.",
        "",
        "Review these before installing anything. This file is a proposal list, not an ingest queue.",
        "",
    ]
    if not new:
        lines.append("No new candidates in this window.")
    else:
        lines += [
            "| model id | name | baseModel (queried / version) | triggers | files | link |",
            "|---|---|---|---|---|---|",
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
            trig = ", ".join(f"`{w}`" for w in words[:8]) or "—"
            fn = ", ".join(f"`{n}`" for n in files[:6]) or "—"
            base = ", ".join(bases) or it["queried_base"]
            name = (it.get("name") or "").replace("|", "\\|")
            lines.append(
                f"| {it['id']} | {name} | {base} | {trig} | {fn} | [{it['id']}]({it['url']}) |"
            )
        lines += ["", "## Details", ""]
        for it in new:
            lines.append(f"### {it.get('name') or it['id']}")
            lines.append("")
            lines.append(f"- CivitAI: {it['url']}")
            lines.append(f"- nsfw flag: {it.get('nsfw')}")
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
