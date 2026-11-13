# Raw harvest dumps

`scripts/harvest.py` writes CivitAI list pages and Hugging Face repo listings here (`civitai/` and `huggingface/`). Those subfolders are gitignored because they are tens of megabytes.

They contain **JSON metadata only** — no LoRA weights. Re-create them with:

```
python3 scripts/harvest.py --sorts newest
python3 scripts/harvest.py --verify-sorts
python3 scripts/harvest.py --hf-only
```

`--verify-sorts` checks the first page of Most Downloaded and Highest Rated against the Newest crawl so popular models are not missed.
