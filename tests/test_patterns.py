"""Patterns across games: grading and tags on games with obvious errors, and the summary arithmetic."""
import chess
import pytest

from jarvis_chess import analysis
from jarvis_chess.analysis import Analyst
from jarvis_chess.patterns import analyse_game, drills, phase, summarise


def _have_engine():
    try:
        analysis.engine_path()
        return True
    except FileNotFoundError:
        return False


engine_missing = pytest.mark.skipif(not _have_engine(), reason="Stockfish not installed")


def lichess_game(moves, me="black", winner="white", clocks=None, initial=180, created=0, gid="g1", opening="Test"):
    players = {"white": {"user": {"id": "me" if me == "white" else "them"}, "rating": 2500},
               "black": {"user": {"id": "me" if me == "black" else "them"}, "rating": 2500}}
    g = {"id": gid, "players": players, "moves": moves, "speed": "blitz", "createdAt": created,
         "clock": {"initial": initial}, "clocks": clocks or [], "opening": {"name": opening}}
    if winner:
        g["winner"] = winner
    return g


@pytest.fixture(scope="module")
def engine():
    if not _have_engine():
        pytest.skip("Stockfish not installed")
    a = Analyst(threads=2)
    yield a.engine
    a.close()


@engine_missing
def test_allowed_mate_is_tagged(engine):
    # Scholar's mate: Black's 3...Nf6 allows Qxf7#
    g = analyse_game(engine, lichess_game("e4 e5 Bc4 Nc6 Qh5 Nf6 Qxf7#"), "me", nodes=50_000)
    nf6 = next(m for m in g["moves"] if m["played"] == "Nf6")
    assert nf6["grade"] == "blunder"
    assert "allowed_mate" in nf6["tags"]
    assert g["result"] == 0.0 and g["color"] == "black"


@engine_missing
def test_hung_piece_and_time_trouble(engine):
    # 1.e4 e5 2.Nf3 Qh4?? (the queen can be taken by the knight) 3.Nxh4; clocks say 10 s were left at Black's move
    g = analyse_game(engine, lichess_game("e4 e5 Nf3 Qh4 Nxh4", clocks=[18000, 18000, 17900, 1000, 17800]),
                     "me", nodes=50_000)
    qh4 = next(m for m in g["moves"] if m["played"] == "Qh4")
    assert qh4["grade"] == "blunder"
    assert "hung_piece" in qh4["tags"] and "time_trouble" in qh4["tags"]
    assert drills([g]) == []                                  # time-trouble errors are not drills


def test_phase():
    assert phase(chess.Board(), 1) == "opening"
    assert phase(chess.Board(), 30) == "middlegame"
    assert phase(chess.Board("4k3/8/8/8/8/8/8/R3K3 w - - 0 1"), 5) == "endgame"


def _g(gid, created, result, errors=0, moves=20, phase_="middlegame", left=100.0):
    ms = [{"grade": "mistake" if i < errors else None, "phase": phase_, "clock_left": left, "tags": [],
           "chances_before": 0.0, "drop": 0.25, "fen": chess.STARTING_FEN, "best": "e4", "best_line": "", "played": "a3",
           "ply": i + 1} for i in range(moves)]
    return {"id": gid, "url": f"https://lichess.org/{gid}", "color": "white", "speed": "blitz", "created": created,
            "initial": 180, "opening": "Sicilian Defense: Najdorf", "result": result, "moves": ms}


def test_summary_counts_tilt_and_rates():
    m = 60 * 1000
    games = [_g("a", 0, 0.0, errors=2), _g("b", 10 * m, 1.0), _g("c", 100 * m, 0.0, errors=1), _g("d", 200 * m, 0.5)]
    s = summarise(games, min_games=2)
    assert s["games"] == 4 and s["errors"] == 3
    assert s["per_40_moves"] == 1.5                            # 3 errors in 80 moves
    assert s["after_a_loss"]["next_game_within_30_min"] == {"games": 1, "score": 100}   # only b follows a loss quickly
    assert s["openings"][0] == {"opening": "Sicilian Defense", "color": "white", "games": 4, "score": 38, "errors_per_game": 0.75}
    assert s["by_game_in_session"]["1-3"]["games"] == 4
    assert len(drills(games)) == 3
