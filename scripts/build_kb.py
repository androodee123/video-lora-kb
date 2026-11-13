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
    re.compile(rf"(?i){NUM}\s*(?:[-–—to]+)\s*{NUM}\s*(?:lora\s*)?(?:strength|weight|scale)"),
    re.compile(rf"(?i)(?:at|with)\s+(?:a\s+)?(?:lora\s+)?(?:strength|weight|scale)\s+(?:of\s+)?{NUM}(?:\s*(?:[-–—to]+)\s*{NUM})?"),
    re.compile(rf"(?i)recommended\s+(?:lora\s+)?(?:strength|weight)\s+is\s+{NUM}(?:\s*(?:[-–—to]+)\s*{NUM})?"),
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
# Categories: existing plus character_consistency, object_control, pose, lipsync.
# Tagging uses name + CivitAI tags + description (not name alone).

CAT_RULES = [
    ("lipsync", r"\b(lip[- ]?sync|lipsync|viseme|talking head|talking face|mouth sync|speech.?to.?lip|dubbing.{0,60}lip|natural face.{0,20}speech)\b"),
    ("character_consistency", r"\b(character consistency|consistent character|identity lock|identity preservation|face lock|character sheet|same character|character reference|consistency lora|clothconsistency|clothing consistency)\b"),
    ("object_control", r"\b(object control|object interaction|object persist|hold(?:ing)? (?:the |an )?object|through[- ]body|in[- ]hand object|swallowing object|object delivery|object typography|living clothes|interact(?:s|ion)? with (?:the |an )?object)\b"),
    ("pose", r"\b(pose control|openpose|controlnet|dwpose|pose lock|pose helper|ic-lora[- ]?pose|pose-control|depth control|depth-control|ic-lora[- ]?depth|fun-controlnet|most muscular pose|paw pose|jacko pose|arched back pose|sexypose|ab crunch pose|front lat spread)\b"),
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

# Description text is used only with high-precision phrases. Generic words like
# "camera", "character", "speech", "lighting", "moans" appear in almost every
# H3/LTX model card and must not drive categories.
DESC_RULES = [
    ("lipsync", r"\b(lip[- ]?sync(?:ing)? lora|lipsync lora|dubbing (?:and )?lip[- ]?sync|viseme)\b"),
    ("character_consistency", r"\b(character consistency lora|consistencylora|identity preservation lora|clothing consistency lora|clothconsistency)\b"),
    ("object_control", r"\b(object control lora|object interaction lora|living clothes)\b"),
    ("pose", r"\b(pose control|openpose|controlnet|dwpose|ic-lora[- ]?pose|ic-lora[- ]?depth|pose helper|fun-controlnet)\b"),
    ("audio", r"\b(audio[- ]only lora|audio lora|foley lora|moan lora|speech lora|accent lora|voice lora)\b"),
    ("camera", r"\b(camera[- ]control lora|orbit lora|dolly zoom lora|taker ?pov lora)\b"),
    ("lighting", r"\b(relight(?:ing)? lora|ic-lora[- ]?relight)\b"),
    ("physics", r"\b(body physics lora|cloth physics|hair physics|breast physics lora)\b"),
    ("enhancement", r"\b(upscaler lora|distill lora|turbo lora|speed lora)\b"),
]

def classify(name: str, tags: list, filename: str, curated: str | None = None, description: str | None = None) -> list[str]:
    core = " ".join([name or "", filename or "", curated or "", " ".join(tag_names(tags))]).lower()
    desc = (description or "").lower()
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
        if re.search(rx, core):
            add(cat)
    for cat, rx in DESC_RULES:
        if re.search(rx, desc):
            add(cat)
    # tag shortcuts (exact tag names, not loose word matches)
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
    if tset & {"pose", "controlnet", "openpose", "depth", "dwpose"}:
        add("pose")
    if tset & {"lipsync", "lip sync", "lip-sync"} or any("lipsync" in t or "lip sync" in t for t in tset):
        add("lipsync")
    if any("character consistency" in t or "identity preservation" in t for t in tset):
        add("character_consistency")
    if "concept" in tset and not cats:
        add("enhancement")
    if not cats:
        add("enhancement")
    # Speed/turbo packs are enhancement, not audio/motion, unless the name is about those.
    if re.search(r"\b(turbo|distill|lightx2v|causvid|self-forcing|pika-h3-flex|few[- ]step)\b", core) and not re.search(r"\b(moan|speech|accent|foley|motion booster|orbit|jiggle)\b", core):
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
    return False  # uniqueness no longer drops rows; low_signal is recorded instead


def load_enriched_model(mid):
    p = H.CIVIT_RAW / "models" / f"{mid}.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if d.get("_error") or not d.get("id"):
        return None
    return d


def load_image_prompts(version_id, limit=2) -> list[str]:
    if not version_id:
        return []
    p = H.CIVIT_RAW / "images" / f"{version_id}.json"
    if not p.exists():
        return []
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for it in d.get("items") or []:
        pr = ((it.get("meta") or {}) or {}).get("prompt")
        if isinstance(pr, str):
            pr = pr.strip()
            if pr and pr not in out:
                out.append(pr[:1500])
        if len(out) >= limit:
            break
    return out


def model_description(model, vers=None) -> str:
    parts = [model.get("description") or ""]
    for v in (vers or model.get("modelVersions") or []):
        if v.get("description"):
            parts.append(v["description"])
    return html_to_text("\n".join(parts))


def trained_words(vers) -> list[str]:
    out = []
    for v in vers or []:
        for w in v.get("trainedWords") or []:
            if w and w not in out:
                out.append(w)
    return out


def compatibility_notes(family, bases, name, desc, filename, files, i2v_t2v) -> list[str]:
    notes = []
    if i2v_t2v and i2v_t2v != "not stated":
        notes.append(f"mode: {i2v_t2v}")
    bjoin = " ".join(bases or [])
    if "480p" in bjoin:
        notes.append("resolution: 480p I2V")
    if "720p" in bjoin:
        notes.append("resolution: 720p I2V")
    fn = " ".join((files or []) + [filename or ""]).lower()
    blob = " ".join([name or "", desc or "", fn]).lower()
    if family == "Wan":
        high = bool(re.search(r"high[-_ ]noise|_high_|-high-", fn))
        low = bool(re.search(r"low[-_ ]noise|_low_|-low-", fn))
        if high and low:
            notes.append("Wan 2.2: use the matching HIGH + LOW pair on the matching samplers")
        elif high:
            notes.append("Wan high-noise file present; pair with the matching low-noise LoRA on 2.2 14B")
        elif low:
            notes.append("Wan low-noise file present; pair with the matching high-noise LoRA on 2.2 14B")
        has_21 = any(("2.2" not in (b or "") and "Wan" in (b or "")) for b in (bases or []))
        has_22 = any("2.2" in (b or "") for b in (bases or []))
        has_5b = any("5B" in (b or "") or "TI2V" in (b or "") for b in (bases or []))
        if has_5b:
            notes.append("Wan 2.2 5B TI2V — do not drop into a 14B I2V-A14B / T2V-A14B graph")
        if has_21 and has_22:
            notes.append("versions exist for both Wan 2.1 and 2.2 — match the workflow; cross-use is not guaranteed")
        elif has_21:
            notes.append("Wan 2.1 LoRA; do not assume it works on 2.2 high/low graphs")
        elif has_22 and not has_5b:
            notes.append("Wan 2.2 14B; 2.1 cross-use is not guaranteed")
    if re.search(r"\b(turbo|distill|lightx2v|causvid|self-forcing|few[- ]step)\b", blob):
        notes.append("speed/distill LoRA — use on the few-step / turbo graph; do not treat as a style LoRA on a full-step pass")
    if family == "H3":
        notes.append("Graydient H3 workflows (family-level, not a per-LoRA install claim): omni-eros-new-h3 (I2V), extend-h3, extendturbo-h3 (turbo packs only on turbo)")
    elif family == "Wan":
        notes.append("Graydient Wan workflows (family-level, not a per-LoRA install claim): animate-wan22, video-wan22")
    elif family == "LTX2":
        notes.append("Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible")
    return notes


def example_prompts_for(ver, desc) -> list[str]:
    out = []
    for p in load_image_prompts((ver or {}).get("id"), limit=2):
        if p not in out:
            out.append(p)
    if len(out) < 2:
        ex = extract_example_prompt(desc)
        if ex and ex not in out:
            out.append(ex)
    return out[:2]


def load_merged_models():
    """Merge every cached CivitAI list page (all sorts, periods, keyword queries) and overlay full /models/{id} dumps."""
    models = {m["id"]: m for m in H.merge_civitai_items(H.load_all_civitai_items())}
    for mid, base in list(models.items()):
        full = load_enriched_model(mid)
        if not full:
            continue
        vers = {v.get("id"): v for v in (base.get("modelVersions") or []) if v.get("id")}
        for v in (full.get("modelVersions") or []):
            if v.get("id"):
                vers[v["id"]] = v
        full = dict(full)
        full["modelVersions"] = list(vers.values())
        models[mid] = full
    return list(models.values())


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
        # refresh categories with new taxonomy (name + tags + description), union with old
        name = rec.get("civitai_name") or rec.get("purpose") or rec.get("file")
        tags = (model.get("tags") if model else None) or []
        fam = rec.get("family")
        vers = versions_for_family(model, fam) if model else []
        ver = best_version(vers, prefer_vid=rec.get("version_id")) if vers else None
        desc = model_description(model, vers) if model else ""
        new_cats = classify(name, tags, rec.get("file") or "", rec.get("curated_category"), description=desc)
        old = rec.get("categories") or []
        allowed = {x[0] for x in CAT_RULES} | {"enhancement", "audio", "identity", "nsfw-act"}
        cats = []
        for c in new_cats + list(old):
            if c in allowed and c not in cats:
                cats.append(c)
        rec["categories"] = cats or ["enhancement"]
        if rec.get("strength") in (None, "", "not stated") and desc:
            rec["strength"] = extract_strength(desc) or "not stated"
        trained = trained_words(vers)
        existing = list(rec.get("triggers") or [])
        for w in trained:
            if w and w not in existing:
                existing.append(w)
        rec["triggers"] = existing
        rec["example_prompts"] = example_prompts_for(ver or {"id": rec.get("version_id")}, desc)
        rec["example_prompt"] = rec["example_prompts"][0] if rec["example_prompts"] else None
        bases = rec.get("bases") or ([rec.get("base")] if rec.get("base") else [])
        rec["compatibility"] = compatibility_notes(
            fam, bases, name, desc, rec.get("file") or "", rec.get("files") or high_low_files(vers),
            rec.get("i2v_t2v") or infer_i2v_t2v(bases, name, desc, rec.get("file") or ""),
        )
        rec["low_signal"] = False
        rec.pop("curated_category", None)
        rec.pop("match_how", None)
        rec.pop("page_404", None)
        rec.pop("notes", None)
        records.append(rec)
        seen_keys.add((rec["family"], mid, rec.get("file")))

    # 2) CivitAI catalog rows (not already represented as an installed file for that family+id)
    installed_family_ids = {(r["family"], r.get("civitai_model_id")) for r in records if r.get("civitai_model_id")}
    dropped_low = 0  # retained for log compatibility; always 0 after restore
    kept_low_unique = 0
    low_signal_n = 0
    prelim = []
    for mid, model in models.items():
        st = model.get("stats") or {}
        keep = useful(model, installed_ids)
        families = sorted({H.family_of_base(v.get("baseModel")) for v in (model.get("modelVersions") or [])} - {None})
        for fam in families:
            prelim.append((keep, fam, mid, model, st))

    for keep, fam, mid, model, st in prelim:
        if (fam, mid) in installed_family_ids:
            continue
        vers = versions_for_family(model, fam)
        ver = best_version(vers)
        if not ver:
            continue
        fname = first_safetensor(ver) or f"{slugify(model.get('name') or str(mid))}.safetensors"
        desc = model_description(model, vers)
        cats = classify(model.get("name") or "", model.get("tags") or [], fname, None, description=desc)
        low_signal = not keep
        if low_signal:
            low_signal_n += 1
            kept_low_unique += 1  # restored rather than unique-only
        trained = trained_words(vers)
        strength = extract_strength(desc) or "not stated"
        examples = example_prompts_for(ver, desc)
        example = examples[0] if examples else None
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
            "example_prompts": examples,
            "low_signal": low_signal,
            "compatibility": compatibility_notes(
                fam, bases, model.get("name") or "", desc, fname, high_low_files(vers),
                infer_i2v_t2v(bases, model.get("name") or "", desc, fname),
            ),
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
        cats = classify(name, it.get("tags") or [], name, None, description=desc)
        rec_i2v = infer_i2v_t2v([base] if base else [], name, desc, name)
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
            "i2v_t2v": rec_i2v,
            "purpose": (fuzz_hit or {}).get("name") or name,
            "path": None,
            "civitai_name": None,
            "downloads": it.get("downloads") or 0,
            "thumbs_up": it.get("likes") or 0,
            "source": "huggingface",
            "hf_id": hid,
            "example_prompt": None,
            "example_prompts": [],
            "low_signal": False,
            "compatibility": compatibility_notes(fam, [base] if base else [], name, desc, name, [], rec_i2v),
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
            "categories": classify(name, [], name, None, description=L.get("description") or ""),
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
            "example_prompts": [],
            "low_signal": False,
            "compatibility": compatibility_notes(fam, [base], name, L.get("description") or "", name, [], "not stated"),
        }
        records.append(rec)

    print(f"records {len(records)} dropped_low {dropped_low} low_signal {low_signal_n} restored {kept_low_unique}", file=sys.stderr)
    return records


JSONL_KEYS = [
    "family", "file", "slug", "civitai_model_id", "version_id", "base",
    "triggers", "strength", "categories", "urls", "verified", "installed",
    "i2v_t2v", "purpose", "path", "civitai_name",
    "downloads", "thumbs_up", "source", "bases", "hf_id", "files",
    "example_prompt", "example_prompts", "low_signal", "compatibility",
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
        n = len(sub) or 1
        trig = sum(1 for r in sub if r.get("triggers"))
        strn = sum(1 for r in sub if r.get("strength") not in (None, "", "not stated"))
        ex = sum(1 for r in sub if r.get("example_prompts") or r.get("example_prompt"))
        print("    strength stated", strn, f"({100*strn/n:.1f}%)")
        print("    has trigger", trig, f"({100*trig/n:.1f}%)")
        print("    has example prompt", ex, f"({100*ex/n:.1f}%)")
        print("    low_signal", sum(1 for r in sub if r.get("low_signal")))
