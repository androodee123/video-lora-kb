#!/usr/bin/env python3
"""Suggest LoRAs from the catalog for a draft prompt (identical script in image-lora-kb and video-lora-kb).

  python3 scripts/suggest.py "a redhead woman in a black latex catsuit kneeling in a neon alley, from below" --base krea2
  echo "<prompt>" | python3 scripts/suggest.py --base anima --intent "pin-up comic look" --top 10
  python3 scripts/suggest.py "..." --base h3 --json

How it works: the prompt (+ optional --intent) is parsed into the same semantic categories used to tag the catalog
(subject/character, concept/intent, clothing/outfit, expression, object/prop, pose/action/camera, style/medium,
anatomy, video motion). Each LoRA in data/semantic_catalog.jsonl is scored on
  * exact words/phrases from the prompt in its name, slug and source triggers (IDF weighted: rare words count more),
  * shared semantic tags per category,
  * small priors: on Graydient > HF/RAID only, Andrew's own (onemoreepoch), verified CivitAI metadata, downloads.
Versions/epochs of the same LoRA are collapsed to the best one. LoRAs already in the prompt (`<slug:w>`) are skipped
and checked for conflicts. Output: ranked picks per category with why it matched, trigger, weight and stacking notes,
then a proposed LoRA block. Never invents triggers: no-trigger LoRAs are used by slug only. Weights are source-stated
when known; otherwise the workflow default is shown and labelled as a default.
"""
from __future__ import annotations
import argparse, json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import semantic as S

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "semantic_catalog.jsonl"
IS_VIDEO = (ROOT / "scripts" / "video_lora.py").exists()

BASE_ALIASES = {
    "illustrious": ["illustrious"], "il": ["illustrious"], "ill": ["illustrious"], "noob": ["illustrious"], "noobai": ["illustrious"],
    "anima": ["anima"], "krea": ["krea2"], "krea2": ["krea2"], "detailed-krea2": ["krea2"], "moss": ["moss"], "kromoss": ["moss"],
    "sdxl": ["sdxl"], "xl": ["sdxl", "illustrious", "pony"], "pony": ["pony"], "flux": ["flux"], "zimage": ["zimage"],
    "h3": ["H3"], "minimax": ["H3"], "omni-eros-new-h3": ["H3"], "wan": ["Wan"], "wan2.1": ["Wan"], "wan2.2": ["Wan"], "wan22": ["Wan"],
    "ltx": ["LTX2"], "ltx2": ["LTX2"], "ltx2.3": ["LTX2"],
}
# Family pairs that can share LoRAs at reduced reliability (all SDXL-architecture). Shown with a warning.
NEAR = {"illustrious": ["sdxl", "pony"], "pony": ["sdxl", "illustrious"], "sdxl": ["illustrious", "pony"]}
DEFAULT_WEIGHT = {"krea2": (0.7, "detailed-krea2 workflow default"), "moss": (0.4, "kromoss helper default (identity 0.8)"),
                  "H3": (0.8, "H3 default — tune 0.6–1.0"), "Wan": (0.8, "Wan default — tune 0.6–1.0"), "LTX2": (0.8, "LTX default — tune 0.6–1.0")}
CAT_W = {"subject": 2.2, "concept": 1.6, "clothing": 2.0, "expression": 1.6, "object": 1.6, "pose": 1.8, "style": 2.0, "anatomy": 1.4, "motion": 2.2}
GENERIC = {"woman", "man", "lighting", "background", "detail enhancement", "hair", "face", "eyes", "domestic", "nude", "hands", "standing",
           "hand on hip", "facial expression", "photoreal", "breasts", "skin"}  # weak alone

