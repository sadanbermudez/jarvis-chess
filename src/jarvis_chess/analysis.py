"""Engine review and machine-checked position facts.

The rule for anything Jarvis says about a position: it comes from here, computed by the rules
(python-chess) or the engine (Stockfish), never from the language model's own reading of the
board. Move quality uses Lichess's published method: convert centipawns to winning chances and
grade the drop in the mover's chances (0.1 inaccuracy, 0.2 mistake, 0.3 blunder).
"""
from __future__ import annotations

import io
import math
import os
import shutil
from pathlib import Path

import chess
import chess.engine
import chess.pgn

VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
NAMES = {chess.PAWN: "pawn", chess.KNIGHT: "knight", chess.BISHOP: "bishop", chess.ROOK: "rook", chess.QUEEN: "queen", chess.KING: "king"}
DEFAULT_ENGINE = r"C:\Users\sadan\tools\stockfish-19\stockfish\stockfish-windows-x86-64-universal.exe"
MATE_CP = 10000


def engine_path() -> str:
    p = os.environ.get("STOCKFISH_PATH") or (DEFAULT_ENGINE if Path(DEFAULT_ENGINE).exists() else shutil.which("stockfish"))
    if not p:
        raise FileNotFoundError("Stockfish not found: set STOCKFISH_PATH")
    return p


def win_chances(cp: int) -> float:
    """Lichess's centipawn to winning-chances curve, in [-1, 1] for the side the score is for."""
    return 2 / (1 + math.exp(-0.00368208 * cp)) - 1


def grade(drop: float) -> str | None:
    if drop >= 0.3:
        return "blunder"
    if drop >= 0.2:
        return "mistake"
    if drop >= 0.1:
        return "inaccuracy"
    return None


def cp_white(score: chess.engine.PovScore) -> int:
    return score.white().score(mate_score=MATE_CP)


def describe_score(score: chess.engine.PovScore) -> str:
    w = score.white()
    if w.is_mate():
        m = w.mate()
        return f"White mates in {m}" if m > 0 else f"Black mates in {-m}"
    return f"{w.score() / 100:+.2f}"


def facts(board: chess.Board) -> dict:
    """What is true on the board right now, computed by the rules alone."""
    side = board.turn
    hanging, attacked_by_lower, pinned = [], [], []
    for sq, piece in board.piece_map().items():
        if piece.piece_type == chess.KING:
            continue
        attackers = board.attackers(not piece.color, sq)
        if not attackers:
            if board.is_pinned(piece.color, sq):
                pinned.append(f"{NAMES[piece.piece_type]} {chess.square_name(sq)}")
            continue
        who = "White" if piece.color else "Black"
        label = f"{who} {NAMES[piece.piece_type]} on {chess.square_name(sq)}"
        if not board.attackers(piece.color, sq):
            hanging.append(label)
        elif min(VALUES[board.piece_at(a).piece_type] for a in attackers) < VALUES[piece.piece_type]:
            attacked_by_lower.append(label)
        if board.is_pinned(piece.color, sq):
            pinned.append(f"{NAMES[piece.piece_type]} {chess.square_name(sq)}")
    material = sum(VALUES[p.piece_type] * (1 if p.color else -1) for p in board.piece_map().values())
    mate_in_one = []
    for mv in board.legal_moves:
        board.push(mv)
        if board.is_checkmate():
            board.pop(); mate_in_one.append(board.san(mv)); continue
        board.pop()
    return {
        "side_to_move": "White" if side else "Black",
        "in_check": board.is_check(),
        "material_white_minus_black": material,
        "hanging_pieces": hanging,
        "attacked_by_a_cheaper_piece": attacked_by_lower,
        "pinned_pieces": pinned,
        "mate_in_one_for_side_to_move": mate_in_one,
        "checks_available": [board.san(m) for m in board.legal_moves if board.gives_check(m)][:8],
        "legal_moves": board.legal_moves.count(),
    }


