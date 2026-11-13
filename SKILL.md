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

Recipes 1–16 and 49–64 are MiniMax H3, 17–32 and 65–78 Wan, 33–45 and 79–90 LTX, 46–48 and 91–96 cross-family (96 recipes). “Installed” means present on the 13 Nov 2026 RAID snapshot. Prompt templates: `guides/prompt-patterns.md`.

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

### 49. Talking head / lipsync (H3)

- Installed but **unverified**, no recorded trigger: `natural-face-speech-minimax-h3`. Test it; do not invent a trigger.
- Catalog: `nafasp_h3_lora_v2_500` (Natural Face & Speech H3/LTX 2.5, stated **0.6–0.8**); `aswhm_lora_v1_500` (ASMR Whisper Audio, stated **0.6–0.8**); Kokoro female voices (stated **0.5–0.7**).
- Put dialogue in the H3 `</d\\>` block and describe lip motion and breaths. Conflict: a moan LoRA will not add clear English speech.

### 50. Character consistency across an H3 clip

- Start with a complete `retention_analysis` (see `guides/prompt-patterns.md`). Add **one** installed identity LoRA (recipe 12) if you have it.
- To change the face but keep motion: recipe 11 (`akatz-ai/MiniMax-H3-Character-Swap-LoRA`, Ref2VA; not on RAID). Catalog face-swap: `FaceSwap - MiniMax REF2VA` (trigger `Faceswap`); `BFS - Best Face Swap` uses a structured `body_swap` / subject-definition trigger — follow the page, do not invent one.
- Conflict: two identity LoRAs, or swap + a second character LoRA on the first test.

### 51. Pose or ControlNet guidance (H3)

- HF (not on RAID): `MiniMax-H3-Fun-Controlnet-Union` / `Union-2.0` — use the pack’s control input. Strength not stated.
- Installed pose-like: `Jacko pose minimax h3 v1` (trigger not stated). Catalog: `ADD SexyPose H3` (trigger `sexypose`); `BLACKED Style — Cowgirl Pose [MiniMax H3 Ref2VA]` (trigger not stated; Ref2VA graph); `Genshin-like ultimate burst poses` (trigger `ulti`).
- Drive the pose in the action sentence; do not stack two pose LoRAs.

### 52. Lighting, caustics, relight (H3)

- Installed: `Underwater Sunlight Caustics & Ocean Refraction Slider` (trigger not stated).
- Catalog / texture already in recipes 7–8 (`teal-orange-cinematic-h3` installed). Pick one lighting/texture direction.
- Conflict: caustics/underwater look vs dry cinematic teal-orange on the same pass.

### 53. First-last / FL2VA transitions (H3)

- Frozen-time orbit is recipe 5 (`minimax-h3-orb360-cardspin-h3`; HF `pablodawson/MiniMax-H3-360-Orbit-LoRA` needs first-last frames).
- 2D↔real transformation catalog: `Realistic → Anime Transformation | MiniMax H3` (trigger `anime_tx`, stated **0.8–1.0**) — that is a look change, not a scene cut.
- Do not treat a plain I2V still as a first-last transition.

### 54. Cloth and hair motion (H3)

- Catalog hair: `Minimax H3: t2va (T2V) – Polyhedron: Better Hair` (triggers `ha8ir`, `perfect hair`, `thick hair`, `airy volume`, `natural`; stated **0.6–0.7**). That pack is T2VA — check `i2v_t2v` before using it on I2V.
- Installed: `Latex clothes Minimax H3` (trigger `latex,`); `hair pulling h3 101` (trigger not stated).
- Catalog: `[Invisible person / Living clothes]` (triggers `living clothes`, `magic clothes`, `livingclothes`, `invisible`; stated **0.6–0.9**).

### 55. Water, fire, smoke / elemental VFX (H3)

- Installed: underwater caustics (recipe 52). Catalog: `Water Foam World`; `KinetiX Elemental VFX Suite`; `KinetiX Ghost Rider Hellfire Wheels & Molten Ground Concept Slider`. Triggers and strengths for those catalog rows are `not stated` unless the family table records them after enrichment — do not invent any.
- Keep to one VFX LoRA; describe the element in prose.

