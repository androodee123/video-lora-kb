#!/usr/bin/env python3
"""Harvest CivitAI + Hugging Face *metadata* for video LoRAs.

Pages CivitAI /api/v1/models for every confirmed video baseModel string,
with configurable sorts (Most Downloaded, Highest Rated, Newest), nsfw=true.
Optionally lists official/community Hugging Face LoRA repos.

This script MUST NEVER download LoRA weights, archives, or media files.
It only writes JSON metadata under data/raw/.

Usage:
  python3 scripts/harvest.py                  # resume/cache-aware full harvest
  python3 scripts/harvest.py --refresh        # re-fetch CivitAI pages
  python3 scripts/harvest.py --hf-only        # refresh Hugging Face listings
  python3 scripts/harvest.py --verify-sorts   # first page of downloads/rated, report gaps
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CIVIT_RAW = RAW / "civitai"
HF_RAW = RAW / "huggingface"

# Exact CivitAI baseModel strings confirmed 2026-11-13.
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

SORTS = {
    "newest": "Newest",
    "downloads": "Most Downloaded",
    "rated": "Highest Rated",
}

API = "https://civitai.com/api/v1/models"
HF_API = "https://huggingface.co/api/models"
UA = "video-lora-kb/harvest.py (metadata only; never download weights)"

# Authors/queries we always include when harvesting HF (video LoRAs only).
HF_AUTHORS = ["Lightricks", "lightx2v", "alibaba-pai", "Kijai", "Cseti", "fal", "Pika-Labs", "FuzzPuppy"]
HF_SEARCHES = [
    "CausVid Wan LoRA",
    "self-forcing Wan LoRA",
    "MiniMax H3 LoRA",
    "Wan2.2 Distill LoRA",
    "LTX-2 Camera-Control LoRA",
]


def _get(url: str, retries: int = 5):
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
    raise RuntimeError(f"GET failed {url}: {last}")


def safe_base(base_model: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", base_model)


def page_key(base_model: str, cursor) -> str:
    h = hashlib.sha1(f"{base_model}|{cursor or ''}".encode()).hexdigest()[:16]
    return f"{safe_base(base_model)}_{h}.json"


def iter_civitai_pages(base_model: str, sort: str, limit: int = 100, max_pages: int = 80,
                       refresh: bool = False, delay: float = 0.35, cache_name: str | None = None):
    """Yield raw page dicts, caching each under data/raw/civitai/<cache_name or sort>/. """
    sort_dir = CIVIT_RAW / (cache_name or sort)
    sort_dir.mkdir(parents=True, exist_ok=True)
    cursor = None
    pages = 0
    while pages < max_pages:
        dest = sort_dir / page_key(base_model, cursor)
        if dest.exists() and dest.stat().st_size > 20 and not refresh:
            data = json.loads(dest.read_text(encoding="utf-8"))
        else:
            params = {
                "types": "LORA",
                "limit": limit,
                "baseModels": base_model,
                "nsfw": "true",
                "sort": SORTS.get(sort, sort),
            }
            if cursor:
                params["cursor"] = cursor
            url = API + "?" + urllib.parse.urlencode(params)
            data = _get(url)
            dest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            time.sleep(delay)
        yield data
        pages += 1
        items = data.get("items") or []
        cursor = (data.get("metadata") or {}).get("nextCursor")
        if not items or not cursor:
            break


def merge_civitai_items(items_iter):
    """Merge list-endpoint items, unioning modelVersions across baseModel filters."""
    merged = {}
    for it in items_iter:
        mid = it.get("id")
        if not mid:
            continue
        if mid not in merged:
            merged[mid] = json.loads(json.dumps(it))  # copy
            # index versions by id
            vers = {v["id"]: v for v in (merged[mid].get("modelVersions") or []) if v.get("id")}
            merged[mid]["_ver"] = vers
            continue
        cur = merged[mid]
        # keep richer description / higher stats
        if len(it.get("description") or "") > len(cur.get("description") or ""):
            cur["description"] = it["description"]
        st, ost = it.get("stats") or {}, cur.get("stats") or {}
        if (st.get("downloadCount") or 0) >= (ost.get("downloadCount") or 0):
            cur["stats"] = st
        for t in it.get("tags") or []:
            if t not in (cur.get("tags") or []):
                cur.setdefault("tags", []).append(t)
        for v in it.get("modelVersions") or []:
            if v.get("id"):
                cur["_ver"][v["id"]] = v
    # flatten version maps
    out = []
    for mid, cur in merged.items():
        cur["modelVersions"] = list(cur.pop("_ver").values())
        out.append(cur)
    return out


def load_cached_sort(sort: str):
    d = CIVIT_RAW / sort
    if not d.exists():
        return []
    items = []
    for p in sorted(d.glob("*.json")):
        if p.name.startswith("manifest"):
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        items.extend(data.get("items") or [])
    return items


def harvest_civitai(sorts=("newest",), refresh: bool = False, max_pages: int = 80, log=sys.stderr):
    RAW.mkdir(parents=True, exist_ok=True)
    CIVIT_RAW.mkdir(parents=True, exist_ok=True)
    all_items = []
    summary = {}
    for sort in sorts:
        counts = {}
        for bm in BASE_MODELS:
            n = 0
            for page in iter_civitai_pages(bm, sort, max_pages=max_pages, refresh=refresh):
                n += len(page.get("items") or [])
            counts[bm] = n
            print(f"  {sort} {bm}: {n} listed", file=log)
        summary[sort] = counts
        all_items.extend(load_cached_sort(sort))
    models = merge_civitai_items(all_items)
    manifest = {
        "harvested_at": datetime.now().isoformat(timespec="seconds"),
        "sorts": list(sorts),
        "baseModels": BASE_MODELS,
        "page_counts": summary,
        "unique_models": len(models),
        "note": "Metadata only. No weights downloaded.",
    }
    (CIVIT_RAW / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # slim machine-readable index (ids + stats + bases) for check_new
    index_path = CIVIT_RAW / "index.jsonl"
    with index_path.open("w", encoding="utf-8") as f:
        for m in models:
            bases = sorted({v.get("baseModel") for v in (m.get("modelVersions") or []) if v.get("baseModel")})
            st = m.get("stats") or {}
            f.write(json.dumps({
                "id": m["id"],
                "name": m.get("name"),
                "bases": bases,
                "downloadCount": st.get("downloadCount") or 0,
                "thumbsUpCount": st.get("thumbsUpCount") or 0,
                "nsfw": m.get("nsfw"),
            }, ensure_ascii=False) + "\n")
    print(f"merged {len(models)} unique CivitAI models -> {index_path}", file=log)
    return models, manifest


def is_video_hf_repo(it: dict) -> bool:
    ident = (it.get("id") or "") + " " + " ".join(it.get("tags") or [])
    ident_l = ident.lower()
    pipe = (it.get("pipeline_tag") or "")
    video_pipes = {
        "text-to-video", "image-to-video", "image-text-to-video",
        "video-to-video", "any-to-any",
    }
    if pipe in video_pipes:
        return True
    video_needles = (
        "ltx", "ltx-2", "ltx2", "wan2", "wan-2", "wan video", "minimax", "h3",
        "causvid", "self-forcing", "lightx2v", "ic-lora", "camera-control",
        "i2v", "t2v", "ti2v",
    )
    if any(n in ident_l for n in video_needles) and (
        "lora" in ident_l or "ic-lora" in ident_l or "LoRA" in ident
    ):
        # drop obvious image-only models
        if any(x in ident_l for x in ("qwen-image", "flux.", "flux-2", "kontext", "z-image")):
            if not any(n in ident_l for n in ("wan", "ltx", "minimax", "h3")):
                return False
        return True
    return False


def harvest_hf(refresh: bool = False, log=sys.stderr):
    HF_RAW.mkdir(parents=True, exist_ok=True)
    seen = {}
    for author in HF_AUTHORS:
        dest = HF_RAW / f"author-{author}.json"
        if dest.exists() and not refresh:
            items = json.loads(dest.read_text(encoding="utf-8"))
        else:
            url = HF_API + "?" + urllib.parse.urlencode({
                "author": author, "limit": 100, "sort": "downloads", "direction": -1,
            })
            items = _get(url)
            dest.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.25)
        for it in items:
            if is_video_hf_repo(it):
                seen[it["id"]] = it
        print(f"  HF author {author}: {len(items)} listed, running total video LoRAs {len(seen)}", file=log)
    for q in HF_SEARCHES:
        dest = HF_RAW / f"search-{safe_base(q)}.json"
        if dest.exists() and not refresh:
            items = json.loads(dest.read_text(encoding="utf-8"))
        else:
            url = HF_API + "?" + urllib.parse.urlencode({
                "search": q, "limit": 20, "sort": "downloads", "direction": -1,
            })
            items = _get(url)
            dest.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.25)
        for it in items:
            if is_video_hf_repo(it):
                seen[it["id"]] = it
        print(f"  HF search {q!r}: {len(items)}", file=log)
    catalog = list(seen.values())
    (HF_RAW / "index.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"HF video LoRA repos: {len(catalog)}", file=log)
    return catalog


def verify_sorts(log=sys.stderr):
    """Fetch first page of Most Downloaded and Highest Rated; report ids missing from Newest cache."""
    cached = merge_civitai_items(load_cached_sort("newest"))
    known = {m["id"] for m in cached}
    print(f"newest cache unique ids: {len(known)}", file=log)
    missing = []
    for sort in ("downloads", "rated"):
        for bm in BASE_MODELS:
            pages = list(iter_civitai_pages(bm, sort, max_pages=1, refresh=False))
            items = pages[0].get("items") or [] if pages else []
            miss = [it for it in items if it.get("id") not in known]
            print(f"  {sort} {bm}: first page {len(items)}, missing from newest cache {len(miss)}", file=log)
            for it in miss:
                missing.append((sort, bm, it.get("id"), it.get("name"), (it.get("stats") or {}).get("downloadCount")))
    return missing


def family_of_base(base: str | None) -> str | None:
    b = base or ""
    if b == "MiniMax H3":
        return "H3"
    if b.startswith("Wan"):
        return "Wan"
    if b.startswith("LTX"):
        return "LTX2"
    return None


def main():
    ap = argparse.ArgumentParser(description="Harvest CivitAI/HF video LoRA metadata (no weights).")
    ap.add_argument("--refresh", action="store_true", help="re-fetch pages even if cached")
    ap.add_argument("--hf-only", action="store_true")
    ap.add_argument("--civitai-only", action="store_true")
    ap.add_argument("--verify-sorts", action="store_true",
                    help="first page of Most Downloaded / Highest Rated vs newest cache")
    ap.add_argument("--sorts", default="newest",
                    help="comma list: newest,downloads,rated (default newest; cache is already a full Newest crawl)")
    ap.add_argument("--max-pages", type=int, default=80)
    args = ap.parse_args()

    if args.verify_sorts:
        miss = verify_sorts()
        if miss:
            print("GAPS vs newest cache:", file=sys.stderr)
            for row in miss:
                print(" ", row, file=sys.stderr)
        else:
            print("No gaps: first pages of downloads/rated are already in the newest cache.", file=sys.stderr)
        return

    sorts = [s.strip() for s in args.sorts.split(",") if s.strip()]
    if not args.hf_only:
        harvest_civitai(sorts=sorts, refresh=args.refresh, max_pages=args.max_pages)
    if not args.civitai_only:
        harvest_hf(refresh=args.refresh)


if __name__ == "__main__":
    main()