LOW = set("""red blue green black white pink purple yellow orange brown grey gray silver gold golden blonde dark light
woman women girl girls man men boy holding wearing hair long short big small large wet young adult female male body look looking
background scene shot photo image picture render""".split())
# Content a LoRA adds that the prompt did not ask for (it would drift the image): penalised unless the prompt has it.
DRIFT = {"subject": {"futanari", "femboy", "furry", "monster", "monster girl", "giantess", "zombie", "robot", "man", "group", "couple", "mature", "bbw"},
         "pose": {"face sitting", "cowgirl", "missionary", "doggystyle", "69", "standing sex", "piledriver", "spooning", "all fours", "spread legs", "presenting"},
         "concept": {"worship", "toys", "exhibitionism", "tentacles", "transformation", "size difference", "pregnancy", "watersports", "gay", "lesbian", "groupsex", "horror",
                     "sex", "oral", "anal", "cumshot", "bdsm", "medical", "humiliation"}}

LORA_RE = re.compile(r"<\s*(?:lora:)?([^:<>\s]+)\s*(?::\s*(-?[0-9.]+))?[^<>]*>", re.I)

def load():
    rows = []
    with open(CATALOG, encoding="utf-8") as f:
        for l in f:
            if l.strip():
                rows.append(json.loads(l))
    return rows

def doc_fields(o):
    name = S.tokens(f"{o.get('name')} {o['slug']}")
    trig = S.tokens(" ".join(o.get("triggers") or []))
    tags = S.tokens(" ".join(o.get("civit_tags") or []))
    desc = S.tokens(o.get("desc") or "")
    return name, trig, tags, desc

def build_index(rows):
    df = Counter()
    tagdf = Counter()
    fields = []
    for o in rows:
        name, trig, tags, desc = doc_fields(o)
        f = {"name": set(name), "trig": set(trig), "tags": set(tags), "desc": set(desc),
             "bi": set(S.bigrams(name)) | set(S.bigrams(trig))}
        fields.append(f)
        for t in f["name"] | f["trig"] | f["tags"] | f["desc"]:
            df[t] += 1
        for c, ts in (o.get("semantic") or {}).items():
            for t in ts:
                tagdf[(c, t)] += 1
    n = max(1, len(rows))
    idf = lambda t: math.log(1 + n / (1 + df[t]))
    tidf = lambda c, t: math.log(1 + n / (1 + tagdf[(c, t)]))
    return fields, idf, tidf

def parse_existing(prompt):
    used = [(m.group(1), m.group(2)) for m in LORA_RE.finditer(prompt)]
    return used, LORA_RE.sub(" ", prompt)

def families_for(base):
    if not base:
        return None
    out = []
    for b in re.split(r"[,\s]+", base.lower()):
        out += BASE_ALIASES.get(b, [b])
    return out

def weight_of(o):
    if o.get("weight_value") is not None:
        return o["weight_value"], f"source-stated ({o.get('weight')})"
    d = DEFAULT_WEIGHT.get(o["family"])
    if d:
        w, why = d
        if o["family"] == "moss" and o.get("role") == "identity":
            w, why = 0.8, "kromoss identity default"
        return w, why + " — not source-stated"
    return 0.7, "not stated — start 0.6–0.8 and test"

