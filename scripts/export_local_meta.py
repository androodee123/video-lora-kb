#!/usr/bin/env python3
"""Refresh the sanitized local-metadata snapshots used by build_semantic.py (read-only on every source).

Run on the home Mac (where the AIOps library and ingest work dirs live), or on any machine that has copies:

  python3 scripts/export_local_meta.py \
      --aiops-db ~/AI/ai-ops-portal/data/catalog-index.sqlite \
      --plans '/Users/AndrewD/downloadtemp/civit-ingest-*/plan.json' \
      --batches /workspace/ingest-batches \
      --out data/local

Also accepts pre-exported gz JSONL (--aiops-jsonl / --plans-jsonl) instead of the DB / plan files.
Writes data/local/aiops_graydient.jsonl.gz, ingest_plans.jsonl.gz, safety_skips.json.
Sanitized: keeps only public metadata (no RAID paths, download URLs, logins, notes, tokens or signed URLs).
The sqlite DB is opened read-only (mode=ro). Nothing is downloaded or ingested.
"""
from __future__ import annotations
import argparse, glob, gzip, json, os, re, sqlite3, sys
from pathlib import Path

SECRET_RE = re.compile(r"(hf_[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|[?&](token|sig|signature|expires|auth|X-Amz-[A-Za-z]+)=[^&\s]*|Bearer\s+[A-Za-z0-9._-]+|magic[-_ ]?link\S*|/login\?\S*)", re.I)

IS_VIDEO = (Path(__file__).resolve().parent / "video_lora.py").exists()
VIDEO_FAM = {"h3", "wan", "ltx2", "ltx"}

def in_repo(family, base_model=""):
    f = (family or "").lower()
    b = (base_model or "").lower()
    vid = f in VIDEO_FAM or any(x in b for x in ("h3", "minimax", "wan video", "ltx"))
    return vid if IS_VIDEO else not vid

def scrub(s, n=None):
    if s is None:
        return None
    s = SECRET_RE.sub("", str(s))
    return s[:n] if n else s

AIOPS_KEEP = ["slug", "graydient_slug", "family", "filename", "token", "creator", "hf_repo_file", "on_graydient", "on_hf",
              "on_raid", "kind", "mine", "ingested_at"]
PLAN_KEEP = ["state", "model_id", "model_name", "creator", "version_id", "version_name", "base_model", "type", "kind", "slug",
             "token", "family", "tags", "nsfw", "hf_repo", "hf_filename", "graydient_slug", "registration_hold", "queued_at",
             "published_at", "duplicate_of"]

def aiops_rows(db=None, jsonl=None):
    if jsonl:
        with gzip.open(jsonl, "rt") as f:
            for l in f:
                yield json.loads(l)
        return
    c = sqlite3.connect(f"file:{os.path.expanduser(db)}?mode=ro", uri=True)
    for (rj,) in c.execute("select row_json from loras"):
        yield json.loads(rj)

def plan_rows(pattern=None, jsonl=None):
    if jsonl:
        with gzip.open(jsonl, "rt") as f:
            for l in f:
                yield json.loads(l)
        return
    for p in sorted(glob.glob(os.path.expanduser(pattern))):
        d = json.load(open(p))
        items = d.get("items", []) if isinstance(d, dict) else d
        items = items if isinstance(items, list) else list(items.values())
        for it in items:
            it = dict(it)
            it["plan"] = Path(p).parent.name
            it["plan_created"] = d.get("created") if isinstance(d, dict) else None
            it["plan_mtime"] = os.path.getmtime(p)
            yield it

