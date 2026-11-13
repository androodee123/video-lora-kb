# Skill: choose a video LoRA

Comprehensive goal→LoRA chooser for MiniMax H3, Wan 2.1 / 2.2 (14B high/low and 5B TI2V), and LTX-2 / 2.3 / 2.5. Prefer **installed** LoRAs (flagged in `families/*` tables and `data/loras.jsonl`) when they cover the goal; otherwise recommend a popular catalog or Hugging Face pack. Adult NSFW LoRAs are in scope — describe them factually.

**Never invent a trigger or a strength.** If the catalog says `not stated`, say so and tune on a short test clip. A general H3 starting range of 0.6–0.9 is only a rule of thumb, not per-file data.

Installed names below use RAID slugs. Catalog / Hugging Face packs use published names and links from the family tables.

---

## How to stack (read this first)

### MiniMax H3

Typical Graydient paths: `omni-eros-new-h3` (I2V from a still), `extend-h3`, `extendturbo-h3`. H3 already emits synchronized audio.

A first-test stack is four slots, one each:

1. Identity *or* style/realism (not both unless you know they agree).
2. One motion or physics helper if the body morphs or the motion jitters.
3. One audio helper if speech is robotic or you need a specific moan/accent.
4. One act LoRA only if the still does not already read as the act.

Do not stack two motion boosters and two realism LoRAs on the first pass. Turbo / few-step packs (`lightx2v/Minimax-h3-Turbo`, `larryvrh/MiniMax-H3-Turbo-Lora`, installed `minimax-h3-turbo-loras-h3`) belong only on turbo workflows.

### Wan 2.1 and Wan 2.2

- **Wan 2.2 14B needs paired HIGH and LOW noise LoRAs** for the same concept when both exist. Same strength on both, high file on the high-noise sampler, low file on the low-noise sampler. Do not mix a high from concept A with a low from concept B.
- Wan 2.1 (`Wan Video`, `Wan Video 14B i2v 480p/720p`, `Wan Video 14B t2v`) does **not** use that split.
- Wan 2.2 5B TI2V (`Wan Video 2.2 TI2V-5B`) is a different graph — do not drop 5B LoRAs into a 14B I2V-A14B workflow.
- Speed LoRAs (LightX2V distill, CausVid, self-forcing) go on the speed/turbo graph, not as a fifth style LoRA on a full-step 14B pass.
- Trigger usually at the front of a natural-language prompt.

### LTX-2 / 2.3 / 2.5

- No high/low pair. One concept LoRA plus, if needed, one official IC-LoRA or camera-control LoRA.
- Match `base` (`LTXV2` vs `LTXV 2.3` vs `LTXV 2.5`) to the workflow when you can. A 2.3 LoRA may or may not behave on 2.5.
- Describe camera and sound in prose; the model already emits audio. Official Lightricks camera-control and IC-LoRAs live on Hugging Face (see recipes 37–45) and are mostly **not** on the RAID.

### Conflicts worth remembering

- Digicam / Y2K texture vs cinematic / teal-orange — pick one look.
- Two character identity LoRAs — pick one, or use a character-swap LoRA instead of stacking.
- Two general motion boosters (e.g. shake-harder + better-motion) — start with one.
- H3 audio LoRAs will not fix Wan or LTX speech.
- A still that already reads as the act often needs less act-LoRA, not more.

---

## Goal recipes

Recipes 1–16 are MiniMax H3, 17–32 Wan, 33–45 LTX, 46–48 cross-family. “Installed” means present on the 13 Nov 2026 RAID snapshot.

### 1. Realistic, less-morphing human motion (H3)

- Installed: `h3-ltx-2-3-ltx2-better-nsfw-motion-h3`, `sss-rank-minimax-h3-smooth-slow-sync-h3`, `grindlg-a-better-grinding-motion-assist-h3`, `motion-speed-mmh3-h3`.
- Catalog (not on RAID): `better-motion-h3` (CivitAI “Better Human Motion H3/LTX 2.5”, stated 0.4–0.8), `motion-repair-h3` (BUNNY continuity repair), `shake-harder-h3` / `shake-harder-ref-h3` (trigger `dynv2`, stated 0.6–0.8), `deeper-h3`.
- Stack: one booster only. Conflict: shake-harder + better-motion together on the first test.

### 2. Breathy moans / pleasure vocals (H3)