class Analyst:
    def __init__(self, path: str | None = None, threads: int = 8, hash_mb: int = 256):
        self.engine = chess.engine.SimpleEngine.popen_uci(path or engine_path())
        self.engine.configure({"Threads": threads, "Hash": hash_mb})
        self.name = self.engine.id.get("name", "engine")

    def close(self) -> None:
        # at interpreter exit the engine's event loop may already be gone: quit politely if we
        # can, otherwise kill the process, and never raise or block shutdown
        try:
            self.engine.quit()
        except Exception:
            try:
                self.engine.close()
            except Exception:
                pass

    def position(self, fen: str, seconds: float = 1.0, lines: int = 3) -> dict:
        board = chess.Board(fen)
        infos = self.engine.analyse(board, chess.engine.Limit(time=seconds), multipv=lines)
        out = []
        for info in infos:
            pv = info.get("pv", [])[:8]
            out.append({"eval": describe_score(info["score"]), "line": board.variation_san(pv) if pv else ""})
        return {"fen": fen, "engine": self.name, "top_lines": out, "facts": facts(board)}

    def review(self, pgn: str, seconds_per_move: float = 0.15, key_moments: int = 5) -> dict:
        game = chess.pgn.read_game(io.StringIO(pgn))
        if game is None:
            raise ValueError("not a PGN game")
        board = game.board()
        limit = chess.engine.Limit(time=seconds_per_move)
        info = self.engine.analyse(board, limit)
        moves, loss = [], {chess.WHITE: [], chess.BLACK: []}
        for node in game.mainline():
            mv, mover = node.move, board.turn
            before = info
            best = before.get("pv", [None])[0]
            fen_before, san = board.fen(), board.san(mv)
            best_san = board.san(best) if best else None
            best_line = board.variation_san(before["pv"][:6]) if before.get("pv") else ""
            board.push(mv)
            info = self.engine.analyse(board, limit) if not board.is_game_over() else None
            cp_before = cp_white(before["score"])
            if info is not None:
                cp_after = cp_white(info["score"])
            else:
                cp_after = MATE_CP if board.is_checkmate() and not board.turn else (-MATE_CP if board.is_checkmate() else 0)
            sign = 1 if mover == chess.WHITE else -1
            drop = max(0.0, win_chances(sign * cp_before) - win_chances(sign * cp_after))
            loss[mover].append(max(0, sign * (cp_before - cp_after)) if abs(cp_before) < MATE_CP and abs(cp_after) < MATE_CP else 0)
            moves.append({
                "ply": len(moves) + 1, "move_number": (len(moves) // 2) + 1, "side": "White" if mover else "Black",
                "played": san, "best": best_san, "best_line": best_line,
                "eval_before": describe_score(before["score"]),
                "eval_after": describe_score(info["score"]) if info else ("checkmate" if board.is_checkmate() else "game over"),
                "win_chance_drop": round(drop, 3), "grade": grade(drop) if san != best_san else None,
                "fen_before": fen_before,
            })
        h = game.headers
        worst = sorted((m for m in moves if m["grade"]), key=lambda m: -m["win_chance_drop"])[:key_moments]
        for m in worst:
            m["facts_before"] = facts(chess.Board(m["fen_before"]))
        count = lambda side, g: sum(1 for m in moves if m["side"] == side and m["grade"] == g)
        summary = {}
        for side, col in (("White", chess.WHITE), ("Black", chess.BLACK)):
            summary[side] = {"player": h.get(side, "?"), "elo": h.get(f"{side}Elo", ""),
                             "average_centipawn_loss": round(sum(loss[col]) / max(1, len(loss[col]))),
                             "inaccuracies": count(side, "inaccuracy"), "mistakes": count(side, "mistake"), "blunders": count(side, "blunder")}
        return {"engine": self.name, "seconds_per_move": seconds_per_move, "result": h.get("Result", "*"),
                "opening": h.get("Opening", ""), "summary": summary,
                "key_moments": sorted(worst, key=lambda m: m["ply"]), "moves": moves}
