# Skill: choose a video LoRA

Use this skill when Andrew wants to pick MiniMax H3, Wan, or LTX-2/2.3/2.5 LoRAs for a generation goal. Prefer LoRAs that are **installed** (see `data/loras.jsonl` `installed: true`) unless he asks to hunt for something new.

Adult NSFW LoRAs are in this catalog on purpose. Describe them factually. Do not invent trigger words or strengths. If strength is `not stated`, say so and tune on a test clip.

## Pick by goal

### Realistic human motion

- **H3, installed:** `h3-ltx-2-3-ltx2-better-nsfw-motion-h3`, `grindlg-a-better-grinding-motion-assist-h3`, `sss-rank-minimax-h3-smooth-slow-sync-h3`, `motion-speed-mmh3-h3`, `pornmaster-mmh3-fast-motion-slider-h3`, `face-slap-motion-minimax-h3-ref2va-h3`.
- **H3, curated but not in the 13 Nov 2026 RAID snapshot:** `better-motion-h3`, `motion-repair-h3`, `shake-harder-h3` / `shake-harder-ref-h3` (trigger `dynv2`; page-stated strength 0.6–0.8), `deeper-h3`. Start with one motion booster, not three at once.
- **Wan:** act LoRAs often *are* the motion (cowgirl, doggy, standing sex, twerking). There is no separate general "better motion" file in the installed Wan set.
- **LTX:** `LTX2-i2v-SexThrust`, `LTX2-i2v-SexyMove` (page-stated strength 0.2–0.91, with 0.75–0.8 called the best zone), swing-in-out / swing-up-down.

### Breathy / whisper / more natural voice

H3 is the family that actually carries dialogue and breaths well.

- Installed, verified: `jav-moans-audio-only-minimax-h3` (trigger `jpnMoans`), `minimax-female-accents-north-american-h3` (page-stated strength 0.4–0.5).
- Installed, **unverified**, no recorded trigger: `natural-face-speech-minimax-h3`. Still the closest installed "less robotic speech" file from the MCB notes — test it, do not invent a trigger.
- Curated, not in the snapshot: `moawxx-h3` (female pleasure moans + body writhing; page-stated 0.6–0.85).
- Wan / LTX installed set has no dedicated whisper LoRA. LTX already generates native audio; describe breaths and voice in the prompt rather than stacking a missing audio LoRA.

### Camera orbit / locked camera / POV

- **Orbit:** installed `minimax-h3-orb360-cardspin-h3`. Fuzz Puppy also lists pablodawson's MiniMax H3 360 Orbit (FL2VA, frozen-time orbit) — not in the RAID snapshot.
- **Lock / chase:** `mmh3-locked-stabilization-camera-locked-to-h3`, `crash-zoom-minimax-h3`, `pov-fisheye-immersive-sexy-chasing-track-h-h3`, `smart-glasses-pov-minimax-h3`, `amateur-pov-h3`.
- **LTX POV:** `LTX-2_takerpov_lora_v1.2` (trigger `taker pov`; page-stated weight 0.8–1.0).
- Official Lightricks LTX camera-control LoRAs (dolly / jib / static) are listed in `guides/fuzzpuppy-directory.md` and are **not** installed here.

### Character swap or identity

- Installed H3 identity files include character LoRAs such as `candi-h3`, `anabelle-phoenix-h3`, `milena-belwyn-h3`, `sophie-minimax-h3`, and the NordhavenLove names. Use **one** primary identity LoRA.
- Fuzz Puppy lists akatz-ai MiniMax H3 Character Swap (Ref2VA, V1.5 recommended) — not in the RAID snapshot. Prefer that path for "replace the person, keep the motion" rather than stacking two character LoRAs.
- Wan identity: `belle-delphine-t2v-i2v-wan-14b-wan` is in the inventory but its CivitAI id 404'd; treat as unverified.

### Style and realism texture