- Installed, verified: `jav-moans-audio-only-minimax-h3` (trigger `jpnMoans`).
- Catalog: `moawxx-h3` (female pleasure moans + writhing, stated 0.6–0.85) — curated, not in the snapshot.
- Put the trigger in the spoken/sound part of the H3 prompt. Do not expect this to add English dialogue.

### 3. Less robotic speech / natural face talking (H3)

- Installed but **unverified**, no recorded trigger: `natural-face-speech-minimax-h3`. Still the closest installed “talking face” helper — test it, do not invent a trigger.
- Describe lip motion, breaths, and language in the `detailed_description` / `</d\\>` blocks (see `guides/image-to-video.md`).

### 4. North American accent (H3)

- Installed: `minimax-female-accents-north-american-h3`, page-stated strength **0.4–0.5**. Keep it modest; it is easy to overpower the base voice.

### 5. Frozen-time camera orbit / card spin (H3)

- Installed: `minimax-h3-orb360-cardspin-h3`.
- Catalog / HF: `pablodawson/MiniMax-H3-360-Orbit-LoRA` (FL2VA, same image as both endpoint frames; trigger not stated here). Requires a first-last / FL2VA workflow, not a plain I2V still-to-clip unless the pack says otherwise.

### 6. Locked camera or chase / fisheye POV (H3)

- Installed: `mmh3-locked-stabilization-camera-locked-to-h3`, `crash-zoom-minimax-h3`, `pov-fisheye-immersive-sexy-chasing-track-h-h3`, `smart-glasses-pov-minimax-h3`, `amateur-pov-h3`.
- Catalog: `camera-motion-h3` (trigger `camera motion`) if you need a general camera booster and it is not on RAID.

### 7. Phone / digicam / Y2K nude realism (H3)

- Catalog (not installed): `digicam-h3` (trigger `d1g1cam`).
- Conflict: do not stack with `cinematic-h3`, `real-cinematic-h3`, or `teal-orange-cinematic-h3` on the same pass.

### 8. Cinematic film texture (H3)

- Installed: `teal-orange-cinematic-h3`.
- Catalog: `cinematic-h3`, `real-cinematic-h3` (MiniMax H3 Cinematic / Authentic Cinematic Texture).
- Pick one texture LoRA. Pair with a realism slider only after a baseline.

### 9. Realism slider / skin and detail (H3)

- Installed: `mmh3-realism-slider-h3`, `mmh3-realism-slider-v2-hyperflow-h3-flash-h3` (stated 0.65–0.85 / 0.65–0.90 on the v2 page), `mmh3-detail-slider-h3`.
- Catalog / HF: `fal/MiniMax-H3-Realism-People-LoRA` (Fuzz Puppy notes the trigger `r34l1sm` — use that only as cited there).
- Catalog: `eyes-skin-hands-h3` (trigger `perfe8ct`) for eyes, skin, and hands.

### 10. Few-step / turbo speed (H3)

- Installed: `minimax-h3-turbo-loras-h3` (verified CivitAI turbo pack). `minimax-h3-hardgravy-6-step-turbo-merge-h3` 404'd — unverified.
- HF (very widely used, not necessarily on RAID): `lightx2v/Minimax-h3-Turbo`, `larryvrh/MiniMax-H3-Turbo-Lora`, `drbaph/MiniMax-H3-Turbo-Lora-ComfyUI`, `alibaba-pai/MiniMax-H3-Acc-LoRAs` (PDD, separate FL2VA / Ref2VA 8-step adapters), `Pika-Labs/Pika-H3-Flex` and `Pika-H3-Flex-Turbo-LoRA` (pick the file that matches the base-model mode).
- Only on turbo / flex / PDD workflows. Strength usually not stated — follow the pack’s workflow, not a guessed weight.

### 11. Character swap, keep the motion (H3)

- HF: `akatz-ai/MiniMax-H3-Character-Swap-LoRA` (Ref2VA; Fuzz Puppy recommends V1.5). Not on the RAID snapshot.
- Do not stack a second identity LoRA on top for the first test.

### 12. Load a specific character / identity (H3)

- Installed examples: `candi-h3`, `anabelle-phoenix-h3`, `sophie-minimax-h3`, `milena-belwyn-h3`, NordhavenLove names. Use **one** identity LoRA.
- Browse `families/h3/identity.md` (installed first, then by downloads).

### 13. Breast / body physics and jiggle (H3)

- Installed: `breast-play-jiggle-for-minimax-h3` (stated 0.7–0.8), `minimax-h3-heavy-breasts-physics-v1-h3` (triggers `bbwbounce`, `she shakes her breasts`; stated 0.6), `softbreastmotion-h3` (stated 0.9), `boobslider-minimax-h3` (size slider, not a motion booster).
- Catalog: `boob-physics-minimax-h3-wan2-2-h3` if you need the cross-family physics pack and it is not on RAID.

