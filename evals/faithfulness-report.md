# Faithfulness eval: first run

How often are a local model's chess statements true? This is the first measurement, on 22 key moments from 5 real games, with the model given the jarvis-chess review (grounded) or only the position (ungrounded).

## Result

| Condition | Checkable claims | True | False | Faithfulness | Wilson 95% interval |
|---|---|---|---|---|---|
| Grounded (review JSON and server instructions) | 67 | 52 | 15 | 0.776 | 0.663 to 0.859 |
| Ungrounded (FEN, move played, engine best move) | 41 | 27 | 14 | 0.659 | 0.505 to 0.784 |

Model: Qwen3.6-35B-A3B (UD-Q4_K_M, llama.cpp), thinking off, temperature 0.7, one reply per moment. The two intervals overlap, so this sample does not show a difference between the conditions with confidence.

Most `best_move` claims repeat the best move the prompt already gave the model (21 of 22 grounded, 20 of 20 ungrounded). Without `best_move` claims, the numbers are:

| Condition | Checkable | True | Faithfulness |
|---|---|---|---|
| Grounded | 45 | 32 | 0.711 |
| Ungrounded | 21 | 8 | 0.381 |

Per claim type (checkable / true):

| Type | Grounded | Ungrounded |
|---|---|---|
| advantage | 17 / 16 | 7 / 4 |
| attacked_by_cheaper | 1 / 0 | 1 / 0 |
| best_move | 22 / 20 | 20 / 19 |
| hanging | 15 / 10 | 9 / 1 |
| in_check | 2 / 0 | 0 / 0 |
| mate_in_one | 2 / 0 | 0 / 0 |
| material | 7 / 5 | 4 / 3 |
| pinned | 1 / 1 | 0 / 0 |

Not in the score, listed for hand labelling: 204 free-text statements outside the eight types (84 grounded, 120 ungrounded) and 2 ungrounded structured claims of an unknown type. One ungrounded reply had a JSON block that did not parse (its claims are lost; the commentary is saved).

## What the false claims look like

- Grounded, game ZRLfDc2e, ply 28 (14...Nxd5): the commentary says the e5 pawn "was hanging and pinned, as confirmed by the pre-move facts". The facts block the model was given lists no hanging, pinned or attacked pieces. The model cited its source while contradicting it.
- Grounded, game movw8h7M, ply 45: three `hanging` claims (h8, f3, b3) that the rules reject, and an `in_check` claim for a position where nobody is in check.
- Grounded, game dlymlJeF, ply 43: two `mate_in_one` claims (Ne8+, h6+) where no mate in one exists.
- Ungrounded: 4 claims name a square with no piece on it (for example "the piece on e5 is hanging" with e5 empty), a board-reading failure the grounded condition did not show (0 such claims).

## Method

1. **Frozen set.** `python evals/faithfulness.py freeze` took the 5 most recent standard games of Lichess user dr_namer (all 3+0, played 2026-10-12 to 2026-10-20), reviewed each with `Analyst.review` (Stockfish 19, 0.15 s per move, up to 5 key moments) and wrote `evals/frozen_set.json`: game ids, PGNs, the full reviews and the 22 key-moment FENs. It was committed in its own commit, `b018a6b`, before any scored run. The run reads the frozen reviews; it does not re-review.
2. **Prompts.** Grounded: system prompt is the MCP server's instructions; the user message holds the review as `review_game` returns it (key moments carry `facts_before`) and names the moment. Ungrounded: a one-line system prompt; the user message holds only the FEN before the move, the move played and the engine's best move. Both end with the same task: 3 to 5 sentences of commentary for a FIDE Master, then one JSON block listing the claims made, in the eight types `check_claims` supports, each tagged with the position it refers to (before or after the move played), plus every other factual statement as free text.
3. **Scoring.** Claims of a supported type go through `claims.check` on the tagged position and `claims.score` gives checkable, true, false and faithfulness. Engine claims use the checker's defaults (0.5 s search, top 2 lines). A claim with no valid position tag is checked on the position before the move.
4. **One engine search per position.** In a smoke run, two 0.5 s searches of the same FEN returned different top-2 moves, so the same `best_move` claim was true in one condition and false in the other. The harness now caches one checker search per position, so both conditions face the same engine verdict. `claims.py` is unchanged.
5. **Audit files.** Every commentary is saved next to its extracted claims and verdicts, and everything the checker cannot judge goes to a CSV with an empty label column.

Run time: 718 s for 44 model calls plus checking (446 s of model time grounded, 258 s ungrounded), on the laptop in the README.

## Limits

- **The model extracts its own claims.** The JSON list may leave out statements the prose makes, or add ones it does not. The commentary file exists so a human can check this; it has not been checked yet. 37 of 110 structured claims (14 grounded, 23 ungrounded) had no valid position tag and were checked on the position before the move; a claim meant for the position after the move can be scored false for that reason alone.
- **The review and the checker are separate searches.** The review's best move comes from a 0.15 s search, the checker's from 0.5 s. In 1 grounded and 1 ungrounded case the model named the review's best move and the checker scored it false (movw8h7M ply 51: review Rad1, checker top 2 Rfe1 and Kh1).
- **Small sample, one model, one sample per moment.** 22 moments from 5 blitz games of one player, one reply each at temperature 0.7. Claims within a moment are not independent, so the Wilson intervals, which assume independent claims, are narrower than the real uncertainty.
- **Eight claim types.** Most of what the model says (204 free-text statements) is outside them and is not in the score. The score must be read next to the checkable counts.
- **The checker's own limits apply** (docs/DECISIONS.md): `hanging` means attacked and undefended in a static one-move view, pins are absolute pins only.
- **No tools in the grounded condition.** The server instructions tell the model to verify with `check_claims`; here it had no tools, so this measures narration of a review, not an agent that can check itself.

## Files

- `evals/faithfulness.py`: freeze and run
- `evals/frozen_set.json`: the frozen games and moments (commit `b018a6b`)
- `evals/results/faithfulness-20261022-142830.json`: every reply, parsed claim, verdict and the summary (prompts are rebuilt from the frozen set by `prompts()`)
- `evals/results/faithfulness-20261022-142830-commentary.md`: commentary next to its claims, for auditing the extraction
- `evals/results/faithfulness-20261022-142830-to-label.csv`: 206 statements for hand labelling
- `tests/test_faithfulness_parse.py`: parser, position handling and interval tests

## Next

The Dr. labels the CSV and audits the extraction on a sample of commentaries; then the same frozen set runs on other models, and the hand-labelled share is reported next to the checkable one.
