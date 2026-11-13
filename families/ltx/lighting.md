# LTX2: Lighting

7 LoRAs (0 installed on the 13 Nov 2026 RAID snapshot). Installed rows are listed first, then the rest by CivitAI/HF download count.

Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.

| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |
|---|---|---|---|---|---:|---|---|
| `ltx-2-5-22b-ic-lora-day-to-night` | — | not stated | not stated | LTX-2.5-22b-IC-LoRA-Day-To-Night | 6,183 | catalog, verified | [HF](https://huggingface.co/Lightricks/LTX-2.5-22b-IC-LoRA-Day-To-Night) |
| `ltx-2-3-22b-ic-lora-relight` | — | not stated | not stated | LTX-2.3 22B IC-LoRA Relight | 1,514 | catalog, verified | [HF](https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Relight) |
| `ltx-2-3-22b-ic-lora-day-to-night` | — | not stated | not stated | LTX-2.3 22B IC-LoRA Day To Night | 259 | catalog, verified | [HF](https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Day-To-Night) |
| `ltx-2-3-black-magic-lora` | — | not stated | not stated | LTX-2.3 Black Magic LoRA | 100 | catalog, verified | [HF](https://huggingface.co/FuzzPuppy/LTX-2.3-Black-Magic-LoRA) |
| `blackout-ic-lora-ltx23` | `BL4CKOUT` | 0.8; 1 | not stated | blackout-ic-lora-ltx23 | 38 | catalog, verified | [HF](https://huggingface.co/cfryant/blackout-ic-lora-ltx23) |
| `ltx-2-3-22b-ic-lora-golden-hour` | `ADD GOLDEN HOUR` | not stated | not stated | LTX-2.3-22b-IC-LoRA-Golden-Hour | 0 | catalog, verified | [HF](https://huggingface.co/Hoffm4nz/LTX-2.3-22b-IC-LoRA-Golden-Hour) |
| `ltx-2-5-22b-ic-lora-golden-hour` | — | 1.0 | not stated | LTX-2.5-22b-IC-LoRA-Golden-Hour | 0 | catalog, verified | [HF](https://huggingface.co/Hoffm4nz/LTX-2.5-22b-IC-LoRA-Golden-Hour) |

## Details

### `LTX-2.3-Black-Magic-LoRA`

**LTX-2.3 Black Magic LoRA**
- base `LTXV 2.3` · not stated · strength: not stated

Example prompts (from the images API, page, or sidecar; never invented):

Example 1:
```
Restore this underexposed video to a natural, well-exposed version with realistic colors and recovered shadow detail. A woman performs poi fire dancing. She has her back to the camera and is facing an audience.
```

Example 2:
```
Restore this underexposed video to a natural, well-exposed version with realistic colors and recovered shadow detail. A man and woman dance at a nightclub.
```

Compatibility: Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible; HF card base_model: Lightricks/LTX-2.3; HF base_model_relation: adapter

Source: [HF](https://huggingface.co/FuzzPuppy/LTX-2.3-Black-Magic-LoRA)

### `blackout-ic-lora-ltx23`

**blackout-ic-lora-ltx23**
- base `LTXV 2.3` · not stated · strength (stated): 0.8; 1 · triggers: `BL4CKOUT`

Example prompts (from the images API, page, or sidecar; never invented):

Example 1:
```
BL4CKOUT same scene, every light switched off, only a camera-mounted flashlight from the viewer's point of view, same camera motion and action.
```

Example 2:
```
`BL4CKOUT same scene, every light switched off, only a camera-mounted flashlight from the viewer's point of view, same camera motion and action.` - **Negative prompt (optional):** `lights on, bright lighting, lit lamps, glowing ceiling lights, lit screens, daylight, sunlight, flat even lighting, overexposed, visible flashlight, flicker, jitter, warped geometry, changed camera motion` - **Resolution:** v2 was trained at 1280x704, so 1280x720 / 1280x704 at 24 fps works well. - **fal:** works with `fal-ai/ltx-2.3-22b/reference-video-to-video/lora` (`loras: [{path: <resolve URL of this file>, scale: 0.8}]`).
```

Compatibility: Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible; HF card base_model: Lightricks/LTX-2.3; HF base_model_relation: adapter

Source: [HF](https://huggingface.co/cfryant/blackout-ic-lora-ltx23)

### `LTX-2.3-22b-IC-LoRA-Golden-Hour`

**LTX-2.3-22b-IC-LoRA-Golden-Hour**
- base `LTXV 2.3` · not stated · strength: not stated · triggers: `ADD GOLDEN HOUR`

Example prompts (from the images API, page, or sidecar; never invented):

Example 1:
```
Reference shows a coastal beach under bright midday daylight. Edited shows the same scene with golden hour lighting. ADD GOLDEN HOUR late-day golden backlight, honey-colored highlights, and gentle atmospheric haze. Subject identity, clothing, framing, and background geometry are identical to the reference; only lighting and time of day differ between reference and edited.
```

Example 2:
```
Reference shows a lagoon and forested hills under bright midday daylight. Edited shows the same scene with golden hour lighting. ADD GOLDEN HOUR late-day golden backlight, honey-colored highlights, and gentle atmospheric haze. Subject identity, clothing, framing, and background geometry are identical to the reference; only lighting and time of day differ between reference and edited.
```

Compatibility: Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible; HF card base_model: Lightricks/LTX-2.3; HF base_model_relation: adapter

Source: [HF](https://huggingface.co/Hoffm4nz/LTX-2.3-22b-IC-LoRA-Golden-Hour)

### `LTX-2.5-22b-IC-LoRA-Golden-Hour`

**LTX-2.5-22b-IC-LoRA-Golden-Hour**
- base `LTXV 2.5` · not stated · strength (stated): 1.0

Example prompts (from the images API, page, or sidecar; never invented):

Example 1:
```
Reference shows a cat sitting on a ledge under bright midday daylight. Edited shows the same scene with golden hour lighting. ADD GOLDEN HOUR low warm sun with long soft shadows, amber rim light, and a warm orange-gold sky. Subject identity, clothing, framing, and background geometry are identical to the reference; only lighting and time of day differ between reference and edited.
```

Example 2:
```
Reference shows three women in a wheat field under bright midday daylight. Edited shows the same scene with golden hour lighting. ADD GOLDEN HOUR low warm sun with long soft shadows, amber rim light, and a warm orange-gold sky. Subject identity, clothing, framing, and background geometry are identical to the reference; only lighting and time of day differ between reference and edited.
```

Compatibility: Graydient LTX workflows (family-level, not a per-LoRA install claim): animate-ltx2 / animate-ltx23 / animate-ltx25 — match the LoRA base when possible; HF card base_model: Lightricks/LTX-2.5; HF base_model_relation: adapter

Source: [HF](https://huggingface.co/Hoffm4nz/LTX-2.5-22b-IC-LoRA-Golden-Hour)

