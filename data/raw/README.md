# Raw harvest dumps

`scripts/harvest.py` writes CivitAI list pages, full `/api/v1/models/{id}` dumps, `/api/v1/images` caches, and Hugging Face repo listings here (`civitai/` and `huggingface/`). The large JSON subfolders are gitignored.

They contain **JSON metadata only** — no LoRA weights. Re-create or resume with:

```
python3 scripts/harvest.py --full-sorts --period AllTime
python3 scripts/harvest.py --keywords
python3 scripts/harvest.py --hf-expand
python3 scripts/harvest.py --enrich --enrich-images
```

The harvest is cache-aware and resumable. Keyword list pages may include non-video LoRAs; `write_index` and `--enrich` keep only models with a confirmed video `baseModel`. `--enrich-images` is best-effort: the public CivitAI images API often returns `meta: null`, so example prompts also come from page descriptions when present.
