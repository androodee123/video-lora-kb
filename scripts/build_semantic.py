#!/usr/bin/env python3
"""Build data/semantic_catalog.jsonl: every LoRA we have on Graydient (plus HF/RAID-only ones, flagged) with
semantic tags for prompt matching. Identical script in image-lora-kb and video-lora-kb (repo kind auto-detected).

Inputs (all metadata, committed or rebuilt weekly; nothing is downloaded):
  data/loras.jsonl                     KB catalog (HF Octavian123 listing + CivitAI hash lookups)
  data/local/aiops_graydient.jsonl.gz  sanitized AIOps LoRA library snapshot (creator, CivitAI URL, tags, RAID flag)
  data/local/ingest_plans.jsonl.gz     sanitized civit-to-graydient plan.json snapshot (ingest dates, triggers, descriptions)
  data/local/safety_skips.json         CivitAI model/version ids skipped for safety by the ingest reviews
  data/excluded.jsonl                  KB exclusions
Refresh the data/local snapshots with scripts/export_local_meta.py on the home Mac (see UPDATING.md).

Output: data/semantic_catalog.jsonl (one compact row per Graydient slug) + data/semantic_summary.md.
Never invents triggers or strengths: `triggers` is empty when no source states one (`no_trigger: true`).
"""
from __future__ import annotations
import gzip, json, math, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import semantic as S

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOCAL = DATA / "local"
IS_VIDEO = (ROOT / "scripts" / "video_lora.py").exists()

IMAGE_FAMILIES = ["illustrious", "anima", "krea2", "moss", "sdxl", "pony", "flux", "zimage", "qwen", "chroma", "unknown"]
VIDEO_FAMILIES = ["H3", "Wan", "LTX2"]
FAMILIES = VIDEO_FAMILIES if IS_VIDEO else IMAGE_FAMILIES
AIOPS_FAMILY = {"illustrious": "illustrious", "pony": "pony", "anima": "anima", "krea2": "krea2", "moss": "moss", "sdxl": "sdxl",
                "flux": "flux", "zimage": "zimage", "z-image": "zimage", "qwen": "qwen", "chroma": "chroma", "unknown": "unknown",
                "h3": "H3", "wan": "Wan", "ltx2": "LTX2", "ltx": "LTX2"}
ALLOW_MODEL_IDS = {3044870}  # Shrunk People: Andrew asked to keep it (18 Nov 2026)
OWN_CREATORS = {"onemoreepoch", "octavian123"}

