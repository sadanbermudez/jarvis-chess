# Design decisions

jarvis-chess is an MCP server that lets a language model review chess games without inventing facts about them. This document records the decisions that shape the code, why each one was made, what it costs, and how to verify it from the repository. Every number below comes from the code, the tests, the README, or the project's research notes.

## System in one picture

```
   Lichess API ----+                                   +---- Stockfish (UCI process)
   Chess.com API --+--> sources.py                     |     one SimpleEngine, behind a lock
   (no token)          recent(), summarize()           |
                            |                          |
                            v                          v
  LLM client  <------>  server.py (FastMCP "jarvis-chess")  ------>  analysis.py
  (Claude Code,  stdio   recent_games                              Analyst.review()
   Jarvis)       or      review_game                               Analyst.position()
                 HTTP    analyse_position                          facts()      <- python-chess rules
                         check_claims  ------------------------->  claims.py
                            |                                      check(), score()
                            v
                 JSON facts, grades, verdicts
                 (the model narrates these; it does not compute them)
```

The model sits on the left and only receives JSON. Every evaluation, grade, tactic and verdict is produced on the right by Stockfish or by python-chess.

---

### 1. Engine and rules produce the facts; the model only narrates

**Context.** LLM chess "coaches" built on top of Stockfish already exist (the project research lists several), and the risk they share is that the engine number is right while the explanation of it is invented. The README cites a separate project (photonics-lab-mcp) in which a local model measured a physics result correctly and then explained it wrongly, twice.

**Decision.** Every statement about a position is computed outside the model. `analysis.facts()` derives hanging pieces, pieces attacked by a cheaper piece, pins, checks available, mate in one, material and legal move count from python-chess alone. `Analyst.review()` attaches those facts (`facts_before`) to each key moment, and `Analyst.position()` returns them next to the engine's top lines. The FastMCP `instructions` string in `server.py` tells the model to "say only what these tools report", never invent tactics, and verify anything else with `check_claims`.

**Why.** A model reading a FEN string is doing board reconstruction in its head, which is exactly where hallucinated tactics come from. The rules of chess are cheap to compute exactly, so there is no reason to ask the model for them. Shifting the model's job from "analyse" to "narrate this JSON" turns an open-ended generation problem into a summarisation problem, which is much easier to keep honest and much easier to check.

**Alternatives.** Let the model analyse the board directly and use Stockfish only for the evaluation number. Give the model the engine's lines without any rule-computed facts and let it explain them.

**Trade-offs.** The model can only talk about what `facts()` knows. Ideas that are not on the list (weak squares, pawn structure, plans) have no machine source yet, so the model either stays silent on them or says something unverified. The instructions string is a prompt, not an enforcement mechanism; a model can ignore it, which is why decision 2 exists.

**Check it yourself.** `src/jarvis_chess/analysis.py`, function `facts()`; `src/jarvis_chess/server.py`, the `FastMCP(... instructions=...)` call. Run `analyse_position` on any FEN and read the `facts` block.

---

### 2. A claim checker that returns true, false or "cannot check"

**Context.** Telling the model to be honest does not measure whether it was. The research behind this project found several chess MCP servers and LLM coaches, and none of them publishes how often their explanations are true.

**Decision.** `claims.check()` takes a board and a list of small structured claims (`hanging`, `attacked_by_cheaper`, `pinned`, `in_check`, `mate_in_one`, `best_move`, `advantage`, `material`) and returns a verdict per claim: `True`, `False`, or `None` with a reason. `claims.score()` reduces the list to `checkable`, `true`, `false` and `faithfulness` (true divided by checkable). It is exposed as the `check_claims` tool.

**Why.** Structured claims make verification a lookup, not another round of language understanding. Rule-based claims reuse `facts()`, so the checker and the reviewer can never disagree. Engine-based claims run one multi-PV search per call, cached in `lines`, so several claims about the same position cost one search. The third value matters: an unknown claim type, a malformed claim, or an engine claim with no engine returns `None` and is excluded from the denominator, so "could not check" is never silently counted as "false" or "true". `best_move` passes if the move is among the engine's top `tolerance` lines (default 2), which accepts two near-equal moves instead of punishing the second one. `advantage` needs at least 50 centipawns (0.5 pawns) for the named side.

**Alternatives.** Free-text claims parsed by a second LLM (an LLM judge). A single pass/fail flag per explanation instead of per claim.