- **H3 realism / film:** installed sliders `mmh3-realism-slider-h3`, `mmh3-realism-slider-v2-hyperflow-h3-flash-h3`, `mmh3-detail-slider-h3`, `teal-orange-cinematic-h3`. Curated, not installed: `digicam-h3` (trigger `d1g1cam`), `cinematic-h3`, `real-cinematic-h3`, `eyes-skin-hands-h3` (trigger `perfe8ct`). Pick **one** texture/realism LoRA; digicam and cinematic fight each other.
- **Style:** installed anime/flat, analog print, crayon, manga tone, 1950s western, 1980s cartoon, etc. LTX: `animeflatLTX.2.3`, `retro-anime-mix-by-shrekman-ltx2`, `pvc-anime-figures-ltx-2-3-ltx2`.
- **Turbo / speed (enhancement, not style):** `minimax-h3-turbo-loras-h3` (verified CivitAI pack). `minimax-h3-hardgravy-6-step-turbo-merge-h3` 404'd; unverified.

### Anatomy / body enhancement

Use the breasts/body and futa/penis groups rather than a generic motion LoRA when the failure is anatomy: `boobslider-minimax-h3`, heavy-breast physics, sagging/flat/tiny breasts, `softbreastmotion-h3`, and the penis/futa helpers when those files are installed. Check the family tables — several MCB penis/futa helpers from Sept 2026 are **not** in the 13 Nov 2026 H3 snapshot.

## Per-family stacking

### MiniMax H3

Typical Graydient paths: `omni-eros-new-h3` (I2V from a still), `extend-h3`, `extendturbo-h3`. H3 LoRAs are often usable for I2V, T2V, and Ref2VA, but believe the per-LoRA `i2v_t2v` field when it is stated.

Stack lightly:

1. One identity or style/realism LoRA (or a slider).
2. One motion helper if the body is morphing or the stroke is jittery.
3. One audio helper if speech is robotic or you need a specific moan/accent.
4. One act LoRA if the still does not already read as the act.

Do not stack two motion boosters and two realism LoRAs on the first test. A general starting range of 0.6–0.9 is only a rule of thumb, not per-LoRA data.

### Wan 2.1 and Wan 2.2

- **Wan 2.2 14B needs paired HIGH and LOW noise LoRAs** for the same concept when both exist. Same strength on both, high file on the high-noise sampler, low file on the low-noise sampler.
- Installed pairs include Fondled, Tentacled v2.1, futa cowgirl, futa missionary, and MilkDuct X-ray (some pairs are sidecar-only / unverified pages).
- `b7_test1_wan22_t2v_f17_high_*` is a local T2V high-noise look probe, trigger `b7vhs`. Prefer the final `..._high_noise.safetensors`. There is **no** matching low-noise LoRA from that run.
- Wan 2.1 files (`wan2.1-i2v-480p-flaccid-v1.0`, some older act LoRAs tagged `Wan Video` / `Wan Video 14B *`) do not use the 2.2 high/low split.
- Wan 2.2 5B TI2V files (`wan2-2-5b-i2v-shower`, `genitalhelperv022`) are a different base (`Wan Video 2.2 TI2V-5B`) — do not drop them into a 14B I2V-A14B graph.

### LTX-2 / 2.3 / 2.5

- No high/low pair. One LoRA, trigger in the prompt, describe camera and audio in natural language (the model already emits audio).
- Check `base` on the row: `LTXV2` is LTX-2, `LTXV 2.3` and `LTXV 2.5` are later checkpoints. A 2.3 LoRA may or may not behave on 2.5; do not assume it.
- Sidecar `.txt` files next to the RAID weights are the primary trigger source when present (`taker pov`, `sexy`, `PENISLORA`, etc.).
- Official IC-LoRAs and camera-control packs from Lightricks are documented under Fuzz Puppy; they are mostly not on this RAID.

## What not to do

- Do not invent a strength or trigger for an unverified row.
- Do not mix Wan 2.2 high-noise and low-noise files from *different* concepts.
- Do not assume a LoRA sitting in the H3 folder is an H3 LoRA if the filename says `wan` or `krea2` — read the `base` field.
- Do not download new weights with `scripts/check_new.py`. It only writes a proposal markdown file.
