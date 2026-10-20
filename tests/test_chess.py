"""Facts, grading and claim checks on positions with an unambiguous answer."""
import json

import chess
import pytest

from jarvis_chess import analysis, claims, server, sources
from jarvis_chess.analysis import Analyst, facts, grade, win_chances

HANGING = "4k3/8/8/4n3/8/8/4Q3/4K3 w - - 0 1"        # Qe2 attacks an undefended Ne5
CHEAPER = "4k3/8/3p4/4n3/3P4/8/8/4K3 w - - 0 1"      # Ne5 defended by d6, attacked by pawn d4
PIN = "4k3/4n3/8/8/8/8/8/4R1K1 w - - 0 1"            # Ne7 pinned to Ke8 by Re1
BACK_RANK = "6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1"      # Ra8#
KING_ONLY = "8/8/8/8/8/3qk3/3r4/3K4 w - - 0 1"      # Rd2 defended by Qd3, attacked only by Kd1
SCHOLAR = """[Event "test"]
[White "A"]
[Black "B"]
[Result "1-0"]

1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0
"""

@pytest.fixture(autouse=True, scope="module")
def _stop_server_engine():
    yield
    server.shutdown()


def _have_engine():
    try:
        analysis.engine_path()
        return True
    except FileNotFoundError:
        return False


engine_missing = pytest.mark.skipif(not _have_engine(), reason="Stockfish not installed")


def test_hanging_piece():
    f = facts(chess.Board(HANGING))
    assert f["hanging_pieces"] == ["Black knight on e5"]
    assert f["attacked_by_a_cheaper_piece"] == []


def test_defended_piece_attacked_by_cheaper_is_not_hanging():
    f = facts(chess.Board(CHEAPER))
    assert f["hanging_pieces"] == []
    assert f["attacked_by_a_cheaper_piece"] == ["Black knight on e5"]


def test_king_is_not_a_cheaper_attacker():
    # A king cannot capture a defended piece, so it must not count as "attacked by a cheaper piece".
    f = facts(chess.Board(KING_ONLY))
    assert f["attacked_by_a_cheaper_piece"] == []
    assert f["hanging_pieces"] == []


def test_pin_and_mate_in_one():
    assert "knight e7" in facts(chess.Board(PIN))["pinned_pieces"]
    assert facts(chess.Board(BACK_RANK))["mate_in_one_for_side_to_move"] == ["Ra8#"]


def test_grading_follows_lichess_thresholds():
    assert win_chances(0) == 0
    assert grade(0.05) is None and grade(0.1) == "inaccuracy" and grade(0.2) == "mistake" and grade(0.35) == "blunder"


def test_claims_without_engine():
    r = claims.check(chess.Board(HANGING), [
        {"type": "hanging", "square": "e5"},
        {"type": "hanging", "square": "e2"},
        {"type": "material", "side": "white"},
        {"type": "in_check"},
        {"type": "best_move", "move": "Qxe5"},
        {"type": "teleport"},
    ])
    assert [x["verdict"] for x in r] == [True, False, True, False, None, None]
    assert claims.score(r) == {"checkable": 4, "true": 2, "false": 2, "faithfulness": 0.5}


def test_pgn_summary():
    s = sources.summarize(SCHOLAR, "test")
    assert (s["white"], s["black"], s["result"], s["plies"]) == ("A", "B", "1-0", 7)


@engine_missing
def test_engine_review_finds_the_blunder():
    a = Analyst(threads=2, hash_mb=32)
    try:
        r = a.review(SCHOLAR, seconds_per_move=0.1)
        nf6 = [m for m in r["moves"] if m["played"] == "Nf6"][0]
        assert nf6["grade"] == "blunder" and nf6["best"] in ("g6", "Qe7", "Qf6")
        assert r["summary"]["Black"]["blunders"] >= 1
        assert r["moves"][-1]["eval_after"] == "checkmate"
        best = claims.check(chess.Board(BACK_RANK), [{"type": "best_move", "move": "Ra8#"}, {"type": "advantage", "side": "black"}], a.engine)
        assert [x["verdict"] for x in best] == [True, False]
    finally:
        a.close()


@engine_missing
def test_server_tools_with_pgn():
    out = json.loads(server.review_game(SCHOLAR, seconds_per_move=0.05, key_moments=3))
    assert out["result"] == "1-0" and out["key_moments"]
    assert "facts_before" in out["key_moments"][0]
    pos = json.loads(server.analyse_position(BACK_RANK, seconds=0.2, lines=2))
    assert pos["top_lines"][0]["line"] == "1. Ra8#"
