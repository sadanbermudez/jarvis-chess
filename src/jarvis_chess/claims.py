"""Check a commentator's claims about a position against the rules and the engine.

Each claim is a small dict; the checker returns verified true, false, or unverifiable. This is
what turns "the AI explained the game" into a number: the share of its checkable claims that
hold. Claim types:
  {"type": "hanging", "square": "e5"}            a piece there is attacked and undefended
  {"type": "attacked_by_cheaper", "square": "d4"}
  {"type": "pinned", "square": "c6"}             pinned to its own king
  {"type": "in_check"}
  {"type": "mate_in_one", "move": "Qh7#"}        optional move; without it, any mate in one
  {"type": "best_move", "move": "Nf3"}           among the engine's top `tolerance` lines
  {"type": "advantage", "side": "white"}         engine eval favours that side by >= 0.5
  {"type": "material", "side": "white"}          that side is ahead on material
"""
from __future__ import annotations

import chess
import chess.engine

from .analysis import cp_white, facts


def _square(claim: dict) -> int:
    return chess.parse_square(claim["square"].strip().lower())


def check(board: chess.Board, claims: list[dict], engine: chess.engine.SimpleEngine | None = None,
          seconds: float = 0.5, tolerance: int = 2) -> list[dict]:
    f = facts(board)
    lines = None
    out = []
    for c in claims:
        t = c.get("type", "")
        verdict, why = None, ""
        try:
            if t in ("hanging", "attacked_by_cheaper"):
                sq = _square(c)
                piece = board.piece_at(sq)
                if piece is None:
                    verdict, why = False, f"no piece on {chess.square_name(sq)}"
                else:
                    pool = f["hanging_pieces"] if t == "hanging" else f["attacked_by_a_cheaper_piece"]
                    verdict = any(s.endswith(f"on {chess.square_name(sq)}") for s in pool)
                    why = "computed from attackers and defenders"
            elif t == "pinned":
                sq = _square(c)
                piece = board.piece_at(sq)
                verdict = bool(piece) and board.is_pinned(piece.color, sq)
                why = "pinned to its own king" if verdict else "not pinned to its king"
            elif t == "in_check":
                verdict, why = board.is_check(), "rules"
            elif t == "mate_in_one":
                mates = f["mate_in_one_for_side_to_move"]
                verdict = (c["move"].rstrip("#+") in [m.rstrip("#+") for m in mates]) if c.get("move") else bool(mates)
                why = f"mates available: {mates or 'none'}"
            elif t == "material":
                m = f["material_white_minus_black"]
                verdict = m > 0 if c["side"].lower() == "white" else m < 0
                why = f"material balance {m:+d} for White"
            elif t in ("best_move", "advantage"):
                if engine is None:
                    verdict, why = None, "needs the engine"
                else:
                    if lines is None:
                        lines = engine.analyse(board, chess.engine.Limit(time=seconds), multipv=max(tolerance, 1))
                    if t == "best_move":
                        top = [board.san(i["pv"][0]) for i in lines if i.get("pv")]
                        verdict = c["move"].rstrip("#+!?") in [m.rstrip("#+") for m in top]
                        why = f"engine top {len(top)}: {top}"
                    else:
                        cp = cp_white(lines[0]["score"])
                        verdict = cp >= 50 if c["side"].lower() == "white" else cp <= -50
                        why = f"engine {cp / 100:+.2f} for White"
            else:
                why = f"unknown claim type '{t}'"
        except (KeyError, ValueError) as e:
            why = f"malformed claim: {e}"
        out.append({"claim": c, "verdict": verdict, "why": why})
    return out


def score(results: list[dict]) -> dict:
    checked = [r for r in results if r["verdict"] is not None]
    true = sum(1 for r in checked if r["verdict"])
    return {"checkable": len(checked), "true": true, "false": len(checked) - true,
            "faithfulness": round(true / len(checked), 3) if checked else None}
