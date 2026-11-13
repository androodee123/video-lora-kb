#!/usr/bin/env python3
"""Build data/loras.jsonl and family markdown from harvest + installed inventory.

Metadata only. Never invents strengths or triggers. Never downloads weights.
"""
from __future__ import annotations

import html as htmllib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest as H

ROOT = H.ROOT
TZ = ZoneInfo("Africa/Johannesburg")

# ---- text / extraction ----

def slugify(s: str) -> str:
    s = (s or "").lower().replace(".safetensors", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

def html_to_text(s: str) -> str:
    if not s:
        return ""
    s = htmllib.unescape(s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|h[1-6]|li)>", "\n", s)
    s = re.sub(r"(?i)<li[^>]*>", "- ", s)
    s = re.sub(r"(?i)<h[1-6][^>]*>", "\n", s)
    s = re.sub(r"(?i)<pre[^>]*>", "\n```\n", s)
    s = re.sub(r"(?i)</pre>", "\n```\n", s)
    s = re.sub(r"(?i)<code[^>]*>", "`", s)
    s = re.sub(r"(?i)</code>", "`", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n[ \t]+", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

NUM = r"(0?\.\d+|1(?:\.0+)?)"
STRENGTH_RES = [
    re.compile(rf"(?i)(?:lora\s*)?(?:strength|weight|scale)\s*(?:of\s*)?(?:[:：=\-]|is)?\s*{NUM}\s*(?:[-–—to]+)\s*{NUM}"),
    re.compile(rf"(?i)(?:recommended|suggest(?:ed)?|use(?:d)?(?: at)?|start(?:ing)?(?: at)?|try)\s+(?:a\s+)?(?:lora\s*)?(?:strength|weight|scale)\s*(?:of\s*)?(?:[:：=])?\s*{NUM}(?:\s*(?:[-–—to]+)\s*{NUM})?"),
    re.compile(rf"(?i)(?:lora\s*)?(?:strength|weight)\s*[:：=]\s*{NUM}(?:\s*(?:[-–—to]+)\s*{NUM})?"),
]

def extract_strength(text: str) -> str | None:
    if not text:
        return None
    out = []
    for rx in STRENGTH_RES:
        for m in rx.finditer(text):
            a, b = m.group(1), m.group(2) if m.lastindex and m.lastindex >= 2 else None
            hit = f"{a}–{b}" if b else a
            if hit not in out:
                out.append(hit)
    if not out:
        return None
    return out[0] if len(out) == 1 else "; ".join(out[:3])

def extract_example_prompt(text: str) -> str | None:
    if not text:
        return None
    blocks = re.findall(r"```(?:\w+)?\n(.*?)```", text, re.S)
    for b in blocks:
        b = b.strip()
        if len(b) > 20 and not re.match(r"(?i)^(pip |python |git |cd )", b):
            return b[:1500]
    m = re.search(
        r"(?is)(?:example prompt|example:|prompt example|sample prompt)\s*[:\-]?\s*(.{20,800})",
        text,
    )
    if m:
        cand = re.sub(r"\s+", " ", m.group(1).strip().split("\n\n")[0].strip())
        if len(cand) > 20:
            return cand[:1500]
    return None

def infer_i2v_t2v(bases: list[str], name: str, desc: str, filename: str) -> str:
    blob = " ".join([*(bases or []), name or "", desc or "", filename or ""]).lower()
    has_i2v = bool(re.search(r"\bi2v\b|image[\s-]?to[\s-]?video|ref2va|fl2va|ti2v", blob))
    has_t2v = bool(re.search(r"\bt2v\b|text[\s-]?to[\s-]?video|t2va", blob))
    if any("ti2v" in (b or "").lower() for b in (bases or [])):
        if has_i2v or has_t2v:
            return "TI2V (and " + ("I2V" if has_i2v else "") + ("/T2V" if has_t2v else "") + ")"
        return "TI2V"
    if has_i2v and has_t2v:
        return "I2V and T2V"
    if has_i2v:
        return "I2V"
    if has_t2v:
        return "T2V"
    bjoin = " ".join(bases or []).lower()
    if "i2v" in bjoin and "t2v" in bjoin:
        return "I2V and T2V"
    if "i2v" in bjoin:
        return "I2V"
    if "t2v" in bjoin and "ti2v" not in bjoin:
        return "T2V"
    return "not stated"

# ---- classification ----
# Categories requested: motion, camera, style, enhancement/quality/speed,
# audio/voice, identity/character, effects/VFX, transitions, lighting,
# physics/cloth/hair, NSFW acts, anime/2D, realism.

CAT_RULES = [
    ("audio", r"\b(audio[- ]only|audio lora|moans?|speech|voices?|accents?|whisper|breathy|jpnmoans|jav moans|foley|soundscape|dialogue lora)\b"),
    ("transitions", r"\b(transition|morph cut|scene change|wipe|dissolve|day[- ]to[- ]night|first[- ]last)\b"),
    ("lighting", r"\b(lighting|relight|relighting|teal orange|cinematic color|neon glow|caustic|god rays|volumetric light)\b"),
    ("camera", r"\b(orbit|orb360|cardspin|camera|pov|drone|zoom|fisheye|dolly|jib|tracking shot|crash zoom|locked stabilization|taker ?pov|vertigo|dollyzoom|smartphone snapshot)\b"),
    ("physics", r"\b(physics|cloth|hair sim|hair movement|jiggle|bounce|fluid motion|breast physics|boob physics|softbreast|body physics)\b"),
    ("motion", r"\b(motion|shake harder|motion repair|motion.?speed|continuity|thrust|walk cycle|crash zoom|smooth slow|grinding|sexthrust|sexy.?move|action lora|better motion)\b"),
    ("effects", r"\b(vfx|visual effect|\beffects?\b|explosion|particles|magic fx|growth effect|morph|caustics|glitch|slow motion control|cinemagraph|water simulation)\b"),
    ("enhancement", r"\b(slider|turbo|distill|accelerat|lightx2v|causvid|self-forcing|quality|detailer|enhancer|upscaler|restore|refine|pdd|few[- ]step|4[- ]step|8[- ]step|reward lora)\b"),
    ("realism", r"\b(realism|realistic|photoreal|digicam|d1g1cam|live[- ]action|smartphone snapshot|authentic cinematic)\b"),
    ("anime", r"\b(anime|2d anime|2[- ]d|manga|vtuber|waifu|flat style|animeflat|toon)\b"),
    ("style", r"\b(style|cinematic|claymation|pixar|disney|crayon|ink wash|analog print|western movie|cyberpunk)\b"),
    ("identity", r"\b(character swap|identity|character lora|\bcharacter\b|celeb|vtuber)\b"),
    ("nsfw-act", r"\b(nsfw|sex\b|blowjob|dildo|anal|oral|cumshot|\bcum\b|futa|paizuri|titfuck|masturbat|handjob|footjob|penetration|orgasm|pussy|penis|cowgirl|doggy|missionary|bukkake|creampie|fingering|fisting|twerk|nude|nudity|porn)\b"),
]

def tag_names(tags) -> list[str]:
    out = []
    for t in tags or []:
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, dict) and t.get("name"):
            out.append(t["name"])
    return out

def classify(name: str, tags: list, filename: str, curated: str | None = None) -> list[str]:
    blob = " ".join([name or "", filename or "", curated or "", " ".join(tag_names(tags))]).lower()
    cats = []
    def add(c):
        if c not in cats:
            cats.append(c)
    # curated H3 groups
    if curated:
        cmap = {
            "Motion / camera / realism": ["motion", "camera", "realism"],
            "Audio / voice": ["audio"],
            "Futa / penis / condom-stroke helpers": ["nsfw-act"],
            "Breasts / body": ["physics", "enhancement"],
            "Cum / finish": ["nsfw-act"],
            "Masturbation / stroking": ["nsfw-act"],
        }
        for c in cmap.get(curated, []):
            add(c)
    for cat, rx in CAT_RULES:
        if re.search(rx, blob):
            add(cat)
    # tag shortcuts
    tset = {t.lower() for t in tag_names(tags)}
    if "character" in tset:
        add("identity")
    if "style" in tset:
        add("style")
    if "anime" in tset:
        add("anime")
    if "realistic" in tset or "realism" in tset:
        add("realism")
    if "effect" in tset:
        add("effects")
    if "concept" in tset and not cats:
        add("enhancement")
    if not cats:
        add("enhancement")
    # Speed/turbo packs are enhancement, not audio/motion, unless the name is about those.
    if re.search(r"\b(turbo|distill|lightx2v|causvid|self-forcing|pika-h3-flex|few[- ]step)\b", blob) and not re.search(r"\b(moan|speech|accent|foley|motion booster|orbit|jiggle)\b", blob):
        cats = [c for c in cats if c not in ("audio", "motion")]
        add("enhancement")
    return cats

def versions_for_family(model, family: str):
    out = []
    for v in model.get("modelVersions") or []:
        if H.family_of_base(v.get("baseModel")) == family:
            out.append(v)
    return out

def best_version(vers, prefer_vid=None):
    if prefer_vid:
        for v in vers:
            if v.get("id") == prefer_vid:
                return v
    def score(v):
        st = v.get("stats") or {}
        return (st.get("downloadCount") or 0, st.get("thumbsUpCount") or 0)
    return max(vers, key=score) if vers else None

def first_safetensor(v) -> str | None:
    if not v:
        return None
    for f in v.get("files") or []:
        n = f.get("name") or ""
        if n.lower().endswith(".safetensors"):
            return n
    return None

def high_low_files(vers) -> list[str]:
    names = []
    for v in vers or []:
        for f in v.get("files") or []:
            n = f.get("name") or ""
            if n.lower().endswith(".safetensors") and n not in names:
                names.append(n)
    return names

def useful(model, installed_ids: set) -> bool:
    if model["id"] in installed_ids:
        return True
    st = model.get("stats") or {}
    dl = st.get("downloadCount") or 0
    th = st.get("thumbsUpCount") or 0
    if dl >= 100 or th >= 1:
        return True
    return False  # uniqueness applied later if needed


def load_merged_models():
    items = []
    for sort in ("newest", "downloads", "rated"):
        items.extend(H.load_cached_sort(sort))
    return H.merge_civitai_items(items)


def load_installed():
    p = ROOT / "data" / "loras.jsonl"
    recs = []
    if p.exists():
        # if we already expanded, prefer a backup of the original installed set
        pass
    inst_path = Path("/tmp/vlora-work/records.json")
    if inst_path.exists():
        recs = json.loads(inst_path.read_text())
    elif p.exists():
        recs = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        recs = [r for r in recs if r.get("installed") or r.get("path", "").startswith("(not in")]
    return recs


def load_hf():
    p = H.HF_RAW / "index.json"
    if not p.exists():
        return []
    return json.loads(p.read_text())


def load_fuzz():
    p = Path("/tmp/vlora-work/fuzzpuppy.json")
    if p.exists():
        return json.loads(p.read_text())
    return []


def compile_records():
    models = {m["id"]: m for m in load_merged_models()}
    installed = load_installed()
    hf = load_hf()
    fuzz = load_fuzz()
    installed_ids = {r.get("civitai_model_id") for r in installed if r.get("civitai_model_id")}

    records = []
    seen_keys = set()  # (family, civitai_model_id, file) for installed uniqueness

    # 1) Installed / curated rows first — keep RAID filenames and sidecar triggers
    for r in installed:
        mid = r.get("civitai_model_id")
        model = models.get(mid) if mid else None
        st = (model.get("stats") if model else None) or {}
        rec = dict(r)
        rec["downloads"] = st.get("downloadCount")
        rec["thumbs_up"] = st.get("thumbsUpCount")
        rec["source"] = rec.get("source") or ("civitai" if mid else ("local" if "b7_test1" in (r.get("file") or "") else "inventory"))
        # refresh categories with new taxonomy, union with old
        name = rec.get("civitai_name") or rec.get("purpose") or rec.get("file")
        tags = (model.get("tags") if model else None) or []
        new_cats = classify(name, tags, rec.get("file") or "", rec.get("curated_category"))
        old = rec.get("categories") or []
        # map old enhancement-only leftovers; union
        cats = []
        for c in new_cats + list(old):
            if c == "nsfw-act" or c in {x[0] for x in CAT_RULES} or c in ("enhancement", "audio", "identity"):
                if c not in cats:
                    cats.append(c)
        rec["categories"] = cats or ["enhancement"]
        rec.pop("curated_category", None)
        rec.pop("match_how", None)
        rec.pop("page_404", None)
        rec.pop("notes", None)
        records.append(rec)
        seen_keys.add((rec["family"], mid, rec.get("file")))

    # 2) CivitAI catalog rows (not already represented as an installed file for that family+id)
    installed_family_ids = {(r["family"], r.get("civitai_model_id")) for r in records if r.get("civitai_model_id")}
    dropped_low = 0
    kept_low_unique = 0
    # precompute category occupancy among useful models for uniqueness
    prelim = []
    for mid, model in models.items():
        st = model.get("stats") or {}
        keep = useful(model, installed_ids)
        families = sorted({H.family_of_base(v.get("baseModel")) for v in (model.get("modelVersions") or [])} - {None})
        for fam in families:
            prelim.append((keep, fam, mid, model, st))

    # uniqueness: low-value models whose category would otherwise be empty in that family
    useful_cats = defaultdict(set)
    for keep, fam, mid, model, st in prelim:
        if keep:
            cats = classify(model.get("name") or "", model.get("tags") or [], "", None)
            for c in cats:
                useful_cats[fam].add(c)

    for keep, fam, mid, model, st in prelim:
        if (fam, mid) in installed_family_ids:
            continue
        cats = classify(model.get("name") or "", model.get("tags") or [], first_safetensor(best_version(versions_for_family(model, fam))) or "", None)
        if not keep:
            # keep if it introduces a category that family doesn't have yet among useful
            if any(c not in useful_cats[fam] for c in cats):
                keep = True
                kept_low_unique += 1
            else:
                dropped_low += 1
                continue
        vers = versions_for_family(model, fam)
        ver = best_version(vers)
        if not ver:
            continue
        desc = html_to_text((model.get("description") or "") + "\n" + (ver.get("description") or ""))
        trained = list(ver.get("trainedWords") or [])
        # also union trained words from other family versions
        for v in vers:
            for w in v.get("trainedWords") or []:
                if w and w not in trained:
                    trained.append(w)
        strength = extract_strength(desc) or "not stated"
        example = extract_example_prompt(desc)
        fname = first_safetensor(ver) or f"{slugify(model.get('name') or str(mid))}.safetensors"
        bases = sorted({v.get("baseModel") for v in vers if v.get("baseModel")})
        rec = {
            "family": fam,
            "file": fname,
            "slug": slugify(model.get("name") or fname),
            "civitai_model_id": mid,
            "version_id": ver.get("id"),
            "base": ver.get("baseModel") or (bases[0] if bases else None),
            "bases": bases,
            "triggers": trained,
            "strength": strength,
            "categories": cats,
            "urls": {"civitai": f"https://civitai.com/models/{mid}?modelVersionId={ver.get('id')}"},
            "verified": True,
            "installed": False,
            "i2v_t2v": infer_i2v_t2v(bases, model.get("name") or "", desc, fname),
            "purpose": (model.get("name") or fname).split("|")[0].strip()[:160],
            "path": None,
            "civitai_name": model.get("name"),
            "downloads": st.get("downloadCount") or 0,
            "thumbs_up": st.get("thumbsUpCount") or 0,
            "source": "civitai",
            "files": high_low_files(vers)[:12],
            "example_prompt": example,
        }
        records.append(rec)

    # 3) Hugging Face official / community (skip if already linked by name+family and installed)
    hf_urls = { (r.get("urls") or {}).get("huggingface") for r in records }
    fuzz_by_url = { (x.get("url") or "").rstrip("/"): x for x in fuzz }
    for it in hf:
        hid = it.get("id")
        url = f"https://huggingface.co/{hid}"
        if url in hf_urls:
            continue
        ident = (hid or "") + " " + " ".join(it.get("tags") or [])
        # family
        fam = None
        base = None
        low = ident.lower()
        if "minimax" in low or "h3" in low or "pika-h3" in low:
            fam, base = "H3", "MiniMax H3"
        elif "ltx" in low:
            fam = "LTX2"
            if "2.5" in low:
                base = "LTXV 2.5"
            elif "2.3" in low:
                base = "LTXV 2.3"
            elif re.search(r"ltx-2[^-.]|ltx-2$", low) or "ltx-2-19" in low:
                base = "LTXV2"
            else:
                base = "LTXV"
        elif "wan" in low or "lightx2v" in low or "causvid" in low or "self-forcing" in low:
            fam = "Wan"
            if "2.2" in low and "5b" in low:
                base = "Wan Video 2.2 TI2V-5B"
            elif "2.2" in low and "i2v" in low:
                base = "Wan Video 2.2 I2V-A14B"
            elif "2.2" in low and "t2v" in low:
                base = "Wan Video 2.2 T2V-A14B"
            elif "2.2" in low:
                base = "Wan Video 2.2 I2V-A14B"
            elif "720" in low:
                base = "Wan Video 14B i2v 720p"
            elif "480" in low:
                base = "Wan Video 14B i2v 480p"
            else:
                base = "Wan Video"
        else:
            continue
        # skip if this HF repo is clearly an image model that slipped through
        name = hid.split("/")[-1]
        fuzz_hit = fuzz_by_url.get(url) or fuzz_by_url.get(url + "/")
        desc = (fuzz_hit or {}).get("description") or ""
        cats = classify(name + " " + desc, it.get("tags") or [], name, None)
        rec = {
            "family": fam,
            "file": name,
            "slug": slugify(name),
            "civitai_model_id": None,
            "version_id": None,
            "base": base,
            "bases": [base] if base else [],
            "triggers": [],
            "strength": "not stated",
            "categories": cats,
            "urls": {"huggingface": url},
            "verified": True,
            "installed": False,
            "i2v_t2v": infer_i2v_t2v([base] if base else [], name, desc, name),
            "purpose": (fuzz_hit or {}).get("name") or name,
            "path": None,
            "civitai_name": None,
            "downloads": it.get("downloads") or 0,
            "thumbs_up": it.get("likes") or 0,
            "source": "huggingface",
            "hf_id": hid,
            "example_prompt": None,
        }
        if fuzz_hit and fuzz_hit.get("tutorial"):
            rec["urls"]["tutorial"] = fuzz_hit["tutorial"]
        records.append(rec)

    # fuzzpuppy entries not already in HF or civitai
    have_hf = { (r.get("urls") or {}).get("huggingface") for r in records }
    for L in fuzz:
        url = (L.get("url") or "").rstrip("/")
        if not url or url in have_hf or (url + "/") in have_hf:
            continue
        name = L.get("name") or url
        bm = L.get("baseModel") or ""
        if "MiniMax" in bm or "H3" in bm:
            fam, base = "H3", "MiniMax H3"
        elif "Wan" in bm:
            fam, base = "Wan", "Wan Video 2.2 I2V-A14B"
        elif "2.5" in bm:
            fam, base = "LTX2", "LTXV 2.5"
        elif "2.3" in bm:
            fam, base = "LTX2", "LTXV 2.3"
        else:
            fam, base = "LTX2", "LTXV2"
        rec = {
            "family": fam,
            "file": slugify(name),
            "slug": slugify(name),
            "civitai_model_id": None,
            "version_id": None,
            "base": base,
            "bases": [base],
            "triggers": [],
            "strength": "not stated",
            "categories": classify(name + " " + (L.get("description") or ""), [], name, None),
            "urls": {"huggingface": url} if "huggingface.co" in url else {"source": url},
            "verified": True,
            "installed": False,
            "i2v_t2v": "not stated",
            "purpose": (L.get("description") or name)[:160],
            "path": None,
            "civitai_name": None,
            "downloads": None,
            "thumbs_up": None,
            "source": "fuzzpuppy",
            "example_prompt": None,
        }
        records.append(rec)

    print(f"records {len(records)} dropped_low {dropped_low} kept_low_unique {kept_low_unique}", file=sys.stderr)
    return records


JSONL_KEYS = [
    "family", "file", "slug", "civitai_model_id", "version_id", "base",
    "triggers", "strength", "categories", "urls", "verified", "installed",
    "i2v_t2v", "purpose", "path", "civitai_name",
    "downloads", "thumbs_up", "source", "bases", "hf_id", "files",
]


def write_jsonl(records, path: Path):
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            obj = {k: r.get(k) for k in JSONL_KEYS}
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    recs = compile_records()
    out = ROOT / "data" / "loras.jsonl"
    write_jsonl(recs, out)
    # also dump a rich sidecar for the renderer (includes example prompts)
    rich = ROOT / "data" / ".records-rich.json"
    # keep example_prompt in rich only (jsonl is slimmer but we included most fields)
    Path("/tmp/vlora-work/records-full.json").write_text(json.dumps(recs, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print("total", len(recs))
    for fam in ("H3", "Wan", "LTX2"):
        sub = [r for r in recs if r["family"] == fam]
        inst = [r for r in sub if r.get("installed")]
        print(f"  {fam}: {len(sub)} installed={len(inst)} verified={sum(1 for r in sub if r.get('verified'))}")
        print("    cats", Counter(c for r in sub for c in (r.get("categories") or [])))
        print("    strength stated", sum(1 for r in sub if r.get("strength") not in (None, "not stated")))