def score(o, f, q, idf, tidf, fams_main, fams_near):
    s, why = 0.0, []
    lex_hits = []
    long_trig = len(o.get("triggers") or []) > 6  # a long trigger list is really a tag list
    for t in q["tokens"]:
        w = idf(t) * (0.3 if t in LOW else 1.0)
        if t in f["trig"]:
            s += (0.9 if long_trig else 2.6) * w; lex_hits.append(t)
        elif t in f["name"]:
            s += 2.2 * w; lex_hits.append(t)
        elif t in f["tags"]:
            s += 0.9 * w; lex_hits.append(t)
        elif t in f["desc"]:
            s += 0.3 * w
    bi = q["bigrams"] & f["bi"]
    if bi:
        s += 3.0 * len(bi) * 2
    if lex_hits:
        why.append("words: " + ", ".join(sorted(set(lex_hits))[:6]))
    sem_hits = defaultdict(list)
    strong = False
    for c, ts in q["semantic"].items():
        for t in ts:
            if t in (o.get("semantic") or {}).get(c, []):
                w = CAT_W.get(c, 1.0) * tidf(c, t) * (0.35 if t in GENERIC else 1.0)
                s += w
                sem_hits[c].append(t)
                if t not in GENERIC:
                    strong = True
    for c, ts in sem_hits.items():
        why.append(f"{S.CATEGORY_LABEL[c]}: {', '.join(ts)}")
    specific_lex = [t for t in lex_hits if idf(t) > 3.0 and t not in LOW]
    if not specific_lex and not strong and not bi:
        return 0.0, why, sem_hits
    if o.get("role") == "identity":
        # a character/person LoRA only fits when the prompt names it (rare word in its name/triggers)
        if not any(idf(t) > 5.0 and t not in LOW and (t in f["name"] or t in f["trig"]) for t in lex_hits) and not bi:
            s *= 0.25
        else:
            why.append("name match")
    drift = [t for c, bad in DRIFT.items() for t in (o.get("semantic") or {}).get(c, []) if t in bad and t not in q["semantic"].get(c, [])]
    if drift:
        s *= max(0.2, 0.55 ** len(drift))
        why.append("adds: " + ", ".join(drift))
    # length normalisation: long trigger lists and names match too easily
    s /= (1 + 0.08 * max(0, len(f["trig"]) + len(f["name"]) - 8))
    av = o.get("availability") or {}
    s += 1.0 if av.get("graydient") else -2.0
    if o.get("own"):
        s += 1.5
    if o.get("reliability") == "verified":
        s += 0.3
    s += 0.25 * math.log10(1 + (o.get("downloads") or 0))
    if o.get("epoch") and not o.get("own"):
        s -= 1.0
    if fams_near and o["family"] in fams_near:
        s *= 0.6
    return s, why, sem_hits

def primary_category(o, sem_hits):
    role = o.get("role")
    if role == "identity":
        return "subject"
    if sem_hits:
        return max(sem_hits, key=lambda c: (len(sem_hits[c]) * CAT_W.get(c, 1)))
    return {"style": "style", "clothing": "clothing", "pose": "pose", "anatomy": "anatomy", "motion": "motion"}.get(role, "concept")

NOT_GARMENT = {"nude", "naked", "topless", "bottomless", "undressing", "clothed", "costume"}

def named_by_person_word(why):
    """True when an identity's name match rests on a non-clothing word (a garment like 'plugsuit' alone is not a name)."""
    words = next((w[len("words: "):].split(", ") for w in why if w.startswith("words: ")), [])
    return any(not S.tag_text(t).get("clothing") for t in words if len(t) > 2)

def nsfwish(o):
    """NSFW or anatomy LoRA: never stacked with a minor_coded one."""
    return bool(o.get("nsfw") or o.get("role") in ("act", "anatomy") or (o.get("semantic") or {}).get("anatomy"))

