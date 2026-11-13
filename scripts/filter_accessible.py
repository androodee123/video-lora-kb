#!/usr/bin/env python3
"""Filter the catalog to Graydient-accessible video LoRAs.

A LoRA is on Graydient when a matching weight file exists in any of:
  - Hugging Face Octavian123/civit
  - Hugging Face Octavian123/civit2 (newer ingests)
  - Hugging Face Octavian123/private (included when listable)

aiops/installed remains a secondary flag from the 13 Nov 2026 RAID snapshot
at /Volumes/RAID/Lora/{H3,Wan,LTX2}. RAID files that are not yet in those
HF repos stay in data/loras.jsonl with graydient_status "to add to Graydient"
(or "to add to Graydient (no public source; needs local upload)" when there
is no public CivitAI/HF URL).

The universe rematched each run is data/loras.jsonl plus data/candidates.jsonl.
Matches become available ("on Graydient"). Everything else stays in
data/candidates.jsonl with an ingest_priority score. data/excluded.jsonl is
left untouched except for an explicit drop list (Finder duplicates).

This script never downloads weights. Unmatched HF video files are not
auto-added (that previously inflated the catalog); only existing catalog or
candidate rows are promoted.
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
HF_CACHE_DIR = ROOT / "data" / "raw" / "huggingface"
HF_REPOS = R.HF_REPOS
HF_REPO = HF_REPOS[0]  # backward-compatible alias (civit)
DROP_SLUGS = {"msltx-3fingering-step00005000-comfy-1"}
SLUG_MAP = ROOT / "data" / "graydient_slugs.json"
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
    rel = rel_path(path)
    if rel.startswith("moss/") or path.startswith("moss/"):
        return None
    base = rel.rsplit("/", 1)[-1]
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


def cache_path(repo: str) -> Path:
    return HF_CACHE_DIR / f"octavian123-{repo.split('/')[-1]}-files.txt"


def split_repo_path(path: str) -> tuple[str, str]:
    parts = path.split("/", 2)
    if len(parts) >= 3:
        repo = f"{parts[0]}/{parts[1]}"
        if repo in HF_REPOS:
            return repo, parts[2]
    return "", path


def rel_path(path: str) -> str:
    _, rel = split_repo_path(path)
    return rel


def is_moss(path: str) -> bool:
    rel = rel_path(path)
    return rel.startswith("moss/") or path.startswith("moss/")


def hf_blob_url(repo_rel: str) -> str:
    repo, rel = split_repo_path(repo_rel)
    if repo and rel:
        return f"https://huggingface.co/{repo}/blob/main/{rel}"
    return f"https://huggingface.co/{HF_REPO}/blob/main/{repo_rel}"


def preferred_repo_file(paths: list[str]) -> str | None:
    if not paths:
        return None
    by_repo: dict[str, list[str]] = {}
    for p in paths:
        repo, _rel = split_repo_path(p)
        by_repo.setdefault(repo or "unknown", []).append(p)
    for repo in R.HF_REPO_PREF:
        if by_repo.get(repo):
            return sorted(by_repo[repo])[0]
    return sorted(paths)[0]


def list_hf_files(refresh: bool) -> list[str]:
    """Return repo-prefixed paths (Octavian123/civit2/foo.safetensors). Metadata only."""
    from huggingface_hub import HfApi

    api = None
    all_files: list[str] = []
    HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for repo in HF_REPOS:
        cache = cache_path(repo)
        files = None
        if cache.exists() and not refresh:
            files = [ln.strip() for ln in cache.read_text(encoding="utf-8").splitlines() if ln.strip()]
            print(f"HF file list from cache ({len(files)} paths): {cache}", file=sys.stderr)
        else:
            try:
                if api is None:
                    api = HfApi()
                print(f"listing {repo} via huggingface_hub (metadata only, no weights) ...", file=sys.stderr)
                files = list(api.list_repo_files(repo, repo_type="model"))
                cache.write_text("\n".join(files) + "\n", encoding="utf-8")
                print(f"wrote cache {cache} ({len(files)} paths)", file=sys.stderr)
            except Exception as e:
                print(f"WARNING: could not list {repo}: {type(e).__name__}: {e}", file=sys.stderr)
                if cache.exists():
                    files = [ln.strip() for ln in cache.read_text(encoding="utf-8").splitlines() if ln.strip()]
                    print(f"falling back to cache ({len(files)} paths): {cache}", file=sys.stderr)
                else:
                    files = []
        for f in files or []:
            all_files.append(f"{repo}/{f}")
    combined = HF_CACHE_DIR / "octavian123-graydient-files.txt"
    combined.write_text("\n".join(all_files) + "\n", encoding="utf-8")
    print(f"combined Graydient listing: {len(all_files)} paths across {len(HF_REPOS)} repos", file=sys.stderr)
    return all_files


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
    if is_moss(hf_path) or last_token(hf_slug) in IMAGE_LAST_TOKENS:
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
            if is_moss(path):
                return False
            sl = slugify(path.rsplit("/", 1)[-1])
            if last_token(sl) in IMAGE_LAST_TOKENS:
                return False
            hf_fam = infer_family(path)
            # Exact slug/file/path matches win even when the RAID family and the
            # filename suffix disagree (e.g. an H3 port whose slug still ends in -wan).
            if hf_fam and fam and hf_fam != fam and kind not in {
                "slug", "file", "file_raw", "files", "files_raw", "path",
            }:
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
                        if is_moss(path) or last_token(slugify(path.rsplit("/", 1)[-1])) in IMAGE_LAST_TOKENS:
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
        if is_moss(path):
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
    url = hf_blob_url(path)
    repo, _rel = split_repo_path(path)
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
        "hf_id": repo or HF_REPO,
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
        lab_ord = R.status_rank(r)
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
        on = sum(1 for r in sub if R.is_on_graydient(r))
        to_add = sum(1 for r in sub if R.is_to_add(r))
        a = sum(1 for r in sub if r.get("aiops"))
        out[fam] = {
            "on_graydient": on,
            "to_add": to_add,
            "available": len(sub),
            "candidates": sum(1 for r in cand if r.get("family") == fam),
            "aiops": a,
            # aliases kept for older callers
            "accessible": len(sub),
            "graydient": on,
            "graydient_only": sum(1 for r in sub if R.is_on_graydient(r) and not r.get("aiops")),
            "aiops_only": to_add,
            "both": sum(1 for r in sub if R.is_on_graydient(r) and r.get("aiops")),
        }
    out["ALL"] = {k: sum(out[f][k] for f in ("H3", "Wan", "LTX2")) for k in next(iter(out.values()))}
    return out


def load_slug_map() -> dict[str, str]:
    if not SLUG_MAP.exists():
        return {}
    data = json.loads(SLUG_MAP.read_text(encoding="utf-8"))
    out = {}
    for k, v in (data or {}).items():
        if k and v and k != v:
            out[str(k)] = str(v)
    return out


def load_universe() -> tuple[list[dict], int, list[dict]]:
    """Merge loras.jsonl + candidates.jsonl, dropping Finder duplicates.

    Returns (rows, available_before_merge, dropped_rows).
    """
    acc = load_jsonl(JSONL)
    cand = load_jsonl(CANDIDATES)
    dropped = []
    seen = set()
    rows = []
    for r in acc + cand:
        slug = r.get("slug") or r.get("file") or ""
        if slug in DROP_SLUGS or slugify(slug) in DROP_SLUGS:
            dropped.append(r)
            continue
        # Same CivitAI title can have an H3 version and a Wan version that share a slug.
        # Identity is family + slug + file + version + path, not slug alone.
        key = (
            r.get("family") or "",
            slug,
            r.get("file") or "",
            str(r.get("version_id") or ""),
            r.get("path") or "",
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(r)
    return rows, len(acc), dropped


def stamp_graydient_urls(r: dict, files: list[str], slug_map: dict[str, str]) -> None:
    r["graydient_files"] = sorted(set(files))
    pref = preferred_repo_file(files)
    urls = dict(r.get("urls") or {})
    if pref:
        gd = hf_blob_url(pref)
        urls["graydient_hf"] = gd
        repo, _rel = split_repo_path(pref)
        r["graydient_hf_repo"] = repo or None
        r["hf_id"] = repo or r.get("hf_id")
        # Do not overwrite an upstream public HF page with the Graydient copy.
        if not urls.get("huggingface"):
            urls["huggingface"] = gd
    r["urls"] = urls
    sl = r.get("slug")
    if sl and sl in slug_map:
        r["graydient_slug"] = slug_map[sl]
    elif r.get("graydient_slug") in (None, "", sl):
        # keep an existing distinct slug; otherwise leave unset/same
        pass


def write_ingest_queue(rows: list[dict], now: str) -> None:
    queue = [r for r in rows if R.needs_graydient_ingest(r)]
    md = ROOT / "data" / "graydient_ingest_queue.md"
    txt = ROOT / "data" / "graydient_ingest_queue.txt"
    by_fam = Counter(r.get("family") for r in queue)
    no_src = [r for r in queue if not R.has_source_url(r) or R.graydient_status(r) == R.TO_ADD_NO_SOURCE]
    lines = [
        "# Graydient ingest queue",
        "",
        f"Generated {now}. These **{len(queue)}** LoRAs are on the AIOps RAID "
        f"(`/Volumes/RAID/Lora/{{H3,Wan,LTX2}}`, snapshot 13 Nov 2026) but do not have a matching file in "
        f"Hugging Face `Octavian123/civit`, `Octavian123/civit2`, or `Octavian123/private`. "
        f"They stay in the available set (`data/loras.jsonl`) with `graydient_status` = "
        f"**to add to Graydient (no public source; needs local upload)** when there is no public CivitAI/HF URL. "
        "They need a local RAID upload into the Graydient concept browser — ingest.py cannot fetch them from a URL. "
        "Nothing here is auto-downloaded.",
        "",
        f"Total: **{len(queue)}** (H3 {by_fam.get('H3', 0)}, Wan {by_fam.get('Wan', 0)}, LTX {by_fam.get('LTX2', 0)}). "
        f"No public source URL: {len(no_src)}.",
        "",
        "| family | slug | RAID path | status | source |",
        "|---|---|---|---|---|",
    ]
    fam_ord = {"H3": 0, "Wan": 1, "LTX2": 2}
    for r in sorted(queue, key=lambda x: (fam_ord.get(x.get("family"), 9), x.get("slug") or x.get("file") or "")):
        path = r.get("path") or r.get("file") or ""
        src = "—"
        u = r.get("urls") or {}
        if u.get("civitai"):
            src = f"[source]({u['civitai']})"
        elif u.get("huggingface"):
            src = f"[source]({u['huggingface']})"
        lines.append(
            f"| {r.get('family')} | `{r.get('slug') or r.get('file')}` | `{path}` | "
            f"{R.graydient_status(r)} | {src} |"
        )
    md.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    txt_lines = [
        "# Remaining Graydient ingest items. No public source URL — needs local upload from the RAID path.",
        "# This file is a list, not a download queue. Do not fetch weights automatically.",
    ]
    for r in sorted(queue, key=lambda x: (fam_ord.get(x.get("family"), 9), x.get("slug") or x.get("file") or "")):
        raid = r.get("path") or r.get("file") or r.get("slug")
        txt_lines.append(f"/Volumes/RAID/Lora/{raid}")
    txt.write_text("\n".join(txt_lines).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {md} ({len(queue)}) and {txt}", file=sys.stderr)


def append_excluded(dropped: list[dict], now: str) -> None:
    if not dropped:
        return
    dest = ROOT / "data" / "excluded.jsonl"
    existing = load_jsonl(dest)
    have = {(r.get("slug") or r.get("file")) for r in existing}
    added = 0
    with dest.open("a", encoding="utf-8") as f:
        for r in dropped:
            key = r.get("slug") or r.get("file")
            if key in have:
                continue
            rec = dict(r)
            rec["exclude_reason"] = (
                "Finder duplicate of msltx-3fingering-step00005000-comfy "
                "(identical weights); dropped from the available catalog on 13 Nov 2026."
            )
            rec["excluded_at"] = now
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            added += 1
    if added:
        print(f"appended {added} dropped row(s) to {dest}", file=sys.stderr)


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
    still_to_add: list[dict],
    doubts: list[str],
    promoted: int,
    dropped: list[dict],
    repo_counts: dict[str, int],
) -> str:
    c = counts_block(acc, cand)
    repo_bits = ", ".join(f"`{repo}` {n} paths" for repo, n in repo_counts.items())
    lines = [
        f"# Accessibility report",
        "",
        f"Generated {now}. Source of Graydient access: Hugging Face "
        + ", ".join(f"`{repo}`" for repo in HF_REPOS)
        + f" ({len(hf_files)} combined paths, {len(hf_weights)} weight files, listed via the Hub API — no weights downloaded). "
        f"Per-repo path counts: {repo_bits}. "
        f"Source of RAID presence: `installed=true` / `aiops=true` rows from the 13 Nov 2026 snapshot "
        f"(`/Volumes/RAID/Lora/{{H3,Wan,LTX2}}`).",
        "",
        f"Universe rematched (available + candidates, after dropping Finder duplicates): **{rows_before}**. "
        f"After filter: **{len(acc)}** available, **{len(cand)}** ingest candidates. "
        f"Candidates newly promoted to available because they matched civit / civit2 / private: **{promoted}**. "
        f"Unmatched HF video files auto-added: **{len(unmatched)}** (default is none).",
        "",
        "## Counts",
        "",
        "| Family | on Graydient | still to add | available | candidates |",
        "|---|---:|---:|---:|---:|",
    ]
    for fam, label in (("H3", "MiniMax H3"), ("Wan", "Wan"), ("LTX2", "LTX"), ("ALL", "**Total**")):
        x = c[fam]
        lines.append(
            f"| {label} | {x['on_graydient']} | {x['to_add']} | {x['available']} | {x['candidates']} |"
        )
    lines += [
        "",
        f"HF weight files reviewed: **{len(hf_weights)}**. HF weight files matched to a catalog or candidate row: "
        f"**{len(used_files)}**.",
        "",
        "## Still to add to Graydient",
        "",
        f"{len(still_to_add)} installed RAID video LoRAs have no matching file in "
        + ", ".join(f"`{repo}`" for repo in HF_REPOS)
        + ". They stay in `data/loras.jsonl` labelled "
        f"`{R.TO_ADD_NO_SOURCE}` when they have no public source URL (local upload required). "
        "See `data/graydient_ingest_queue.md`.",
        "",
    ]
    if still_to_add:
        lines += [
            "| family | slug / file | RAID path | status |",
            "|---|---|---|---|",
        ]
        for r in still_to_add:
            lines.append(
                f"| {r.get('family')} | `{r.get('slug') or r.get('file')}` | "
                f"`{r.get('path') or r.get('file') or '—'}` | {R.graydient_status(r)} |"
            )
        lines.append("")
    if dropped:
        lines += [
            "## Dropped from the catalog",
            "",
            f"{len(dropped)} Finder-duplicate row(s) were removed from the available set and appended to "
            "`data/excluded.jsonl`.",
            "",
        ]
        for r in dropped:
            lines.append(f"- `{r.get('slug') or r.get('file')}` (`{r.get('path') or r.get('file')}`)")
        lines.append("")
    lines += [
        "## Unmatched Hugging Face video files added",
        "",
        f"{len(unmatched)} unmatched HF video files were added as new available rows. "
        "The default is to not auto-add unmatched HF files (that previously inflated the catalog). "
        "Use `--add-unmatched` to include them.",
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
    ap = argparse.ArgumentParser(description="Filter catalog to Graydient-accessible video LoRAs.")
    ap.add_argument("--refresh-hf", action="store_true", help="re-list civit, civit2, and private instead of using the cache")
    ap.add_argument("--add-unmatched", action="store_true", help="also add unmatched HF video files as new available rows")
    args = ap.parse_args()

    now = datetime.now(TZ).strftime("%-d %b %Y, %H:%M") + " Africa/Johannesburg (SAST)"
    rows, acc_before, dropped = load_universe()
    if not rows:
        sys.exit(f"missing catalog {JSONL}")
    slug_map = load_slug_map()
    append_excluded(dropped, now)
    if dropped:
        print(f"dropped {len(dropped)} Finder-duplicate row(s): "
              + ", ".join((r.get("slug") or r.get("file") or "?") for r in dropped), file=sys.stderr)

    # How many current candidates will be promoted?
    cand_slugs = {r.get("slug") or r.get("file") for r in load_jsonl(CANDIDATES)}

    hf_files = list_hf_files(refresh=args.refresh_hf)
    repo_counts: dict[str, int] = Counter()
    for path in hf_files:
        repo, _rel = split_repo_path(path)
        repo_counts[repo or "unknown"] += 1
    matches, hf_weights, _by_slug = match_rows(rows, hf_files)

    used: set[str] = set()
    for bag in matches.values():
        for _, path in bag:
            used.add(path)

    accessible = []
    leftover = []
    promoted = 0
    for i, r in enumerate(rows):
        r = dict(r)
        r["aiops"] = bool(r.get("installed") or r.get("aiops"))
        was_candidate = (r.get("slug") or r.get("file")) in cand_slugs and not (
            r.get("graydient") or r.get("aiops") or r.get("installed") or R.is_on_graydient(r) or R.is_to_add(r)
        )
        if i in matches:
            r["graydient"] = True
            r["graydient_status"] = R.ON_GRAYDIENT
            stamp_graydient_urls(r, [p for _, p in matches[i]], slug_map)
            if was_candidate:
                promoted += 1
        else:
            r["graydient"] = False
            r["graydient_files"] = []
            if r["aiops"]:
                r["graydient_status"] = R.TO_ADD_NO_SOURCE if not R.has_source_url(r) else R.TO_ADD
            else:
                r["graydient_status"] = "candidate"
                r.pop("graydient_hf_repo", None)
        if r["graydient"] or r["aiops"]:
            accessible.append(r)
        else:
            leftover.append(r)

    unmatched: list[tuple[str, str]] = []
    added: list[tuple[str, str]] = []
    doubts: list[str] = []
    if args.add_unmatched:
        unmatched = unmatched_video_files(hf_weights, used)
        exist_slugs = {slugify(r.get("slug") or "") for r in accessible}
        exist_slugs |= {slugify(stem(r.get("file") or "")) for r in accessible}
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
                f"on an accessible row: "
                + ", ".join(f"`{p}`" for p, _, _ in skipped_dup[:12])
                + ("…" if len(skipped_dup) > 12 else "")
            )
        unmatched = added
    else:
        doubts.append(
            "Unmatched HF video files were not auto-added in this run. "
            "Only existing catalog and candidate rows can be promoted. Pass --add-unmatched to include them."
        )

    doubts.append(
        "moss/ and *-moss.safetensors were treated as image (KroMoss / Krea) unless an exact catalog video-row "
        "match already used the file."
    )
    doubts.append(
        "Official Hugging Face packs (lightx2v, Lightricks IC-LoRAs, etc.) stay in candidates.jsonl unless the "
        "same weights were also uploaded to Octavian123/civit, Octavian123/civit2, or Octavian123/private, "
        "or are on the RAID. They are scored high for ingest because they fill utility gaps, but they are not "
        "treated as already accessible."
    )
    doubts.append(
        "Version forks (e.g. `…-v2-h3` on RAID vs `…-h3` on Graydient) are not merged. Each slug is its own row. "
        "When Graydient registered a concept under a distinct slug (for example `minimax-h3-t2v-i2v-doublefuck-h3-v2`), "
        "that name is stored in `graydient_slug` on the catalog row."
    )
    doubts.append(
        "Exact slug/file matches are kept even when the RAID family and the filename suffix disagree "
        "(H3 ports whose slugs still end in `-wan`)."
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
    write_ingest_queue(accessible, now)

    still_to_add = [r for r in accessible if R.needs_graydient_ingest(r)]
    report = render_report(
        now, hf_files, hf_weights, accessible, leftover, matches, len(rows),
        added, used, still_to_add, doubts, promoted, dropped, dict(repo_counts),
    )
    REPORT.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT}", file=sys.stderr)

    c = counts_block(accessible, leftover)
    print("COUNTS", json.dumps(c, indent=2))
    print(f"candidates promoted to available: {promoted}")
    print(f"unmatched HF video added: {len(added)}")
    print(f"still to add to Graydient: {len(still_to_add)}")
    print(f"HF weights reviewed: {len(hf_weights)}; matched to a catalog row: {len(used) - len(added)}")



if __name__ == "__main__":
    main()
