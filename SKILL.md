# Skill: choose a video LoRA

Comprehensive goal→LoRA chooser for MiniMax H3, Wan 2.1 / 2.2 (14B high/low and 5B TI2V), and LTX-2 / 2.3 / 2.5. Adult NSFW LoRAs are in scope — describe them factually.

**Recommend available Graydient LoRAs first.** Every LoRA in this skill's available set is a Graydient LoRA. Recipes label each pick **on Graydient** (a matching file already in Hugging Face `Octavian123/civit`) or **to add to Graydient** (the file is on the 13 Nov 2026 RAID snapshot at `/Volumes/RAID/Lora/{H3,Wan,LTX2}` and must be ingested with civit-to-graydient before it appears in the concept browser). There is no “AIOps only” category.

**Suggest ingest when it is useful**, never automatically. A *Suggest ingest* line means: this LoRA is not in the available Graydient set yet; if you want it, download it and ingest it with the civit-to-graydient pipeline. Nothing in this skill downloads or ingests weights.

Suggest-ingest rule (same rule as the family/category pages):

1. **Gap fill.** If the goal or category has no available LoRA, suggest the top candidates that have a CivitAI or Hugging Face link (at most 3).
2. **High-value upgrade.** If something is already available, still suggest a candidate when it has at least **2,000 downloads** and at least **2×** the downloads of the best available LoRA in that same family and category, or when it is an official utility pack (LightX2V, Lightricks IC-LoRA, CausVid, distill) with no available equivalent.
3. **Cap.** At most 3 suggestions per recipe or category. Each line includes the source link and any recorded trigger or strength. If those fields are not stated, say so — never invent them.

A general H3 starting range of 0.6–0.9 is only a rule of thumb, not per-file data.

Names below use catalog slugs. Family tables: `families/*`.

---

## How to stack (read this first)

### MiniMax H3

Typical Graydient paths: `omni-eros-new-h3` (I2V from a still), `extend-h3`, `extendturbo-h3`. H3 already emits synchronized audio.

A first-test stack is four slots, one each:

1. Identity *or* style/realism (not both unless you know they agree).
2. One motion or physics helper if the body morphs or the motion jitters.
3. One audio helper if speech is robotic or you need a specific moan/accent.
4. One act LoRA only if the still does not already read as the act.

Do not stack two motion boosters and two realism LoRAs on the first pass. Turbo / few-step packs belong only on turbo workflows. The turbo pack already on Graydient is `larryvrh-h3` (RAID slug) / `minimax-h3-turbo-loras-h3` (Graydient slug) — same CivitAI model. Official `lightx2v/Minimax-h3-Turbo` is a suggest-ingest candidate — not auto-downloaded.

### Wan 2.1 and Wan 2.2

- **Wan 2.2 14B needs paired HIGH and LOW noise LoRAs** for the same concept when both exist. Same strength on both, high file on the high-noise sampler, low file on the low-noise sampler. Do not mix a high from concept A with a low from concept B.
- Wan 2.1 (`Wan Video`, `Wan Video 14B i2v 480p/720p`, `Wan Video 14B t2v`) does **not** use that split.
- Wan 2.2 5B TI2V (`Wan Video 2.2 TI2V-5B`) is a different graph — do not drop 5B LoRAs into a 14B I2V-A14B workflow.
- Speed LoRAs (LightX2V distill, CausVid, self-forcing) go on the speed/turbo graph, not as a fifth style LoRA on a full-step 14B pass. If they are not already on Graydient, treat them as suggest-ingest candidates.
- Trigger usually at the front of a natural-language prompt.

### LTX-2 / 2.3 / 2.5

- No high/low pair. One concept LoRA plus, if needed, one official IC-LoRA or camera-control LoRA.
- Match `base` (`LTXV2` vs `LTXV 2.3` vs `LTXV 2.5`) to the workflow when you can. A 2.3 LoRA may or may not behave on 2.5.
- Describe camera and sound in prose; the model already emits audio. Official Lightricks camera-control and IC-LoRAs are mostly **not** on Graydient yet — recipes list them as *Suggest ingest* when they fill that gap.

### Conflicts worth remembering

- Digicam / Y2K texture vs cinematic / teal-orange — pick one look.
- Two character identity LoRAs — pick one, or use a character-swap LoRA instead of stacking.
- Two general motion boosters (e.g. shake-harder + better-motion) — start with one.
- H3 audio LoRAs will not fix Wan or LTX speech.
- A still that already reads as the act often needs less act-LoRA, not more.

---

## Goal recipes

Recipes 1–16, 49–64 and 98 are MiniMax H3, 17–32, 65–78 and 97 Wan, 33–45 and 79–90 LTX, 46–48 and 91–96 cross-family (98 recipes). “On Graydient” means a matching file is in `Octavian123/civit`. “To add to Graydient” means the file is on the RAID and must be ingested before use. Prompt templates: `guides/prompt-patterns.md`.

### 1. Realistic, less-morphing human motion (H3)

