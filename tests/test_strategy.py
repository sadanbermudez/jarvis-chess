"""Strategic facts on positions where the answer is known by construction."""
import chess

from jarvis_chess.strategy import ideas, outpost, passed, strategy


def test_open_file_rook_and_passed_pawn():
    b = chess.Board("4k3/8/8/3P4/8/8/8/3RK3 w - - 0 1")          # no pawns on the d-file but White's d5... so not open
    s = strategy(b)["White"]
    assert "passed pawn on d5" in s and not any("rook on the open" in x for x in s)
    b = chess.Board("4k3/p7/8/8/8/8/P7/3RK3 w - - 0 1")
    assert "rook on the open d-file" in strategy(b)["White"]


def test_outpost_needs_pawn_support_and_no_enemy_pawn_able_to_attack():
    b = chess.Board("4k3/p7/8/3N4/4P3/8/8/4K3 w - - 0 1")          # Nd5 defended by e4, no black c/e pawns behind it
    assert outpost(b, chess.D5, chess.WHITE)
    b = chess.Board("4k3/p1p5/8/3N4/4P3/8/8/4K3 w - - 0 1")        # c7 pawn can play c6 and attack d5
    assert not outpost(b, chess.D5, chess.WHITE)


def test_passed_pawn_is_blocked_by_adjacent_enemy_pawn_ahead():
    b = chess.Board("4k3/4p3/8/3P4/8/8/8/4K3 w - - 0 1")
    assert not passed(b, chess.D5, chess.WHITE)


def test_isolated_and_doubled():
    s = strategy(chess.Board("4k3/8/8/8/8/2P5/2P1P3/4K3 w - - 0 1"))["White"]
    assert "doubled pawns on the c-file" in s and any(x.startswith("isolated pawns on") for x in s)


def test_ideas_name_what_a_move_changes():
    b = chess.Board("4k3/p7/8/8/8/8/P7/R3K3 w - - 0 1")
    out = ideas(b, chess.Move.from_uci("a1d1"))
    assert any("rook on the open d-file" in x for x in out), out
    b = chess.Board()
    assert any("develops" in x for x in ideas(b, chess.Move.from_uci("g1f3")))


def test_deep_piece_without_pawn_support_is_named():
    # Karpov-Kasparov 1985, game 16, after 16...Nd3: defended by the bishop on f5, no white c- or e-pawn left
    b = chess.Board("r2qr1k1/5ppp/p4n2/1pbP1bB1/8/N1Nn1B2/PP1Q1PPP/3R1RK1 w - - 2 17")
    assert any(x.startswith("knight deep in the enemy camp on d3") for x in strategy(b)["Black"])
