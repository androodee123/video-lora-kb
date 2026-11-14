#!/usr/bin/env python3
"""Incrementally add NEW CivitAI video LoRAs (H3 / Wan / LTX) to data/candidates.jsonl.

Metadata only: never downloads weights. Reads the newest CivitAI pages for every confirmed video baseModel,
skips models already in loras.jsonl / candidates.jsonl / excluded.jsonl, builds a candidate row with the same
builders as build_kb.py (stated triggers/strength/example prompts only; never invented), and appends it.
Minor-coded / forbidden-identity models go to data/excluded.jsonl instead. ingest_priority and promotion to
'available' are then computed by filter_accessible.py (run right after this script by update.py).

Usage: python3 scripts/add_new_candidates.py [--pages 3] [--dry-run] [--deadline EPOCH]
Prints one JSON line: {"new_candidates": n, "excluded": n, "seen": n, "ids": [...]}.
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_kb as B
import harvest as H
import video_lora as V
import safety as S

ROOT = H.ROOT
DATA = ROOT / "data"

def jl(p):
    return [json.loads(l) for l in p.read_text().split("\n") if l.strip()] if p.exists() else []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--deadline", type=float, default=0)
    a = ap.parse_args()
    known = set()
    for f in ("loras.jsonl", "candidates.jsonl", "excluded.jsonl"):
        for r in jl(DATA / f):
            if r.get("civitai_model_id"):
                known.add(int(r["civitai_model_id"]))
    new_rows, excl_rows, seen = [], [], set()
    for bm in H.BASE_MODELS:
        if a.deadline and time.time() > a.deadline:
            print("deadline reached; stopping early", file=sys.stderr)
            break
        for page in H.iter_civitai_pages(bm, "newest", limit=a.limit, max_pages=a.pages, refresh=True,
                                         cache_name="update_newest", types=["LORA", "LoCon", "DoRA"]):
            for model in page.get("items") or []:
                mid = model.get("id")
                if not mid or mid in seen:
                    continue
                seen.add(mid)
                if mid in known or not V.civitai_is_adapter_type(model) or not V.civitai_has_video_base(model):
                    continue
                st = model.get("stats") or {}
                families = sorted({H.family_of_base(v.get("baseModel")) for v in (model.get("modelVersions") or [])} - {None})
                for fam in families:
                    vers = B.versions_for_family(model, fam)
                    ver = B.best_version(vers)
                    if not ver:
                        continue
                    fname = B.first_safetensor(ver) or f"{B.slugify(model.get('name') or str(mid))}.safetensors"
                    desc = B.model_description(model, vers)
                    trained = B.trained_words(vers)
                    bases = sorted({v.get("baseModel") for v in vers if v.get("baseModel")})
                    # example prompts: description blocks, then list-endpoint image meta (source-stated only)
                    examples = []
                    for im in (ver.get("images") or []):
                        pr = ((im.get("meta") or {}).get("prompt") or "").strip()
                        if pr and pr[:1500] not in examples:
                            examples.append(pr[:1500])
                        if len(examples) >= 2:
                            break
                    if len(examples) < 2:
                        ex = B.extract_example_prompt(desc)
                        if ex and ex not in examples:
                            examples.append(ex)
                    cats = B.classify(model.get("name") or "", model.get("tags") or [], fname, None, description=desc)
                    i2v = B.infer_i2v_t2v(bases, model.get("name") or "", desc, fname)
                    rec = {
                        "family": fam, "file": fname, "slug": B.slugify(model.get("name") or fname),
                        "civitai_model_id": mid, "version_id": ver.get("id"),
                        "base": ver.get("baseModel") or (bases[0] if bases else None), "bases": bases,
                        "triggers": trained, "strength": B.extract_strength(desc) or "not stated", "categories": cats,
                        "urls": {"civitai": f"https://civitai.com/models/{mid}?modelVersionId={ver.get('id')}"},
                        "verified": True, "installed": False, "i2v_t2v": i2v,
                        "purpose": (model.get("name") or fname).split("|")[0].strip()[:160], "path": None,
                        "civitai_name": model.get("name"), "downloads": st.get("downloadCount") or 0,
                        "thumbs_up": st.get("thumbsUpCount") or 0, "source": "civitai",
                        "files": B.high_low_files(vers)[:12], "example_prompt": examples[0] if examples else None,
                        "example_prompts": examples[:2], "low_signal": (st.get("downloadCount") or 0) < 100 and (st.get("thumbsUpCount") or 0) < 1,
                        "compatibility": B.compatibility_notes(fam, bases, model.get("name") or "", desc, fname, B.high_low_files(vers), i2v),
                    }
                    reason = S.minor_reason(model.get("name"), " ".join(B.tag_names(model.get("tags"))), " ".join(trained)) or S.hard_reason(desc[:1500])
                    if reason:
                        rec["exclude_reason"] = reason
                        excl_rows.append(rec)
                        continue
                    keep, why = V.classify_record(rec, model)
                    if keep:
                        new_rows.append(rec)
                    else:
                        rec["exclude_reason"] = why
                        excl_rows.append(rec)
    if not a.dry_run:
        if new_rows:
            with (DATA / "candidates.jsonl").open("a", encoding="utf-8") as f:
                for r in new_rows:
                    f.write(json.dumps({k: r.get(k) for k in B.JSONL_KEYS}, ensure_ascii=False) + "\n")
        if excl_rows:
            keys = list(B.JSONL_KEYS) + ["exclude_reason"]
            with (DATA / "excluded.jsonl").open("a", encoding="utf-8") as f:
                for r in excl_rows:
                    f.write(json.dumps({k: r.get(k) for k in keys}, ensure_ascii=False) + "\n")
    print(json.dumps({"new_candidates": len(new_rows), "excluded": len(excl_rows), "seen": len(seen),
                      "ids": [r["civitai_model_id"] for r in new_rows][:200]}))

if __name__ == "__main__":
    main()