def jl(p: Path):
    if not p.exists():
        return []
    op = gzip.open if p.suffix == ".gz" else open
    out = []
    with op(p, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out

def key(s):
    return (s or "").strip().lower()

def squash(s):
    return re.sub(r"[\W_]+", "", (s or "").lower())

EPOCH_RE = re.compile(r"([-_](v\d+[-_])?0*\d{4,9}$|[-_]e\d{2,3}$|epoch[-_ ]?\d+$|[-_]step\d+$)")
FAM_SUFFIX = re.compile(r"[-_](anima|ill|il|xl|krea2?|moss|pony|sdxl|h3|wan|ltx2?|flux2?|zit|zimage|qwen|chroma)([-_]\d+)?$", re.I)

def group_key(r, mid):
    """Versions/epochs of one LoRA share a group (suggest.py shows the best one)."""
    if mid:
        return f"civ{mid}-{r['family']}"
    base = EPOCH_RE.sub("", key(r["slug"]))
    base = re.sub(r"[-_]v\d+$", "", base)
    base = re.sub(r"[-_](anima|ill|illustrious|il|xl|krea2?|moss|pony|sdxl|h3|wan|ltx2?|flux2?)(?=[-_]|$)", "", base)
    return f"{squash(base)}-{r['family']}"

def civ_ids(url):
    m = re.search(r"models/(\d+)", url or "")
    v = re.search(r"modelVersionId=(\d+)", url or "")
    return (int(m.group(1)) if m else None, int(v.group(1)) if v else None)

def clean_url(u):
    if not u:
        return ""
    u = re.sub(r"[?&](token|sig|signature|expires|X-Amz-[A-Za-z]+|auth)=[^&#]*", "", u)
    return u.replace("civitai.red", "civitai.com")

def family_of_unknown(slug):
    s = slug.lower()
    if re.search(r"(sd15|sd-15|1-5)$", s):
        return None
    if re.search(r"flux2?$", s):
        return "flux"
    if s.endswith("ltx2"):
        return "LTX2"
    return "unknown"

def first_weight(w):
    if not w:
        return None
    w = re.sub(r"(\d)\s*(?:-|–|~|to)\s*(\d)", r"\1 \2", str(w))  # "0.6-0.8" is a range, not -0.8
    nums = re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", w)
    try:
        vals = [float(n) for n in nums if -3 <= float(n) <= 3]
    except ValueError:
        return None
    if not vals or (min(vals[:2]) < 0 < max(vals[:2])):
        return None  # signed slider range: pick the direction yourself
    return round(sum(vals[:2]) / len(vals[:2]), 2)

def split_triggers(t):
    if not t:
        return []
    if isinstance(t, list):
        out = []
        for x in t:
            out += split_triggers(x)
        return out
    parts = [p.strip() for p in re.split(r"[,\n]|\s{2,}|\t", str(t)) if p.strip()]
    seen, out = set(), []
    for p in parts:
        if p.lower() not in seen and len(p) < 120:
            seen.add(p.lower()); out.append(p)
    return out[:25]

def main():
    safety = json.loads((LOCAL / "safety_skips.json").read_text()) if (LOCAL / "safety_skips.json").exists() else {"model_ids": [], "version_ids": []}
    bad_models = set(safety.get("model_ids", [])) - ALLOW_MODEL_IDS
    bad_versions = set(safety.get("version_ids", []))
    excl_models, excl_slugs, epoch_slugs = set(), set(), set()
    for r in jl(DATA / "excluded.jsonl"):
        reason = str(r.get("reason") or r.get("exclude_reason") or "")
        if reason.startswith("out of scope"):
            continue  # another family; the family filter handles it
        names = {key(r.get(k)) for k in ("slug", "file") if r.get(k)} | {key(Path(r.get(k)).stem) for k in ("path", "file") if r.get(k)}
        names.discard("")
        if reason.startswith("intermediate training epoch"):
            epoch_slugs |= names  # kept only for own LoRAs (every epoch is catalogued by onemoreepoch)
            continue
        excl_slugs |= names
        if re.search(r"minor|forbidden", reason, re.I):
            mid = r.get("civitai_model_id")
            try:
                if mid: excl_models.add(int(mid))
            except (TypeError, ValueError):
                pass
    excl_models -= ALLOW_MODEL_IDS

    rec: dict[str, dict] = {}
    alias: dict[str, str] = {}   # any known name -> canonical slug key

    def get(k):
        k = alias.get(k, k)
        return rec.get(k)

    def put(k, row):
        rec[k] = row
        alias[k] = k

    # ---- 1. KB rows (authoritative for HF/Graydient availability + verified CivitAI metadata)
    for r in jl(DATA / "loras.jsonl"):
        if r.get("duplicate_of"):
            continue
        if IS_VIDEO:
            slug = r.get("graydient_slug") or r.get("slug") or Path(r.get("file") or "").stem
            fam = r.get("family")
            mid, vid = r.get("civitai_model_id"), r.get("version_id")
            row = dict(slug=slug, family=fam, base_model=r.get("base"), name=r.get("civitai_name") or r.get("purpose") or slug,
                       triggers=split_triggers(r.get("triggers")), weight=r.get("strength"), weight_source="KB (source-stated)" if r.get("strength") else None,
                       source_url=clean_url((r.get("urls") or {}).get("civitai") or (r.get("urls") or {}).get("huggingface") or ""),
                       civitai_model_id=mid, civitai_version_id=vid, creator=None, ingest_date=None,
                       graydient=bool(r.get("graydient")), hf=bool(r.get("graydient_files") or r.get("hf_id")),
                       hf_files=r.get("graydient_files") or [], raid=bool(r.get("aiops")),
                       civit_tags=list(r.get("categories") or []), kb_category=",".join(r.get("categories") or []),
                       desc=(r.get("purpose") or ""),
                       downloads=r.get("downloads") or 0, reliability="verified" if r.get("verified") else "unverified",
                       i2v_t2v=r.get("i2v_t2v"), example=(r.get("example_prompt") or "")[:300], kb=True)
        else:
            slug = r["slug"]
            fam = r.get("family")
            ex = r.get("example") or {}
            row = dict(slug=slug, family=fam, base_model=r.get("base_model"), name=r.get("name") or slug,
                       triggers=split_triggers(r.get("trigger_words")), weight=r.get("strength"),
                       weight_source=r.get("strength_source") if r.get("strength") else None,
                       source_url=clean_url(r.get("source_url")), civitai_model_id=r.get("civitai_model_id"),
                       civitai_version_id=r.get("civitai_version_id"), creator=r.get("creator"), ingest_date=None,
                       graydient=bool(r.get("graydient")), hf=bool(r.get("hf_files")),
                       hf_files=[f"{h['repo']}/{h['path']}" for h in (r.get("hf_files") or [])], raid=False,
                       civit_tags=list(r.get("tags") or []), kb_category=r.get("category"),
                       desc=(r.get("description") or "")[:600], downloads=r.get("downloads") or 0,
                       reliability=r.get("reliability"), example=(ex.get("prompt") or "")[:300], kb=True)
        k = key(slug)
        put(k, row)
        for f in row["hf_files"]:
            alias.setdefault(key(Path(f).stem), k)

    # ---- 2. AIOps library snapshot
    for a in jl(LOCAL / "aiops_graydient.jsonl.gz"):
        if a.get("kind") and a.get("kind") != "lora":
            continue
        fam = AIOPS_FAMILY.get((a.get("family") or "").lower())
        if fam == "unknown":
            fam = family_of_unknown(a.get("slug") or "")
        if not fam or fam not in FAMILIES:
            continue
        gslug = a.get("graydient_slug") or a.get("slug")
        cands = [key(gslug), key(a.get("slug")), key(Path(a.get("hf_repo_file") or "").stem), key(Path(a.get("filename") or "").stem)]
        row = next((get(c) for c in cands if c and get(c)), None)
        creator = a.get("creator") or None
        own = bool(a.get("mine")) or key(creator) in OWN_CREATORS
        if row is None:
            if not (a.get("on_graydient") or a.get("on_hf") or a.get("on_raid")):
                continue
            mid, vid = civ_ids(a.get("source_url"))
            row = dict(slug=gslug, family=fam, base_model=None, name=a.get("name") or gslug,
                       triggers=split_triggers(a.get("token")), weight=None, weight_source=None,
                       source_url=clean_url(a.get("source_url")), civitai_model_id=mid, civitai_version_id=vid,
                       creator=creator, ingest_date=None, graydient=bool(a.get("on_graydient")), hf=bool(a.get("on_hf")),
                       hf_files=[a["hf_repo_file"]] if a.get("hf_repo_file") else [], raid=bool(a.get("on_raid")),
                       civit_tags=[t for t in (a.get("tags") or []) if not str(t).startswith("-")], kb_category=None,
                       desc=(a.get("description") or "")[:600], downloads=0, reliability="aiops", example="", kb=False)
            put(key(gslug), row)
        else:
            row["graydient"] = row["graydient"] or bool(a.get("on_graydient"))
            row["raid"] = row["raid"] or bool(a.get("on_raid"))
            row["hf"] = row["hf"] or bool(a.get("on_hf"))
            if not row.get("creator") and creator:
                row["creator"] = creator
            if not row.get("source_url") and a.get("source_url"):
                row["source_url"] = clean_url(a["source_url"])
                row["civitai_model_id"], row["civitai_version_id"] = civ_ids(a["source_url"])
            if not row["triggers"] and a.get("token") and not a["token"].strip().lower() == key(gslug):
                row["triggers"] = split_triggers(a.get("token"))
            if len(row.get("desc") or "") < 80 and a.get("description"):
                row["desc"] = (row.get("desc") or "") + " " + a["description"][:600]
            extra = [t for t in (a.get("tags") or []) if not str(t).startswith("-")]
            row["civit_tags"] = list(dict.fromkeys((row.get("civit_tags") or []) + extra))
        if own:
            row["own"] = True
            row["creator"] = "onemoreepoch"
        if a.get("ingested_at") and not row.get("ingest_date"):
            row["ingest_date"] = str(a["ingested_at"])[:10]
        if a.get("example_prompts") and not row.get("example"):
            row["example"] = str(a["example_prompts"][0])[:300]
        for c in cands:
            if c:
                alias.setdefault(c, key(row["slug"]))

    # ---- 3. ingest plans (dates, triggers, CivitAI descriptions, holds)
    by_vid = {}
    for k, r in rec.items():
        if r.get("civitai_version_id"):
            by_vid.setdefault(int(r["civitai_version_id"]), k)
    for p in jl(LOCAL / "ingest_plans.jsonl.gz"):
        if p.get("kind") not in (None, "lora") and str(p.get("type", "")).upper() not in ("LORA", "LOCON", "DORA", "LYCORIS"):
            continue
        st = p.get("state")
        if st not in ("registered", "verified", "uploaded"):
            continue  # pending / error / skipped are not "we have it"
        fam = AIOPS_FAMILY.get((p.get("family") or "").lower()) or p.get("family")
        bm = (p.get("base_model") or "").lower()
        if not fam or fam not in FAMILIES:
            fam = ("H3" if "h3" in bm else "Wan" if "wan" in bm else "LTX2" if "ltx" in bm else
                   "anima" if "anima" in bm else "krea2" if "krea" in bm else "moss" if "moss" in bm else
                   "illustrious" if ("illustrious" in bm or "noob" in bm) else "pony" if "pony" in bm else
                   "sdxl" if "sdxl" in bm else None)
        if fam not in FAMILIES:
            continue
        gslug = p.get("graydient_slug") or p.get("slug")
        k = alias.get(key(gslug)) or alias.get(key(p.get("slug"))) or by_vid.get(p.get("version_id") or -1)
        row = rec.get(k) if k else None
        date = None
        for d in (p.get("queued_at"), p.get("plan_created")):
            if isinstance(d, str) and re.match(r"\d{4}-\d{2}-\d{2}", d):
                date = d[:10]; break
            if isinstance(d, (int, float)) and not isinstance(d, bool) and d > 1e9:
                date = datetime.fromtimestamp(d, timezone.utc).strftime("%Y-%m-%d"); break
        if not date and p.get("plan_mtime"):
            date = datetime.fromtimestamp(p["plan_mtime"], timezone.utc).strftime("%Y-%m-%d")
        if row is None:
            row = dict(slug=gslug, family=fam, base_model=p.get("base_model"), name=p.get("model_name") or gslug,
                       triggers=split_triggers(p.get("token")) if p.get("token") and key(p.get("token")) != key(gslug) else [],
                       weight=None, weight_source=None, source_url=clean_url(p.get("civit_url")),
                       civitai_model_id=p.get("model_id"), civitai_version_id=p.get("version_id"), creator=p.get("creator"),
                       ingest_date=date, graydient=st in ("registered", "verified") and not p.get("registration_hold"),
                       hf=bool(p.get("hf_filename") or p.get("hf_repo")),
                       hf_files=[f"{p.get('hf_repo') or 'Octavian123/civit'}/{p['hf_filename']}"] if p.get("hf_filename") else [],
                       raid=bool(p.get("archived") or p.get("archived_path")), civit_tags=list(p.get("tags") or []), kb_category=None,
                       desc=(p.get("description") or "")[:600], downloads=0, reliability="ingest-plan", example="", kb=False)
            put(key(gslug), row)
        else:
            row["ingest_date"] = row.get("ingest_date") or date
            if st in ("registered", "verified") and not p.get("registration_hold"):
                row["graydient"] = True
            row["raid"] = row["raid"] or bool(p.get("archived") or p.get("archived_path"))
            if not row.get("creator") and p.get("creator"):
                row["creator"] = p["creator"]
            if not row.get("base_model"):
                row["base_model"] = p.get("base_model")
            if len(row.get("desc") or "") < 120 and p.get("description"):
                row["desc"] = ((row.get("desc") or "") + " " + p["description"])[:800]
            row["civit_tags"] = list(dict.fromkeys((row.get("civit_tags") or []) + list(p.get("tags") or [])))
            if not row.get("source_url"):
                row["source_url"] = clean_url(p.get("civit_url"))
        if p.get("version_id") and not row.get("civitai_version_id"):
            row["civitai_version_id"] = p["version_id"]
        if p.get("model_id") and not row.get("civitai_model_id"):
            row["civitai_model_id"] = p["model_id"]
        if p.get("registration_hold"):
            row["hold"] = str(p.get("registration_hold"))[:80]

    # ---- 4. safety + tagging + finalize
    out, dropped = [], Counter()
    for k, r in rec.items():
        mid = r.get("civitai_model_id")
        vid = r.get("civitai_version_id")
        try:
            mid = int(mid) if mid else None
            vid = int(vid) if vid else None
        except (TypeError, ValueError):
            mid = vid = None
        if mid in ALLOW_MODEL_IDS:
            pass
        elif mid in bad_models or vid in bad_versions:
            dropped["safety-skip id"] += 1; continue
        elif mid in excl_models or k in excl_slugs or any(key(Path(h).stem) in excl_slugs for h in r.get("hf_files") or []):
            dropped["KB excluded (minor-coded / not a LoRA)"] += 1; continue
        epoch = k in epoch_slugs or any(key(Path(h).stem) in epoch_slugs for h in r.get("hf_files") or []) or bool(EPOCH_RE.search(k))
        if epoch and not (r.get("own") or key(r.get("creator")) in OWN_CREATORS) and k in epoch_slugs:
            dropped["intermediate epoch (final kept)"] += 1; continue
        why = S.blocked(r["slug"], r.get("name"), " ".join(r.get("triggers") or []), " ".join(r.get("civit_tags") or []))
        if not why:
            why = S.blocked_character(r["slug"], r.get("name"), " ".join(r.get("triggers") or []), " ".join(r.get("civit_tags") or []))
            if why:
                dropped["minor-coded character/franchise"] += 1
                continue
        if not why:
            hard = re.search(r"\b(loli\w*|shota\w*|underage|preteen|child|kids?|(1[0-7]|[1-9]) ?years? old)\b", S.norm_text(r.get("desc") or "")[:600])
            why = f"description: {hard.group(0)}" if hard else None
        if why and mid not in ALLOW_MODEL_IDS:
            dropped["minor/school-coded text"] += 1; continue
        trig = r.get("triggers") or []
        # a "trigger" identical to the slug is the Graydient no-trigger convention, not a source trigger
        trig = [t for t in trig if squash(t) != squash(r["slug"])]  # slug-as-token = Graydient no-trigger convention
        w = r.get("weight")
        wsrc = r.get("weight_source")
        if not w:
            w2 = S.weight_from_text(r.get("desc") or "")
            if w2:
                w, wsrc = w2, "stated in description"
        sem = S.tag_text(r.get("name"), r["slug"], " ".join(trig), " ".join(r.get("civit_tags") or []), (r.get("desc") or "")[:350])
        if not IS_VIDEO:
            sem.pop("motion", None)
        kind = role_of(r, sem)
        own = bool(r.get("own")) or key(r.get("creator")) in OWN_CREATORS
        o = {
            "slug": r["slug"], "family": r["family"], "base_model": r.get("base_model"), "name": (r.get("name") or "")[:140],
            "triggers": trig, "no_trigger": not trig,
            "weight": w, "weight_value": first_weight(w), "weight_source": wsrc,
            "source_url": r.get("source_url") or "", "civitai_model_id": mid, "civitai_version_id": vid,
            "creator": "onemoreepoch" if own else (r.get("creator") or None), "own": own,
            "ingest_date": r.get("ingest_date"),
            "availability": {"graydient": bool(r["graydient"]), "hf": bool(r["hf"]), "raid": bool(r["raid"])},
            "hf_files": (r.get("hf_files") or [])[:3],
            "role": kind, "kb_category": r.get("kb_category"), "group": group_key(r, mid),
            "semantic": sem, "civit_tags": [t for t in (r.get("civit_tags") or []) if isinstance(t, str)][:15],
            "desc": re.sub(r"\s+", " ", (r.get("desc") or "")).strip()[:220],
            "downloads": r.get("downloads") or 0, "reliability": r.get("reliability"),
        }
        if epoch:
            o["epoch"] = True
        if r.get("i2v_t2v"):
            o["i2v_t2v"] = r["i2v_t2v"]
        if r.get("hold"):
            o["hold"] = r["hold"]
        if r.get("example"):
            o["example"] = re.sub(r"\s+", " ", r["example"])[:240]
        out.append(o)
    out.sort(key=lambda o: (FAMILIES.index(o["family"]) if o["family"] in FAMILIES else 99, o["slug"].lower()))
    with open(DATA / "semantic_catalog.jsonl", "w", encoding="utf-8") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "\n")
    write_summary(out, dropped)
    print(json.dumps({"semantic_catalog": len(out), "dropped": dropped, "tagged": sum(1 for o in out if o["semantic"])}))