**Trade-offs.** Only eight claim types exist, so many real chess statements are unverifiable today and fall out of the score. Excluding `None` from the denominator means a model that makes mostly unverifiable claims can still post a high faithfulness number; the score must always be reported together with `checkable`. The 50 centipawn and top-2 tolerances are judgment calls written into the code, not derived values.

**Check it yourself.** `src/jarvis_chess/claims.py`, `check()` and `score()`. `tests/test_chess.py::test_claims_without_engine` feeds six claims (including an unknown `teleport` type and an engine claim with no engine) and asserts verdicts `[True, False, True, False, None, None]` and a score of 4 checkable, 2 true, faithfulness 0.5.

---

### 3. Grade moves by Lichess's winning-chances drop, not raw centipawn cutoffs

**Context.** A review needs to label moves as inaccuracies, mistakes and blunders. The naive rule is a centipawn threshold (for example "lost 300 centipawns, so blunder"). That rule misfires in positions that are already decided.

**Decision.** `analysis.win_chances(cp)` maps a centipawn score to a value in [-1, 1] with Lichess's published curve, `2 / (1 + exp(-0.00368208 * cp)) - 1`. `Analyst.review()` computes the drop in the mover's winning chances across the move, and `analysis.grade()` labels it: 0.1 or more is an inaccuracy, 0.2 a mistake, 0.3 a blunder. A move equal to the engine's best move is never graded. Mate scores are converted to 10000 centipawns (`MATE_CP`), which maps to winning chances of 1.0.

**Why.** The curve is a logistic: steep near equality, flat near the ends. Losing material matters a lot when the game is balanced and very little when one side is already winning by a lot. Concrete values from the formula in the code:

| Eval before | Eval after | Centipawns lost | Winning-chance drop | Grade |
|---|---|---|---|---|
| +1.00 | -1.00 | 200 | 0.364 | blunder |
| 0.00 | -3.00 | 300 | 0.502 | blunder |
| +8.00 | +5.00 | 300 | 0.174 | inaccuracy |
| +10.00 | +7.00 | 300 | 0.092 | none |

A flat 300 centipawn rule would call all three 300 centipawn moves blunders and miss the 200 centipawn one that throws away a balanced game. The winning-chances rule tracks what a strong player actually means by "that move changed the result". It also gives mates a sensible place on the same scale. Skipping the grade when the played move equals the engine's best move stops search noise (the score after the move can differ slightly from the score before it at short time budgets) from flagging the best move as an inaccuracy. Using the grading method Lichess publishes keeps the labels in line with what players already see on Lichess.

**Alternatives.** Fixed centipawn thresholds. Lichess's accuracy percentage instead of counted errors.

**Trade-offs.** The constant and thresholds are inherited from Lichess, not fitted to this engine or time budget. Average centipawn loss is still reported per side (it is the familiar number), and moves where either score is a mate contribute 0 loss to it, so a missed mate does not show up in the average, only in the grade.

