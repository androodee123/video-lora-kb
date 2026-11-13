# Accessibility report

Updated 13 Nov 2026, 22:18 Africa/Johannesburg (SAST). The available set is **Graydient LoRAs** — every row in `data/loras.jsonl`.

`graydient_status` is **on Graydient** when a matching file is in Hugging Face `Octavian123/civit`, or **to add to Graydient** when the LoRA is on the 13 Nov 2026 AIOps RAID snapshot and still needs civit-to-graydient ingest before it appears in the concept browser. There is no “AIOps only” category: anything on the RAID must be added to Graydient. The `aiops` boolean is kept as secondary information (present on the RAID).

Public CivitAI / Hugging Face video LoRAs not yet in this set live in `data/candidates.jsonl`. RAID files still to add are listed in `data/graydient_ingest_queue.md`. Nothing was auto-downloaded or ingested.

## Counts

| Family | On Graydient | To add to Graydient | Available total | Candidates |
|---|---:|---:|---:|---:|
| MiniMax H3 | 224 | 50 | 274 | 981 |
| Wan | 54 | 19 | 73 | 2706 |
| LTX | 27 | 17 | 44 | 774 |
| **Total** | **305** | **86** | **391** | **4461** |

The 86 *to add to Graydient* rows are the RAID-installed video LoRAs with no matching file in `Octavian123/civit`. See `data/graydient_ingest_queue.md`.

## Unmatched Hugging Face video files added

8 root-level weight files looked like H3 / Wan / LTX video LoRAs and did not match an existing catalog row. Each was added with `graydient=true`, `verified=false`, no invented trigger or strength.

| family | file | slug |
|---|---|---|
| H3 | `Auto-Cunnilingus Legs Behind Head Pose - Minimax H3 - MM-H3 - Auto-cunnilingus.safetensors` | `auto-cunnilingus-legs-behind-head-pose-minimax-h3-mm-h3-auto-cunnilingus` |
| H3 | `Fetish Submission Chain Teddy - Minimax H3 - MM-H3 - Fetish Submission Chain Teddy.safetensors` | `fetish-submission-chain-teddy-minimax-h3-mm-h3-fetish-submission-chain-teddy` |
| LTX2 | `Futa-Masturbation Cumshot - I2V MH3LTXWAN - LTX2.3_v1.0 - ltxcum_13_000002500.safetensors` | `futa-masturbation-cumshot-i2v-mh3ltxwan-ltx2-3-v1-0-ltxcum-13-000002500` |
| H3 | `MiniMax H3 - Pussy spread - v0.1 i2v - minimax_h3_pussy_spread_v0.1.safetensors` | `minimax-h3-pussy-spread-v0-1-i2v-minimax-h3-pussy-spread-v0-1` |
| H3 | `Nipple Play - MiniMax H3 - v1.0 - MiniMaxH3-Nipple_Play-1and3run.safetensors` | `nipple-play-minimax-h3-v1-0-minimaxh3-nipple-play-1and3run` |
| H3 | `Slop Twerk MiniMax H3 LoRa - H3 slop twerk v0.1 - H3_Slop_Twerk_V0.1.safetensors` | `slop-twerk-minimax-h3-lora-h3-slop-twerk-v0-1-h3-slop-twerk-v0-1` |
| H3 | `anime-pixel-h3.safetensors` | `anime-pixel-h3` |
| Wan | `fantasymovie80s-high-wan.safetensors` | `fantasymovie80s-high-wan` |

## Classification doubts

- 3 unmatched HF video files were not added because their slug already exists on an accessible row (likely a long original filename next to a slugged upload): `deepthroat-face-fuck-high-wan.safetensors`, `fingering-high-wan.safetensors`, `sexy-massage-high-wan.safetensors`
- moss/ and *-moss.safetensors were treated as image (KroMoss / Krea) unless an exact catalog video-row match already used the file. No catalog video row matched a moss file in this run, so none were kept.
- Official Hugging Face packs (lightx2v, Lightricks IC-LoRAs, etc.) stay in candidates.jsonl unless the same weights were also uploaded to Octavian123/civit or are on the RAID. They are scored high for ingest because they fill utility gaps, but they are not treated as already accessible.
- Version forks (e.g. `…-v2-h3` on RAID vs `…-h3` on Graydient) are not merged. Each slug is its own row.

## Ingest priority

Candidates in `data/candidates.jsonl` are scored with `scripts/access_rules.py` (log downloads and thumbs, bonuses for recorded trigger/strength/example, gap bonus, official-util bonus). See SKILL.md for the suggest-ingest rule used in recipes and family pages.