IDENTITY_TAGS = {"celebrity", "game character", "anime character", "cartoon character", "original character"}

def role_of(r, sem):
    kc = (r.get("kb_category") or "").lower()
    name = S.norm_text(f"{r.get('name')} {r['slug']}")
    if "character" in kc or IDENTITY_TAGS & set(sem.get("subject", [])):
        return "identity"
    if any(x in kc for x in ("utility",)) or {"speed", "slider"} & set(sem.get("concept", [])):
        return "utility"
    if "style" in kc or (sem.get("style") and re.search(r"\b(style|artist|aesthetic|look|art style)\b", name + " " + S.norm_text(" ".join(r.get("civit_tags") or []) + " " + (r.get("desc") or "")[:160]))):
        return "style"
    if "quality" in kc or {"realism enhancement", "detail enhancement"} & set(sem.get("concept", [])):
        return "detail"
    if "lighting" in kc:
        return "lighting"
    for c, rname in (("clothing", "clothing"), ("pose", "pose"), ("anatomy", "anatomy")):
        if c in kc.replace("pose-composition", "pose") and sem.get(c):
            return rname
    if "nsfw-act" in kc:
        return "act"
    if "motion" in kc or sem.get("motion"):
        return "motion" if IS_VIDEO else "concept"
    return "concept"

