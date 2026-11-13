#!/usr/bin/env python3
"""Filter the catalog to Graydient- or AIOps-accessible video LoRAs.

Accessible:
  - graydient: a matching file exists in Hugging Face repo Octavian123/civit
    (private Graydient concepts are registered from those {slug}.safetensors
    files). Metadata only — this script never downloads weights.
  - aiops: the row is already on the AIOps RAID (installed=true), from the
    13 Nov 2026 snapshot at /Volumes/RAID/Lora/{H3,Wan,LTX2}.

data/loras.jsonl is rewritten to accessible rows only (graydient OR aiops).
Everything else goes to data/candidates.jsonl with an ingest_priority score.
data/excluded.jsonl is left untouched.

Unmatched Octavian123/civit files that are clearly video LoRAs (H3 / Wan / LTX)
are added as graydient=true, verified=false rows. Image-family files
(-krea2, -anima, -moss, -ill, … and moss/ checkpoints) are not added unless
they already match a catalog video row.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import access_rules as R
import build_kb as B
import harvest as H

ROOT = H.ROOT
JSONL = ROOT / "data" / "loras.jsonl"
CANDIDATES = ROOT / "data" / "candidates.jsonl"
REPORT = ROOT / "data" / "accessibility_report.md"
HF_CACHE = ROOT / "data" / "raw" / "huggingface" / "octavian123-civit-files.txt"
HF_REPO = "Octavian123/civit"
TZ = ZoneInfo("Africa/Johannesburg")

WEIGHT_EXT = (".safetensors", ".sft")
IMAGE_LAST_TOKENS = {
    "krea2", "anima", "ill", "pony", "moss", "flux", "flux2", "xl", "zimage",
    "qwen", "sd15", "illustrious", "il", "ilxl", "sdxl", "ponyxl", "chroma",
    "hidream", "sd3", "kolors", "nova", "wai", "prefect", "lustify", "semireal",
    "realismxl", "zit", "zib", "klein",
}
VIDEO_SUFFIX = {
    "h3": "H3", "mh3": "H3", "mmh3": "H3",
    "wan": "Wan", "wan21": "Wan", "wan22": "Wan", "wan2": "Wan",
    "ltx2": "LTX2", "ltx23": "LTX2", "ltx25": "LTX2", "ltxv": "LTX2", "ltx": "LTX2",
}

H3_NAME_RE = re.compile(r"(minimax[\s\-]*h3|\bmh3\b|\bmm[\s\-]?h3\b|hailuo\s*0?2|mini[\s\-]?max[\s\-]*h3)", re.I)
WAN_NAME_RE = re.compile(
    r"(wan\s*2\.[12]|wan2[\._][12]|wan\s*video|\bwan[\s\-]?14b\b|i2v[\s\-]?wan|wan[\s\-]?i2v|wan[\s\-]?t2v|t2v[\s\-]?wan|ti2v[\s\-]?5b)",
    re.I,
)
LTX_NAME_RE = re.compile(r"(\bltx[\s\-]?2(?:\.[0-9])?\b|\bltxv(?:2)?\b|\bltx23\b|\bltx25\b)", re.I)


def slugify(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"\.(safetensors|sft)$", "", s, flags=re.I)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def stem(name: str) -> str:
    base = (name or "").rsplit("/", 1)[-1]
    return re.sub(r"\.(safetensors|sft)$", "", base, flags=re.I)


def last_token(sl: str) -> str:
    parts = [p for p in (sl or "").split("-") if p]
    return parts[-1] if parts else ""


def family_suffix(sl: str) -> str | None:
    tok = last_token(sl)
    return VIDEO_SUFFIX.get(tok)


def infer_family(path: str) -> str | None:
    """Classify an Octavian123/civit filename as H3 / Wan / LTX2, or None.

    Suffix after slugify is the primary signal. Image-family last tokens
    (-krea2, -anima, -moss, -ill, …) return None even if the name mentions
    'wan' or 'h3' as a word. moss/ tree is image training checkpoints unless
    a later exact catalog match already used the file.
    """
    if path.startswith("moss/"):
        return None
    base = path.rsplit("/", 1)[-1]
    sl = slugify(base)
    tok = last_token(sl)
    if tok in IMAGE_LAST_TOKENS:
        return None
    if tok in VIDEO_SUFFIX:
        return VIDEO_SUFFIX[tok]
    # Long original CivitAI names often end in a unique weight stem, not a family suffix.
    if H3_NAME_RE.search(base):
        return "H3"
    if WAN_NAME_RE.search(base) and not re.search(r"\bwants?\b|\bwand\b|\bwana\b|\bwang\b|\bwayne\b", base, re.I):
        return "Wan"
    if LTX_NAME_RE.search(base):
        return "LTX2"
    return None


def list_hf_files(refresh: bool) -> list[str]:
    if HF_CACHE.exists() and not refresh:
        files = [ln.strip() for ln in HF_CACHE.read_text(encoding="utf-8").splitlines() if ln.strip()]
        print(f"HF file list from cache ({len(files)} paths): {HF_CACHE}", file=sys.stderr)
        return files
    from huggingface_hub import HfApi
    print(f"listing {HF_REPO} via huggingface_hub (metadata only, no weights) ...", file=sys.stderr)
    files = list(HfApi().list_repo_files(HF_REPO, repo_type="model"))
    HF_CACHE.parent.mkdir(parents=True, exist_ok=True)
    HF_CACHE.write_text("\n".join(files) + "\n", encoding="utf-8")
    print(f"wrote cache {HF_CACHE} ({len(files)} paths)", file=sys.stderr)
    return files


def catalog_keys(r: dict) -> list[tuple[str, str]]:
    """(kind, slugified_or_raw) keys used to match a catalog row to an HF file."""
    out: list[tuple[str, str]] = []
    seen = set()

    def add(kind, val, raw=False):
        if not val:
            return
        key = val if raw else slugify(val)
        if not key or (kind, key) in seen:
            return
        seen.add((kind, key))
        out.append((kind, key))

    add("slug", r.get("slug"))
    if r.get("file"):
        add("file", stem(r["file"]))
        add("file_raw", r["file"].rsplit("/", 1)[-1].lower(), raw=True)
    for n in r.get("files") or []:
        add("files", stem(n))
        add("files_raw", n.rsplit("/", 1)[-1].lower(), raw=True)
    path = r.get("path") or ""
    if path and not path.startswith("(not"):
        add("path", stem(path))
    # civitai_name is useful when the RAID slug differs from the Graydient slug
    # (e.g. larryvrh-h3 vs minimax-h3-turbo-loras-h3). Only used with family checks.
    if r.get("civitai_name"):
        add("civitai_name", r["civitai_name"])
    return out


def trailing_weight_name(hf_basename: str) -> str | None:
    """CivitAI uploads often look like 'Title - version - actual_file.safetensors'."""
    base = hf_basename
    if " - " not in base:
        return None
    tail = base.rsplit(" - ", 1)[-1].strip()
    if tail.lower().endswith(WEIGHT_EXT) and len(tail) >= 8:
        return tail
    return None


def build_hf_indexes(hf_files: list[str]):
    weights = [f for f in hf_files if f.lower().endswith(WEIGHT_EXT)]
    by_slug: dict[str, list[str]] = defaultdict(list)
    by_lower: dict[str, list[str]] = defaultdict(list)
    by_stem: dict[str, list[str]] = defaultdict(list)
    for f in weights:
        base = f.rsplit("/", 1)[-1]
        by_slug[slugify(base)].append(f)
        by_lower[base.lower()].append(f)
        by_stem[stem(base).lower()].append(f)
        tail = trailing_weight_name(base)
        if tail:
            by_lower[tail.lower()].append(f)
            by_stem[stem(tail).lower()].append(f)
            by_slug[slugify(tail)].append(f)
    return weights, by_slug, by_lower, by_stem


def keys_compatible(row_key: str, hf_slug: str, row_family: str, hf_path: str) -> str | None:
    """Return a reason if this is a conservative non-exact match, else None.

    Rejects version forks like foo-v2-h3 vs foo-h3, cross-family hits, and
    short/generic prefixes.
    """
    if not row_key or not hf_slug or row_key == hf_slug:
        return "exact" if row_key == hf_slug else None
    if hf_path.startswith("moss/") or last_token(hf_slug) in IMAGE_LAST_TOKENS:
        return None
    hf_fam = infer_family(hf_path)
    if hf_fam and row_family and hf_fam != row_family:
        return None
    # If both end with the same video family suffix, compare the stem before it.
    suf = family_suffix(row_key)
    suf_h = family_suffix(hf_slug)
    if suf and suf_h and suf != suf_h:
        return None

    def strip_suf(s, family_name):
        for token, fam in VIDEO_SUFFIX.items():
            if fam == family_name and s.endswith("-" + token):
                return s[: -(len(token) + 1)]
        return s

    a = strip_suf(row_key, row_family) if suf else row_key
    b = strip_suf(hf_slug, hf_fam or row_family) if suf_h else hf_slug
    if a == b:
        return "same-stem"
    # Version fork: foo-v2 vs foo, or foo-v1 vs foo-v0-1
    if re.sub(r"-v?\d+(?:-\d+)*$", "", a) == re.sub(r"-v?\d+(?:-\d+)*$", "", b) and a != b:
        # only allow if one is exactly the other plus a trailing qualifier that is NOT a version
        return None
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    if not longer.startswith(shorter):
        # common prefix, possible truncation at ~70-90 chars
        n = 0
        for x, y in zip(a, b):
            if x == y:
                n += 1
            else:
                break
        if n >= 36 and abs(len(a) - len(b)) <= 20:
            return f"common-prefix-{n}"
        return None
    # Prefix: require a reasonably long shorter key so "motion-h3" does not
    # swallow every motion-* file. Truncated Graydient slugs are typically long.
    if len(shorter) < 28:
        return None
    # If the shorter one looks version-stripped from the longer (shorter + -vN)
    rest = longer[len(shorter):]
    if re.match(r"-v?\d+", rest):
        return None
    return "prefix"


def match_rows(rows: list[dict], hf_files: list[str]):
    weights, by_slug, by_lower, by_stem = build_hf_indexes(hf_files)
    matches: dict[int, list[tuple[str, str]]] = {}  # idx -> (reason, hf_path)

    def add_hit(idx, reason, path, bag):
        if path not in {p for _, p in bag}:
            bag.append((reason, path))

    for i, r in enumerate(rows):
        bag: list[tuple[str, str]] = []
        fam = r.get("family") or ""
        def usable(path, kind):
            # Image-family uploads (-krea2, -anima, -moss, -ill, qwen, zimage, moss/)
            # are not Graydient video access, even when they share a CivitAI title.
            if path.startswith("moss/"):
                return False
            sl = slugify(path.rsplit("/", 1)[-1])
            if last_token(sl) in IMAGE_LAST_TOKENS:
                return False
            hf_fam = infer_family(path)
            if hf_fam and fam and hf_fam != fam:
                return False
            # civitai_name / fuzzy need a clear video family; exact file/slug/path
            # may still match an oddly named video weight.
            if kind in ("civitai_name",) and not hf_fam:
                return False
            return True

        for kind, key in catalog_keys(r):
            if kind.endswith("_raw"):
                for path in by_lower.get(key, []) + by_stem.get(key.replace(".safetensors", "").replace(".sft", ""), []):
                    if usable(path, kind):
                        add_hit(i, f"exact-{kind}", path, bag)
                continue
            for path in by_slug.get(key, []):
                if usable(path, kind):
                    add_hit(i, f"exact-{kind}", path, bag)
        # conservative fuzzy only if nothing exact yet, or to attach long-name duplicates
        if not bag:
            for kind, key in catalog_keys(r):
                if kind.endswith("_raw") or len(key) < 28:
                    continue
                # only probe HF slugs that share a 20-char prefix
                prefix = key[:20]
                for sl, paths in by_slug.items():
                    if not sl.startswith(prefix) and not key.startswith(sl[:20]):
                        continue
                    for path in paths:
                        if path.startswith("moss/") or last_token(slugify(path.rsplit("/", 1)[-1])) in IMAGE_LAST_TOKENS:
                            continue
                        reason = keys_compatible(key, sl, fam, path)
                        if reason and reason != "exact":
                            add_hit(i, f"{reason}-{kind}", path, bag)
        if bag:
            matches[i] = bag
    return matches, weights, by_slug


def unmatched_video_files(hf_weights: list[str], used: set[str]) -> list[tuple[str, str]]:
    out = []
    for path in hf_weights:
        if path in used:
            continue
        if path.startswith("moss/"):
            continue
        fam = infer_family(path)
        if fam:
            out.append((path, fam))
    return out


def new_row_from_hf(path: str, family: str) -> dict:
    base = path.rsplit("/", 1)[-1]
    sl = slugify(base)
    purpose = sl
    for tok, fam in VIDEO_SUFFIX.items():
        if fam == family and sl.endswith("-" + tok):
            purpose = sl[: -(len(tok) + 1)]
            break
    purpose = purpose.replace("-", " ").strip() or sl
    url = f"https://huggingface.co/{HF_REPO}/blob/main/{path}"
    rec = {
        "family": family,
        "file": base,
        "slug": sl,
        "civitai_model_id": None,
        "version_id": None,
        "base": {"H3": "MiniMax H3", "Wan": None, "LTX2": None}[family],
        "triggers": [],
        "strength": "not stated",
        "categories": B.classify(purpose, [], base, None, None),
        "urls": {"huggingface": url},
        "verified": False,
        "installed": False,
        "i2v_t2v": B.infer_i2v_t2v([], purpose, "", base),
        "purpose": purpose,
        "path": None,
        "civitai_name": None,
        "downloads": None,
        "thumbs_up": None,
        "source": "octavian123-civit",
        "bases": None,
        "hf_id": HF_REPO,
        "files": [base],
        "example_prompt": None,
        "example_prompts": [],
        "low_signal": False,
        "compatibility": B.compatibility_notes(family, [], purpose, "", base, [base], B.infer_i2v_t2v([], purpose, "", base)),
        "graydient": True,
        "aiops": False,
        "graydient_files": [path],
    }
    return rec


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(rows: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    print(f"wrote {path} ({len(rows)})", file=sys.stderr)


def sort_accessible(rows: list[dict]) -> list[dict]:
    fam_ord = {"H3": 0, "Wan": 1, "LTX2": 2}

    def key(r):
        lab = R.access_label(r)
        lab_ord = {R.ON_GRAYDIENT: 0, R.TO_ADD: 1}.get(lab, 3)
        inst = 0 if r.get("aiops") or r.get("installed") else 1
        dl = -(r.get("downloads") or 0)
        return (fam_ord.get(r.get("family"), 9), lab_ord, inst, dl, r.get("slug") or r.get("file") or "")

    return sorted(rows, key=key)


def sort_candidates(rows: list[dict]) -> list[dict]:
    fam_ord = {"H3": 0, "Wan": 1, "LTX2": 2}

    def key(r):
        return (
            -(r.get("ingest_priority") or 0),
            fam_ord.get(r.get("family"), 9),
            -(r.get("downloads") or 0),
            r.get("slug") or r.get("file") or "",
        )

    return sorted(rows, key=key)


def counts_block(acc: list[dict], cand: list[dict]) -> dict:
    out = {}
    for fam in ("H3", "Wan", "LTX2"):
        sub = [r for r in acc if r.get("family") == fam]
        g = sum(1 for r in sub if r.get("graydient"))
        a = sum(1 for r in sub if r.get("aiops"))
        both = sum(1 for r in sub if r.get("graydient") and r.get("aiops"))
        out[fam] = {
            "graydient_only": g - both,
            "aiops_only": a - both,
            "both": both,
            "accessible": len(sub),
            "graydient": g,
            "aiops": a,
            "candidates": sum(1 for r in cand if r.get("family") == fam),
        }
    out["ALL"] = {k: sum(out[f][k] for f in ("H3", "Wan", "LTX2")) for k in next(iter(out.values()))}
    return out


def render_report(
    now: str,
    hf_files: list[str],
    hf_weights: list[str],
    acc: list[dict],
    cand: list[dict],
    matches: dict,
    rows_before: int,
    unmatched: list[tuple[str, str]],
    used_files: set[str],
    aiops_not_graydient: list[dict],
    doubts: list[str],
) -> str:
    c = counts_block(acc, cand)
    lines = [
        f"# Accessibility report",
        "",
        f"Generated {now}. Source of Graydient access: Hugging Face `{HF_REPO}` "
        f"({len(hf_files)} paths, {len(hf_weights)} weight files, listed via the Hub API — no weights downloaded). "
        f"Source of AIOps access: `installed=true` rows from the 13 Nov 2026 RAID snapshot "
        f"(`/Volumes/RAID/Lora/{{H3,Wan,LTX2}}`).",
        "",
        f"Catalog before filter: **{rows_before}** video LoRAs. After filter: **{len(acc)}** accessible, "
        f"**{len(cand)}** ingest candidates. Unmatched HF video files added: **{len(unmatched)}** "
        f"(verified=false).",
        "",
        "## Counts",
        "",
        "| Family | Graydient only | AIOps only | Both | Accessible total | Candidates |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for fam, label in (("H3", "MiniMax H3"), ("Wan", "Wan"), ("LTX2", "LTX"), ("ALL", "**Total**")):
        x = c[fam]
        lines.append(
            f"| {label} | {x['graydient_only']} | {x['aiops_only']} | {x['both']} | "
            f"{x['accessible']} | {x['candidates']} |"
        )
    lines += [
        "",
        f"HF weight files reviewed: **{len(hf_weights)}**. HF weight files matched to a catalog row: "
        f"**{len(used_files)}**.",
        "",
        "## AIOps (installed) not on Graydient",
        "",
        f"{len(aiops_not_graydient)} of the installed RAID video LoRAs have no matching file in `{HF_REPO}`. "
        "They stay in `data/loras.jsonl` as AIOps-only.",
        "",
    ]
    if aiops_not_graydient:
        lines += [
            "| family | slug / file | source |",
            "|---|---|---|",
        ]
        for r in aiops_not_graydient:
            lines.append(f"| {r.get('family')} | `{r.get('slug') or r.get('file')}` | {r.get('source') or '—'} |")
        lines.append("")
    lines += [
        "## Unmatched Hugging Face video files added",
        "",
        f"{len(unmatched)} root-level weight files looked like H3 / Wan / LTX video LoRAs and did not match "
        "an existing catalog row. Each was added with `graydient=true`, `verified=false`, no invented trigger or strength.",
        "",
    ]
    if unmatched:
        lines += ["| family | file | slug |", "|---|---|---|"]
        for path, fam in unmatched:
            lines.append(f"| {fam} | `{path}` | `{slugify(path.rsplit('/',1)[-1])}` |")
        lines.append("")
    lines += [
        "## Classification doubts",
        "",
    ]
    if doubts:
        for d in doubts:
            lines.append(f"- {d}")
    else:
        lines.append("- None recorded.")
    lines += [
        "",
        "## Ingest priority",
        "",
        "Candidates in `data/candidates.jsonl` are scored with `scripts/access_rules.py` "
        "(log downloads and thumbs, bonuses for recorded trigger/strength/example, gap bonus, official-util bonus). "
        "See SKILL.md for the suggest-ingest rule used in recipes and family pages.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Filter catalog to Graydient- or AIOps-accessible video LoRAs.")
    ap.add_argument("--refresh-hf", action="store_true", help="re-list Octavian123/civit instead of using the cache")
    args = ap.parse_args()

    now = datetime.now(TZ).strftime("%-d %b %Y, %H:%M") + " Africa/Johannesburg (SAST)"
    rows = load_jsonl(JSONL)
    if not rows:
        sys.exit(f"missing catalog {JSONL}")
    rows_before = len(rows)

    hf_files = list_hf_files(refresh=args.refresh_hf)
    matches, hf_weights, _by_slug = match_rows(rows, hf_files)

    used: set[str] = set()
    for bag in matches.values():
        for _, path in bag:
            used.add(path)

    # Flag rows
    accessible = []
    leftover = []
    for i, r in enumerate(rows):
        r = dict(r)
        r["aiops"] = bool(r.get("installed"))
        if i in matches:
            r["graydient"] = True
            r["graydient_status"] = R.ON_GRAYDIENT
            r["graydient_files"] = sorted({p for _, p in matches[i]})
        else:
            r["graydient"] = False
            r["graydient_status"] = R.TO_ADD if r["aiops"] else "candidate"
            r["graydient_files"] = []
        if r["graydient"] or r["aiops"]:
            accessible.append(r)
        else:
            leftover.append(r)

    unmatched = unmatched_video_files(hf_weights, used)
    doubts = []
    # Don't add an unmatched HF file whose slug already exists in accessible
    exist_slugs = {slugify(r.get("slug") or "") for r in accessible}
    exist_slugs |= {slugify(stem(r.get("file") or "")) for r in accessible}
    added = []
    skipped_dup = []
    for path, fam in unmatched:
        sl = slugify(path.rsplit("/", 1)[-1])
        if sl in exist_slugs:
            skipped_dup.append((path, fam, sl))
            continue
        rec = new_row_from_hf(path, fam)
        accessible.append(rec)
        added.append((path, fam))
        exist_slugs.add(sl)
        used.add(path)
    if skipped_dup:
        doubts.append(
            f"{len(skipped_dup)} unmatched HF video files were not added because their slug already exists "
            f"on an accessible row (likely a long original filename next to a slugged upload): "
            + ", ".join(f"`{p}`" for p, _, _ in skipped_dup[:12])
            + ("…" if len(skipped_dup) > 12 else "")
        )

    # Family inference doubts: long names mentioning more than one family
    multi = []
    for path, fam in added:
        blob = path.lower()
        hits = []
        if H3_NAME_RE.search(blob):
            hits.append("H3")
        if WAN_NAME_RE.search(blob):
            hits.append("Wan")
        if LTX_NAME_RE.search(blob):
            hits.append("LTX")
        if len(set(hits)) > 1:
            multi.append((path, fam, hits))
    if multi:
        doubts.append(
            f"{len(multi)} added HF files mention more than one family in the filename; family was taken from the "
            f"clearest token/suffix (may be a multi-base upload of a single version). Examples: "
            + "; ".join(f"`{p}` → {fam} (also {hits})" for p, fam, hits in multi[:8])
        )
    doubts.append(
        "moss/ and *-moss.safetensors were treated as image (KroMoss / Krea) unless an exact catalog video-row "
        "match already used the file. No catalog video row matched a moss file in this run, so none were kept."
    )
    doubts.append(
        "Official Hugging Face packs (lightx2v, Lightricks IC-LoRAs, etc.) stay in candidates.jsonl unless the "
        "same weights were also uploaded to Octavian123/civit or are on the RAID. They are scored high for ingest "
        "because they fill utility gaps, but they are not treated as already accessible."
    )
    doubts.append(
        "Version forks (e.g. `…-v2-h3` on RAID vs `…-h3` on Graydient) are not merged. Each slug is its own row."
    )

    # Ingest scores
    acc_by_cat: dict[tuple[str, str], int] = Counter()
    for r in accessible:
        for cat in r.get("categories") or ["enhancement"]:
            acc_by_cat[(r.get("family"), cat)] += 1
    for r in leftover:
        r["graydient"] = False
        r["aiops"] = False
        r["graydient_files"] = r.get("graydient_files") or []
        r["ingest_priority"] = R.ingest_priority(r, acc_by_cat)

    accessible = sort_accessible(accessible)
    leftover = sort_candidates(leftover)

    write_jsonl(accessible, JSONL)
    write_jsonl(leftover, CANDIDATES)

    aiops_only = [r for r in accessible if r.get("aiops") and not r.get("graydient")]
    report = render_report(
        now, hf_files, hf_weights, accessible, leftover, matches, rows_before,
        added, used, aiops_only, doubts,
    )
    REPORT.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT}", file=sys.stderr)

    c = counts_block(accessible, leftover)
    print("COUNTS", json.dumps(c, indent=2))
    print(f"unmatched HF video added: {len(added)}")
    print(f"AIOps not on Graydient: {len(aiops_only)}")
    print(f"HF weights reviewed: {len(hf_weights)}; matched to a catalog row: {len(used) - len(added)}")


if __name__ == "__main__":
    main()
