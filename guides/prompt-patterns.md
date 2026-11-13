# Prompt patterns and trigger usage

Per-family templates for I2V / T2V (and H3 Ref2VA / FL2VA) when you already know which LoRA to load. For *which* LoRA, start with [`SKILL.md`](../SKILL.md). For Graydient workflow slugs and the longer H3 block, see [`image-to-video.md`](image-to-video.md).

**Never invent a trigger or a strength.** If `data/loras.jsonl` or the family table says `not stated` or leaves `triggers` empty, do not guess. Put only recorded trigger words into the prompt. When a strength is `not stated`, tune on a short test clip.

---

## Rules that apply to every family

1. **One job per LoRA.** Identity *or* style, one motion or physics helper, one audio helper, one act LoRA only if the still does not already read as the act.
2. **Trigger placement.** If the row lists `trainedWords` / triggers, put them where that family expects them (below). Do not sprinkle invented tags. Multi-word triggers are used exactly as recorded (including unusual spellings like `d1g1cam`, `jpnMoans`, `ha8ir`).
3. **Strength.** Use the stated range when the catalog has one. If the page gives a “best zone” inside a wider range (for example SexyMove 0.2–0.91 with 0.75–0.8 called out), start in the stated best zone. Otherwise start mid-range of what is stated, or make a short test if nothing is stated.
4. **I2V vs T2V.** I2V should *retain* the still and describe only what changes. T2V must describe appearance, wardrobe, and identity in the prompt because there is no still. Ref2VA / FL2VA need the reference or first-last frames the pack asks for — a plain single still is not enough.
5. **Conflicts.** Digicam vs cinematic texture: pick one. Two character identity LoRAs: pick one, or use a character-swap LoRA. Two general motion boosters: start with one. H3 audio LoRAs will not fix Wan or LTX speech.

---

## MiniMax H3

H3 emits synchronized video and audio. Typical Graydient paths: `omni-eros-new-h3` (I2V), `extend-h3`, `extendturbo-h3` (turbo packs only on turbo). Observed I2V recipe (not a universal default): `/size:640x640` `/length:200` with the still as `/image1:`.

### I2V template (structured block)

```
subject_definitions:
<Subject 1> is the person in <Picture 1>, with [identity details you must keep].

summary:
[reference generation] The target video shows <Subject 1> [framing, action, and speech intent].

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - [hair, face, wardrobe, anatomy, prop state from <Picture 1>].

detailed_description:
The target video is [camera, lighting, space].
[Shot 1] [Visible action, hands, props, one or two motions only.]
[If a LoRA lists a trigger, place it here or in the spoken/sound lines as the row implies.]
She speaks … </d\\> [language] DIALOGUE. </d\\> </d\\>
[Breaths, moans, Foley.]

overall_soundscape:
[Room tone, cloth/skin, breathing.]

non_diegetic_music:
[Optional, keep it under the voice.]
```

### T2V template

Drop `retention_analysis` and `<Picture 1>`. Expand `subject_definitions` with appearance, wardrobe, and identity. Keep the shot count low.

### Ref2VA / FL2VA / first-last

Use the pack’s graph (character-swap, 360° orbit, some face-swap and pose LoRAs). Supply the reference frames it asks for. A single I2V still will not drive a first-last camera orbit.

### Trigger usage (H3)

- Audio / accent / moan triggers belong in the spoken or soundscape lines (`jpnMoans` in the moan/Foley part, not as a style tag).
- Camera and motion triggers go in `detailed_description` with the shot (`lockstab` / `the camera is centred on` for locked stabilization; `dynv2` only with shake-harder).
- Identity triggers (`sophie`, `candi`, …) stay with the subject definition; use **one** identity LoRA.
- Style triggers (`d1g1cam`, `analog_print_blackwhite`, `2D-animated`, `anime_tx`, `2dan1m`) go in the look/texture sentences. Do not stack a hard 2D trigger with a realism slider on the first pass.

### Prompt add-ons by goal (H3)

| Goal | What to write | What not to do |
|---|---|---|
| Talking / lipsync | Describe lip motion, breaths, language, and the exact line in the `</d\\>` dialogue block. `natural-face-speech-minimax-h3` is installed but unverified — no recorded trigger. | Do not invent a lipsync trigger. |
| Character consistency | Fill `retention_analysis` completely. One identity LoRA, or the character-swap pack on Ref2VA. | Two identity LoRAs at once. |
| Camera | Name the move (locked off, crash zoom, fisheye chase, orbit) and what stays still. | A second general camera booster on the first test. |
| Physics / jiggle | Name the body motion in one clause; use a stated physics LoRA (`bbwbounce`, `she shakes her breasts` only with the heavy-breasts pack). | Stack jiggle + shake-harder + better-motion together. |
| Audio | Put the accent/moan trigger in the sound lines; describe room tone. North American accent pack is stated **0.4–0.5**. | Expect an H3 moan LoRA to add English dialogue. |

---

## Wan 2.1 / 2.2

Graydient: `animate-wan22` (I2V, speed-optimized), `video-wan22` (T2V). Wan 2.2 14B needs **paired HIGH + LOW** LoRAs for the same concept when both exist, same strength, on the matching samplers. Wan 2.1 has no high/low split. Wan 2.2 5B TI2V is a different graph — do not drop 5B LoRAs into I2V-A14B / T2V-A14B. Speed / distill LoRAs belong on the few-step graph, not as a style LoRA on a full-step pass. 2.1 ↔ 2.2 cross-use is not guaranteed; match `base`.

### I2V / T2V template