def write_summary(out, dropped):
    fam = Counter(o["family"] for o in out)
    gd = Counter(o["family"] for o in out if o["availability"]["graydient"])
    own = Counter(o["family"] for o in out if o["own"])
    nt = Counter(o["family"] for o in out if o["no_trigger"])
    tagged = Counter(o["family"] for o in out if o["semantic"])
    cat = Counter(c for o in out for c in o["semantic"])
    L = ["# Semantic LoRA catalog summary", "",
         f"Built {datetime.now().strftime('%Y-%m-%d')} by `scripts/build_semantic.py` from `data/loras.jsonl`, the AIOps library snapshot and the ingest plans. "
         "Adults only: safety-skipped CivitAI ids and minor/school-coded names are excluded.", "",
         "| family | entries | on Graydient | own (onemoreepoch) | no trigger | with semantic tags |", "|---|---:|---:|---:|---:|---:|"]
    for f in FAMILIES:
        if fam[f]:
            L.append(f"| {f} | {fam[f]} | {gd[f]} | {own[f]} | {nt[f]} | {tagged[f]} |")
    L += [f"| **total** | {len(out)} | {sum(gd.values())} | {sum(own.values())} | {sum(nt.values())} | {sum(tagged.values())} |", "",
          "Entries per semantic category: " + ", ".join(f"{S.CATEGORY_LABEL[c]} {cat[c]}" for c in S.CATEGORIES if cat[c]) + ".", "",
          "Excluded while building: " + (", ".join(f"{k} {v}" for k, v in dropped.items()) or "none") + ".", "",
          "Fields: slug, family, base_model, name, triggers (empty = no trigger; registered on Graydient by slug), weight (+source), "
          "source_url, creator (onemoreepoch = Andrew's own), ingest_date, availability{graydient,hf,raid}, role, semantic{category:[tags]}.", ""]
    (DATA / "semantic_summary.md").write_text("\n".join(L))