### 56. Sharper / upscaled H3 video

- Catalog: `Minimax H3 Image Upscaler (LORA + Workflow & Batch)` (trigger not stated); `Sharper Video` (stated **1** / **1.0**).
- These are post / tool LoRAs, not style LoRAs. Do not stack with a turbo pack unless the upscaler workflow says to.

### 57. Stereo / depth video (H3)

- Catalog: `Real Stereo Depth Video - H3 Minimax` (stated **1**). Trigger not stated. This is a depth/stereo helper, not a pose ControlNet.

### 58. JOI gesture (H3)

- Installed: `minimax-joi-gesture-h3` (stated **0.6–0.8**). Trigger not stated. Describe the pointing / looking-at-camera gesture in `detailed_description`.

### 59. Pegging (H3)

- Installed: `minimax-pegging-h3` (stated **0.5–0.8**). Trigger not stated. If the still already reads as the act, start at the low end of the stated range.

### 60. Cum / finish / squirt (H3)

- Installed: `hmsquirt-squirting-for-minimax-h3` (trigger `hmsquirt`, stated **0.4–0.8**), `h3-edge-time-h3` (stated **1**), `h3-throat-time-h3` (stated **1.0**). Triggers for the last two are not stated.
- One finish LoRA at a time. Conflict: stacking edge-time + throat-time + squirt on the first test.

### 61. Penis detail / futa helpers (H3)

- Installed: `dirtylarry-s-dick-detailer-h3` (stated **1**; trigger not stated). Other futa / condom-stroke helpers are in `families/h3/nsfw-acts.md` (installed first).
- Pair with one act LoRA, not a second detailer.

### 62. Face-slap motion (H3, Ref2VA)

- Installed: `face-slap-motion-minimax-h3-ref2va-h3` (trigger `f4c3sl4p`, stated **1.0**). Requires the Ref2VA graph, not a plain I2V still-to-clip unless the page says otherwise.

### 63. Bursting / wardrobe break (H3)

- Installed: `bursting-out-minimax-h3` (trigger `brstingout`, stated **0.75**). Describe a single burst, not a long sequence of costume changes.

### 64. Hair-pulling motion (H3)

- Installed: `hair pulling h3 101` (trigger not stated). Catalog may list other hair-pull acts; use the family table. Strength not stated — short test clip.

### 65. Talking / lipsync on Wan

- Do not use H3 audio LoRAs. Wan rows tagged lipsync/speech are listed in `families/wan/lipsync.md` and `audio.md` when present. If the row’s trigger and strength are `not stated`, describe mouth motion in prose and test.
- Conflict: expecting a Wan act LoRA to fix lip sync.

### 66. Character or clothing consistency (Wan)

- Catalog: `ClothConsistency-Wan2.2-I2V-ConsistencyLoRA2` (I2V; recorded intent is clothing consistency with the first frame; strength not stated).
- Identity: recipe 24, one character LoRA. Face/head swap catalog: `BFS - Best Face Swap` (Wan trigger recorded as `head_swap:`, stated **0.7–1.0** on the Wan version). Follow the page’s subject-definition pattern.

### 67. Object interaction / living clothes (Wan)

- Catalog: `[Invisible person / Living clothes] WAN2.1 T2V I2V 14B` (triggers `invisible`, `living cloth`, `living clothes`, `magic cloth`; stated **0.75–1.0**). Match 2.1 vs 2.2; this page is Wan 2.1.
- Catalog typography / object: `ObjectTypo-Redmond-T2V-14B` (trigger `ObjectTypography`, strength not stated).
- Describe the held or transforming object in the action clause. Through-body errors: drop extra act LoRAs before adding a second object pack.

### 68. Pose control (Wan)