Natural language, trigger at the front when the row has one:

```
<trigger>, [shot size and camera], [who is in frame — for I2V, as they appear in the start frame], [the action in time order], [what stays still], [lighting]
```

I2V: do not re-describe the face unless you want it to change. T2V: describe appearance and wardrobe fully.

Local high-noise-only example (installed `b7` test, trigger `b7vhs`, ~17 frames / 480p / 16 fps):

```
b7vhs, three women in a dark brick dungeon, white lingerie, locked-off wide shot, they slowly move together
```

### Trigger usage (Wan)

- Keep unusual spellings exact: `m3lt1ng`, `submer8ge`, `[r3al_f1re]`, `b4ll3t t1m3`, `4ct3ion`, `cstm_actn_facial`.
- Act / pose LoRAs often ship a short action phrase as the trigger (paw pose, pronebone, most muscular). Use that phrase as the action, not as a trailing tag soup.
- Cloth-consistency: the catalog records a phrase like “clothing consistency / used the clothing in the first frame” — put that intent in the prompt only as recorded, and keep wardrobe still.
- Upscale tool LoRAs may use an instruction-like trigger (`upscale this video` is recorded for the LuisaP WAN 2.2 upscaler). Use it only with that pack.
- Fire / water: match the base (a 5B fire LoRA stays on 5B TI2V). Recorded examples: Wan 2.2 I2V 5B Realistic Fire, trigger `fire`, stated **0.8**; Wan 2.1 T2V Realistic Fire, trigger `[r3al_f1re]`, stated **1.0**.

### Prompt add-ons by goal (Wan)

| Goal | What to write | What not to do |
|---|---|---|
| High/low pair | Same prompt and strength on both samplers. | Mix concept A’s high with concept B’s low. |
| Camera / time FX | Name the move; official or catalog triggers only (`b4ll3t t1m3` only with the Matrix bullet-time LoRA). | Use an H3 orbit LoRA on Wan. |
| Underwater | Triggers such as `submer8ge` only with the Polyhedron Submerge pack; mention caustics / open water as recorded. | A 14B underwater LoRA on 5B, or the reverse. |
| Transitions | `m3lt1ng` only with Melt It (stated strength **1**). | Stack a hard-cut LTX LoRA on Wan. |
| Consistency | One character LoRA, or the cloth-consistency pack; say what must not change. | Two identity LoRAs plus a style LoRA on the first test. |

---

## LTX-2 / 2.3 / 2.5

Graydient: `animate-ltx2` / `animate-ltx23` / `animate-ltx25` (I2V with audio), `video-ltx2` / `video-ltx23` / `video-ltx25` (T2V with audio), `extend-ltx23`. No high/low pair. Match `base` (`LTXV2` vs `LTXV 2.3` vs `LTXV 2.5`) to the workflow when you can; a 2.3 LoRA may or may not behave on 2.5. Official Lightricks camera-control and IC-LoRAs (pose, depth, relight, upscaler, water, Foley, clean plate) live on Hugging Face and are mostly not on the RAID.

### I2V / T2V template

Natural language; describe shot, motion, and sound in prose:

```
<trigger if any>. A [camera] shot of [subject as they appear in the start frame].
[What moves, how fast, what stays still.]
Audio: [room, body, voice].
```

T2V must describe the subject fully. Official IC-LoRAs often expect a control video or reference images (pose, depth, identity, multi-subject) — follow the pack card, not this prose template alone.

### Trigger usage (LTX)

- Recorded examples: `takerpov` / `LTX takerpov` (stated **0.8–1.0**), SexyMove (`LTX2-i2v-SexyMove`, `sexy`; stated **0.2–0.91**, page calls 0.75–0.8 the best zone), `D4S1W4_NSFWSME` (body-physics enhancer, **0.5–1.0**), `j1ggle` / `bounce` (BBW jiggle, **0.6–1**), `Crossview` (CrossView IC-LoRA, stated **1**), `sh1nka1 style` (Shinkai, **0.8–1.0**), `btssetstyle` (BTS Movie Set, **0.8–1.0**).
- Foley / lipsync / dubbing packs: strength often `not stated`. Describe the speech performance you want; do not invent a viseme trigger.
- Pose / depth IC-LoRAs: drive them with the control input the pack requires, not with a made-up prompt tag.

### Prompt add-ons by goal (LTX)

| Goal | What to write | What not to do |
|---|---|---|
| Camera | Official dolly / jib / static control LoRAs, or describe the move in prose if no control pack is loaded. | A Wan or H3 camera LoRA on an LTX graph. |
| Lipsync / dubbing | Use the LTX-2.3 dubbing / lip-sync LoRA when you have it; describe the line and performance. | An H3 moan LoRA. |
| Consistency | Identity or multi-reference IC-LoRAs with the reference images the card asks for. | Two character LoRAs plus a style LoRA on the first test. |
| Time / slow-mo | Official Slow-Motion-Control, or the 2.3 floaty-movement reducer slider; say whether time should stretch or stay natural. | A second general motion booster (SexyMove + shake-style pack) together at first. |
| Transitions | Cinematic hardcut pack is stated **0.2–1.0** — start mid-range and test. | Expect a hard cut from a motion LoRA alone. |

---

## Stacking a prompt with multiple LoRAs

Write one coherent paragraph (or H3 block) that covers identity retention, the single main action, camera, and sound. Include every *recorded* trigger you are actually loading. Do not add triggers for LoRAs you did not load. If two loaded LoRAs both want to own the camera or the body physics, drop one and reshoot a short clip.