### 14. Anime / 2D look, or a 2D↔real slider (H3)

- Installed: `2d-anime-style-nsfw-h3` (trigger often `2d anime style` in the skeleton), `minimax-h3-2d-anime-realism-style-slider-h3`, `bobby-s-general-purpose-h-anime-h3` (trigger `2D-animated`), crayon / manga-tone / analog packs in `families/h3/style.md` and `anime.md`.
- Conflict: a hard 2D style LoRA vs a realism slider — pick a direction.

### 15. Age slider or subtle temporal look (H3)

- Installed: `mmh3-video-age-slider-h3`. Strength not stated — inch it, do not slam it.

### 16. Object interaction / fewer through-body errors (H3)

- HF: `LiconStudio/Minimax-H3-VBVR` (image-to-video reasoning / cleaner interactions). Not on the RAID snapshot. Use when hands and props clip or duplicate.

### 17. Wan 2.2 high/low pairing (general)

- Whenever the row’s `files` (or installed filenames) include `HIGH` and `LOW` / `high_noise` and `low_noise`, load both at the same strength.
- Installed pairs: Tentacled v2.1 high/low (sidecars present), futa cowgirl high/low, plus unverified sidecar-only pairs `Fondled_*`, `wan22_i2v_futa_missionary_*`, `xMilkDuctXrayx_*`.
- Local `b7_test1_wan22_t2v_f17_high_*` is **high-noise only**, trigger `b7vhs`. Prefer the final `..._high_noise.safetensors`. There is no matching low from that run.

### 18. Faster Wan 2.2 / 2.1 (distill, LightX2V, CausVid, self-forcing)

- HF: `lightx2v/Wan2.2-Distill-Loras` (and `Wan2.2-Distill-Models` — some files are full models, not LoRAs; only use the LoRA files), `lightx2v/Wan2.1-Distill-Loras`.
- CausVid: `lightx2v/Wan2.1-T2V-14B-CausVid`. Self-forcing / AccVid packs circulate under Kijai-related repos; confirm the filename is a LoRA before hanging it on a graph.
- Graydient: `animate-wan22` / `video-wan22` (supports LoRAs). Rapid-all-in-one (`Phr00t/WAN2.2-14B-Rapid-AllInOne`) is a fused checkpoint, not a LoRA — do not treat it as a stackable adapter.

### 19. Wan camera: orbit, dolly zoom, snapshot lens (Wan)

- Catalog: `VERTIGO - (Perfect DollyZoom)` (Wan 2.1 t2v and 2.2 T2V-A14B versions). Trigger not stated here unless the row has one.
- Catalog: `[WAN2.2] Smartphone Snapshot Photo Reality [STYLE]` for phone-look T2V.
- Installed Wan set is thin on dedicated camera LoRAs; `drift-stop-from-close-up-face-wan2-2-i2v-a-wan` is a specific I2V camera move (Akira-style drift stop), not a general orbit.

### 20. Wan I2V 14B vs T2V 14B vs 5B TI2V

- Match `base`: `Wan Video 2.2 I2V-A14B` → I2V graph (`animate-wan22`); `Wan Video 2.2 T2V-A14B` → T2V (`video-wan22`); `Wan Video 2.2 TI2V-5B` → 5B TI2V only.
- Installed 5B: `wan2-2-5b-i2v-shower-safetensors-wan`, `wan2-2-5b-ti2v-genitalhelperv022-safetenso-wan`.

### 21. Wan 2.1 480p vs 720p I2V

- Installed 2.1 example: `wan2.1-i2v-480p-flaccid-v1.0` (sidecar trigger present). Do not hang it on a 2.2 14B high/low pair.
- Catalog 720p I2V uses `Wan Video 14B i2v 720p`. Check the row’s `base` before downloading or recommending.

### 22. General NSFW motion on Wan 2.2 I2V (catalog)

- Popular catalog pack: `lopi999/Wan2.2-I2V_General-NSFW-LoRA` (Hugging Face; also mirrored widely). Use the high/low files if the pack publishes both. Triggers: only those on the model card — do not invent.
- Installed `quorum-general-nsfw-for-wan-2-2-i2v-a14b-wan` is the on-RAID general NSFW 2.2 I2V option.

### 23. Wan act LoRAs already on RAID (cowgirl, doggy, blowjob, etc.)

