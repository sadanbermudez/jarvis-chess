"""Strategic facts: the positional ideas a coach talks about, computed from the board by the rules alone.

Same rule as analysis.facts(): nothing here is a judgement by a language model. Each item is a property of the
position that python-chess can check, for example "a rook stands on an open file", "a knight sits on an outpost" or
"a passed pawn". ideas(before, move) compares the position before and after a move and names what the move changed,
which is how the master-games pages explain a quiet move.

Definitions (standard ones):
  open file       no pawns of either colour on it; half-open: none of one side's own pawns
  passed pawn     no enemy pawn ahead of it on its own or an adjacent file
  isolated pawn   no friendly pawn on an adjacent file; doubled: two or more of one side's pawns on one file
  outpost         a square in the enemy half, defended by an own pawn, that no enemy pawn can ever attack
  development     knights and bishops moved off their starting squares
  king cover      own pawns on the three squares in front of a castled king
"""
from __future__ import annotations

import chess

NAMES = {chess.PAWN: "pawn", chess.KNIGHT: "knight", chess.BISHOP: "bishop", chess.ROOK: "rook", chess.QUEEN: "queen", chess.KING: "king"}
SIDE = {chess.WHITE: "White", chess.BLACK: "Black"}
FILES = "abcdefgh"


def _pawns(board: chess.Board, color: bool) -> list[int]:
    return list(board.pieces(chess.PAWN, color))


def file_state(board: chess.Board, f: int) -> str:
    w = any(chess.square_file(s) == f for s in _pawns(board, chess.WHITE))
    b = any(chess.square_file(s) == f for s in _pawns(board, chess.BLACK))
    return "open" if not w and not b else "half-open for White" if not w else "half-open for Black" if not b else "closed"


def passed(board: chess.Board, sq: int, color: bool) -> bool:
    f, r = chess.square_file(sq), chess.square_rank(sq)
    for e in _pawns(board, not color):
        ef, er = chess.square_file(e), chess.square_rank(e)
        if abs(ef - f) <= 1 and ((er > r) if color == chess.WHITE else (er < r)):
            return False
    return True


def isolated(board: chess.Board, sq: int, color: bool) -> bool:
    f = chess.square_file(sq)
    return not any(abs(chess.square_file(s) - f) == 1 for s in _pawns(board, color))


def safe_from_pawns(board: chess.Board, sq: int, color: bool) -> bool:
    """No enemy pawn on an adjacent file can ever advance to attack this square."""
    f, r = chess.square_file(sq), chess.square_rank(sq)
    for e in _pawns(board, not color):
        ef, er = chess.square_file(e), chess.square_rank(e)
        if abs(ef - f) == 1 and ((er > r) if color == chess.WHITE else (er < r)):
            return False
    return True


def in_enemy_half(sq: int, color: bool) -> bool:
    r = chess.square_rank(sq)
    return r >= 4 if color == chess.WHITE else r <= 3


def outpost(board: chess.Board, sq: int, color: bool) -> bool:
    """In the enemy half, defended by an own pawn, and no enemy pawn can ever attack it."""
    if not in_enemy_half(sq, color) or not safe_from_pawns(board, sq, color):
        return False
    return any(board.piece_at(a) and board.piece_at(a).piece_type == chess.PAWN for a in board.attackers(color, sq))


def deep_piece(board: chess.Board, sq: int, color: bool) -> bool:
    """Defended, at least on the 6th rank from its own side, and no enemy pawn can ever attack it (Kasparov's knight on d3)."""
    r = chess.square_rank(sq)
    deep = r >= 5 if color == chess.WHITE else r <= 2
    return deep and safe_from_pawns(board, sq, color) and bool(board.attackers(color, sq)) and not outpost(board, sq, color)


def king_cover(board: chess.Board, color: bool) -> int | None:
    """Own pawns on the three squares in front of the king, if it has castled to a wing (file a-c or f-h)."""
    k = board.king(color)
    if k is None or chess.square_file(k) in (3, 4):
        return None
    step = 1 if color == chess.WHITE else -1
    r = chess.square_rank(k) + step
    if not 0 <= r <= 7:
        return None
    n = 0
    for df in (-1, 0, 1):
        f = chess.square_file(k) + df
        if 0 <= f <= 7:
            p = board.piece_at(chess.square(f, r))
            n += bool(p and p.piece_type == chess.PAWN and p.color == color)
    return n


