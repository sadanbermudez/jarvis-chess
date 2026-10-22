"""Parsing of the model's reply in evals/faithfulness.py: commentary, claims block, positions."""
import importlib.util
from pathlib import Path

import chess

_spec = importlib.util.spec_from_file_location(
    "faithfulness", Path(__file__).resolve().parent.parent / "evals" / "faithfulness.py")
fe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fe)


def test_fenced_block_splits_commentary_and_claims():
    reply = ('Nf6 drops f7: Qxf7 is mate.\n\n```json\n{"claims": [{"type": "mate_in_one", "move": "Qxf7#", '
             '"position": "after"}, {"type": "best_move", "move": "g6"}], "other_claims": ["g6 holds"]}\n```')
    p = fe.parse_reply(reply)
    assert p["error"] is None
    assert p["commentary"] == "Nf6 drops f7: Qxf7 is mate."
    assert [c["position"] for c in p["claims"]] == ["after", "before"]
    assert p["claims"][1]["position_defaulted"] is True
    assert p["other_claims"] == ["g6 holds"]


def test_unfenced_json_and_last_block_wins():
    reply = 'Text with {braces} first. {"claims": [{"type": "in_check", "position": "AFTER"}, "junk"]}'
    p = fe.parse_reply(reply)
    assert p["commentary"] == "Text with {braces} first."
    assert p["claims"] == [{"type": "in_check", "position": "after"}]
    assert "dropped" in p["error"]


def test_no_json_is_an_error_not_a_crash():
    p = fe.parse_reply("Just prose, no claims.")
    assert p["error"] == "no JSON block" and p["claims"] == []


def test_claims_are_checked_on_the_right_board():
    # Scholar's mate: after 3...Nf6 White has Qxf7#, before it Black is to move and has no mate.
    moment = {"fen_before": "r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3", "played": "Nf6"}
    parsed = {"claims": [{"type": "mate_in_one", "move": "Qxf7#", "position": "after"},
                         {"type": "mate_in_one", "move": "Qxf7#", "position": "before"}]}
    r = fe.check_moment(moment, parsed, engine=None)
    by_pos = {x["claim"]["position"]: x["verdict"] for x in r}
    assert by_pos == {"after": True, "before": False}
    assert chess.Board(r[0]["fen"]).is_valid()


def test_wilson_interval():
    assert fe.wilson(0, 0) is None
    assert fe.wilson(8, 10) == [0.49, 0.943]
