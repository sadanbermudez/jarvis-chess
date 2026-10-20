"""jarvis-chess: an MCP server that lets Jarvis review chess games honestly.

The engine and the rules produce every fact; the language model only narrates them, and any
claim it makes can be checked with check_claims. Tools:
  recent_games      latest games from Lichess or Chess.com (public APIs)
  review_game       full engine review: per-side average centipawn loss, graded mistakes, key moments with facts
  analyse_position  top engine lines plus rule-computed facts for one position
  check_claims      verify a commentator's claims about a position
"""
from __future__ import annotations

import argparse
import json
import os
import threading

import chess
from mcp.server.fastmcp import FastMCP

from . import claims as claim_checker
from . import sources
from .analysis import Analyst

DEFAULT_USER = os.environ.get("CHESS_USERNAME", "dr_namer")
mcp = FastMCP("jarvis-chess", instructions=(
    "Chess review tools backed by Stockfish and the rules of chess. When you comment on a game, "
    "say only what these tools report: evaluations, best moves, graded mistakes and the listed "
    "facts. Never invent tactics, threats or evaluations. If you want to claim something the tools "
    "did not report, verify it first with check_claims. Speak to a strong player (FIDE Master): "
    "be concrete, name moves in SAN, skip beginner explanations."))
_lock = threading.Lock()
_analyst: Analyst | None = None
_last: list[dict] = []


def analyst() -> Analyst:
    global _analyst
    if _analyst is None:
        _analyst = Analyst()
    return _analyst


def shutdown() -> None:
    """Stop the engine. Must run before interpreter exit: python-chess keeps a non-daemon thread
    for the engine, so an atexit hook would never be reached and the process would hang."""
    global _analyst
    if _analyst is not None:
        _analyst.close()
        _analyst = None


@mcp.tool()
def recent_games(site: str = "lichess", username: str = DEFAULT_USER, count: int = 5) -> str:
    """List the player's most recent games. site: 'lichess' or 'chesscom'. Returns index, players,
    ratings, result, time control, opening and URL; pass the index (or URL or PGN) to review_game."""
    global _last
    games = sources.recent(site, username, max(1, min(count, 20)))
    _last = games
    return json.dumps([{k: v for k, v in g.items() if k != "pgn"} | {"index": i} for i, g in enumerate(games)], indent=1)


@mcp.tool()
def review_game(game: str = "0", seconds_per_move: float = 0.15, key_moments: int = 5) -> str:
    """Engine review of one game. game: an index from the last recent_games call, a game URL from
    it, or a full PGN. Returns per-side average centipawn loss, counts of inaccuracies, mistakes and
    blunders (Lichess winning-chance method), and the key moments with the move played, the
    engine's best move and line, and rule-computed facts about the position before the move."""
    pgn = game
    if game.strip().isdigit():
        if not _last:
            raise ValueError("call recent_games first, or pass a PGN")
        pgn = _last[int(game)]["pgn"]
    elif game.startswith("http"):
        hit = [g for g in _last if g["url"].rstrip("/") == game.rstrip("/")]
        if not hit:
            raise ValueError("URL not in the last recent_games list; call recent_games first")
        pgn = hit[0]["pgn"]
    with _lock:
        r = analyst().review(pgn, max(0.05, min(seconds_per_move, 2.0)), max(1, min(key_moments, 10)))
    r["moves"] = [{k: m[k] for k in ("ply", "side", "played", "best", "eval_after", "grade")} for m in r["moves"]]
    return json.dumps(r, indent=1)


@mcp.tool()
def analyse_position(fen: str, seconds: float = 1.0, lines: int = 3) -> str:
    """Engine top lines and rule-computed facts (hanging pieces, pins, checks, mate in one,
    material) for a FEN position."""
    with _lock:
        return json.dumps(analyst().position(fen, max(0.1, min(seconds, 10.0)), max(1, min(lines, 5))), indent=1)


@mcp.tool()
def check_claims(fen: str, claims: list[dict]) -> str:
    """Verify claims about a position before saying them. Each claim is a dict, for example
    {"type":"hanging","square":"e5"}, {"type":"pinned","square":"c6"}, {"type":"mate_in_one","move":"Qh7#"},
    {"type":"best_move","move":"Nf3"}, {"type":"advantage","side":"white"}, {"type":"material","side":"black"},
    {"type":"in_check"}, {"type":"attacked_by_cheaper","square":"d4"}. Returns a verdict per claim
    (true, false, or null when it cannot be checked) and the share that held."""
    board = chess.Board(fen)
    with _lock:
        results = claim_checker.check(board, claims, analyst().engine)
    return json.dumps({"results": results, "score": claim_checker.score(results)}, indent=1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--http", action="store_true", help="serve Streamable HTTP on 127.0.0.1 instead of stdio")
    ap.add_argument("--port", type=int, default=8772)
    a = ap.parse_args()
    try:
        if a.http:
            mcp.settings.host, mcp.settings.port = "127.0.0.1", a.port
            mcp.run("streamable-http")
        else:
            mcp.run()
    finally:
        shutdown()


if __name__ == "__main__":
    main()
