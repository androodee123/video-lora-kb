# Wan: Character consistency

6 LoRAs (0 installed on the 13 Nov 2026 RAID snapshot). Installed rows are listed first, then the rest by CivitAI/HF download count.

Strength is recorded only when a page or sidecar states it. Otherwise `not stated`.

| slug / file | trigger | strength | I2V/T2V | purpose | downloads | status | links |
|---|---|---|---|---|---:|---|---|
| `clothconsistency-wan2-2-i2v-consistencylora2` | `clothing consistency.used the clothing in the first frame, generate a video of a model wearing the clothing.` | not stated | I2V and T2V | ClothConsistency-Wan2.2-I2V-ConsistencyLoRA2 | 2,740 | catalog, verified | [CivitAI](https://civitai.com/models/1993310?modelVersionId=2262812) |
| `wan2-2-pinkiepie-pony-mix-breast-consistency-lora` | — | 0.8 | I2V | WAN2.2 PinkiePie Pony Mix Breast Consistency LoRA | 2,360 | catalog, verified | [CivitAI](https://civitai.com/models/2558769?modelVersionId=2875505) |
| `productconsistency-wan2-2-i2v-consistencylora3` | `Product Consistency. Used the product in the first frame, generate a commercial-quality video of the product.` | not stated | I2V and T2V | ProductConsistency-Wan2.2-I2V-ConsistencyLoRA3 | 1,875 | catalog, verified | [CivitAI](https://civitai.com/models/2000699?modelVersionId=2266118) |
| `carconsistency-wan2-2-i2v-consistencylora1` | `Car Consistency. Used the car in the first frame, generate a commercial-quality video of the car.` | not stated | I2V | CarConsistency-Wan2.2-I2V-ConsistencyLoRA1 | 931 | catalog, verified | [CivitAI](https://civitai.com/models/1990350?modelVersionId=2253029) |
| `wan-2-2-asian-consistent-character-instagram-influencer-private-waifu` | `m1npar8`, `black hair`, `bangs` | 0.7–0.9 | T2V | [WAN 2.2] Asian Consistent Character | 772 | catalog, verified | [CivitAI](https://civitai.com/models/2068097?modelVersionId=2340163) |
| `sharon-flux-wan` | — | 1.0–1 | I2V | Sharon - Flux | 158 | catalog, verified | [CivitAI](https://civitai.com/models/2924390?modelVersionId=3312475) |

## Details

### `wan22-tool3-ProductConsistency-16-8-NoH-000080.safetensors`

**ProductConsistency-Wan2.2-I2V-ConsistencyLoRA3**
- base `Wan Video 2.2 I2V-A14B` · I2V and T2V · strength: not stated · triggers: `Product Consistency. Used the product in the first frame, generate a commercial-quality video of the product.`

Example prompt (from the images API, page, or sidecar; never invented):


```
,for more,please check the info of the video: "Product Consistency. Used the product in the first frame, generate a commercial-quality video of the product. The product is a canned drink.The product is floating in the air in the dark with some neon green light shineing. Suddenly the product is grabed by a huge monster hand. The overall atomsphere is dark and cyberpunk." ProductConsistency 是该系列的第三个模型.该模型希望通过直接输入产品的白底图,通过prompt直接生成产品的视频.从我个人测试的来看(推荐强度: high0.9,low0.9,lightning low:1.0 ).在写好prompt和使用lightning low lora加速的情况下,ProductConsistency的效果很不错.但相较于CarConsistency和ClothConsistency我之前发布的两个Consistency模型,可能因为Wan2.2训练的数据较少,对于广告场景的Prompt的遵循程度比较一般,需要一定程度的PromptEnginering才能得出比较好的结果,还有值得注意的是,不建议写关于商品主体的Prompt(容易产生主体一致性问题),然后在样例中的, 我会将产品的类型说明出来(使得T5更理解商品本身的形状,生成更加生动), 比如The product is a canned drin
```

Compatibility: mode: I2V and T2V; Wan low-noise file present; pair with the matching high-noise LoRA on 2.2 14B; Wan 2.2 14B; 2.1 cross-use is not guaranteed; Graydient Wan workflows (family-level, not a per-LoRA install claim): animate-wan22, video-wan22

Source: [CivitAI](https://civitai.com/models/2000699?modelVersionId=2266118)