- Catalog poses (triggers as recorded; strengths mostly `not stated`): Paw Pose (`paw pose`, `panting` on 2.1; a 2.2 I2V/T2V variant uses a longer “moves into a paw pose…” phrase — use the row that matches the base), `Arched Back Pose` (`sensual back arch`), `Most Muscular/Crab Flex` (`most muscular pose`), `Ab Crunch Pose` (`ab crunch pose`), `Front Lat Spread Pose`, `Full Extension Split Pose`, `WAN2.2_T2V_14b - Female Bodybuilder Pose`, `Pronebone Poses - XL` (trigger starts `pronebone sex…`).
- One pose LoRA. Match 2.1 vs 2.2 and I2V vs T2V.

### 69. Underwater / submerge (Wan)

- Catalog: `Wan 2.2 T2V Motion (High & Low Noise) – Polyhedron: Submerge` (triggers `submer8ge`, `underwater`, `caustics`, `open water`, `swimming`; high/low pair). Strength not stated — same value on both noises.
- Other underwater style rows exist (`Freedive girls`, `Underwater`) with triggers `not stated` or as in the table. Do not put a 5B LoRA on this 14B T2V pair.

### 70. Fire and smoke (Wan)

- `Realistic Fire (Wan2.1 T2V LoRA)`: trigger `[r3al_f1re]`, stated **1.0**.
- `Realistic Fire Wan 2.2 I2V 5B`: trigger `fire`, stated **0.8**. **5B TI2V only**.
- Catalog also: `Colored smoke effects-wan2.1`, `Shadow smoke` (trigger `<shadow>`), `Morph From The Influence Of Smoke` (trigger `5M0K3 EFFECT`). Strengths not stated unless the table says so.
- Match base. One element LoRA.

### 71. Dissolve / melt transition (Wan)

- Catalog: `Melt It (Acid Dissolve) I Wan 2.1 I2V` (triggers `m3lt1ng` plus a long demo sentence on some rows; stated **1**). Wan 2.1 I2V — do not assume 2.2 high/low behavior.

### 72. Wan upscale tool

- Catalog: `[LuisaP] WAN 2.2 UPSCALER [TOOL]` (trigger `upscale this video`, strength not stated). Use as a tool pass, not as a style LoRA on a generation graph.

### 73. Stereo / depth (Wan)

- Catalog: `Real Stereo Depth Video - WAN 2.2 I2V` (trigger and strength not stated). Separate from pose/depth ControlNet packs.

### 74. Bullet time / hero-run camera FX (Wan)

- Catalog Wan 2.1 I2V: `Matrix Bullet Time Camera Effect` (trigger `b4ll3t t1m3 bullet time shot`, stated **1.0**); `Hero Run Effect` (trigger `4ct3ion Action Run`, stated **1.0**).
- Conflict: a general orbit/dolly LoRA plus bullet-time on the first test. 2.1 LoRAs are not a free upgrade to 2.2 high/low.

### 75. Clothing tightness / ripped clothes (Wan)

- Catalog: `Clothing Tightness Slider (Wan2.2)` (trigger not stated); `Ripped Clothing - Wan` (triggers `ripped`, `ripped and frayed`); `Wet Translucent clothes (Wan t2v)` (triggers `w3tcl0`, `wet clothes`, `Translucent clothes`, …). Strengths not stated unless the table records them.
- One wardrobe-modifier LoRA.

### 76. Using a Wan 2.1 LoRA on a 2.2 graph (or the reverse)

- Do not assume cross-use. If you try it anyway, keep a short test, do not invent a high/low twin for a 2.1 file, and do not drop a 5B TI2V LoRA into 14B (or a 480p I2V LoRA into a 720p / 2.2 sampler) without a recorded reason.
- Prefer the row whose `base` / `bases` match the workflow (recipes 20–21).

### 77. Wan audio / accent / Foley

- H3 moan and accent LoRAs will not transfer. Use only Wan-family audio rows in `families/wan/audio.md`. If triggers/strengths are `not stated`, describe the sound in prose and test. Official LTX Foley packs are LTX-only (recipe 43).

### 78. Macromastia / clothed body (Wan)

- Catalog: `Macromastia (Clothed)` (trigger `macromastia`, stated **0.5–1** / **0.5–1.0** / **0.3–0.5** — use the stated range from the matching version, not a guess). Start mid-range and test. Conflict: a size slider plus a second body-physics pack on the first pass.