- Available (on Graydient): `h3-ltx-2-3-ltx2-better-nsfw-motion-h3` (trigger `h3 ltx 2 3 ltx2 better nsfw motion h3`; strength 0.8; 0.9; 1); `sss-rank-minimax-h3-smooth-slow-sync-h3` (trigger not stated; strength not stated); `grindlg-a-better-grinding-motion-assist-h3` (trigger not stated; strength 1.0); `motion-speed-mmh3-h3` (trigger not stated; strength not stated).
- Suggest ingest: `shake-harder-h3` [CivitAI](https://civitai.com/models/2840146?modelVersionId=3228867) (trigger `dynv2`; strength 0.6–0.8); `shake-harder-ref-h3` [CivitAI](https://civitai.com/models/2840146?modelVersionId=3246346) (trigger `dynv2`; strength 0.6–0.8); `better-motion-h3` [CivitAI](https://civitai.com/models/2734359?modelVersionId=3256084) (trigger not stated; strength 0.4–0.8). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Stack: one booster only. Conflict: shake-harder + better-motion together on the first test.

### 2. Breathy moans / pleasure vocals (H3)

- Available (on Graydient): `jav-moans-audio-only-minimax-h3` (trigger `jpnMoans`; strength not stated).
- Suggest ingest: `moawxx-h3` [CivitAI](https://civitai.com/models/2857965?modelVersionId=3228089) (trigger not stated; strength 0.6–0.85). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Put the trigger in the spoken/sound part of the H3 prompt. Do not expect this to add English dialogue.

### 3. Less robotic speech / natural face talking (H3)

- Available (on Graydient): `natural-face-speech-minimax-h3` (trigger not stated; strength not stated; unverified).
- Describe lip motion, breaths, and language in the `detailed_description` / `</d\\>` blocks (see `guides/image-to-video.md`).

### 4. North American accent (H3)

- Available (to add to Graydient): `minimax-female-accents-north-american-h3` (trigger not stated; strength 0.4–0.5). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**

### 5. Frozen-time camera orbit / card spin (H3)

- Available (on Graydient): `minimax-h3-orb360-cardspin-h3` (trigger `ORB360_CARDSPIN`, `ORB360_CW`; strength 1.0).
- Suggest ingest: `minimax-h3-360-orbit-lora` [HF](https://huggingface.co/pablodawson/MiniMax-H3-360-Orbit-LoRA) (trigger not stated; strength 1.0). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**

### 6. Locked camera or chase / fisheye POV (H3)

- Available (on Graydient): `mmh3-locked-stabilization-camera-locked-to-h3` (trigger `the camera is centred on`, `lockstab`; strength 1); `crash-zoom-minimax-h3` (trigger `crash_zm`; strength not stated); `pov-fisheye-immersive-sexy-chasing-track-h-h3` (trigger not stated; strength not stated); `amateur-pov-h3` (trigger `zy_amateurpov`; strength 0.4–0.85).
- Available (to add to Graydient): `smart-glasses-pov-minimax-h3` (trigger `povsint`; strength not stated). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**
- Suggest ingest: `camera-motion-h3` [CivitAI](https://civitai.com/models/2914784?modelVersionId=3297480) (trigger `camera motion`; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**

### 7. Phone / digicam / Y2K nude realism (H3)

- Suggest ingest: `digicam-h3` [CivitAI](https://civitai.com/models/2855485?modelVersionId=3224980) (trigger `d1g1cam`; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Conflict: do not stack with `cinematic-h3`, `real-cinematic-h3`, or `teal-orange-cinematic-h3` on the same pass.

### 8. Cinematic film texture (H3)

- Available (to add to Graydient): `teal-orange-cinematic-h3` (trigger not stated; strength not stated). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**
- Suggest ingest: `cinematic-h3` [CivitAI](https://civitai.com/models/2849726?modelVersionId=3217898) (trigger `See LoRA describtion`, `see LoRA description`; strength not stated); `real-cinematic-h3` [CivitAI](https://civitai.com/models/2890588?modelVersionId=3267949) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Pick one texture LoRA. Pair with a realism slider only after a baseline.

### 9. Realism slider / skin and detail (H3)

- Available (on Graydient): `mmh3-realism-slider-h3` (trigger not stated; strength not stated); `mmh3-detail-slider-h3` (trigger not stated; strength not stated).
- Available (to add to Graydient): `mmh3-realism-slider-v2-hyperflow-h3-flash-h3` (trigger not stated; strength 0.65–0.85; 0.65–0.90). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**
- Suggest ingest: `minimax-h3-realism-people-lora` [HF](https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA) (trigger `r34l1sm`; strength 1.0). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Suggest ingest: `eyes-skin-hands-h3` [CivitAI](https://civitai.com/models/2899220?modelVersionId=3278036) (trigger `perfe8ct`, `perfect hands`, `perfect skin`; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**

### 10. Few-step / turbo speed (H3)

- Available (on Graydient): `minimax-h3-turbo-loras-h3` (trigger not stated; strength not stated); `minimax-h3-hardgravy-6-step-turbo-merge-h3` (trigger `minimax h3 hardgravy 6 step turbo merge h3`; strength not stated; unverified).
- Suggest ingest: `minimax-h3-turbo` [HF](https://huggingface.co/lightx2v/Minimax-h3-Turbo) (trigger not stated; strength not stated); `minimax-h3-turbo-lora` [HF](https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora) (trigger not stated; strength 1.0); `pika-h3-flex` [HF](https://huggingface.co/Pika-Labs/Pika-H3-Flex) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Only on turbo / flex / PDD workflows. Strength usually not stated — follow the pack’s workflow, not a guessed weight.

### 11. Character swap, keep the motion (H3)

- Suggest ingest: `minimax-h3-character-swap-lora` [HF](https://huggingface.co/akatz-ai/MiniMax-H3-Character-Swap-LoRA) (trigger not stated; strength 1.0). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Do not stack a second identity LoRA on top for the first test.

### 12. Load a specific character / identity (H3)

- Available (on Graydient): `candi-h3` (trigger `Candi`; strength not stated); `anabelle-phoenix-h3` (trigger not stated; strength not stated); `sophie-minimax-h3` (trigger `sophie`; strength 0.7–0.8); `milena-belwyn-h3` (trigger not stated; strength not stated).
- Browse `families/h3/identity.md` (installed first, then by downloads).

### 13. Breast / body physics and jiggle (H3)

- Available (on Graydient): `breast-play-jiggle-for-minimax-h3` (trigger `breast play jiggle for minimax h3`; strength 0.7–0.8); `minimax-h3-heavy-breasts-physics-v1-h3` (trigger `bbwbounce`, `she shakes her breasts`; strength 0.6); `softbreastmotion-h3` (trigger not stated; strength 0.9); `boobslider-minimax-h3` (trigger not stated; strength not stated).
- Catalog: `boob-physics-minimax-h3-wan2-2-h3` if you need the cross-family physics pack and it is not on RAID.

### 14. Anime / 2D look, or a 2D↔real slider (H3)

- Available (on Graydient): `2d-anime-style-nsfw-h3` (trigger `2d anime style`; strength not stated); `minimax-h3-2d-anime-realism-style-slider-h3` (trigger not stated; strength not stated); `bobby-s-general-purpose-h-anime-h3` (trigger `2D-animated`; strength not stated).
- Conflict: a hard 2D style LoRA vs a realism slider — pick a direction.

### 15. Age slider or subtle temporal look (H3)

- Available (on Graydient): `mmh3-video-age-slider-h3` (trigger not stated; strength not stated).

### 16. Object interaction / fewer through-body errors (H3)

- Suggest ingest: `minimax-h3-vbvr-lora` [HF](https://huggingface.co/LiconStudio/Minimax-H3-VBVR) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**

### 17. Wan 2.2 high/low pairing (general)

- Whenever the row’s `files` (or installed filenames) include `HIGH` and `LOW` / `high_noise` and `low_noise`, load both at the same strength.
- Available pairs (ingest any that are still *to add to Graydient* before use): Tentacled v2.1 high/low (sidecars present), futa cowgirl high/low, plus unverified sidecar-only pairs `Fondled_*`, `wan22_i2v_futa_missionary_*`, `xMilkDuctXrayx_*`.
- Local `b7_test1_wan22_t2v_f17_high_*` is **high-noise only**, trigger `b7vhs`. Prefer the final `..._high_noise.safetensors`. There is no matching low from that run.

### 18. Faster Wan 2.2 / 2.1 (distill, LightX2V, CausVid, self-forcing)

- Suggest ingest: `wan2-2-distill-loras` [HF](https://huggingface.co/lightx2v/Wan2.2-Distill-Loras) (trigger not stated; strength 1.0); `wan2-2-distill-models` [HF](https://huggingface.co/lightx2v/Wan2.2-Distill-Models) (trigger not stated; strength not stated); `wan2-1-distill-loras` [HF](https://huggingface.co/lightx2v/Wan2.1-Distill-Loras) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Suggest ingest: `wan2-1-t2v-14b-causvid` [HF](https://huggingface.co/lightx2v/Wan2.1-T2V-14B-CausVid) (trigger not stated; strength not stated). Self-forcing / AccVid packs circulate under Kijai-related repos; confirm the filename is a LoRA before hanging it on a graph. Download and ingest into Graydient with civit-to-graydient if you want it. **Not auto-downloaded.**
- Graydient: `animate-wan22` / `video-wan22` (supports LoRAs). Rapid-all-in-one (`Phr00t/WAN2.2-14B-Rapid-AllInOne`) is a fused checkpoint, not a LoRA — do not treat it as a stackable adapter.

### 19. Wan camera: orbit, dolly zoom, snapshot lens (Wan)

- Catalog: `VERTIGO - (Perfect DollyZoom)` (Wan 2.1 t2v and 2.2 T2V-A14B versions). Trigger not stated here unless the row has one.
- Suggest ingest: `wan2-2-smartphone-snapshot-photo-reality-style` [CivitAI](https://civitai.com/models/1834338?modelVersionId=2079658) (trigger `amateur photo`, `image in an early 2010s amateur photo artstyle with washed out colors`; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Suggest ingest: `360-orbit-camera-motion-wan2-1-i2v-lora` [HF](https://huggingface.co/Muapi/360-orbit-camera-motion-wan2.1-i2v-lora) (trigger `0rb4it 360 degree orbit`; strength 1.0). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- The available Wan camera set is thin; `drift-stop-from-close-up-face-wan2-2-i2v-a-wan` is a specific I2V camera move (Akira-style drift stop), not a general orbit.

### 20. Wan I2V 14B vs T2V 14B vs 5B TI2V

- Match `base`: `Wan Video 2.2 I2V-A14B` → I2V graph (`animate-wan22`); `Wan Video 2.2 T2V-A14B` → T2V (`video-wan22`); `Wan Video 2.2 TI2V-5B` → 5B TI2V only.
- Available (on Graydient): `wan2-2-5b-i2v-shower-safetensors-wan` (trigger not stated; strength not stated); `wan2-2-5b-ti2v-genitalhelperv022-safetenso-wan` (trigger not stated; strength not stated).

### 21. Wan 2.1 480p vs 720p I2V

- Available (to add to Graydient): `wan2-1-i2v-480p-flaccid-v1-0` (trigger `flaccid-v0.6-musubi`, `wan2.1 i2v 480p flaccid`, `penis`; strength not stated). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**
- Catalog 720p I2V uses `Wan Video 14B i2v 720p`. Check the row’s `base` before downloading or recommending.

### 22. General NSFW motion on Wan 2.2 I2V (catalog)

- Popular catalog pack: `lopi999/Wan2.2-I2V_General-NSFW-LoRA` (Hugging Face; also mirrored widely). Use the high/low files if the pack publishes both. Triggers: only those on the model card — do not invent.
- Available (on Graydient): `quorum-general-nsfw-for-wan-2-2-i2v-a14b-wan` is the general NSFW 2.2 I2V option already in the set.

### 23. Wan act LoRAs already on RAID (cowgirl, doggy, blowjob, etc.)

- Available act files (some still to add to Graydient) include cowgirl, reverse-cowgirl, doggystyle, standing sex, side/spoon, handjobs, blowjobs, twerking, dildoing, facial/cumshot packs. Many are single-file Wan 2.1-era or unpaired 2.2 — read `base` and whether a high/low mate exists.
- Triggers: prefer the sidecar or catalog `triggers` field. Several older skeleton rows use the slug as the trigger; if `triggers` is empty, say not stated.

### 24. Wan identity / character

- Browse `families/wan/identity.md` (large; sorted by downloads). Available identity coverage is thin (`belle-delphine-t2v-i2v-wan-14b-wan` is in the available set but its CivitAI id 404'd — unverified).
- One character LoRA at a time. For 2.2, use the high/low pair of *that* character if published.

### 25. Wan anime or 2D style

- Suggest ingest: `wan-14b-shinkai-anime-style-lora-v1` [HF](https://huggingface.co/Cseti/wan-14b-shinkai-anime-style-lora-v1) (trigger `sh1nka1 style`; strength 0.8–1.0). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- See `families/wan/anime.md` and `style.md`. Available Wan style is almost empty; plan on a suggest-ingest style LoRA (smartphone-reality, anime packs). Do not combine two strong style LoRAs.

### 26. Wan realism / live-action look

- See `families/wan/realism.md` (and the snapshot-style camera LoRA in recipe 19). No realism LoRA is currently on Graydient for Wan — use *Suggest ingest* on that category page. Strength only if the row states it.

### 27. Wan body physics / breast play (catalog)

- High-download catalog: `Wan2.2 - Breast Play (I2V)` (CivitAI 1913617). Use the published I2V-A14B high/low files. Triggers/strength: only as on the page.

### 28. Wan effects / VFX

- Catalog examples include special-effect character packs and stylized FX in `families/wan/effects.md`. The available Wan set has no dedicated VFX LoRA.

### 29. Wan transitions

- Few dedicated transition LoRAs (`families/wan/transitions.md`). If the row is empty of triggers, describe the transition in the prompt rather than inventing a token.

### 30. Wan lighting

- Thin category. Prefer prompt lighting, or an H3 teal-orange / cinematic LoRA if you are on H3 instead.

### 31. Wan reward / quality LoRAs (HF)

- `alibaba-pai/Wan2.2-Fun-Reward-LoRAs` and `Wan2.1-Fun-Reward-LoRAs` (also `Kijai/Wan2.1-Fun-Reward-LoRAs-comfy`). These are quality/reward adapters, not style packs. Follow the pack’s suggested graph; strength not stated here.

### 32. Local Wan look probe (VHS / 90s tape)

- Available (to add to Graydient): `b7_test1` high-noise T2V, trigger `b7vhs`. Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.** Example from the sidecar README: `b7vhs, three women in a dark brick dungeon, white lingerie, locked-off wide shot, they slowly move together`. No low-noise mate.

### 33. LTX taker POV

- Available (to add to Graydient): `ltx-2-takerpov-lora-v1-2` (trigger `LTX-2_takerpov_lora_v1.2`, `LTX takerpov`, `takerpov1`; strength 0.8–1.0). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**

### 34. LTX official camera control (dolly, jib, static) — not on RAID

- Suggest ingest: `ltx-2-19b-lora-camera-control-static` [HF](https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Static) (trigger not stated; strength not stated); `ltx-2-19b-lora-camera-control-dolly-in` [HF](https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-In) (trigger not stated; strength not stated); `ltx-2-19b-lora-camera-control-dolly-left` [HF](https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Left) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Use one camera-control LoRA at a time. Strength not stated in this catalog — follow Lightricks’ card.

### 35. LTX sexy / thrust / swing motion (installed)

- Available (on Graydient): `ltx23-i2v-swing-in-out-os` (trigger `ltx23-i2v-swing-in-out2`, `ltx23 i2v swing in out os`; strength not stated); `ltx23-i2v-swing-up-down-os` (trigger `ltx23-i2v-swing-up-down`, `ltx23 i2v swing up down os`; strength not stated).
- Available (to add to Graydient): `ltx2-i2v-sexymove` (trigger `LTX2-i2v-SexyMove`, `LTX2 i2v SexyMove`, `sexy`; strength 0.2–0.91); `ltx2-i2v-sexthrust` (trigger `LTX2-i2v-SexThrust_1`, `LTX2 i2v SexThrust`; strength 0.8–1.0; 0.2–0.4). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**
- Start SexyMove around the stated best zone, not at 0.91.

### 36. LTX body physics / better breasts (catalog)

- Catalog: `LTX 2.3 - I2V Better Physics PhysLTX`, `LTX 2.3 - I2V Better Breasts motion and jiggle`. Triggers/strength only if the row has them.

### 37. LTX anime / flat / retro style

- Available (on Graydient): `pvc-anime-figures-ltx-2-3-ltx2` (trigger not stated; strength not stated).
- Available (to add to Graydient): `retro-anime-mix-by-shrekman-ltx2` (trigger `Flat 2D, Retro anime style`; strength not stated). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**
- Catalog: Posing Dynamics (`PosingDynamicsDaal`), 90s anime style (`ANIMSTY`, …) in `families/ltx/anime.md` / `style.md`.

### 38. LTX realism / amateur look

- Available (on Graydient): `warped-female-body-parts-for-ltxv-2-5-ltx2` (trigger `sloped_breasts`, `round_breasts`, `perfect_breasts`; strength not stated).
- Suggest ingest: `realism` [CivitAI](https://civitai.com/models/2552181?modelVersionId=2868212) (trigger `realism`; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**

### 39. LTX restore, refine, upscale, SDR→HDR (official IC-LoRAs, HF)

- Suggest ingest: `ltx-2-5-22b-ic-lora-restore` [HF](https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-Restore); `ltx-2-5-22b-ic-lora-refine-details` [HF](https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-Refine-Details); `ltx-2-5-22b-ic-lora-sdr-to-hdr` [HF](https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-SDR-To-HDR). Plus the Pixel-Spatial-Upscaler and 2.3 Deblur / Decompression / Colorization cousins. Trigger and strength not stated — follow the Lightricks card. Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
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

- Available (on Graydient): `natural-face-speech-minimax-h3` (trigger not stated; strength not stated; unverified).
- Catalog: `nafasp_h3_lora_v2_500` (Natural Face & Speech H3/LTX 2.5, stated **0.6–0.8**); `aswhm_lora_v1_500` (ASMR Whisper Audio, stated **0.6–0.8**); Kokoro female voices (stated **0.5–0.7**).
- Put dialogue in the H3 `</d\\>` block and describe lip motion and breaths. Conflict: a moan LoRA will not add clear English speech.

### 50. Character consistency across an H3 clip

- Start with a complete `retention_analysis` (see `guides/prompt-patterns.md`). Add **one** installed identity LoRA (recipe 12) if you have it.
- To change the face but keep motion: recipe 11 (`akatz-ai/MiniMax-H3-Character-Swap-LoRA`, Ref2VA; not on Graydient yet). Catalog face-swap: `FaceSwap - MiniMax REF2VA` (trigger `Faceswap`); `BFS - Best Face Swap` uses a structured `body_swap` / subject-definition trigger — follow the page, do not invent one.
- Conflict: two identity LoRAs, or swap + a second character LoRA on the first test.

### 51. Pose or control LoRA guidance (H3)

- Fun ControlNet Union packs are **not LoRAs** and are out of this catalog. Use a pose or control *LoRA* instead.
- Available (on Graydient): `jacko-pose-minimax-h3-v1-h3` (trigger not stated; strength not stated).
- Suggest ingest: `blacked-style-cowgirl-pose-minimax-h3-ref2va` [CivitAI](https://civitai.com/models/2938209?modelVersionId=3326247) (trigger not stated; strength not stated); `add-sexypose-h3` [CivitAI](https://civitai.com/models/3006075?modelVersionId=3410709) (trigger `sexypose`; strength not stated); `shinjutsu-h3-control-lora` [HF](https://huggingface.co/makotolabs/SHINJUTSU-H3-Control-LoRA) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Drive the pose in the action sentence; do not stack two pose LoRAs.

### 52. Lighting, caustics, relight (H3)

- Available (to add to Graydient): `Underwater Sunlight Caustics & Ocean Refraction Slider` (trigger not stated). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**
- Catalog / texture already in recipes 7–8 (`teal-orange-cinematic-h3` installed). Pick one lighting/texture direction.
- Conflict: caustics/underwater look vs dry cinematic teal-orange on the same pass.

### 53. First-last / FL2VA transitions (H3)

- Frozen-time orbit is recipe 5 (`minimax-h3-orb360-cardspin-h3`; HF `pablodawson/MiniMax-H3-360-Orbit-LoRA` needs first-last frames).
- 2D↔real transformation catalog: `Realistic → Anime Transformation | MiniMax H3` (trigger `anime_tx`, stated **0.8–1.0**) — that is a look change, not a scene cut.
- Do not treat a plain I2V still as a first-last transition.

### 54. Cloth and hair motion (H3)

- Suggest ingest: `minimax-h3-t2va-t2v-polyhedron-better-hair` [CivitAI](https://civitai.com/models/3038528?modelVersionId=3453108) (trigger `ha8ir`, `perfect hair`, `thick hair`; strength 0.6–0.7). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Available (on Graydient): `latex-clothes-minimax-h3` (trigger `latex,`; strength not stated).
- Catalog: `[Invisible person / Living clothes]` (triggers `living clothes`, `magic clothes`, `livingclothes`, `invisible`; stated **0.6–0.9**).

### 55. Water, fire, smoke / elemental VFX (H3)

- Available underwater caustics (recipe 52). Catalog: `Water Foam World`; `KinetiX Elemental VFX Suite`; `KinetiX Ghost Rider Hellfire Wheels & Molten Ground Concept Slider`. Triggers and strengths for those catalog rows are `not stated` unless the family table records them after enrichment — do not invent any.
- Keep to one VFX LoRA; describe the element in prose.

### 56. Sharper / upscaled H3 video

- Suggest ingest: `minimax-h3-image-upscaler-lora-workflow-batch` [CivitAI](https://civitai.com/models/2924512?modelVersionId=3309188) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- These are post / tool LoRAs, not style LoRAs. Do not stack with a turbo pack unless the upscaler workflow says to.

### 57. Stereo / depth video (H3)

- Suggest ingest: `real-stereo-depth-video-h3-minimax` [CivitAI](https://civitai.com/models/2969930?modelVersionId=3365446) (trigger not stated; strength 1). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**

### 58. JOI gesture (H3)

- Available (on Graydient): `minimax-joi-gesture-h3` (trigger not stated; strength 0.6–0.8).

### 59. Pegging (H3)

- Available (on Graydient): `minimax-pegging-h3` (trigger not stated; strength 0.5–0.8).

### 60. Cum / finish / squirt (H3)

- Available (on Graydient): `hmsquirt-squirting-for-minimax-h3` (trigger `hmsquirt`, `hmmasturbation`; strength 0.4–0.8); `h3-edge-time-h3` (trigger not stated; strength 1); `h3-throat-time-h3` (trigger not stated; strength 1.0).
- One finish LoRA at a time. Conflict: stacking edge-time + throat-time + squirt on the first test.

### 61. Penis detail / futa helpers (H3)

- Available (to add to Graydient): `dirtylarry-s-dick-detailer-h3` (trigger not stated; strength 1). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.**
- Pair with one act LoRA, not a second detailer.

### 62. Face-slap motion (H3, Ref2VA)

- Available (on Graydient): `face-slap-motion-minimax-h3-ref2va-h3` (trigger `f4c3sl4p`; strength 1.0).

### 63. Bursting / wardrobe break (H3)

- Available (on Graydient): `bursting-out-minimax-h3` (trigger `brstingout`; strength 0.75).

### 64. Hair-pulling motion (H3)

- Available (to add to Graydient): `hair-pulling-h3-101-h3` (trigger not stated). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.** Catalog may list other hair-pull acts; use the family table. Strength not stated — short test clip.

### 65. Talking / lipsync on Wan

- Do not use H3 audio LoRAs. Wan rows tagged lipsync/speech are listed in `families/wan/lipsync.md` and `audio.md` when present. If the row’s trigger and strength are `not stated`, describe mouth motion in prose and test.
- Conflict: expecting a Wan act LoRA to fix lip sync.

### 66. Character or clothing consistency (Wan)

- Suggest ingest: `clothconsistency-wan2-2-i2v-consistencylora2` [CivitAI](https://civitai.com/models/1993310?modelVersionId=2262812) (trigger `clothing consistency.used the clothing in the first frame, generate a video of …`; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Identity: recipe 24, one character LoRA. Face/head swap catalog: `BFS - Best Face Swap` (Wan trigger recorded as `head_swap:`, stated **0.7–1.0** on the Wan version). Follow the page’s subject-definition pattern.

### 67. Object interaction / living clothes (Wan)

- Suggest ingest: `invisible-person-living-clothes-wan2-1-t2v-i2v-14b` [CivitAI](https://civitai.com/models/1650084?modelVersionId=1867692) (trigger `invisible, living cloth, living clothes, magic clothes, magic cloth, livingclot…`; strength 0.75–1.0). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Catalog typography / object: `ObjectTypo-Redmond-T2V-14B` (trigger `ObjectTypography`, strength not stated).
- Describe the held or transforming object in the action clause. Through-body errors: drop extra act LoRAs before adding a second object pack.

### 68. Pose control (Wan)

- Suggest ingest: `wan2-2-t2v-14b-female-bodybuilder-pose` [CivitAI](https://civitai.com/models/2009066?modelVersionId=2273914) (trigger `Wellness, side pose, wellness posing. a bodybuilder woman posing`, `Wellness, front pose, wellness posing. a bodybuilder woman posing`; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
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

- Suggest ingest: `ripped-clothing-wan` [CivitAI](https://civitai.com/models/2302625?modelVersionId=2590903) (trigger `ripped`, `ripped and frayed`; strength not stated); `clothing-tightness-slider-wan2-2` [CivitAI](https://civitai.com/models/2015480?modelVersionId=2281140) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
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

- Suggest ingest: `ltx-video-iclora-pose-13b-0-9-7` [HF](https://huggingface.co/Lightricks/LTX-Video-ICLoRA-pose-13b-0.9.7) (trigger not stated; strength not stated); `ltx-video-iclora-depth-13b-0-9-7` [HF](https://huggingface.co/Lightricks/LTX-Video-ICLoRA-depth-13b-0.9.7) (trigger not stated; strength not stated); `ltx-2-19b-ic-lora-pose-control` [HF](https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Pose-Control) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Suggest ingest: `ltx-2-3-lora-pose-helper-i2v` [CivitAI](https://civitai.com/models/2402694?modelVersionId=2783626) (trigger not stated; strength not stated); `ltx-2-3-most-muscular-pose-lora` [CivitAI](https://civitai.com/models/2533614?modelVersionId=2847433) (trigger `mm_pose`; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Match 2 / 2.3 / 2.5 and I2V vs the IC-LoRA graph.

### 82. Slow motion vs floaty-motion reduction (LTX)

- Suggest ingest: `ltx-2-5-22b-lora-slow-motion-control` [HF](https://huggingface.co/Lightricks/LTX-2.5-22b-LoRA-Slow-Motion-Control) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Say whether you want time stretched or more natural timing. Conflict: Slow-Motion-Control + SexyMove + a second motion booster together.

### 83. Hard cut / cinematic transition (LTX)

- Suggest ingest: `ltx-2-3-cinematic-hardcut` [CivitAI](https://civitai.com/models/2508281?modelVersionId=2819456) (trigger not stated; strength 0.2–1.0). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**

### 84. LTX 2.3 vs 2.5 (and LTXV2) cross-use

- Match `base` to `animate-ltx2` / `animate-ltx23` / `animate-ltx25` (or the T2V `video-ltx*` slugs) when you can. A 2.3 LoRA may or may not behave on 2.5; official IC-LoRAs are often version-specific (2.3 relight vs 2.5 water/upscaler).
- Available SexyMove and taker POV: check the row’s `base` (recipes 33, 35).

### 85. Watermark / subtitle removal (LTX)

- Catalog: `Watermark and Subtitle Remover` (trigger and strength not stated). Tool pass, not a style LoRA. Official clean-plate / object-removal IC-LoRAs are recipe 40.

### 86. LTX image / spatial upscaler

- Suggest ingest: `ltx-2-5-22b-ic-lora-pixel-spatial-upscaler` [HF](https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-Pixel-Spatial-Upscaler) (trigger not stated; strength not stated); `ltx-2-3-22b-ic-lora-pixel-spatial-upscaler` [HF](https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Pixel-Spatial-Upscaler) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Strengths usually `not stated`. Use on the upscaler / IC graph, not as a fifth style LoRA on a generate pass.

### 87. Bouncy walk / body physics add-on (LTX, also Wan)

- Catalog: `Bouncy Walk - LTX / Wan I2V 14B` (triggers include `walking into the direction of the moving camera`, stated **0.75**). Versions exist for LTX 2.3 and Wan — pick the family that matches the graph.
- Other LTX physics: recipe 36 (`D4S1W4_NSFWSME` **0.5–1.0**; BBW `j1ggle` / `bounce` **0.6–1**).

### 88. Wind / melt / surreal LTX effects

- Available (on Graydient): `lana-wind-motion-ltx` (trigger not stated; strength 0.8–1).

### 89. Installed LTX multi-purpose NSFW

- Available (to add to Graydient): `LTX 2/2.3 [I2V] NSFW (+furry) - Multi purpose sex lora` (trigger `ltx2 nsfw+furry`, strength not stated). Ingest into Graydient with civit-to-graydient before use. **Not auto-downloaded.** Use with one additional motion helper at most (SexyMove in its **0.75–0.8** best zone if needed).
- Browse `families/ltx/nsfw-acts.md` for more installed acts.

### 90. CrossView / alternate camera IC-LoRA (LTX)

- Suggest ingest: `crossview-ic-lora-for-ltx-2-3-22b` [CivitAI](https://civitai.com/models/2779316?modelVersionId=3130001) (trigger `Crossview`; strength 1). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**

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

- H3: recipe 51 (Jacko / SexyPose / other named pose LoRAs, or `SHINJUTSU-H3-Control-LoRA`).
- Wan: recipe 68 (named pose LoRAs; match 2.1/2.2).
- LTX: recipe 81 (official pose/depth IC-LoRAs or Pose Helper).
- Official IC / ControlNet packs need their control input. A trigger-only pose LoRA does not replace a pose map.

### 94. Object interaction: pick a family

- H3: recipe 16 (`LiconStudio/Minimax-H3-VBVR`) and catalog `Swallowing Object` (stated **0.75–1**, trigger starts `She inserts the [object] inside her mouth…` — use the recorded wording, filling only the object slot the page leaves open). Available `Vaginal object delivery` has a recorded delivery trigger in the table — ingest it first if it is still *to add to Graydient*.
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

### 97. Wan 2.1 1.3B T2V LoRAs (not 14B)

- The CivitAI base `Wan Video 1.3B t2v` is a **1.3B** graph. Do not drop these files into Wan 2.2 14B high/low or 5B TI2V, or into 14B I2V 480p/720p, unless a row also publishes a matching 14B version (some multi-base models do — check `bases`).
- None of these 1.3B example packs are currently on Graydient. Treat the list as **suggest ingest** (review, then ingest with civit-to-graydient if you want one). **Not auto-downloaded.** Triggers as recorded; strengths `not stated` unless noted: `wan2.1 1.3b female anatomy` (`NTM`); `wan2.1 1.3b male anatomy` (`ntm-male`); `wan2.1 1.3b static rotation` (`sttcrttn`); `Wan 2.1 1.3B tools` (`low speed`, `high speed`); `Beauty of rain [Wan 1.3B]` (`b3@ut1f0ll_r@in`); `Genshin TCG Style [Wan 1.3B]` (`Genshin_TCG`, stated **0.75–1.0**); `PixelArtRedmond - Wan Lora` (`Pixel Art`, `PixArFK`); `Kubakub_Architecture_Wan2.1_1.3B_t2v` (`Kubakub`); `Enchanted - Giselle` (`2DGiselle`); `Vintage 1980s anime` (stated **0.7–1.0**, trigger not stated).
- `Sex helper for NSFW Wan 1.3b` and the 1.3B furry I2V pack have no recorded trigger — do not invent one.
- Two low-download 1.3B rows are flagged `low_signal` (`Twerk - Wan2.1 - 1.3b`, `Etot`).

### 98. Convert H3 FL2VA to Ref2VA (LoHA)

- Suggest ingest: `minimax-h3-fl2va-to-ref2va-conversion` [CivitAI](https://civitai.com/models/2841039?modelVersionId=3207111) (trigger not stated; strength not stated). Download and ingest into Graydient with civit-to-graydient if you want them. **Not auto-downloaded.**
- Page note: load it with a model-only LoRA loader — do not use a joint model+CLIP node.
- This is a graph conversion helper, not a style LoRA. Pair with a Ref2VA workflow once converted (recipes 11, 53), and do not stack a second conversion adapter.

---

## Where to look next

- Tables: `families/h3/`, `families/wan/`, `families/ltx/` — available Graydient LoRAs first (on Graydient, then to add). A *Suggest ingest* block lists high-value public candidates that are not yet in the set.
- Prompt shapes: `guides/image-to-video.md` and per-family templates in `guides/prompt-patterns.md`.
- Official utility directory: `guides/fuzzpuppy-directory.md` (many of these are ingest candidates if they are not already on Graydient).
- New CivitAI uploads that are not yet accessible: `python3 scripts/check_new.py` (proposal markdown only, no downloads).
- RAID files still to add to Graydient: `data/graydient_ingest_queue.md`.
- Candidate backlog with ingest-priority scores: `data/candidates.jsonl`.