def stack_notes(picks, used_rows):
    notes = []
    roles = Counter(o.get("role") for o in picks + used_rows)
    fams = Counter(o["family"] for o in picks + used_rows)
    if roles["identity"] > 1:
        notes.append("More than one identity LoRA: only keep several when the image has that many different people.")
    if roles["style"] > 1:
        notes.append("Two or more style LoRAs fight each other: keep one, or halve both weights.")
    REAL, TOON = {"photoreal", "amateur", "cinematic"}, {"anime", "comic", "cartoon", "hentai", "retro anime"}
    lanes = [set((o.get("semantic") or {}).get("style", [])) for o in picks + used_rows if o.get("role") in ("style", "detail")]
    if any(l & REAL and not l & TOON for l in lanes) and any(l & TOON and not l & REAL for l in lanes):
        notes.append("Realism and anime/comic style LoRAs rarely agree: choose one lane.")
    if roles["utility"]:
        notes.append("Speed/slider LoRAs: speed ones only on the matching turbo/few-step workflow; sliders are signed (negative weight reverses).")
    if len(fams) > 1:
        notes.append("Mixed families in one stack: keep every LoRA in the checkpoint's family (" + ", ".join(fams) + ").")
    if IS_VIDEO:
        wan = [o for o in picks if o["family"] == "Wan" and re.search(r"(high|low)", o["slug"])]
        if wan:
            notes.append("Wan 2.2 A14B LoRAs come in high-noise/low-noise pairs: load the matching partner on the other expert.")
    if sum(1 for o in picks) > 5:
        notes.append("Large stack: add LoRAs one at a time and keep helpers at 0.2–0.5.")
    return notes

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt", nargs="?", help="draft prompt (or stdin)")
    ap.add_argument("--intent", default="", help="extra intent/goal text (counts like the prompt)")
    ap.add_argument("--base", default="", help="checkpoint family: " + ", ".join(sorted(BASE_ALIASES)))
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--per-category", type=int, default=3)
    ap.add_argument("--include-unavailable", action="store_true", help="also show HF/RAID-only LoRAs (not on Graydient)")
    ap.add_argument("--own", action="store_true", help="only Andrew's own (onemoreepoch) LoRAs")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    prompt = a.prompt if a.prompt is not None else sys.stdin.read()
    used, clean = parse_existing(prompt)
    text = f"{clean} {a.intent}"
    toks = S.tokens(text)
    q = {"tokens": list(dict.fromkeys(toks)), "bigrams": set(S.bigrams(toks)), "semantic": S.tag_text(text)}
    if not IS_VIDEO:
        q["semantic"].pop("motion", None)
    rows = load()
    fams = families_for(a.base)
    fams_near = []
    if fams:
        for f in fams:
            fams_near += [x for x in NEAR.get(f, []) if x not in fams]
        pool = [o for o in rows if o["family"] in fams or o["family"] in fams_near]
    else:
        pool = rows
    if not a.include_unavailable:
        pool = [o for o in pool if (o.get("availability") or {}).get("graydient")]
    if a.own:
        pool = [o for o in pool if o.get("own")]
    used_names = {u[0].lower() for u in used}
    used_rows = [o for o in rows if o["slug"].lower() in used_names]
    # safety: minor_coded LoRAs (minor/school-age characters, age sliders) are SFW-only
    nsfw_prompt = S.is_nsfw(q["semantic"], text) or any(nsfwish(o) for o in used_rows)
    if any(o.get("minor_coded") for o in used_rows) and not nsfw_prompt:
        pool = [o for o in pool if not nsfwish(o)]
    fields, idf, tidf = build_index(pool)
    scored = []
    garments = set(q["semantic"].get("clothing", [])) - NOT_GARMENT
    best_identity = (0.0, None)  # strongest name-matched character LoRA, flagged or not
    for o, f in zip(pool, fields):
        if o["slug"].lower() in used_names:
            continue
        s, why, hits = score(o, f, q, idf, tidf, fams, fams_near)
        if o.get("role") == "identity" and "name match" in why and s > best_identity[0] and named_by_person_word(why):
            best_identity = (s, o)
        if nsfw_prompt and o.get("minor_coded"):
            continue
        # garment-first: when the prompt names an outfit, clothing-only LoRAs for that garment rank first
        if s > 0 and garments and o.get("role") == "clothing" and garments & set((o.get("semantic") or {}).get("clothing", [])):
            s *= 1.5
            why.append("outfit match")
        if s > 0:
            scored.append((s, o, why, hits))
    minor_named = nsfw_prompt and best_identity[1] is not None and best_identity[1].get("minor_coded")
    if minor_named:
        # the prompt names a minor-coded character with NSFW wording: no suggestions and no outfit substitutes
        msg = (f"The prompt names a minor-coded character ({best_identity[1]['slug']}: {best_identity[1].get('minor_reason')}) "
               "and is NSFW. Minor-coded characters are SFW-only, so nothing is suggested and no outfit substitute is offered. "
               "Remove the NSFW wording, or drop the character.")
        if a.json:
            print(json.dumps({"prompt_semantic": q["semantic"], "nsfw_prompt": True, "minor_coded_character": best_identity[1]["slug"],
                              "suggestions": [], "stack_notes": [msg]}, ensure_ascii=False, indent=1))
        else:
            print(msg)
        return 0
    scored.sort(key=lambda x: -x[0])
    best, seen_group, other_versions = [], {}, Counter()
    for s, o, why, hits in scored:
        g = o.get("group") or o["slug"]
        if g in seen_group:
            other_versions[g] += 1
            continue
        seen_group[g] = o
        best.append((s, o, why, hits))
    by_cat = defaultdict(list)
    for s, o, why, hits in best:
        c = primary_category(o, hits)
        if len(by_cat[c]) < a.per_category:
            by_cat[c].append((s, o, why))
    # diversify: walk prompt categories round-robin (strongest category weight first), then fill by score
    order = sorted(q["semantic"], key=lambda c: -CAT_W.get(c, 1))
    top, taken = [], set()
    cat_lists = defaultdict(list)
    for item in best:
        cat_lists[primary_category(item[1], item[3])].append(item)
    rnd = 0
    while len(top) < a.top and rnd < a.per_category:
        for c in order + [c for c in cat_lists if c not in order]:
            lst = [x for x in cat_lists.get(c, []) if x[1]["slug"] not in taken]
            if lst and len(top) < a.top:
                top.append(lst[0]); taken.add(lst[0][1]["slug"])
        rnd += 1
    for item in best:
        if len(top) >= a.top:
            break
        if item[1]["slug"] not in taken:
            top.append(item); taken.add(item[1]["slug"])
    top.sort(key=lambda x: ("outfit match" not in x[2], -x[0]))
    picks = []
    for s, o, why, hits in top:
        w, wsrc = weight_of(o)
        picks.append({"slug": o["slug"], "family": o["family"], "score": round(s, 2), "category": primary_category(o, hits),
                      "role": o.get("role"), "why": why, "triggers": o.get("triggers") or [], "no_trigger": o.get("no_trigger"),
                      "weight": w, "weight_note": wsrc, "own": o.get("own"), "creator": o.get("creator"),
                      "availability": o.get("availability"), "source_url": o.get("source_url"),
                      "other_versions": other_versions.get(o.get("group") or o["slug"], 0),
                      "near_family": bool(fams_near and o["family"] in fams_near),
                      "minor_coded": bool(o.get("minor_coded")), "nsfw": nsfwish(o)})
    notes = stack_notes([o for _, o, _, _ in top[:6]], used_rows)
    if IS_VIDEO:
        slugs = {o["slug"].lower(): o["slug"] for o in rows}
        for p in picks[:6]:
            sl = p["slug"].lower()
            for x, y in (("high", "low"), ("low", "high"), ("hn", "ln"), ("ln", "hn")):
                if re.search(rf"(^|[-_]){x}([-_]|$)", sl):
                    partner = re.sub(rf"(^|[-_]){x}([-_]|$)", rf"\g<1>{y}\g<2>", sl, count=1)
                    if partner in slugs:
                        p["pair"] = slugs[partner]
                        notes.append(f"Pair <{p['slug']}> (high/low-noise) with <{slugs[partner]}>.")
                    break
    if any(p["minor_coded"] for p in picks):
        notes.append("Flagged minor_coded picks are SFW-only: never pair them with NSFW/anatomy LoRAs or explicit wording.")
    if nsfw_prompt and any(o.get("minor_coded") for o in used_rows):
        notes.insert(0, "Minor-coded LoRA already in an NSFW prompt: SFW-only, remove it or the NSFW wording.")
    result = {"prompt_semantic": q["semantic"], "nsfw_prompt": nsfw_prompt, "already_in_prompt": [u[0] for u in used], "families": fams or "all",
              "suggestions": picks, "by_category": {c: [o["slug"] for _, o, _ in v] for c, v in by_cat.items()}, "stack_notes": notes}
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0
    print("Prompt reads as: " + ("; ".join(f"{S.CATEGORY_LABEL[c]}: {', '.join(v)}" for c, v in q["semantic"].items()) or "(no category words found)"))
    if used:
        print("Already in prompt: " + ", ".join(f"{n}:{w or '?'}" for n, w in used))
    if nsfw_prompt:
        print("NSFW prompt: minor-coded LoRAs are excluded.")
        bad = [o["slug"] for o in used_rows if o.get("minor_coded")]
        if bad:
            print("WARNING: minor-coded LoRA(s) " + ", ".join(bad) + " are SFW-only: remove them or remove the NSFW/explicit wording.")
    print(f"Families: {', '.join(fams) if fams else 'all'}" + (f" (+ near: {', '.join(fams_near)}, down-weighted)" if fams_near else "") + "\n")
    for i, p in enumerate(picks, 1):
        flags = []
        if p["own"]:
            flags.append("OWN (onemoreepoch)")
        av = p["availability"] or {}
        flags.append("on Graydient" if av.get("graydient") else "NOT on Graydient (" + "/".join(k for k in ("hf", "raid") if av.get(k)) + ")")
        if p["near_family"]:
            flags.append(f"{p['family']} LoRA on another SDXL family: may degrade")
        if p["minor_coded"]:
            flags.append("MINOR-CODED: SFW only")
        if p["other_versions"]:
            flags.append(f"+{p['other_versions']} other versions")
        trig = ", ".join(p["triggers"][:6]) + (" …" if len(p["triggers"]) > 6 else "") if p["triggers"] else "no trigger (registered by slug; use the <slug> only)"
        print(f"{i:2}. <{p['slug']}:{p['weight']}>  [{p['family']} · {p['role']} · {S.CATEGORY_LABEL.get(p['category'], p['category'])}]  score {p['score']}")
        print(f"    why: {' | '.join(p['why'][:4])}")
        print(f"    trigger: {trig}")
        print(f"    weight: {p['weight']} ({p['weight_note']}) · creator: {p['creator'] or 'unknown'} · {' · '.join(flags)}")
        if p["source_url"]:
            print(f"    source: {p['source_url']}")
    if by_cat:
        print("\nBest per category:")
        for c in S.CATEGORIES:
            if by_cat.get(c):
                print(f"  {S.CATEGORY_LABEL[c]}: " + ", ".join(o["slug"] for _, o, _ in by_cat[c]))
    if notes:
        print("\nStacking notes:")
        for n in notes:
            print("  - " + n)
    # proposed block: best per category, max 4, one style, one identity unless asked
    chosen, roles = [], Counter()
    floor = (picks[0]["score"] * 0.25) if picks else 0
    for p in picks:
        if p["score"] < floor or any(w.startswith("adds:") for w in p["why"]):
            continue
        if len(chosen) >= 4:
            break
        if p["role"] in ("style", "identity", "utility") and roles[p["role"]] >= 1:
            continue
        if p["category"] in [c["category"] for c in chosen]:
            continue
        if p["role"] == "identity" and "name match" not in p["why"]:
            continue
        if p["near_family"] or not (p["availability"] or {}).get("graydient"):
            continue
        if (p["minor_coded"] and any(c["nsfw"] for c in chosen)) or (p["nsfw"] and any(c["minor_coded"] for c in chosen)):
            continue
        roles[p["role"]] += 1
        chosen.append(p)
    if chosen:
        block = " ".join(f"<{p['slug']}:{p['weight']}>" for p in chosen)
        trig = ", ".join(dict.fromkeys(t for p in chosen for t in p["triggers"][:3]))
        print("\nProposed addition (test one LoRA at a time):")
        print(f"  {block}" + (f"  {trig}," if trig else "") + " <your prompt>")
    return 0

if __name__ == "__main__":
    sys.exit(main())