def developed(board: chess.Board, color: bool) -> int:
    home = [chess.B1, chess.G1, chess.C1, chess.F1] if color == chess.WHITE else [chess.B8, chess.G8, chess.C8, chess.F8]
    kinds = [chess.KNIGHT, chess.KNIGHT, chess.BISHOP, chess.BISHOP]
    return sum(1 for sq, k in zip(home, kinds) if not (board.piece_at(sq) and board.piece_at(sq).piece_type == k and board.piece_at(sq).color == color))


def strategy(board: chess.Board) -> dict:
    """The strategic picture: lists of short, checkable statements per side."""
    out = {}
    for color in (chess.WHITE, chess.BLACK):
        side, items = SIDE[color], []
        for sq in board.pieces(chess.ROOK, color):
            st = file_state(board, chess.square_file(sq))
            if st == "open" or st == f"half-open for {side}":
                items.append(f"rook on the {st.split(' for')[0]} {FILES[chess.square_file(sq)]}-file")
        for sq in _pawns(board, color):
            if passed(board, sq, color):
                items.append(f"passed pawn on {chess.square_name(sq)}")
        iso = sorted(chess.square_name(s) for s in _pawns(board, color) if isolated(board, s, color))
        if iso:
            items.append("isolated pawn" + ("s" if len(iso) > 1 else "") + " on " + ", ".join(iso))
        for f in range(8):
            n = sum(1 for s in _pawns(board, color) if chess.square_file(s) == f)
            if n >= 2:
                items.append(f"doubled pawns on the {FILES[f]}-file")
        for kind in (chess.KNIGHT, chess.BISHOP):
            for sq in board.pieces(kind, color):
                if outpost(board, sq, color):
                    items.append(f"{NAMES[kind]} on an outpost on {chess.square_name(sq)}")
                elif deep_piece(board, sq, color):
                    items.append(f"{NAMES[kind]} deep in the enemy camp on {chess.square_name(sq)}, where no enemy pawn can ever attack it")
        if len(board.pieces(chess.BISHOP, color)) >= 2:
            items.append("the bishop pair")
        cover = king_cover(board, color)
        if cover is not None and cover <= 1:
            items.append(f"king on {chess.square_name(board.king(color))} with {'no' if cover == 0 else 'one'} pawn in front")
        k = board.king(color)
        if k is not None and chess.square_file(k) in (3, 4) and board.fullmove_number >= 12 and board.queens:
            items.append(f"king still in the centre on {chess.square_name(k)}")
        out[side] = items
    out["development"] = {SIDE[c]: developed(board, c) for c in (chess.WHITE, chess.BLACK)}
    return out


def ideas(before: chess.Board, move: chess.Move) -> list[str]:
    """What a move changes in the strategic picture, in short sentences about the side that moved."""
    mover = SIDE[before.turn]
    other = SIDE[not before.turn]
    after = before.copy(stack=False)
    piece = before.piece_at(move.from_square)
    san = before.san(move)
    after.push(move)
    a, b = strategy(before), strategy(after)
    new_mine = [s for s in b[mover] if s not in a[mover]]
    gone_theirs = [s for s in a[other] if s not in b[other]]
    new_theirs = [s for s in b[other] if s not in a[other]]
    out = []
    for s in new_mine:
        if s.startswith("king ") and "pawn in front" in s:
            out.append(f"{mover}'s own king cover is thinner now: {s}.")
        elif s.startswith("king still"):
            continue
        else:
            out.append(f"{san} gives {mover} {('a ' if not s.startswith(('the ', 'doubled', 'isolated')) else '')}{s}.")
    for s in new_theirs:
        if s.startswith(("isolated", "doubled")) or ("pawn in front" in s):
            out.append(f"{other} is left with {s}.")
    for s in gone_theirs:
        if s.startswith(("passed pawn", "rook on", "the bishop pair")) or "outpost" in s or "enemy camp" in s:
            out.append(f"{other} no longer has {s}.")
    if piece and piece.piece_type in (chess.KNIGHT, chess.BISHOP) and b["development"][mover] > a["development"][mover]:
        out.append(f"{mover} develops: {b['development'][mover]} of 4 minor pieces out, against {b['development'][other]} for {other}.")
    if before.has_castling_rights(before.turn) and piece and piece.piece_type == chess.KING and before.is_castling(move):
        out.append(f"{mover} castles, tucking the king away and bringing a rook towards the centre.")
    return out
