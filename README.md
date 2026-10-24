# jarvis-chess

[![tests](https://github.com/sadanbermudez/jarvis-chess/actions/workflows/ci.yml/badge.svg)](https://github.com/sadanbermudez/jarvis-chess/actions/workflows/ci.yml)

An MCP server that lets an AI assistant review chess games without making things up. Stockfish and the rules of chess produce every fact; the language model only narrates them, and anything it wants to claim can be checked first.

Built for Jarvis, my local assistant, and for a specific reader: me, a FIDE Master who notices immediately when an "AI coach" invents a tactic.

## Why

Many projects pair an LLM with Stockfish to explain games. They share one weakness: nobody measures how often the explanation is true. In a separate project ([photonics-lab-mcp](https://github.com/sadanbermudez/photonics-lab-mcp)) a local model measured a physics result correctly and then explained it wrongly, twice. Chess is a sharper test of the same problem, because most claims about a position can be checked by a program.

## Tools

| Tool | What it returns |
|---|---|
| `recent_games` | Latest games from Lichess or Chess.com (public APIs, no token) |
| `review_game` | Per-side average centipawn loss; inaccuracies, mistakes and blunders graded by Lichess's winning-chances method; key moments with move played, best move, best line and the facts of the position |
| `analyse_position` | Top engine lines and rule-computed facts for a FEN: hanging pieces, pieces attacked by a cheaper piece, pins, checks, mate in one, material |
| `check_claims` | Verdicts on a commentator's claims (hanging, attacked by a cheaper piece, pinned, mate in one, best move, advantage, material, check) and the share that held |

The server's instructions tell the model to say only what the tools report and to verify anything else with `check_claims`.

## Measured

- Review of a 39-ply blitz game: 6.5 s with Stockfish 19 at 0.15 s per move, on an AMD Ryzen AI Max+ 392 laptop.
- 9 tests on positions with unambiguous answers (hanging piece, defended piece attacked by a pawn, a defended piece attacked only by a king, pin, back-rank mate, Scholar's mate blunder, claim scoring), plus 5 tests for the faithfulness eval's reply parser.
- Faithfulness, first run ([report](evals/faithfulness-report.md)): Qwen3.6-35B-A3B commenting on 22 key moments from 5 of my Lichess games. Given the review, 52 of its 67 checkable claims were true (0.776); given only the position, 27 of 41 (0.659). Without the best-move claims, which mostly repeat the move the prompt gave it: 32 of 45 (0.711) against 8 of 21 (0.381). 204 other statements wait for my hand labels.

## Design

[docs/DECISIONS.md](docs/DECISIONS.md) explains each design decision (engine and rules as the only source of facts, the three-valued claim checker, Lichess's winning-chances grading, the engine lifecycle), with trade-offs, known limits and how to check each claim.

## Run

```
python -m venv .venv
.venv\Scripts\pip install -e .
set STOCKFISH_PATH=C:\path\to\stockfish.exe
.venv\Scripts\python -m pytest
jarvis-chess                 # stdio MCP server
jarvis-chess --http          # Streamable HTTP on 127.0.0.1:8772
```

`CHESS_USERNAME` sets the default player for `recent_games`.

## Next

- Faithfulness eval, next steps: label the free-text statements by hand, audit the model's own claim extraction, and run the same frozen set on other models.
- Maia-2 for "what would a human at this rating play" next to Stockfish's best move.
- An interactive board on my site replaying a reviewed game with each AI claim marked true or false.

Built with AI assistance (Claude Code), directed and reviewed by Sergio Adan Bermudez.

## Master games and strategic facts

`scripts/master_games.py` builds the "learn from the masters" games on the portfolio chess page: twelve classic games, from Morphy's Opera Game (1858) to Kasparov against Topalov (1999), each chosen for one idea.

- Moves come from the [PGN Mentor](https://www.pgnmentor.com/files.html) player collections and are checked by python-chess. Every move a lesson names must be in the game at that point, or the build fails. The exact games used are in `data/master-games.pgn`.
- Stockfish evaluates every position, with two lines each. The key moments are found, not chosen: a sacrifice that still leaves the mover down material after its next move while the evaluation holds; an only move, where the next best gives away a large share of the winning chances; and the losing side's turning point.
- `src/jarvis_chess/strategy.py` computes the positional facts a coach talks about, from the board alone: open and half-open files with rooks on them, passed, isolated and doubled pawns, outposts, pieces deep in enemy territory that no pawn can attack, the bishop pair, development and king cover. `ideas(board, move)` names what a move changed, for example "Nd3 gives Black a knight deep in the enemy camp on d3, where no enemy pawn can ever attack it". As everywhere here, the language model never decides a fact.
