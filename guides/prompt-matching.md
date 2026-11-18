# Prompt → LoRA matching (worked examples)

Generated 2026-11-18 by `scripts/matcher_examples.py` from `data/semantic_catalog.jsonl` (real slugs; rerun after the weekly update). Reproduce any example with the command shown.

Read each pick's *why* before adding it: the matcher ranks by shared words and semantic tags, not by looking at images. Triggers are copied from the source; an empty trigger means the LoRA is registered on Graydient by slug only. Weights marked *default* are workflow defaults, not source-stated values.

## POV ride with body physics (H3)

```bash
python3 scripts/suggest.py "POV cowgirl, a busty redhead woman riding and bouncing, breasts jiggling, moaning, slow push-in camera, phone footage look" --base h3
```

Prompt reads as: subject: woman; expression: pleasure; object: phone, camera; pose: pov, cowgirl; anatomy: breasts, huge breasts; motion: bouncing, riding motion, camera push, talking motion

| # | LoRA | role | why it matches | trigger | weight |
|---:|---|---|---|---|---|
| 1 | `<simply-sybian-bouncing-edition-h3:0.8>` | detail | words: bouncing, riding; pose/action/camera: cowgirl; video motion: bouncing, riding motion | riding a Sybian | 0.8 (default) |
| 2 | `<friend-s-pov-minimax-h3:0.8>` | style | words: camera, pov; object/prop: phone, camera; pose/action/camera: pov | celsint | 0.8 (default) |
| 3 | `<pov-fisheye-immersive-sexy-chasing-track-h-h3:0.8>` | concept | words: camera, pov; object/prop: camera; pose/action/camera: pov | — (slug only) | 0.8 (default) |
| 4 | `<bouncing-boobs-ltx-wan-h3:0.8>` | detail | words: bouncing; subject/character: woman; anatomy: breasts | her breast is bouncing up and down, her breast is bouncing from left to right | 0.8 (default) |
| 5 | `<sagging-breasts-h3:1.0>` | detail | words: breasts; anatomy: breasts, huge breasts | sagging breasts, breasts apart | 1.0 (source) |
| 6 | `<pornmaster-mmh3-fast-motion-slider-h3:0.8>` | utility | words: slow | the person moves at fast speed, performing the action quickly and energetically. fast motion., the person moves at slow speed | 0.8 (default) |

Stacking notes: Realism and anime/comic style LoRAs rarely agree: choose one lane. Speed/slider LoRAs: speed ones only on the matching turbo/few-step workflow; sliders are signed (negative weight reverses). Large stack: add LoRAs one at a time and keep helpers at 0.2–0.5.

## Dance with camera orbit (Wan 2.2)

```bash
python3 scripts/suggest.py "woman doing a slow 360 orbit dance in a neon club, hair swaying" --base wan
```

Prompt reads as: subject: woman; concept: nightlife, lighting; pose: dancing; style: neon cyberpunk; anatomy: hair; motion: bouncing, camera orbit, dance motion

| # | LoRA | role | why it matches | trigger | weight |
|---:|---|---|---|---|---|
| 1 | `<slow-twerk-high-wan:0.8>` | motion | words: slow; pose/action/camera: dancing; video motion: bouncing, dance motion | twerking | 0.8 (default) |
| 2 | `<hip-swayass-wan21:0.8>` | motion | words: dance; pose/action/camera: dancing; video motion: bouncing, dance motion | performs an ass shaking dance | 0.8 (default) |
| 3 | `<iwara-hentai-mmd-dynamic-hip-swing-dance-wan2-2-i2v-14b:0.8>` | act | words: dance; subject/character: woman; pose/action/camera: dancing | She performs a dynamic hip-swinging dance., She performs a dynamic hip-shaking dance., She performs a dynamic hip-swinging dance. | 0.8 (default) |
| 4 | `<exotic-dancer-yet:0.8>` | detail | subject/character: woman; pose/action/camera: dancing; video motion: dance motion | — (slug only) | 0.8 (default) |
| 5 | `<radio-dancing-wan:0.8>` | detail | subject/character: woman; pose/action/camera: dancing; video motion: dance motion | 5odp3g | 0.8 (default) |
| 6 | `<grinding-cowgirl-high-wan:0.8>` | motion | pose/action/camera: dancing; adds: cowgirl, sex | — (slug only) | 0.8 (default) |