def catalog_slugs():
    p = DATA / "semantic_catalog.jsonl"
    return {json.loads(l)["slug"] for l in p.read_text(encoding="utf-8").split("\n") if l.strip()} if p.exists() else set()

def report_lines(before: set) -> list[str]:
    """Markdown for check_new.py: what the weekly semantic refresh changed and what still lacks metadata."""
    rows = [json.loads(l) for l in (DATA / "semantic_catalog.jsonl").read_text(encoding="utf-8").split("\n") if l.strip()]
    new = [r for r in rows if r["slug"] not in before]
    untagged = [r for r in rows if not r["semantic"]]
    no_src = [r for r in rows if not r["source_url"] and not r["own"]]
    ages = []
    for f in ("aiops_graydient.jsonl.gz", "ingest_plans.jsonl.gz", "safety_skips.json"):
        p = LOCAL / f
        if p.exists():
            d = (datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)).days
            ages.append(f"`{f}` {d} d old")
    L = ["## Semantic tags for the prompt matcher", "",
         f"`data/semantic_catalog.jsonl` rebuilt: {len(rows)} LoRAs ({len(rows) - len(untagged)} tagged). "
         f"{len(new)} new since the last build, {len(untagged)} with no semantic tags, {len(no_src)} without a source URL.", "",
         "Local snapshots: " + (", ".join(ages) or "missing") + ". Refresh them on the home Mac with `scripts/export_local_meta.py` "
         "when they are older than a week (AIOps library, ingest plans, safety skips; read-only).", ""]
    for r in new[:40]:
        tags = "; ".join(f"{S.CATEGORY_LABEL[c]}: {', '.join(v[:4])}" for c, v in r["semantic"].items()) or "no tags"
        L.append(f"- new `{r['slug']}` ({r['family']}, {r['role']}) — {', '.join(r['triggers'][:3]) or 'no trigger'} — {tags}")
    if untagged:
        L += ["", "Untagged (name/description too thin; add tags by hand in data/local or improve the lexicon in scripts/semantic.py):", ""]
        L += [f"- `{r['slug']}` ({r['family']})" for r in untagged[:25]]
    return L + [""]