### 79. Lipsync / dubbing (LTX)

- HF / catalog: dubbing and lip-sync LoRA for LTX-2.3 (speech-performance transfer). Strength and trigger often `not stated` — follow the pack card.
- Describe the line and mouth motion in prose (`Audio:` sentence). Do not use an H3 speech LoRA on LTX. Natural Face & Speech also has an LTX 2.5 version (`nafasp_ltx_25_500`, stated **0.6–0.8**).

### 80. Character consistency / multi-reference (LTX)

- HF official / community: identity in-context LoRA for LTX-2.3; packs that combine up to five visual references for consistent characters and objects; multi-subject reference (two to five images). Strengths usually `not stated`.
- Supply the reference images the card asks for. Conflict: two character LoRAs plus a style LoRA on the first test. Face/head swap is recipe 45.

### 81. Pose and depth control (LTX)

- HF official: `LTX-2-19b-IC-LoRA-Pose-Control`, `LTX-2-19b-IC-LoRA-Depth-Control`, `LTX-Video-ICLoRA-pose-13b-0.9.7`, `LTX-Video-ICLoRA-depth-13b-0.9.7`. These need a control video / map, not a prompt tag you invent.
- Catalog helpers: `(LTX-2.3 Lora) - Pose Helper (I2V)` (trigger not stated); `Front Lat Spread Pose` (trigger `FrontLatSpreadPose`); `LTX-2.3 Most Muscular Pose LoRA` (trigger `mm_pose`).
- Match 2 / 2.3 / 2.5 and I2V vs the IC-LoRA graph.

### 82. Slow motion vs floaty-motion reduction (LTX)

- Official: `LTX-2.5-22b-LoRA-Slow-Motion-Control` and the 2.3 counterpart (recipe 41). Catalog slider: `LTX 2.3 – Slow Motion & Floaty Movement Reducer Slider` (trigger not stated).
- Say whether you want time stretched or more natural timing. Conflict: Slow-Motion-Control + SexyMove + a second motion booster together.

### 83. Hard cut / cinematic transition (LTX)

- Catalog: `LTX-2.3_Cinematic hardcut` (stated **0.2–1.0**, trigger not stated). Start mid-range. This is not a dissolve (Wan Melt It is a different family).

### 84. LTX 2.3 vs 2.5 (and LTXV2) cross-use

- Match `base` to `animate-ltx2` / `animate-ltx23` / `animate-ltx25` (or the T2V `video-ltx*` slugs) when you can. A 2.3 LoRA may or may not behave on 2.5; official IC-LoRAs are often version-specific (2.3 relight vs 2.5 water/upscaler).
- Installed SexyMove and taker POV: check the row’s `base` (recipes 33, 35).

### 85. Watermark / subtitle removal (LTX)

- Catalog: `Watermark and Subtitle Remover` (trigger and strength not stated). Tool pass, not a style LoRA. Official clean-plate / object-removal IC-LoRAs are recipe 40.

### 86. LTX image / spatial upscaler

- Official IC-LoRAs: `LTX-2.5 22B IC-LoRA Pixel Spatial Upscaler`, `LTX-2.3-22b-IC-LoRA-Pixel-Spatial-Upscaler`, older `ltxv-spatial-upscaler-0.9.7`. Catalog: `LTX 2.3 - LTX Image Upscaler (LORA + Workflow)`.
- Strengths usually `not stated`. Use on the upscaler / IC graph, not as a fifth style LoRA on a generate pass.

### 87. Bouncy walk / body physics add-on (LTX, also Wan)

- Catalog: `Bouncy Walk - LTX / Wan I2V 14B` (triggers include `walking into the direction of the moving camera`, stated **0.75**). Versions exist for LTX 2.3 and Wan — pick the family that matches the graph.
- Other LTX physics: recipe 36 (`D4S1W4_NSFWSME` **0.5–1.0**; BBW `j1ggle` / `bounce` **0.6–1**).

### 88. Wind / melt / surreal LTX effects

