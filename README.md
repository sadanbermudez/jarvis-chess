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
| `check_claims` | Verdicts on a commentator's claims (hanging, pinned, mate in one, best move, advantage, material, check) and the share that held |

The server's instructions tell the model to say only what the tools report and to verify anything else with `check_claims`.

## Measured

- Review of a 39-ply blitz game: 6.5 s with Stockfish 19 at 0.15 s per move, on an AMD Ryzen AI Max+ 392 laptop.
- 8 tests on positions with unambiguous answers (hanging piece, defended piece attacked by a pawn, pin, back-rank mate, Scholar's mate blunder, claim scoring).

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

- A faithfulness eval: the local model comments on key moments, every checkable claim goes through `check_claims`, and I label the rest. The output is one number per model: the share of its chess statements that are true.
- Maia-2 for "what would a human at this rating play" next to Stockfish's best move.
- An interactive board on my site replaying a reviewed game with each AI claim marked true or false.

Built with AI assistance (Claude Code), directed and reviewed by Sergio Adan Bermudez.
