# Semantic LoRA catalog summary

Built 2026-11-23 by `scripts/build_semantic.py` from `data/loras.jsonl`, the AIOps library snapshot and the ingest plans. Only LoRAs with an explicit loli/shota/underage-type term in their own name, triggers or tags (or a forbidden identity) are excluded. 13 entries are kept but flagged `minor_coded` (canonically minor/school-age characters, age sliders/de-aging, ingest-review safety skips, or a child term in the description): the matcher offers them only for SFW prompts and never stacks them with NSFW/anatomy LoRAs. 807 entries are marked `nsfw`.

| family | entries | on Graydient | own (onemoreepoch) | no trigger | with semantic tags |
|---|---:|---:|---:|---:|---:|
| H3 | 496 | 463 | 0 | 232 | 484 |
| Wan | 1059 | 1016 | 0 | 464 | 950 |
| LTX2 | 57 | 42 | 0 | 25 | 49 |
| **total** | 1612 | 1521 | 0 | 721 | 1483 |

Entries per semantic category: subject/character 376, concept/intent 1079, clothing/outfit 57, expression 69, object/prop 156, pose/action/camera 420, style/medium 625, anatomy 607, video motion 397.

Excluded while building: KB excluded (explicit minor term / forbidden identity / not a LoRA) 2.

Fields: slug, family, base_model, name, triggers (empty = no trigger; registered on Graydient by slug), weight (+source), source_url, creator (onemoreepoch = Andrew's own), ingest_date, availability{graydient,hf,raid}, role, semantic{category:[tags]}.