- Catalog: `Lana_Wind_Motion_LTX` (stated **0.8–1**, trigger not stated); `Melting | Surreal Dissolution Effects - LTXV 13b` (trigger `Melting`, stated **1.0**). Check `base` (older LTXV vs 2.3 / 2.5). One effect LoRA.

### 89. Installed LTX multi-purpose NSFW

- Installed: `LTX 2/2.3 [I2V] NSFW (+furry) - Multi purpose sex lora` (trigger `ltx2 nsfw+furry`, strength not stated). Use with one additional motion helper at most (SexyMove in its **0.75–0.8** best zone if needed).
- Browse `families/ltx/nsfw-acts.md` for more installed acts.

### 90. CrossView / alternate camera IC-LoRA (LTX)

- Catalog: `CrossView IC-LoRA for LTX 2.3 22B` (trigger `Crossview`, stated **1**). This is an IC-LoRA — use the pack’s control/prompt pattern, not a plain I2V still unless the card says that works.

### 91. Lipsync: pick a family

- H3: recipe 49 (structured dialogue block; Natural Face & Speech **0.6–0.8** when using the catalog version).
- LTX: recipe 79 (2.3 dubbing/lip-sync pack, or `nafasp_ltx_25_500` **0.6–0.8**).
- Wan: recipe 65; do not borrow H3 or LTX audio LoRAs.
- The still should already show a near-frontal face when you care about mouth lock.

### 92. Character consistency: pick a family

- H3: recipe 50 (retention block + one identity, or Ref2VA swap).
- Wan: recipe 66 (cloth-consistency LoRA and/or one character LoRA; BFS `head_swap:` **0.7–1.0** on the Wan version).
- LTX: recipe 80 (identity / multi-ref IC-LoRAs).
- Conflict in every family: two identity LoRAs at once.

### 93. Pose or ControlNet: pick a family

- H3: recipe 51 (Fun ControlNet Union, or a named pose LoRA).
- Wan: recipe 68 (named pose LoRAs; match 2.1/2.2).
- LTX: recipe 81 (official pose/depth IC-LoRAs or Pose Helper).
- Official IC / ControlNet packs need their control input. A trigger-only pose LoRA does not replace a pose map.

### 94. Object interaction: pick a family

- H3: recipe 16 (`LiconStudio/Minimax-H3-VBVR`) and catalog `Swallowing Object` (stated **0.75–1**, trigger starts `She inserts the [object] inside her mouth…` — use the recorded wording, filling only the object slot the page leaves open). Installed `Vaginal object delivery` has a recorded delivery trigger in the table.
- Wan: recipe 67 (living clothes **0.75–1.0** on 2.1; ObjectTypo).
- LTX: official clean-plate / ingredients / edit packs (recipe 40) and prompt-based object-edit LoRAs; strength often `not stated`.

### 95. Fire, water, smoke: pick a family

- H3: recipe 55 + caustics (52).
- Wan: recipe 70 (fire **1.0** on 2.1 T2V with `[r3al_f1re]`; **0.8** on 2.2 I2V 5B with `fire`) and recipe 69 (submerge).
- LTX: official water-simulation IC-LoRAs (recipe 41). Do not cross-load these packs across families.

### 96. The still already looks right, but T2V would have to invent the person

- Prefer I2V (H3 `omni-eros-new-h3`, Wan `animate-wan22`, LTX `animate-ltx2` / `23` / `25`) and spend the prompt on action, camera, and sound — not on re-describing the face.
- Use T2V (`video-h3`, `video-wan22`, `video-ltx*`) only when there is no still, and then write a full appearance description. Identity LoRAs help T2V more than a good I2V still does.
- FL2VA / first-last / Ref2VA packs still need their extra frames (recipes 5, 11, 53).

---

## Where to look next

- Tables: `families/h3/`, `families/wan/`, `families/ltx/` — installed first, then by downloads.
- Prompt shapes: `guides/image-to-video.md` and per-family templates in `guides/prompt-patterns.md`.
- Official utility directory: `guides/fuzzpuppy-directory.md`.
- New CivitAI uploads: `python3 scripts/check_new.py` (proposal markdown only, no downloads).