**Check it yourself.** `src/jarvis_chess/analysis.py`, `win_chances()`, `grade()`, and the `drop` line in `Analyst.review()`. `tests/test_chess.py::test_grading_follows_lichess_thresholds` and `test_engine_review_finds_the_blunder` (3...Nf6 in Scholar's mate graded a blunder). Reproduce the table with `python -c "from jarvis_chess.analysis import win_chances as w; print(w(100)-w(-100))"`.

---

### 4. Public game APIs, no account and no token

**Context.** `recent_games` needs the player's latest games from Lichess and Chess.com.

**Decision.** `sources.py` uses the public, unauthenticated endpoints with Python's standard `urllib`. Lichess: `/api/games/user/{username}` with `pgnInJson=true` and `opening=true`, read as NDJSON. Chess.com: `/pub/player/{username}/games/archives`, then monthly archives walked from newest to oldest until `count` standard-chess games are collected (variants are skipped by `rules == "chess"`). Requests carry a descriptive `User-Agent`. Both sites reduce to the same dict through `summarize()`.

**Why.** Game history for a public account is public data, so a token adds setup friction and a secret to manage without adding capability. Anyone cloning the repo can run it with only a username. Standard library HTTP keeps the dependency list at two pinned packages (`chess==1.11.2`, `mcp==1.30.0`). Normalising both sites into one shape means `review_game` does not care where a game came from.

**Alternatives.** OAuth or personal API tokens. A third-party wrapper library per site.

**Trade-offs.** Private games and anything that needs authentication are out of reach. Rate limits are the sites' public ones, and there is no retry or backoff. The Chess.com walk makes one request per month of history it has to read, so a player with few recent games costs several requests. The network path has no automated test; only `summarize()` is tested.

**Check it yourself.** `src/jarvis_chess/sources.py`, `lichess_recent()`, `chesscom_recent()`, `summarize()`. `tests/test_chess.py::test_pgn_summary`.

---

### 5. One long-lived Stockfish process, created lazily, shared behind a lock

**Context.** Starting a UCI engine costs a process launch, a handshake and hash allocation. MCP tool calls arrive one at a time over stdio, but can overlap over HTTP.

**Decision.** `server.analyst()` creates a single `Analyst` (a `chess.engine.SimpleEngine` configured with 8 threads and 256 MB hash) on first use and keeps it for the life of the server. Every tool that touches the engine (`review_game`, `analyse_position`, `check_claims`) holds the module-level `threading.Lock` while it runs.

**Why.** A warm engine with a filled hash table answers follow-up questions about the same game faster, and the startup cost is paid once. Lazy creation means `recent_games` works even before Stockfish is needed. A UCI engine is a single conversation over stdin and stdout; two searches interleaved on one process would corrupt each other, so the lock serialises access.

**Alternatives.** A new engine per tool call. A pool of engines for parallel requests.

**Trade-offs.** Requests are strictly serial: a long `review_game` blocks every other engine call until it finishes. 8 threads and 256 MB are fixed defaults in `Analyst.__init__()`, not tuned to the host the server runs on. `check_claims` always passes the engine, so even a rule-only claim list starts Stockfish on first use.

**Check it yourself.** `src/jarvis_chess/server.py`, `analyst()` and `_lock`; `src/jarvis_chess/analysis.py`, `Analyst.__init__()`.

---

### 6. Explicit engine shutdown, because `atexit` never fires

**Context.** During development the process hung at exit. The cause, banked in the project notes: python-chess's `SimpleEngine` runs its event loop on a non-daemon thread. Python waits for all non-daemon threads before it runs `atexit` handlers, so an `atexit` hook that closes the engine is never reached, and the thread never ends because nothing closed the engine. A deadlock at shutdown.

**Decision.** `server.shutdown()` closes the engine, and `server.main()` calls it in a `finally` block around `mcp.run()`, for both transports. `Analyst.close()` tries a polite `quit()`, falls back to `close()`, and swallows exceptions so shutdown can never raise or block. The test suite uses a module-scoped autouse fixture that calls `server.shutdown()` after the tests, and the direct-engine test closes its own `Analyst` in a `finally`.

**Why.** Cleanup tied to control flow (`finally`) runs before the interpreter starts waiting on threads, so it does not depend on interpreter exit order at all. The defensive `close()` exists because at the very end of a run the engine's event loop may already be gone, and a cleanup path that throws would just replace one hang or crash with another.

**Alternatives.** An `atexit` hook (the version that hung). A context manager around the engine for each call, which would give up decision 5.

**Trade-offs.** Every entry point that creates an engine must remember to close it; a new script that imports `Analyst` and forgets will hang the same way. The bare `except Exception` hides real shutdown errors.

**Check it yourself.** `src/jarvis_chess/server.py`, `shutdown()` docstring and `main()`; `src/jarvis_chess/analysis.py`, `Analyst.close()`; `tests/test_chess.py`, fixture `_stop_server_engine`. Per the banked note, removing the fixture makes `pytest` hang after the tests finish.

---

### 7. A fixed time budget per move, with clamped tool arguments

**Context.** A full game review analyses every position, so cost grows with game length, and an MCP client (a model) chooses the arguments.

**Decision.** `Analyst.review()` searches each position for a fixed time, `seconds_per_move=0.15` by default, with `chess.engine.Limit(time=...)`. Each position is searched once and reused as the "before" of the next move. The tool layer clamps what a model can ask for: `review_game` limits `seconds_per_move` to 0.05 to 2.0 and `key_moments` to 1 to 10; `analyse_position` limits `seconds` to 0.1 to 10.0 and `lines` to 1 to 5; `recent_games` limits `count` to 1 to 20. Only the moves of the worst graded positions get the full `facts_before` block, and the per-move list returned to the model is trimmed to six fields.

**Why.** A time limit makes review cost predictable: plies plus one searches, each 0.15 s. The README measures a 39-ply blitz game at 6.5 s with Stockfish 19 at 0.15 s per move. Reusing each search as the next move's "before" halves the engine work compared with searching before and after every move separately. Clamps stop a model from requesting a 60-second search per move by mistake. Trimming the output keeps the model's context on the key moments, where the facts are.

**Alternatives.** A fixed depth per move. Adaptive time (more for critical positions).

**Trade-offs.** Time-limited results depend on the hardware, so the same game can grade slightly differently on a slower machine or in CI. 0.15 s is shallow for sharp tactical positions; a deep tactic can be missed or misgraded. That is acceptable for a first pass over a blitz game, not for serious analysis, and the tool exposes `seconds_per_move` so the caller can raise it.

**Check it yourself.** `src/jarvis_chess/analysis.py`, `Analyst.review()`; `src/jarvis_chess/server.py`, the `max(...min(...))` clamps in each tool. README, section "Measured".

---

### 8. MCP over stdio by default, Streamable HTTP on localhost as an option

**Context.** The first client is Claude Code (registered through `.mcp.json` as a stdio server, per the project notes). The intended home is Jarvis, the author's local assistant (README), and not every client wants to spawn the server as a child process.

**Decision.** `server.main()` runs FastMCP over stdio by default. `--http` switches to Streamable HTTP bound to `127.0.0.1` on port 8772 (`--port` overrides). The package installs a `jarvis-chess` console script.

**Why.** MCP makes the tools usable by any MCP client without client-specific glue. Stdio is the simplest and most private transport: the client spawns the server, there is no port, and nothing listens on the network. HTTP lets one engine-backed server outlive a client session and serve more than one client. Binding to `127.0.0.1` keeps that server off the local network.

**Alternatives.** A plain REST API. A Python library imported directly by the agent.

**Trade-offs.** The HTTP mode has no authentication; it relies on being bound to localhost. State is process-global: `_last` (the list from the last `recent_games` call, which `review_game` reads by index or URL) is shared by every HTTP client, so two clients can see each other's game lists.

**Check it yourself.** `src/jarvis_chess/server.py`, `main()`; `pyproject.toml`, `[project.scripts]`. Run `jarvis-chess --http` and connect an MCP client to the Streamable HTTP endpoint on `127.0.0.1:8772`.

---

### 9. Test positions chosen so the answer is not a matter of opinion

**Context.** Chess analysis is full of judgment calls. A test that asserts a judgment call breaks when the engine version or time budget changes.

**Decision.** `tests/test_chess.py` uses minimal positions where the correct answer is forced by the rules: a queen attacking an undefended knight (`HANGING`), a defended knight attacked by a pawn (`CHEAPER`, which must not be called hanging), a knight pinned to its king by a rook (`PIN`), a defended rook attacked only by a king (`KING_ONLY`, which must not be called attacked by a cheaper piece), a back-rank mate (`BACK_RANK`, only `Ra8#`), and Scholar's mate (`SCHOLAR`), where 3...Nf6 is a blunder by any standard. Engine tests accept a set of best moves (`g6`, `Qe7`, `Qf6`) instead of one. Tests that need Stockfish are marked `skipif` when no engine is found. 9 tests in total.

**Why.** If a test fails, the code is wrong, not the chess. Positions with very few pieces isolate the one rule under test. The `CHEAPER` case guards the distinction between "hanging" and "attacked by a cheaper piece", which is exactly the kind of claim a model gets wrong. Accepting several defences to Qxf7 keeps the test stable across engine versions and time limits. The skip marker lets the rule tests run on a machine without Stockfish.

**Alternatives.** Snapshot tests of a full game review. A test suite built from real games with engine-labelled answers.

**Trade-offs.** Clean positions do not exercise the hard cases: x-rays, pinned defenders, exchanges, discovered attacks. A test run without Stockfish silently skips the two engine tests, which is why CI installs it (decision 10).

**Check it yourself.** `tests/test_chess.py`, constants at the top. `pytest -v` lists 9 tests.

---

### 10. CI installs Stockfish from apt and points to it with `STOCKFISH_PATH`

**Context.** Two of the 9 tests need a real engine, and they skip without one. A green CI run that skipped them would prove little.

**Decision.** `.github/workflows/ci.yml` runs on every push and pull request on `ubuntu-24.04` with Python 3.11, installs Stockfish with `apt-get install -y stockfish`, installs the package in editable mode with `pytest==9.1.1`, and sets `STOCKFISH_PATH=/usr/games/stockfish` for the test step. `analysis.engine_path()` resolves the engine in a fixed order: `STOCKFISH_PATH`, then the local Windows default path if it exists, then `stockfish` on `PATH`.

**Why.** The distribution package is one command and needs no download script or checksum handling in the workflow. Setting the path explicitly removes any dependence on whether `/usr/games` is on the runner's `PATH`. The same environment variable is the documented way to run locally (README, "Run"), so CI and a developer machine configure the engine identically. Pinned versions for `chess`, `mcp` and `pytest` keep runs reproducible.

**Alternatives.** Downloading an official Stockfish release binary in CI. Mocking the engine.

**Trade-offs.** The apt Stockfish is whichever version Ubuntu 24.04 packages, not necessarily the Stockfish 19 used locally, so engine results in CI and on the development machine can differ. The engine tests are written to tolerate that (decision 9). The fallback `DEFAULT_ENGINE` is a hardcoded path on the author's Windows machine, harmless elsewhere because it is only used if it exists, but it is personal configuration living in source.

**Check it yourself.** `.github/workflows/ci.yml`; `src/jarvis_chess/analysis.py`, `engine_path()`. The CI badge in the README links to the run history.

---

## Known limits and what comes next

- **The faithfulness eval has not been run.** The checker exists and is tested, but there is no published number yet for how often a model's chess statements are true. That eval (model comments on key moments, checkable claims through `check_claims`, the rest labelled by a FIDE Master) is the first item in the README's "Next" section and the point of the project.
- **`facts()` is a static, one-move view.** "Hanging" means attacked with zero defenders. It does not resolve exchange sequences, x-ray defenders, pinned defenders or overloaded pieces, so a piece can be listed as safe and still be lost, or listed as hanging when taking it loses. Pins are only absolute pins to the king.
- **Fixed: king attackers.** A defended piece attacked only by the enemy king used to be reported as attacked by a cheaper piece (the king has value 0 in `VALUES`, but cannot capture a defended piece). `facts()` now ignores the king when comparing attacker values; `test_king_is_not_a_cheaper_attacker` covers it with FEN `8/8/8/8/8/3qk3/3r4/3K4 w - - 0 1`.
- **`checks_available` is cut to the first 8 checks**, so a "there is a check with X" claim can be true without appearing in that list.
- **Average centipawn loss ignores mate-scored moves** (decision 3), so it understates the cost of missed mates.
- **Shallow, hardware-dependent search** (decision 7). Grades near a threshold can change between machines.
- **Shared process state in HTTP mode** (decision 8), and no authentication on that transport.
- **No tests for the network path** to Lichess and Chess.com, and no retry on failure.
- **Planned, per the README:** Maia-2 for "what would a human at this rating play" next to Stockfish's best move, and an interactive board on the author's site that replays a reviewed game with each AI claim marked true or false.

## Questions a reviewer might ask

**Why not just let the LLM analyse the position? Modern models are good at chess.**
Kaggle's 2025 text-only LLM chess exhibition (per the project research) was won by a model at an estimated 1686 rating, and another lost games on illegal moves. That is far below the level of the intended reader, a FIDE Master. The rules and Stockfish are exact and cheap, so the model is given the one job it is good at: turning structured facts into language.

**How do you know the model's commentary is actually faithful?**
Not yet measured, and the README says so. What exists is the instrument: `check_claims` turns each checkable statement into true, false or "cannot check", and `score()` gives the share that held. The next step is to run it over a model's commentary on real key moments and report that share together with how many claims were checkable.

**Why winning chances instead of centipawns?**
Centipawns are linear and the game result is not. With the Lichess curve in `win_chances()`, a 200 centipawn swing from +1 to -1 is a 0.364 drop (blunder), while a 300 centipawn swing from +10 to +7 is a 0.092 drop (no grade). That matches how a strong player judges a move: did it change the likely result.

**Why does the process hang without the explicit shutdown?**
python-chess runs the engine's event loop on a non-daemon thread. Python joins non-daemon threads before running `atexit` handlers, so an `atexit` hook that closes the engine is never reached, and the thread never stops. Closing the engine in `main()`'s `finally` (and in a test fixture) breaks the cycle.

**What happens if two clients call `review_game` at the same time over HTTP?**
They are serialised by `_lock`, so the second waits for the first. That is required, because one UCI process cannot run two searches at once. The visible issue is shared state: `_last` is global, so clients share the game list that index-based review reads from.

**Your claim checker excludes unverifiable claims from the score. Is that not gaming the number?**
It would be if the score were reported alone, so `score()` also returns `checkable`, `true` and `false`. The alternative, counting unverifiable claims as false, would punish a model for talking about plans and structure, which are legitimate topics the checker cannot cover yet. The honest report is both numbers side by side.

**How would you scale this to review thousands of games?**
The current design is one engine behind a lock, which is right for one interactive user. For batch work the review loop would move to a pool of engine processes with one game per worker, a fixed depth instead of fixed time so results do not depend on load, and cached results per position.
