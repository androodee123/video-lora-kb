#!/usr/bin/env python3
"""One idempotent entry point to update video-lora-kb (H3 / Wan / LTX video LoRAs).

  bash scripts/update.sh [--dry-run] [--no-civitai] [--max-minutes 30] [--pages 3] [--allow-dirty] [--no-push]

Steps: pull -> add new CivitAI video LoRAs as candidates -> re-list Graydient HF sources (civit, civit2, private)
and rematch (candidates that are now on Graydient move to available) -> rebuild families/README/SKILL auto block/
accessibility report/ingest queue/export pack -> proposals + CHANGELOG -> secret scan -> commit + push only if
something changed -> print ONE machine-readable JSON line as the last stdout line.

Metadata only. Never downloads weights, never runs ingest.py, never ingests to Graydient.
"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, time
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_lib as U

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPO = "androodee123/video-lora-kb"
PY = sys.executable

def jl(p):
    return [json.loads(l) for l in p.read_text().split("\n") if l.strip()] if p.exists() else []

def key(r):
    return f"{r.get('family')}|{r.get('slug') or r.get('file')}|{r.get('file')}|{r.get('version_id')}"

def snapshot():
    avail = {key(r): r for r in jl(DATA / "loras.jsonl")}
    cand = {key(r): r for r in jl(DATA / "candidates.jsonl")}
    excl = {key(r) for r in jl(DATA / "excluded.jsonl")}
    return avail, cand, excl

def desc(r):
    url = (r.get("urls") or {}).get("civitai") or (r.get("urls") or {}).get("huggingface") or ""
    trig = ", ".join(r.get("triggers") or []) or "trigger not stated"
    return f"`{r.get('slug') or r.get('file')}` ({r.get('family')}) — {trig}" + (f" — {url}" if url else "")

def counts(avail, cand):
    c = {}
    for fam in ("H3", "Wan", "LTX2"):
        rows = [r for r in avail.values() if r.get("family") == fam]
        c[fam] = {"on_graydient": sum(1 for r in rows if r.get("graydient")), "to_add": sum(1 for r in rows if not r.get("graydient")),
                  "available": len(rows), "candidates": sum(1 for r in cand.values() if r.get("family") == fam)}
    c["total"] = {k: sum(c[f][k] for f in ("H3", "Wan", "LTX2")) for k in ("on_graydient", "to_add", "available", "candidates")}
    return c

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="run everything, print summary, but do not commit/push and restore the tree")
    ap.add_argument("--no-civitai", action="store_true", help="HF/Graydient rematch only (no CivitAI requests)")
    ap.add_argument("--no-push", action="store_true", help="commit locally but do not push")
    ap.add_argument("--allow-dirty", action="store_true", help="do not abort when the working tree has uncommitted changes")
    ap.add_argument("--max-minutes", type=float, default=30.0)
    ap.add_argument("--pages", type=int, default=3, help="CivitAI 'Newest' pages per baseModel (cap)")
    a = ap.parse_args()
    U.sanitize_env()
    clock = U.Clock(a.max_minutes)
    today = datetime.now().strftime("%Y-%m-%d")
    summary = {"repo": REPO, "date": today, "mode": "dry-run" if a.dry_run else "apply", "status": "error", "warnings": []}
    with U.Lock(ROOT):
        clean_start = not U.dirty(ROOT)
        summary["_clean_start"] = clean_start
        try:
            run(a, clock, summary, today)
        except SystemExit as e:
            summary["status"] = "aborted"; summary["error"] = str(e)
            if clean_start:
                U.restore_tree(ROOT)
        except Exception as e:  # keep the routine report machine-readable
            summary["status"] = "error"; summary["error"] = f"{type(e).__name__}: {e}"[:400]
            U.log(summary["error"])
            if clean_start:
                U.restore_tree(ROOT)
    summary.pop("_clean_start", None)
    summary["runtime_s"] = round(time.time() - clock.t0, 1)
    summary["steps_s"] = clock.steps
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["status"] in ("pushed", "no-change", "dry-run-ok", "committed-not-pushed") else 1

def run(a, clock, summary, today):
    ok, detail = U.check_gh_account(ROOT, need_push=not (a.dry_run or a.no_push))
    if not ok:
        raise SystemExit(f"github account check failed: {detail}")
    U.ensure_git_identity(ROOT)
    if not summary["_clean_start"] and not a.allow_dirty:
        raise SystemExit("working tree not clean; commit/stash first (or --allow-dirty)")
    with clock.step("git pull --rebase"):
        r = U.sh(["git", "pull", "--rebase"], ROOT, check=False)
        if r.returncode != 0:
            U.sh(["git", "rebase", "--abort"], ROOT, check=False)
            raise SystemExit("git pull --rebase failed: " + (r.stderr or "")[-300:])
    before_avail, before_cand, before_excl = snapshot()
    new_ids = []
    if not a.no_civitai:
        with clock.step("civitai: add new video LoRAs as candidates"):
            r = U.sh([PY, "scripts/add_new_candidates.py", "--pages", str(a.pages), "--deadline", str(clock.deadline - 600)], ROOT, check=False)
            if r.returncode == 0 and r.stdout.strip():
                j = json.loads(r.stdout.strip().splitlines()[-1])
                new_ids = j.get("ids", [])
                summary["civitai_seen"] = j["seen"]; summary["civitai_new_candidates"] = j["new_candidates"]; summary["civitai_excluded_minor_or_nonvideo"] = j["excluded"]
            else:
                summary["warnings"].append("civitai step failed: " + (r.stderr or "")[-200:])
    with clock.step("rematch Graydient HF sources (civit, civit2, private)"):
        r = U.sh([PY, "scripts/filter_accessible.py", "--refresh-hf"], ROOT, check=False)
        if r.returncode != 0:
            raise SystemExit("filter_accessible failed: " + (r.stderr or "")[-300:])
        listed_ok = "could not list" not in (r.stderr or "")
        summary["hf_listing_ok"] = listed_ok
        if not listed_ok:
            raise SystemExit("could not list one of the Graydient HF repos; refusing to rematch from cache (no changes kept)")
        m = re.search(r"HF weights reviewed: (\d+)", r.stdout)
        summary["hf_weights_reviewed"] = int(m.group(1)) if m else None
    after_avail, after_cand, after_excl = snapshot()

    # diff
    moved = [k for k in after_avail if k in before_cand]
    added = [k for k in after_avail if k not in before_avail and k not in before_cand]
    removed = [k for k in before_avail if k not in after_avail]
    became_gray = [k for k in after_avail if k in before_avail and after_avail[k].get("graydient") and not before_avail[k].get("graydient")]
    new_cand = [k for k in after_cand if k not in before_cand and k not in before_avail]
    dropped_cand = [k for k in before_cand if k not in after_cand and k not in after_avail]
    new_excl = len(after_excl - before_excl)
    summary["counts"] = counts(after_avail, after_cand)
    summary["changes"] = {"candidates_moved_to_available": len(moved), "added_available": len(added), "removed_available": len(removed),
                          "became_on_graydient": len(became_gray), "new_candidates": len(new_cand), "dropped_candidates": len(dropped_cand), "new_excluded": new_excl}

    with clock.step("rebuild families / README / SKILL auto block"):
        # render_kb reads an optional rich sidecar from /tmp; regenerate it from loras.jsonl so rendering is stable.
        side = Path("/tmp/vlora-work/records-full.json")
        side.parent.mkdir(parents=True, exist_ok=True)
        side.write_text(json.dumps(list(after_avail.values()), ensure_ascii=False))
        U.sh([PY, "scripts/render_kb.py"], ROOT)
        recent = update_recent(today, [after_avail[k] for k in moved + added + became_gray], [after_cand[k] for k in new_cand])
        U.patch_markers(ROOT / "SKILL.md", skill_block(summary["counts"], recent, today), "## How to stack")
    with clock.step("export pack"):
        r = U.sh([PY, "scripts/export_pack.py"], ROOT, check=False)
        if r.returncode != 0:
            summary["warnings"].append("export_pack failed: " + (r.stderr or "")[-200:])
        else:
            share = Path("/workspace/share")
            if share.is_dir():
                for z in (ROOT / "dist").glob("*.zip"):
                    shutil.copy2(z, share / z.name)

    changed_semantic = any(summary["changes"].values())
    reverted = U.revert_cosmetic(ROOT) if summary["_clean_start"] else []
    if reverted:
        U.log("reverted timestamp-only diffs:", reverted)
    changed_files = U.dirty(ROOT)
    if changed_files:
        if True:
            write_reports(today, summary, [after_avail[k] for k in moved], [after_avail[k] for k in added], [before_avail[k] for k in removed],
                          [after_avail[k] for k in became_gray], [after_cand[k] for k in new_cand], after_cand)
    summary["files_changed"] = len([l for l in changed_files.splitlines() if l.strip()])
    if a.dry_run:
        summary["diffstat"] = U.sh(["git", "diff", "--stat", "--no-color"], ROOT).stdout.strip().splitlines()[-1:] or []
        if summary["_clean_start"]:
            U.restore_tree(ROOT)
        summary["status"] = "dry-run-ok"
        return
    if not changed_files:
        summary["status"] = "no-change"; summary["commit"] = U.sh(["git", "rev-parse", "HEAD"], ROOT).stdout.strip()
        return
    ch = summary["changes"]
    msg = (f"Auto-update {today}: {ch['candidates_moved_to_available']} moved to available, {ch['added_available']} added, "
           f"{ch['new_candidates']} new candidates; {summary['counts']['total']['on_graydient']} on Graydient / {summary['counts']['total']['candidates']} candidates")
    with clock.step("commit + push"):
        res = U.commit_and_push(ROOT, msg, push=not a.no_push)
    summary["status"] = res["status"]; summary["commit"] = res["sha"]
    if res["hits"]:
        summary["secret_scan_hits"] = [f"{k}:{f}" for k, f in res["hits"]]
    if res["status"] == "pushed":
        summary["visibility"] = U.visibility(ROOT, REPO)
    if res["status"] == "aborted-secret-scan":
        raise SystemExit("secret scan hit; nothing committed: " + ", ".join(summary["secret_scan_hits"]))

def update_recent(today, newly_available, new_cands):
    p = DATA / "recent_additions.json"
    cur = json.loads(p.read_text()) if p.exists() else {"available": [], "candidates": []}
    def pack(r, ev):
        url = (r.get("urls") or {}).get("civitai") or (r.get("urls") or {}).get("huggingface") or ""
        return {"date": today, "event": ev, "family": r.get("family"), "slug": r.get("slug") or r.get("file"), "triggers": (r.get("triggers") or [])[:4], "url": url}
    if newly_available:
        cur["available"] = ([pack(r, "available") for r in newly_available] + cur["available"])[:120]
    if new_cands:
        cur["candidates"] = ([pack(r, "candidate") for r in sorted(new_cands, key=lambda r: -(r.get("ingest_priority") or 0))[:15]] + cur["candidates"])[:60]
    p.write_text(json.dumps(cur, indent=1, ensure_ascii=False))
    return cur

def skill_block(c, recent, today):
    t = c["total"]
    L = [f"## Live inventory (auto-updated by `scripts/update.py`, {today})", "",
         f"On Graydient **{t['on_graydient']}** · to add to Graydient **{t['to_add']}** · available **{t['available']}** · ingest candidates **{t['candidates']}** "
         f"(H3 {c['H3']['available']}, Wan {c['Wan']['available']}, LTX {c['LTX2']['available']} available). Ranked candidates: `data/candidates.jsonl`, queue: `data/graydient_ingest_queue.md`.", ""]
    if recent["available"]:
        L += ["**Recently became available on Graydient (newest first, max 20):**", ""]
        for r in recent["available"][:20]:
            L.append(f"- {r['date']} `{r['slug']}` ({r['family']}) — {', '.join(r['triggers']) or 'trigger not stated'}" + (f" — {r['url']}" if r['url'] else ""))
        L.append("")
    if recent["candidates"]:
        L += ["**Newest ingest candidates found by the weekly update (proposals only, nothing auto-downloads; max 10):**", ""]
        for r in recent["candidates"][:10]:
            L.append(f"- {r['date']} `{r['slug']}` ({r['family']}) — {', '.join(r['triggers']) or 'trigger not stated'}" + (f" — {r['url']}" if r['url'] else ""))
        L.append("")
    L.append("Recipes below are curated; newly available LoRAs appear in the family pages (`families/`) and here until a recipe is updated.")
    return "\n".join(L)

def write_reports(today, summary, moved, added, removed, became, new_cand, after_cand):
    ch, c = summary["changes"], summary["counts"]["total"]
    lines = [f"# Update {today}", "", f"Applied automatically by `scripts/update.py`. Counts: on Graydient {c['on_graydient']}, to add {c['to_add']}, available {c['available']}, candidates {c['candidates']}.", ""]
    sections = [("Candidates now on Graydient (moved to available)", moved), ("Newly added to the available set", added), ("Existing rows that became on Graydient", became), ("Removed from the available set", removed)]
    for title, rows in sections:
        if rows:
            lines += [f"## {title} ({len(rows)})", ""] + U.fmt_items([desc(r) for r in rows]) + [""]
    top = sorted(new_cand, key=lambda r: -(r.get("ingest_priority") or 0))
    if top:
        lines += [f"## New ingest candidates ({len(new_cand)}) — proposals only", "", "Nothing is downloaded or ingested. Ingest runs only when Andrew asks (civit-to-graydient).", ""] + U.fmt_items([f"{desc(r)} — {int(r.get('downloads') or 0):,} dl, priority {r.get('ingest_priority')}" for r in top], 40) + [""]
    if len(lines) <= 4:
        lines += ["Only metadata refreshed (counts, rankings, download stats); no new, moved or removed LoRAs.", ""]
    (ROOT / "proposals").mkdir(exist_ok=True)
    (ROOT / "proposals" / f"{today}.md").write_text("\n".join(lines))
    entry = [f"## {today}", "", f"Counts: on Graydient {c['on_graydient']} · to add {c['to_add']} · candidates {c['candidates']}. "
             f"Moved candidate→available {ch['candidates_moved_to_available']}, added {ch['added_available']}, became on Graydient {ch['became_on_graydient']}, removed {ch['removed_available']}, new candidates {ch['new_candidates']}."]
    for title, rows in sections[:3]:
        if rows:
            entry += ["", f"{title}:"] + U.fmt_items([desc(r) for r in rows], 15)
    U.changelog_prepend(ROOT, "\n".join(entry))

if __name__ == "__main__":
    sys.exit(main())
