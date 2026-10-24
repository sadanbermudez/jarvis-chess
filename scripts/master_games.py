"""Build the "learn from the masters" games for the portfolio chess page.

  .venv\\Scripts\\python.exe scripts\\master_games.py --pgn-dir <folder with PGN Mentor player zips> --out <site>/data/master-games.js

For each classic game in GAMES: find it in the PGN Mentor collections (pgnmentor.com/players/<Name>.zip), check that
every move is legal and that each move the lesson names is really in the game at that point, then run Stockfish over
every position (two best lines) and write the viewer's format. Key moments are found by the engine and the rules,
not chosen by hand:
  sacrifice       the mover is down material two plies later, and the engine says the position did not get worse
  only move       the move played is the engine's best, and the next best move gives away a large share of the winning chances
  turning point   the losing side's biggest graded mistake
Every ply also carries ideas: what the move changed in the strategic picture (strategy.py). The lesson text is mine;
all moves are the games' own. Also writes data/master-games.pgn, the exact games used.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import sys
import zipfile
from pathlib import Path

import chess
import chess.engine
import chess.pgn

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from jarvis_chess.analysis import engine_path, facts, win_chances  # noqa: E402
from jarvis_chess.strategy import ideas, strategy  # noqa: E402

VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

# key, players and event as PGN Mentor writes them, the lesson, and the moves the lesson names: (move number, side, SAN)
GAMES = [
    dict(key="opera", zip="Morphy", white="Morphy", black="Duke Karl", year="1858", title="The Opera Game", theme="Development and open lines",
         lesson="Paris, 1858, played in a box at the opera. Morphy brings a new piece into play almost every move while his opponents move "
                "the same pieces twice and leave the rest at home. When the lines open, every white piece is active and Black's are not: "
                "the queen sacrifice 16.Qb8+ ends with mate by the last rook to arrive, 17.Rd8#.",
         expect=[(16, "w", "Qb8+"), (17, "w", "Rd8#")]),
    dict(key="immortal", zip="Anderssen", white="Anderssen", black="Kieseritzky", year="1851", event="Immortal", title="The Immortal Game",
         theme="Initiative over material",
         lesson="London, 1851, a casual game. Anderssen gives away a bishop, both rooks and finally his queen, because every sacrifice "
                "gains time to bring another piece towards Black's king. He mates with the three minor pieces he has left: 23.Be7#.",
         expect=[(23, "w", "Be7#")]),
    dict(key="evergreen", zip="Anderssen", white="Anderssen", black="Dufresne", year="1852", title="The Evergreen Game",
         theme="The king left in the centre",
         lesson="Berlin, 1852. Black wins time with threats on the other wing and never castles. Anderssen opens the centre, and the "
                "rook sacrifice 20.Rxe7+ and the queen sacrifice 21.Qxd7+ start a forced finish against the uncastled king, "
                "ending 24.Bxe7#.",
         expect=[(20, "w", "Rxe7+"), (21, "w", "Qxd7+"), (24, "w", "Bxe7#")]),
    dict(key="steinitz", zip="Steinitz", white="Steinitz", black="Bardeleben", year="1895", title="Steinitz's combination",
         theme="Forcing play against a stranded king",
         lesson="Hastings, 1895. Black's king cannot castle, and Steinitz keeps it there. 22.Rxe7+ begins a sequence of checks in which "
                "the rook cannot be taken without losing; Black left the hall instead of resigning.",
         expect=[(22, "w", "Rxe7+")]),
    dict(key="lasker-bauer", zip="Lasker", white="Lasker", black="Bauer, Johann", year="1889", title="The double bishop sacrifice",
         theme="Stripping the king's cover",
         lesson="Amsterdam, 1889. Lasker gives up both bishops, 15.Bxh7+ and 17.Bxg7, to remove the pawns in front of Black's king; "
                "the queen and rook then arrive before the defence can. The pattern is still called Lasker's combination.",
         expect=[(15, "w", "Bxh7+"), (17, "w", "Bxg7")]),
    dict(key="rotlewi", zip="Rubinstein", white="Rotlewi", black="Rubinstein", year="1907", event="Lodz", title="Rubinstein's immortal",
         theme="Bishops aimed at the king",
         lesson="Lodz, 1907. Rubinstein's bishops rake the long diagonals towards White's king. When the moment comes, he gives up "
                "pieces one after another, because each capture opens another line for them."),
    dict(key="zugzwang", zip="Nimzowitsch", white="Saemisch", black="Nimzowitsch", year="1923", event="Copenhagen", title="The Immortal Zugzwang",
         theme="Restriction and zugzwang",
         lesson="Copenhagen, 1923. Nimzowitsch does not attack the king directly. He takes away squares, piece by piece, until White "
                "has no move that does not lose something, and resigns with most of his pieces still on the board."),
    dict(key="capa-tarta", zip="Capablanca", white="Capablanca", black="Tartakower", year="1924", title="Capablanca's rook endgame",
         theme="The active king in the endgame",
         lesson="New York, 1924. In a rook endgame Capablanca lets pawns go so that his king and rook become active, and the active "
                "pieces then decide against Black's extra material. A model of how much an active king is worth once the queens are gone."),
    dict(key="avro", zip="Botvinnik", white="Botvinnik", black="Capablanca", year="1938", title="Botvinnik against Capablanca",
         theme="A plan that ends in a combination",
         lesson="AVRO tournament, 1938. Botvinnik builds a central pawn advance against a former world champion, and the combination "
                "that wins, starting with the bishop move 30.Ba3, grows out of that plan: a passed pawn that cannot be stopped.",
         expect=[(30, "w", "Ba3")]),
    dict(key="century", zip="Fischer", white="Byrne", black="Fischer", year="1956", title="The Game of the Century",
         theme="Activity beats material",
         lesson="New York, 1956. Thirteen-year-old Bobby Fischer gives up his queen with 17...Be6, and his pieces then take far more "
                "than they gave with a run of discovered checks. The game ends with mate by the black rook, 41...Rc2#.",
         expect=[(17, "b", "Be6"), (41, "b", "Rc2#")]),
    dict(key="octopus", zip="Karpov", white="Karpov", black="Kasparov", year="1985", round="16", title="The octopus knight",
         theme="An outpost deep in enemy territory",
         lesson="World Championship, Moscow 1985, game 16. Kasparov plants a knight on d3, inside White's camp, where no white pawn can "
                "ever chase it. From there it ties down White's whole position, and Kasparov wins the game and later the match.",
         expect=[(16, "b", "Nd3")]),
    dict(key="topalov", zip="Kasparov", white="Kasparov", black="Topalov", year="1999", event="Hoogovens", title="Kasparov's immortal",
         theme="Calculation and a king hunt",
         lesson="Wijk aan Zee, 1999. 24.Rxd4 gives up a rook to drive Black's king out of its shelter, and it is hunted up the board. "
                "The point is many moves deep, which is why it is still one of the most analysed sacrifices in chess.",
         expect=[(24, "w", "Rxd4")]),
]


def find(pgn_dir: Path, spec: dict) -> chess.pgn.Game:
    with zipfile.ZipFile(pgn_dir / f"{spec['zip']}.zip") as zf:
        for name in zf.namelist():
            if not name.lower().endswith(".pgn") or "/" in name or "\\" in name:
                continue
            f = io.StringIO(zf.read(name).decode("latin-1"))
            while True:
                g = chess.pgn.read_game(f)
                if g is None:
                    break
                h = g.headers
                if (spec["white"].lower() in h.get("White", "").lower() and spec["black"].lower() in h.get("Black", "").lower()
                        and h.get("Date", "").startswith(spec["year"]) and spec.get("event", "").lower() in h.get("Event", "").lower()
                        and (not spec.get("round") or h.get("Round") == spec["round"])):
                    if g.errors:
                        raise ValueError(f"{spec['key']}: PGN errors {g.errors}")
                    return g
    raise LookupError(f"{spec['key']}: not found in {spec['zip']}.zip")


def check_expect(game: chess.pgn.Game, spec: dict) -> None:
    board = game.board()
    seen = {}
    for mv in game.mainline_moves():
        seen[(board.fullmove_number, "w" if board.turn else "b")] = board.san(mv)
        board.push(mv)
    for n, side, san in spec.get("expect", []):
        if seen.get((n, side)) != san:
            raise AssertionError(f"{spec['key']}: the lesson names {n}{'.' if side == 'w' else '...'}{san}, the game has {seen.get((n, side))}")


def cp_of(score: chess.engine.PovScore) -> tuple[int, int | None]:
    w = score.white()
    if w.is_mate():
        return (1500 if w.mate() > 0 else -1500), w.mate()
    return max(-1500, min(1500, w.score())), None


def describe(cp: int, mate: int | None) -> str:
    if mate is not None:
        return f"{'White' if mate > 0 else 'Black'} mates in {abs(mate)}"
    return f"{'+' if cp >= 0 else ''}{cp / 100:.2f}"


def material(board: chess.Board, color: bool) -> int:
    return sum(VAL[p.piece_type] * (1 if p.color == color else -1) for p in board.piece_map().values())


def build(game: chess.pgn.Game, spec: dict, eng: chess.engine.SimpleEngine, seconds: float) -> dict:
    board = game.board()
    start_fen = board.fen()
    limit = chess.engine.Limit(time=seconds)
    moves = list(game.mainline_moves())
    infos = []                                               # analysis of each position before ply i, two lines
    b = board.copy()
    for mv in moves + [None]:
        if b.is_game_over():
            infos.append(None)
        else:
            infos.append(eng.analyse(b, limit, multipv=2))
        if mv is not None:
            b.push(mv)
    plies, b = [], board.copy()
    mats = []
    for i, mv in enumerate(moves):
        mover = b.turn
        before = infos[i]
        best = before[0]["pv"][0] if before and before[0].get("pv") else None
        best_line = b.variation_san(before[0]["pv"][:6]) if before and before[0].get("pv") else ""
        san, uci, fen_before = b.san(mv), mv.uci(), b.fen()
        idea = ideas(b, mv)
        mats.append(material(b, mover))
        b.push(mv)
        after = infos[i + 1]
        if after:
            cp, mate = cp_of(after[0]["score"])
        else:
            cp, mate = ((1500 if b.turn == chess.BLACK else -1500), None) if b.is_checkmate() else (0, None)
        cpb, mateb = cp_of(before[0]["score"]) if before else (0, None)
        sign = 1 if mover == chess.WHITE else -1
        drop = max(0.0, win_chances(sign * cpb) - win_chances(sign * cp))
        second_gap = None
        if before and len(before) > 1 and best == mv:
            c1, _ = cp_of(before[0]["score"]); c2, _ = cp_of(before[1]["score"])
            second_gap = win_chances(sign * c1) - win_chances(sign * c2)
        grade = None if best == mv else ("blunder" if drop >= 0.3 else "mistake" if drop >= 0.2 else "inaccuracy" if drop >= 0.1 else None)
        plies.append({"fen": b.fen(), "uci": uci, "san": san, "cp": cp, "mate": mate, "side": "White" if mover else "Black",
                      "best": chess.Board(fen_before).san(best) if best else None,
                      "best_uci": best.uci() if best else None, "best_line": best_line, "grade": grade, "drop": round(drop, 3),
                      "ideas": idea, "_gap": second_gap, "_fen_before": fen_before, "_eval_before": describe(cpb, mateb)})
    winner = {"1-0": "White", "0-1": "Black"}.get(game.headers.get("Result"))
    moments = []
    for i, p in enumerate(plies):
        # Material the mover is down after the reply and after its own next move: an exchange is level again by then,
        # a sacrifice is not.
        color = chess.WHITE if p["side"] == "White" else chess.BLACK
        later = [mats[i] - material(chess.Board(plies[k]["fen"]), color) for k in (i + 1, i + 2) if k < len(plies)]
        lost_later = min(later) if later else None
        kind = None
        if (lost_later is not None and lost_later >= 2 and p["drop"] <= 0.08 and not p["grade"] and p["side"] == winner):
            kind = "sacrifice"
        elif p["_gap"] is not None and p["_gap"] >= 0.3 and p["side"] == winner:
            kind = "only move"
        elif p["grade"] in ("blunder", "mistake") and winner and p["side"] != winner:
            kind = "turning point"
        if kind:
            if kind == "sacrifice":
                note = (f"{p['side']} gives up material here, {lost_later} point{'s' if lost_later != 1 else ''} after the reply, "
                        f"yet the engine's evaluation holds ({p['_eval_before']} before, {describe(p['cp'], p['mate'])} after).")
            elif kind == "only move":
                note = (f"The engine's best move, and the only good one: the next best gives away about "
                        f"{round(p['_gap'] * 50)} percentage points of winning chances.")
            else:
                note = (f"The losing side's {p['grade']}: the evaluation goes from {p['_eval_before']} to "
                        f"{describe(p['cp'], p['mate'])}; the engine preferred {p['best']}.")
            moments.append({"ply": i + 1, "side": p["side"], "grade": kind, "played": p["san"], "best": p["best"] or p["san"],
                            "eval_before": p["_eval_before"], "eval_after": describe(p["cp"], p["mate"]), "note": note,
                            "facts_before": {**facts(chess.Board(p["_fen_before"])), "strategy": strategy(chess.Board(p["_fen_before"]))}})
    order = {"sacrifice": 0, "only move": 1, "turning point": 2}
    picked = sorted(moments, key=lambda m: (order[m["grade"]], m["ply"]))
    keep, used = [], set()
    for m in picked:                                         # at most 6, and not two moments in a row
        if len(keep) >= 6 or any(abs(m["ply"] - u) <= 1 for u in used):
            continue
        keep.append(m); used.add(m["ply"])
    for n, side, san in spec.get("expect", []):              # the moves the lesson names are always moments
        ply = (n - 1) * 2 + (2 if side == "b" else 1)
        if any(m["ply"] == ply for m in keep):
            continue
        p = plies[ply - 1]
        note = " ".join(p["ideas"]) or f"The evaluation goes from {p['_eval_before']} to {describe(p['cp'], p['mate'])}."
        keep.append({"ply": ply, "side": p["side"], "grade": "the lesson's move", "played": p["san"], "best": p["best"] or p["san"],
                     "eval_before": p["_eval_before"], "eval_after": describe(p["cp"], p["mate"]), "note": note,
                     "facts_before": {**facts(chess.Board(p["_fen_before"])), "strategy": strategy(chess.Board(p["_fen_before"]))}})
    for p in plies:
        for k in ("_gap", "_fen_before", "_eval_before"):
            p.pop(k)
    h = game.headers
    return {"key": spec["key"], "title": spec["title"], "theme": spec["theme"], "lesson": spec["lesson"],
            "white": h.get("White", "").strip(), "black": h.get("Black", "").strip(), "white_elo": "", "black_elo": "",
            "result": h.get("Result"), "event": h.get("Event", "").strip(), "date": h.get("Date", "")[:4], "opening": "",
            "engine": eng.id.get("name", "Stockfish"), "seconds_per_move": seconds, "start_fen": start_fen,
            "plies": plies, "key_moments": sorted(keep, key=lambda m: m["ply"])}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pgn-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--seconds", type=float, default=0.5)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    eng = chess.engine.SimpleEngine.popen_uci(engine_path())
    out, pgns = [], []
    try:
        for spec in GAMES:
            if a.only and spec["key"] not in a.only.split(","):
                continue
            g = find(a.pgn_dir, spec)
            check_expect(g, spec)
            out.append(build(g, spec, eng, a.seconds))
            pgns.append(str(g))
            print(f"{spec['key']}: {len(out[-1]['plies'])} plies, moments: "
                  + ", ".join(f"{m['ply'] // 2 + m['ply'] % 2}{'.' if m['side'] == 'White' else '...'}{m['played']} ({m['grade']})" for m in out[-1]["key_moments"]),
                  flush=True)
    finally:
        eng.quit()
    a.out.write_text("/* Classic games for learning (jarvis-chess/scripts/master_games.py): moves from PGN Mentor, checked by\n"
                     "   python-chess; evaluations and key moments by Stockfish; ideas by the rules (strategy.py). */\n"
                     "window.MASTER_GAMES = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    (Path(__file__).resolve().parent.parent / "data").mkdir(exist_ok=True)
    (Path(__file__).resolve().parent.parent / "data" / "master-games.pgn").write_text("\n\n".join(pgns) + "\n", encoding="utf-8")
    print(f"wrote {a.out} ({a.out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