def safety_ids(batches):
    SAFE_RE = re.compile(r"safety|minor|school|student|age-coded|canonically adul|franchise|loli|underage|child|teen|adults-only", re.I)
    mids, vids = set(), set()
    def add(m, v):
        for val, s in ((m, mids), (v, vids)):
            try:
                if val: s.add(int(val))
            except (TypeError, ValueError):
                pass
    b = Path(batches)
    for p in list(b.glob("*decisions.json")) + list(b.glob("*decisions.jsonl")):
        txt = p.read_text()
        try:
            d = json.loads(txt); rows = d if isinstance(d, list) else (d.get("items") or d.get("decisions") or list(d.values()))
        except Exception:
            rows = [json.loads(l) for l in txt.splitlines() if l.strip()]
        for r in rows:
            if isinstance(r, dict) and (r.get("decision") in (None, "skip")) and (r.get("reason") == "safety" or SAFE_RE.search(str(r.get("reason")))):
                add(r.get("model_id"), r.get("version_id"))
    for p in b.glob("*safety-models.txt"):
        for l in p.read_text().splitlines():
            f = l.split("\t")
            if len(f) >= 3:
                add(f[1], f[2])
    for p in b.glob("*skip-urls.txt"):
        sec = ""
        for l in p.read_text().splitlines():
            s = l.strip()
            if s and not s.startswith("=") and s.isupper():
                sec = s
            elif s and re.match(r"^[A-Z][A-Z0-9 .()/,'-]+\(\d+\)$", s):
                sec = s
            m = re.search(r"models/(\d+)(?:\?modelVersionId=(\d+))?", l)
            if m and "SAFETY" in sec.upper():
                add(m.group(1), m.group(2))
    return {"model_ids": sorted(mids), "version_ids": sorted(vids)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aiops-db"); ap.add_argument("--aiops-jsonl")
    ap.add_argument("--plans"); ap.add_argument("--plans-jsonl")
    ap.add_argument("--batches", help="dir with *decisions.json / *safety-models.txt / *skip-urls.txt")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "data" / "local"))
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.aiops_db or a.aiops_jsonl:
        n = 0
        with gzip.open(out / "aiops_graydient.jsonl.gz", "wt", encoding="utf-8", compresslevel=9) as f:
            for r in aiops_rows(a.aiops_db, a.aiops_jsonl):
                if r.get("kind", "lora") != "lora" or (r.get("family") or "") == "sd15":
                    continue
                if not (r.get("on_graydient") or r.get("on_hf") or r.get("on_raid")):
                    continue
                if not in_repo(r.get("family")) and (r.get("family") or "") != "unknown":
                    continue
                o = {k: r.get(k) for k in AIOPS_KEEP if r.get(k) not in (None, "", [], False)}
                o["source_url"] = scrub(r.get("source_url"))
                o["description"] = scrub(r.get("description"), 600)
                o["tags"] = [t for t in (r.get("tags") or []) if isinstance(t, str)][:20]
                if r.get("example_prompts"):
                    o["example_prompts"] = [scrub(r["example_prompts"][0], 300)]
                f.write(json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "\n"); n += 1
        print("aiops rows", n)
    if a.plans or a.plans_jsonl:
        n = 0
        with gzip.open(out / "ingest_plans.jsonl.gz", "wt", encoding="utf-8", compresslevel=9) as f:
            for r in plan_rows(a.plans, a.plans_jsonl):
                if r.get("state") not in ("registered", "verified", "uploaded"):
                    continue
                if not in_repo(r.get("family"), r.get("base_model")):
                    continue
                o = {k: r.get(k) for k in PLAN_KEEP if r.get(k) not in (None, "", [], False)}
                o["civit_url"] = scrub(r.get("civit_url"))
                o["description"] = scrub(r.get("description"), 800)
                o["archived"] = bool(r.get("archived_path"))
                for k in ("plan", "plan_created", "plan_mtime"):
                    if r.get(k): o[k] = r[k]
                f.write(json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "\n"); n += 1
        print("plan rows", n)
    if a.batches:
        s = safety_ids(a.batches)
        (out / "safety_skips.json").write_text(json.dumps(s, separators=(",", ":")))
        print("safety ids", len(s["model_ids"]), len(s["version_ids"]))

if __name__ == "__main__":
    sys.exit(main())
