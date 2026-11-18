#!/usr/bin/env python3
"""Regenerate guides/prompt-matching.md: worked examples of scripts/suggest.py on real catalog slugs.
Run after build_semantic.py (update.py does this weekly). Metadata only."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IS_VIDEO = (ROOT / "scripts" / "video_lora.py").exists()

IMAGE = [
    ("Photoreal phone selfie (Krea2, detailed-krea2)", "krea2",
     "photoreal amateur phone selfie of a tanned woman in a red bikini on a beach at golden hour, freckles, smiling", ""),
    ("Andrew's own style LoRA (Anima)", "anima",
     "kiwinestyle comic pin-up, curvy woman with lavender hair in a cowboy hat and pink coat, speech bubble, screentones", ""),
    ("Fantasy character, tag prompt (Pony)", "pony",
     "score_9, score_8_up, 1girl, dark elf, silver hair, bikini armor, holding sword, from below, angry, fantasy forest", ""),
    ("Latex + pose + expression (Illustrious/NoobAI)", "illustrious",
     "1girl, black latex catsuit, high heels, kneeling, looking at viewer, smirk, neon lights, night city", "glossy fetish fashion look"),
    ("Outfit-first: plugsuit-style bodysuit, adult original character (Illustrious/NoobAI)", "illustrious",
     "adult woman, mature female, white and red plugsuit, form-fitting bodysuit, standing in a sci-fi hangar, anime", "get the plugsuit outfit without a character LoRA"),
    ("Noir boudoir (MOSS, kromoss)", "moss",
     "score_9, best quality, woman in a black corset and fishnet stockings sitting on a velvet chair, low-key lighting, film noir", ""),
]
VIDEO = [
    ("POV ride with body physics (H3)", "h3",
     "POV cowgirl, a busty redhead woman riding and bouncing, breasts jiggling, moaning, slow push-in camera, phone footage look", ""),
    ("Dance with camera orbit (Wan 2.2)", "wan",
     "woman doing a slow 360 orbit dance in a neon club, hair swaying", ""),
    ("Talking head, natural speech (H3)", "h3",
     "close-up of a woman talking to the camera, natural lip sync, subtle smile, soft window light", "less robotic speech"),
    ("LTX motion", "ltx",
     "woman swinging her hips while walking toward the camera, slow motion, cinematic lighting", ""),
]

def run(prompt, base, intent):
    cmd = [sys.executable, str(ROOT / "scripts" / "suggest.py"), prompt, "--base", base, "--top", "6", "--json"]
    if intent:
        cmd += ["--intent", intent]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(r.stdout)

def main():
    ex = VIDEO if IS_VIDEO else IMAGE
    L = ["# Prompt → LoRA matching (worked examples)", "",
         f"Generated {datetime.now().strftime('%Y-%m-%d')} by `scripts/matcher_examples.py` from `data/semantic_catalog.jsonl` "
         "(real slugs; rerun after the weekly update). Reproduce any example with the command shown.", "",
         "Read each pick's *why* before adding it: the matcher ranks by shared words and semantic tags, not by looking at images. "
         "Triggers are copied from the source; an empty trigger means the LoRA is registered on Graydient by slug only. "
         "Weights marked *default* are workflow defaults, not source-stated values.", ""]
    for title, base, prompt, intent in ex:
        res = run(prompt, base, intent)
        cmd = f'python3 scripts/suggest.py "{prompt}" --base {base}' + (f' --intent "{intent}"' if intent else "")
        L += [f"## {title}", "", "```bash", cmd, "```", "",
              "Prompt reads as: " + "; ".join(f"{k}: {', '.join(v)}" for k, v in res["prompt_semantic"].items()), "",
              "| # | LoRA | role | why it matches | trigger | weight |", "|---:|---|---|---|---|---|"]
        for i, p in enumerate(res["suggestions"], 1):
            flag = " (own)" if p["own"] else ""
            trig = ", ".join(p["triggers"][:3]) or "— (slug only)"
            why = "; ".join(w for w in p["why"][:3]).replace("|", "/")
            note = "source" if p["weight_note"].startswith("source") else "default"
            L.append(f"| {i} | `<{p['slug']}:{p['weight']}>`{flag} | {p['role']} | {why} | {trig.replace('|', '/')} | {p['weight']} ({note}) |")
        if res["stack_notes"]:
            L += ["", "Stacking notes: " + " ".join(res["stack_notes"])]
        L.append("")
    (ROOT / "guides").mkdir(exist_ok=True)
    (ROOT / "guides" / "prompt-matching.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote guides/prompt-matching.md")

if __name__ == "__main__":
    main()
