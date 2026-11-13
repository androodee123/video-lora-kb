"""Shared accessibility and ingest-suggestion rules for the video LoRA KB.

Accessible = on Graydient (a matching file in Hugging Face Octavian123/civit)
OR on AIOps (installed=true, RAID snapshot /Volumes/RAID/Lora/{H3,Wan,LTX2}).

Suggestions never download or ingest weights. They only point at a CivitAI or
Hugging Face page so a person can run civit-to-graydient if they want the LoRA.
"""
from __future__ import annotations

import math
import re

# --- Suggest-ingest thresholds (documented in SKILL.md) ---
# A candidate is suggested when any of these hold:
#   1. Gap fill: the family+category (or recipe goal) has no accessible LoRA,
#      and the candidate has a source URL. Offer the top MAX_SUGGEST by score.
#   2. High-value upgrade: downloads >= SUGGEST_MIN_DOWNLOADS AND
#      downloads >= SUGGEST_RATIO × the top accessible LoRA in that same
#      family+category (or  the candidate is an official utility pack with
#      no accessible equivalent — LightX2V, Lightricks IC-LoRA, CausVid).
#   3. Hard cap: at most MAX_SUGGEST items per category page or recipe.
SUGGEST_MIN_DOWNLOADS = 2000
SUGGEST_RATIO = 2.0
MAX_SUGGEST_PER_CATEGORY = 3
MAX_SUGGEST_PER_RECIPE = 3

OFFICIAL_UTIL_RE = re.compile(
    r"lightx2v|lightricks|causvid|ic-lora|ic_lora|self-forcing|distill-lora",
    re.I,
)


def access_label(row: dict) -> str:
    g = bool(row.get("graydient"))
    a = bool(row.get("aiops") or row.get("installed"))
    if g and a:
        return "both"
    if g:
        return "Graydient"
    if a:
        return "AIOps"
    return "candidate"


def access_label_pretty(row: dict) -> str:
    lab = access_label(row)
    return {
        "both": "Graydient+AIOps",
        "Graydient": "Graydient",
        "AIOps": "AIOps",
        "candidate": "candidate",
    }[lab]


def _num(v, default=0):
    try:
        if v is None or v == "":
            return default
        return int(v)
    except (TypeError, ValueError):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default


def ingest_priority(row: dict, accessible_by_fam_cat: dict[tuple[str, str], int] | None = None) -> float:
    """Rank ingest candidates. Higher is more useful to ingest first.

    score =
        25 * log10(downloads + 1)
      + 20 * log10(thumbs_up + 1)
      + 10 if a trigger is recorded
      +  8 if a strength is stated
      +  6 if an example prompt is recorded
      +  4 if verified
      - 20 if low_signal
      + 25 if every listed category for this family has 0 accessible LoRAs
      + 10 if a listed category has fewer than 3 accessible LoRAs
           (the larger of these two gap bonuses is used)
      + 15 if the name/repo looks like an official utility pack
           (LightX2V, Lightricks IC-LoRA, CausVid, distill)
    """
    downloads = _num(row.get("downloads"))
    thumbs = _num(row.get("thumbs_up"))
    score = math.log10(downloads + 1) * 25 + math.log10(thumbs + 1) * 20
    if row.get("triggers"):
        score += 10
    if row.get("strength") not in (None, "", "not stated"):
        score += 8
    if row.get("example_prompt") or row.get("example_prompts"):
        score += 6
    if row.get("verified"):
        score += 4
    if row.get("low_signal"):
        score -= 20
    if accessible_by_fam_cat:
        fam = row.get("family")
        gap = 0
        for cat in row.get("categories") or ["enhancement"]:
            n = accessible_by_fam_cat.get((fam, cat), 0)
            if n == 0:
                gap = max(gap, 25)
            elif n < 3:
                gap = max(gap, 10)
        score += gap
    blob = " ".join(
        str(row.get(k) or "")
        for k in ("slug", "file", "purpose", "hf_id", "civitai_name")
    )
    if OFFICIAL_UTIL_RE.search(blob):
        score += 15
    return round(score, 2)


def is_official_util(row: dict) -> bool:
    blob = " ".join(
        str(row.get(k) or "")
        for k in ("slug", "file", "purpose", "hf_id", "civitai_name")
    )
    return bool(OFFICIAL_UTIL_RE.search(blob))


def has_source_url(row: dict) -> bool:
    u = row.get("urls") or {}
    return bool(u.get("civitai") or u.get("huggingface") or u.get("civitai_skeleton") or row.get("hf_id"))


def should_suggest(
    candidate: dict,
    *,
    accessible_rows: list[dict],
    gap: bool,
    max_accessible_downloads: int = 0,
) -> bool:
    """Return True if this candidate meets the documented suggest-ingest rule."""
    if not has_source_url(candidate):
        return False
    if gap:
        return True
    dl = _num(candidate.get("downloads"))
    if dl >= SUGGEST_MIN_DOWNLOADS and dl >= SUGGEST_RATIO * max(max_accessible_downloads, 1):
        return True
    if is_official_util(candidate) and not any(is_official_util(r) for r in accessible_rows):
        return True
    return False


def pick_suggestions(
    candidates: list[dict],
    accessible_rows: list[dict],
    *,
    limit: int = MAX_SUGGEST_PER_CATEGORY,
) -> list[dict]:
    """Filter and rank candidates for a category or recipe."""
    gap = len(accessible_rows) == 0
    max_dl = max((_num(r.get("downloads")) for r in accessible_rows), default=0)
    picked = [c for c in candidates if should_suggest(
        c, accessible_rows=accessible_rows, gap=gap, max_accessible_downloads=max_dl
    )]
    picked.sort(key=lambda r: (-(r.get("ingest_priority") or 0), -(_num(r.get("downloads"))), r.get("slug") or r.get("file") or ""))
    return picked[:limit]