- Installed act files include cowgirl, reverse-cowgirl, doggystyle, standing sex, side/spoon, handjobs, blowjobs, twerking, dildoing, facial/cumshot packs. Many are single-file Wan 2.1-era or unpaired 2.2 — read `base` and whether a high/low mate exists.
- Triggers: prefer the sidecar or catalog `triggers` field. Several older skeleton rows use the slug as the trigger; if `triggers` is empty, say not stated.

### 24. Wan identity / character

- Browse `families/wan/identity.md` (large; sorted by downloads). Installed identity is thin (`belle-delphine-t2v-i2v-wan-14b-wan` is on RAID but its CivitAI id 404'd — unverified).
- One character LoRA at a time. For 2.2, use the high/low pair of *that* character if published.

### 25. Wan anime or 2D style

- See `families/wan/anime.md` and `style.md`. Installed Wan style is almost empty; plan on a catalog style LoRA (smartphone-reality, anime packs). Do not combine two strong style LoRAs.

### 26. Wan realism / live-action look

- Catalog: smartphone-snapshot style (recipe 19), plus `families/wan/realism.md`. Strength only if the row states it.

### 27. Wan body physics / breast play (catalog)

- High-download catalog: `Wan2.2 - Breast Play (I2V)` (CivitAI 1913617). Use the published I2V-A14B high/low files. Triggers/strength: only as on the page.

### 28. Wan effects / VFX

- Catalog examples include special-effect character packs and stylized FX in `families/wan/effects.md`. Installed Wan set has no dedicated VFX LoRA.

### 29. Wan transitions

- Few dedicated transition LoRAs (`families/wan/transitions.md`). If the row is empty of triggers, describe the transition in the prompt rather than inventing a token.

### 30. Wan lighting

- Thin category. Prefer prompt lighting, or an H3 teal-orange / cinematic LoRA if you are on H3 instead.

### 31. Wan reward / quality LoRAs (HF)

- `alibaba-pai/Wan2.2-Fun-Reward-LoRAs` and `Wan2.1-Fun-Reward-LoRAs` (also `Kijai/Wan2.1-Fun-Reward-LoRAs-comfy`). These are quality/reward adapters, not style packs. Follow the pack’s suggested graph; strength not stated here.

### 32. Local Wan look probe (VHS / 90s tape)

- Installed: `b7_test1` high-noise T2V, trigger `b7vhs`. Example from the sidecar README: `b7vhs, three women in a dark brick dungeon, white lingerie, locked-off wide shot, they slowly move together`. No low-noise mate.

### 33. LTX taker POV

- Installed: `LTX-2_takerpov_lora_v1.2` (trigger `taker pov`, stated weight **0.8–1.0**). Describe the taker’s viewpoint in the prompt as well.

### 34. LTX official camera control (dolly, jib, static) — not on RAID

- HF, LTX-2 19B: `Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-In`, `...-Dolly-Out`, `...-Dolly-Left`, `...-Dolly-Right`, `...-Jib-Up`, `...-Jib-Down`, `...-Static`.
- Use one camera-control LoRA at a time. Strength not stated in this catalog — follow Lightricks’ card.

### 35. LTX sexy / thrust / swing motion (installed)

- Installed: `LTX2-i2v-SexyMove` (trigger `sexy`; page-stated strength **0.2–0.91**, with 0.75–0.8 called the best zone), `LTX2-i2v-SexThrust`, `ltx23-i2v-swing-in-out-os`, `ltx23-i2v-swing-up-down-os`.
- Start SexyMove around the stated best zone, not at 0.91.

### 36. LTX body physics / better breasts (catalog)

- Catalog: `LTX 2.3 - I2V Better Physics PhysLTX`, `LTX 2.3 - I2V Better Breasts motion and jiggle`. Triggers/strength only if the row has them.

### 37. LTX anime / flat / retro style

- Installed: `animeflatLTX.2.3` (same family as CivitAI “Anime Flat Style”, LTX 2.3 file), `retro-anime-mix-by-shrekman-ltx2`, `pvc-anime-figures-ltx-2-3-ltx2`.
- Catalog: Posing Dynamics (`PosingDynamicsDaal`), 90s anime style (`ANIMSTY`, …) in `families/ltx/anime.md` / `style.md`.

### 38. LTX realism / amateur look

- Catalog: `phool-realism-ltx-2.3-v1.0` (trigger `realism`), `Amateur Hour`. Installed `warped-female-body-parts-for-ltxv-2-5-ltx2` is a body-shape pack, not a general realism slider.

### 39. LTX restore, refine, upscale, SDR→HDR (official IC-LoRAs, HF)

- `Lightricks/LTX-2.5-22b-IC-LoRA-Restore`, `...-Refine-Details`, `...-Pixel-Spatial-Upscaler`, `...-SDR-To-HDR`, plus 2.3 Deblur / Decompression / Colorization cousins.
- These are **video-to-video IC-LoRAs** with a supplied workflow, not I2V style LoRAs. Do not stack them on a generative I2V act LoRA as if they were the same slot.

### 40. LTX clean plate / object removal / alpha / ingredients (HF)

- `Lightricks/LTX-2.5-22b-IC-LoRA-Clean-Plate` (and the 2.3 Clean-Plate), `...-Alpha-Gen`, `...-Ingredients` (reference sheet of characters/props; V2 on 2.5 can take audio refs in the official nodes).
- Use the official Comfy graph. Strength not stated here.

### 41. LTX relight, day-to-night, water, slow-mo, cinemagraph (HF)

- `Lightricks/LTX-2.3-22b-IC-LoRA-Relight`, `LTX-2.5-22b-IC-LoRA-Day-To-Night`, `...-Water-Simulation`, `LTX-2.5-22b-LoRA-Slow-Motion-Control`, `LTX-2.5-22b-LoRA-Cinemagraph`.
- One IC/control LoRA per pass unless the official workflow says otherwise.

### 42. LTX layout-to-render / in-outpaint / edit-anything (HF)

- `Lightricks/LTX-2.5-22b-IC-LoRA-Layout-To-Render`, `Lightricks/LTX-2.3-22b-IC-LoRA-In-Outpainting`, plus community `Alissonerdx/EditAnything` (in the Fuzz Puppy directory). Instruction-based or layout-based; not a style LoRA.

### 43. LTX Foley / audio-reactive (HF, not on RAID)

- `FuzzPuppy/LTX-2.3-Foley-LoRA`, `fal/ltx2.3-audio-reactive-lora`. LTX already emits audio; these steer Foley or reactive motion. Strength not stated here.

### 44. LTX 3D-real / product / body-positive looks (HF / catalog)

- `fal/LTX-2.3-3DREAL-LoRA`. Other utility looks (body positivity, product-ad) are in the Fuzz Puppy guide. Not on the RAID snapshot.

### 45. LTX face / head swap and multi-subject reference (HF)

- Fuzz Puppy / HF: `Alissonerdx/BFS-Best-Face-Swap-Video`, `Alissonerdx/LTX-Best-Face-ID`, `LiconStudio/LTX-2.5-Multiple-Subject-Reference` (and the 2.3 variant). For identity consistency, prefer these official-style packs over stacking two character LoRAs.

### 46. Same act, pick a family (cross-family)

- If you need **dialogue and breaths**, start on **H3** (`omni-eros-new-h3`) and use recipes 2–4.
- If you need **Wan 2.2 I2V from a strong still** and a high/low act pair, use Wan (recipes 17, 22–23).
- If you need **native audio plus official camera/IC control**, use LTX 2.3/2.5 (recipes 33–34, 39–41).
- Do not mix an H3 LoRA into a Wan graph or a Wan high-noise LoRA into LTX.

### 47. “Make it look expensive” without changing the act

- H3: one realism or cinematic LoRA (recipes 8–9), maybe a detail slider, no second style.
- Wan: smartphone-snapshot or a realism row, plus an optional reward LoRA on a compatible graph (recipe 31).
- LTX: official Refine-Details or a realism trigger LoRA (recipes 38–39), not a second anime style.

### 48. “The motion is broken / jittery / looping badly”

- H3: one of recipe 1 (`sss-rank`, `motion-repair-h3`, `better-motion-h3`). Shorten the action in the prompt (one squeeze, one stroke).
- Wan: confirm high/low are a matching pair at the same strength; drop extra act LoRAs.
- LTX: drop to one motion LoRA (SexyMove in its best zone, or official Slow-Motion-Control for time stretch). Check you are on the matching 2 / 2.3 / 2.5 base.

---

## Where to look next

- Tables: `families/h3/`, `families/wan/`, `families/ltx/` — installed first, then by downloads.
- Prompt shapes: `guides/image-to-video.md`.
- Official utility directory: `guides/fuzzpuppy-directory.md`.
- New CivitAI uploads: `python3 scripts/check_new.py` (proposal markdown only, no downloads).