def _texts(r):
    trig = r.get("trigger_words") or r.get("triggers") or r.get("trainedWords") or []
    if isinstance(trig, str):
        trig = [trig]
    tags = r.get("tags") or r.get("categories") or []
    tags = [t if isinstance(t, str) else str(t.get("name", "")) for t in tags]
    return [str(r.get("slug") or ""), str(r.get("name") or r.get("civitai_name") or ""), str(r.get("purpose") or ""),
            " ".join(map(str, trig)), " ".join(tags)]

def prune_kb():
    """Adults-only guard for the KB catalogs themselves: move safety-skipped / minor-coded rows out of
    data/loras.jsonl and data/candidates.jsonl into data/excluded.jsonl (with the reason)."""
    safety = json.loads((LOCAL / "safety_skips.json").read_text()) if (LOCAL / "safety_skips.json").exists() else {}
    bad_models = set(safety.get("model_ids", [])) - ALLOW_MODEL_IDS
    bad_versions = set(safety.get("version_ids", []))
    moved = Counter()
    excl_path = DATA / "excluded.jsonl"
    excl = excl_path.read_text(encoding="utf-8").rstrip("\n").split("\n") if excl_path.exists() else []
    for name in ("loras.jsonl", "candidates.jsonl"):
        p = DATA / name
        if not p.exists():
            continue
        keep = []
        for line in p.read_text(encoding="utf-8").split("\n"):
            if not line.strip():
                continue
            r = json.loads(line)
            mid = r.get("civitai_model_id") or (r.get("id") if name == "candidates.jsonl" else None)
            vid = r.get("civitai_version_id") or r.get("version_id")
            try:
                mid = int(mid) if mid else None
                vid = int(vid) if vid else None
            except (TypeError, ValueError):
                mid = vid = None
            why = None
            if mid not in ALLOW_MODEL_IDS:
                if mid in bad_models or vid in bad_versions:
                    why = "safety-skipped in an ingest review (adults only)"
                else:
                    t = _texts(r)
                    why = S.blocked_character(*t) or S.blocked(*t)
            if why:
                moved[name] += 1
                e = {"slug": r.get("slug") or r.get("name"), "family": r.get("family"), "civitai_model_id": mid, "reason": why}
                if IS_VIDEO:
                    e["exclude_reason"] = why
                excl.append(json.dumps(e, ensure_ascii=False))
            else:
                keep.append(line)
        p.write_text("\n".join(keep) + "\n", encoding="utf-8")
    excl_path.write_text("\n".join(l for l in excl if l.strip()) + "\n", encoding="utf-8")
    print(json.dumps({"pruned": moved}))

if __name__ == "__main__":
    if "--prune-kb" in sys.argv:
        prune_kb()
    main()
