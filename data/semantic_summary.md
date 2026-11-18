# Semantic LoRA catalog summary

Built 2026-11-18 by `scripts/build_semantic.py` from `data/loras.jsonl`, the AIOps library snapshot and the ingest plans. Adults only: safety-skipped CivitAI ids and minor/school-coded names are excluded.

| family | entries | on Graydient | own (onemoreepoch) | no trigger | with semantic tags |
|---|---:|---:|---:|---:|---:|
| H3 | 487 | 454 | 0 | 229 | 475 |
| Wan | 1044 | 1001 | 0 | 459 | 935 |
| LTX2 | 57 | 42 | 0 | 25 | 49 |
| **total** | 1588 | 1497 | 0 | 713 | 1459 |

Entries per semantic category: subject/character 368, concept/intent 1068, clothing/outfit 55, expression 68, object/prop 153, pose/action/camera 413, style/medium 617, anatomy 596, video motion 388.

Excluded while building: minor/school-coded text 1, minor-coded character/franchise 10, KB excluded (minor-coded / not a LoRA) 2, safety-skip id 2.

Fields: slug, family, base_model, name, triggers (empty = no trigger; registered on Graydient by slug), weight (+source), source_url, creator (onemoreepoch = Andrew's own), ingest_date, availability{graydient,hf,raid}, role, semantic{category:[tags]}.