Stacking notes: Wan 2.2 A14B LoRAs come in high-noise/low-noise pairs: load the matching partner on the other expert. Large stack: add LoRAs one at a time and keep helpers at 0.2–0.5. Pair <slow-twerk-high-wan> (high/low-noise) with <slow-twerk-low-wan>. Pair <grinding-cowgirl-high-wan> (high/low-noise) with <grinding-cowgirl-low-wan>.

## Talking head, natural speech (H3)

```bash
python3 scripts/suggest.py "close-up of a woman talking to the camera, natural lip sync, subtle smile, soft window light" --base h3 --intent "less robotic speech"
```

Prompt reads as: subject: woman; concept: lighting; expression: smile, talking; object: camera; pose: close-up; motion: talking motion

| # | LoRA | role | why it matches | trigger | weight |
|---:|---|---|---|---|---|
| 1 | `<natural-face-speech-minimax-h3:0.8>` | motion | words: natural, speech; expression: talking; video motion: talking motion | — (slug only) | 0.8 (default) |
| 2 | `<foreskin-stretch-h3:0.8>` | detail | words: close, soft; concept/intent: lighting; pose/action/camera: close-up | fskin_stretch, close-up of a hand gently stretching the foreskin of an erect penis, pulling it forward and slightly downward | 0.8 (default) |
| 3 | `<mmh3-locked-stabilization-camera-locked-to-h3:1.0>` | motion | words: camera; object/prop: camera | the camera is centred on, lockstab | 1.0 (source) |
| 4 | `<minimax-female-accents-north-american-h3:0.45>` | motion | subject/character: woman; video motion: talking motion | — (slug only) | 0.45 (source) |
| 5 | `<natural-sagging-breasts-h3:0.8>` | detail | words: natural | — (slug only) | 0.8 (default) |
| 6 | `<whispering-h3:0.8>` | detail | expression: talking | — (slug only) | 0.8 (default) |

Stacking notes: Large stack: add LoRAs one at a time and keep helpers at 0.2–0.5.

## LTX motion

```bash
python3 scripts/suggest.py "woman swinging her hips while walking toward the camera, slow motion, cinematic lighting" --base ltx
```

Prompt reads as: subject: woman; concept: lighting; object: camera; pose: walking, action; style: cinematic; anatomy: hips thighs; motion: slow motion, walking motion

| # | LoRA | role | why it matches | trigger | weight |
|---:|---|---|---|---|---|
| 1 | `<ltx23-i2v-swing-up-down-os:0.8>` | detail | words: motion; pose/action/camera: action; anatomy: hips thighs | ltx23-i2v-swing-up-down | 0.8 (default) |
| 2 | `<ltx23-i2v-swing-in-out-os:0.8>` | detail | words: motion; pose/action/camera: action; anatomy: hips thighs | ltx23-i2v-swing-in-out2 | 0.8 (default) |
| 3 | `<ltx2-i2v-sexymove:0.56>` | motion | words: motion; pose/action/camera: action | sexy | 0.56 (source) |
| 4 | `<dr34ml4y-all-in-one-nsfw-h3-wan-ltx2:0.8>` | detail | words: camera; object/prop: camera | m15510n4ry, bl0wj0b, d0ubl3_bj | 0.8 (default) |
| 5 | `<ltx-2-takerpov-lora-v1-2:0.9>` | act | words: camera; object/prop: camera | LTX takerpov, takerpov1, taker pov | 0.9 (source) |
| 6 | `<pov-missionary-bouncy-bouncy:0.8>` | act | words: camera; subject/character: woman; object/prop: camera | POV missionary, bouncing breasts up and down, mouth open moaning | 0.8 (default) |

Stacking notes: Large stack: add LoRAs one at a time and keep helpers at 0.2–0.5.

