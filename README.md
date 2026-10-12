# Where can I work from?

A small tool that reads a job's location text and returns structured fields:

- allowed countries or regions
- time zones
- EOR, B2B, contractor or freelance setups
- visa sponsorship
- whether someone in India can apply
- a conflict flag, with a reason, when two sources for the same job disagree

Live demo: https://location-text-parser.vercel.app (rules engine, Vercel free tier)

Demo video (75 s): https://github.com/sivaratrisrinivas/location-text-parser/releases/download/v0.1/matcha-location-text-demo.mp4

## Why

Matcha's Founding Software Engineer page says "Fully remote (US, Canada, Europe, UK, Brazil, LATAM)". The founder's HN post from 2026-10-12 says "Fully remote anywhere in the world". So can someone in India apply? One source says no, the other says yes. A job search agent that reads only one of them gives a confident wrong answer. This tool reads both and says "sources conflict" instead.

Case #1 in the eval is exactly that pair. Both pages were fetched and saved on 2026-10-13 (`sources/matcha_fse.html`, `sources/hn_50056667.json`).

## How it works

- `locparse/rules.py`: regex rules. They read only sentences that talk about where the candidate may work from, and skip sentences about the team, customers or offices.
- `locparse/llm.py`: optional LLM parser with the same output schema (Groq free tier, `openai/gpt-oss-120b`, temperature 0).
- `locparse/merge.py`: parses each source on its own, merges them, and sets `conflict` when the sources give different India answers or different visa answers.

```
python -c "from locparse import parse; print(parse(['Remote (US only). We are not able to sponsor visas.']))"
```

## Eval

32 real cases from public job posts, collected on 2026-10-13: 26 single posts from HN "Who is hiring" (October 2026), and 6 jobs with two sources each (job page vs. HN post, or HN post vs. careers page). 3 cases are real conflicts: Matcha FSE, Matcha AI, and Search Atlas (HN says "anywhere", the careers page lists six countries). Gold labels are hand-written in `scripts/build_cases.py`; the inputs and labels are in `data/cases.json`.

Split: case #1 is in dev; the other 31 were shuffled with a fixed seed into 16 dev and 16 held-out before any rule was written. The rules were tuned on dev only. Held-out was scored once and that first run is saved in `evals/heldout_rules_first_run.txt`. The LLM prompt was written once and not tuned.

Exact match per field:

| engine | split | allowed | time zones | engagement | visa | India | conflict | all fields |
|---|---|---|---|---|---|---|---|---|
| rules | dev (16) | 15 | 16 | 16 | 16 | 16 | 16 | 15 |
| rules | held-out (16) | 14 | 13 | 16 | 15 | 16 | 16 | **11** |
| LLM | dev (16) | 14 | 15 | 16 | 16 | 14 | 16 | 13 |
| LLM | held-out (16) | 11 | 13 | 16 | 16 | 12 | 16 | **9** |

The honest reading:

- The number to trust is held-out: rules get all fields right on 11 of 16 jobs (69%), the LLM on 9 of 16 (56%).
- Rules got the India answer right on 32 of 32 and the conflict flag on 32 of 32. But only 3 cases are conflicts, so that conflict score says little. More conflict cases are the first thing to add.
- Engagement and visa are easy here because most posts say nothing; "not stated" counts as a correct answer.
- Most LLM misses are on "EU time zone" style posts: it turns a time zone into an allowed region (Europe), which then turns India into "no" instead of "unknown". Some people would call that fine; my labels say the post did not state a country.
- Rules misses: office cities read as allowed countries (Tether), a curly apostrophe in "don't offer visa sponsorship" (PAGNOS), and multi-role posts with several time-zone lines.
- 32 cases labeled by one person. Treat these numbers as a rough check, not a benchmark.

Full error list: `evals/results.md`.

Code checks (`evals/checks.py`), run on every output: valid schema and vocabulary, a conflict always carries a reason, and the India answer follows from the allowed list. Rules pass 32/32 on all three; LLM outputs pass 32/32 too. `tests/` has pass and fail examples for each check plus a regression test for case #1.

```
python -m pytest -q
python -m evals.run_eval rules heldout
python -m evals.report               # uses cached LLM outputs in evals/out_llm.json
GROQ_API_KEY=... python -m evals.run_eval llm all   # delete evals/out_llm.json to re-run
```

## Run the web demo

```
python web/server.py   # http://localhost:8000
```

No keys needed; the web demo uses the rules engine.

The hosted copy is one bundled Vercel Python function: `python scripts/bundle_vercel.py` writes `build/vercel/`, which is deployed by hand.

## Video

`video/` has the pipeline: Kokoro TTS per line (af_heart, speed 0.95), a headless Playwright recording that waits for each line to finish before the next action, then ffmpeg cuts page-load dead air, burns in captions, and normalizes to -16 LUFS. `video/stt.txt` is the speech-to-text check.
