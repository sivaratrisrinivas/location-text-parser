# Results

Exact match per field. dev = cases the rules were tuned on. heldout = never looked at while writing rules.

| engine | split | n | allowed | timezones | engagement | visa | india | conflict | all fields |
|---|---|---|---|---|---|---|---|---|---|
| rules | dev | 16 | 15/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 | 15/16 |
| rules | heldout | 16 | 14/16 | 13/16 | 16/16 | 15/16 | 16/16 | 16/16 | 11/16 |
| rules | all | 32 | 29/32 | 29/32 | 32/32 | 31/32 | 32/32 | 32/32 | 26/32 |
| llm | dev | 16 | 14/16 | 15/16 | 16/16 | 16/16 | 14/16 | 16/16 | 13/16 |
| llm | heldout | 16 | 11/16 | 13/16 | 16/16 | 16/16 | 12/16 | 16/16 | 9/16 |
| llm | all | 32 | 25/32 | 28/32 | 32/32 | 32/32 | 26/32 | 32/32 | 22/32 |

## Code checks (pass / total outputs)

| check | rules | llm |
|---|---|---|
| check_schema | 32/32 | 32/32 |
| check_conflict_consistent | 32/32 | 32/32 |
| check_india_derivation | 32/32 | 32/32 |

## Errors

- rules / heldout / tether: allowed got ['AT', 'DK', 'SE', 'WORLDWIDE'] want ['WORLDWIDE']
- rules / dev / flexibits: allowed got ['CA', 'DE', 'EUROPE', 'UK', 'US', 'WORLDWIDE'] want ['WORLDWIDE']
- rules / heldout / sourcegraph: allowed got ['CA', 'EUROPE', 'NON_US', 'UK', 'WORLDWIDE'] want ['CA', 'EUROPE', 'US', 'WORLDWIDE']; timezones got ['US_PACIFIC'] want ['US_EAST', 'US_PACIFIC']
- rules / heldout / pagnos: visa got unknown want no
- rules / heldout / vistulo: timezones got ['US_EAST'] want []
- rules / heldout / hospitable: timezones got ['EMEA', 'US_EAST'] want ['EMEA', 'EUROPE', 'US', 'US_EAST']
- llm / dev / flexibits: timezones got ['CET', 'US_PACIFIC', 'US_PACIFIC..CET'] want ['US_PACIFIC..CET']
- llm / heldout / sourcegraph: timezones got ['EUROPE', 'US_EAST', 'US_PACIFIC'] want ['US_EAST', 'US_PACIFIC']
- llm / heldout / sidekick: allowed got ['US'] want []; india got no want unknown
- llm / heldout / checkly: allowed got ['EUROPE', 'LATAM', 'US'] want ['EUROPE', 'US']; timezones got ['EUROPE', 'US_EAST', 'UTC+1..UTC+2', 'UTC-3..UTC+3'] want ['US_EAST', 'UTC+1..UTC+2', 'UTC-3..UTC+3']
- llm / dev / opensanctions: allowed got ['WORLDWIDE'] want []; india got yes want unknown
- llm / heldout / allgravy: allowed got ['DK', 'EUROPE', 'UK'] want []; india got no want unknown
- llm / dev / seeq: allowed got ['WORLDWIDE'] want []; india got yes want unknown
- llm / heldout / vistulo: timezones got ['US_EAST'] want []
- llm / heldout / eventfirst: allowed got ['EUROPE'] want []; india got no want unknown
- llm / heldout / plantingspace: allowed got ['EUROPE'] want []; india got no want unknown
