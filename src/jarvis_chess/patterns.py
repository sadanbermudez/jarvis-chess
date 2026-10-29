"""Patterns across all of a player's games: where the mistakes repeat, and positions to train on.

One game review says what went wrong in that game. This looks at every game a player has on Lichess and
Chess.com and asks
which mistakes keep coming back: in which phase, under how much clock pressure, of which kind, in which
openings, and at what time of day. Every number comes from Stockfish and the rules of chess; nothing here
calls a language model.

Each move by the player gets the same grading as a review (Lichess's winning-chances method). A mistake or
blunder also gets tags, each decided by the rules or the engine:
- hung_piece:     after the move, one of the player's pieces can be taken for free or by a cheaper piece,
                  and the engine's reply takes it
- allowed_mate:   after the move, the opponent has a forced mate
- missed_mate:    before the move, the player had a forced mate and the move lets it go
- missed_tactic:  the best move was a capture or a check, and the move played lost at least 0.2 of the
                  player's winning chances
- threw_win:      the player was clearly winning before the move (winning chances at least 0.5)
- time_trouble:   under 10% of the starting clock, or under 15 seconds, was left

Games are analysed once and kept in a cache, so a nightly run only analyses new games.

Chess.com games are turned into the same shape as Lichess games and named with the Lichess opening table
(openings.tsv, from github.com/lichess-org/chess-openings, CC0), so both sites share opening names.

Run: python -m jarvis_chess.patterns --user dr_namer --chesscom dr_namer --since 2026-07-01 \
         --cache games.json --out patterns.json
"""
from __future__ import annotations

import argparse
import io
import json
import re
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import chess
import chess.engine
import chess.pgn

from .analysis import MATE_CP, Analyst, cp_white, facts, grade, win_chances

UA = {"User-Agent": "jarvis-chess/1.0 (github.com/sadanbermudez/jarvis-chess)"}
VERSION = 1                                           # bump when the analysis changes, to redo cached games


def fetch(user: str, since_ms: int | None = None) -> list[dict]:
    """Every standard game of `user` on Lichess (newest first), with clocks and opening names."""
    url = f"https://lichess.org/api/games/user/{user}?clocks=true&opening=true&variant=standard"
    if since_ms:
        url += f"&since={since_ms + 1}"
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/x-ndjson"})
    with urllib.request.urlopen(req, timeout=300) as r:
        lines = r.read().decode("utf-8").splitlines()
    return [g for g in map(json.loads, filter(None, lines)) if g.get("variant") == "standard" and g.get("moves")]


@lru_cache(maxsize=1)
def _openings() -> dict[str, str]:
    """Position (EPD) -> opening name, from the Lichess opening table."""
    names = {}
    for line in Path(__file__).with_name("openings.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        _, name, pgn = line.split("\t")
        board = chess.Board()
        for tok in pgn.split():
            if not tok[0].isdigit():
                board.push_san(tok)
        names[board.epd()] = name
    return names


def opening_name(sans: list[str]) -> str:
    """Name of the last known opening position the game passes through."""
    table, board, name = _openings(), chess.Board(), "?"
    for san in sans[:40]:
        board.push_san(san)
        name = table.get(board.epd(), name)
    return name


def _clock(comment: str) -> int | None:
    m = re.search(r"\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]", comment)
    return round(100 * (int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]))) if m else None


def chesscom_game(g: dict) -> dict | None:
    """One Chess.com game in the shape of a Lichess game (centisecond clocks, winner, opening name)."""
    if g.get("rules") != "chess" or g.get("time_class") == "daily" or not g.get("pgn"):
        return None
    pgn = chess.pgn.read_game(io.StringIO(g["pgn"]))
    if pgn is None or pgn.headers.get("SetUp") == "1":
        return None
    sans, clocks, board = [], [], pgn.board()
    for node in pgn.mainline():
        sans.append(board.san(node.move))
        board.push(node.move)
        clocks.append(_clock(node.comment))
    if not sans:
        return None
    h = pgn.headers
    start = datetime.strptime(f"{h.get('UTCDate', h.get('Date'))} {h.get('UTCTime', '00:00:00')}", "%Y.%m.%d %H:%M:%S")
    winner = next((c for c in ("white", "black") if g[c]["result"] == "win"), None)
    game = {"id": "cc" + g["url"].rstrip("/").rsplit("/", 1)[-1], "site": "chess.com", "url": g["url"],
            "players": {c: {"user": {"id": g[c]["username"].lower()}, "rating": g[c].get("rating")} for c in ("white", "black")},
            "moves": " ".join(sans), "speed": g["time_class"],
            "createdAt": int(start.replace(tzinfo=timezone.utc).timestamp() * 1000),
            "clock": {"initial": int(g["time_control"].split("+")[0])},
            "clocks": clocks if None not in clocks else [], "opening": {"name": opening_name(sans)}}
    if winner:
        game["winner"] = winner
    return game


def fetch_chesscom(user: str, since_ms: int | None = None) -> list[dict]:
    """Every live standard game of `user` on Chess.com after `since_ms` (from the monthly archives), newest first."""
    def get(url):
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            return json.loads(r.read())
    archives = get(f"https://api.chess.com/pub/player/{user.lower()}/games/archives")["archives"]
    if since_ms:
        first = datetime.fromtimestamp(since_ms / 1000, timezone.utc).strftime("%Y/%m")
        archives = [a for a in archives if a[-7:] >= first]
    games = []
    for a in archives:
        for g in get(a)["games"]:
            c = chesscom_game(g)
            if c and (since_ms is None or c["createdAt"] > since_ms):
                games.append(c)
    return sorted(games, key=lambda g: -g["createdAt"])


def phase(board: chess.Board, ply: int) -> str:
    pieces = sum(1 for p in board.piece_map().values() if p.piece_type not in (chess.PAWN, chess.KING))
    if pieces <= 6:
        return "endgame"
    return "opening" if ply <= 24 else "middlegame"


def mover_chances(cp: int, white: bool) -> float:
    return win_chances(cp if white else -cp)


def analyse_game(engine: chess.engine.SimpleEngine, game: dict, user: str, nodes: int) -> dict:
    """The player's moves in one Lichess game, graded and tagged."""
    me = "white" if game["players"]["white"].get("user", {}).get("id") == user.lower() else "black"
    white = me == "white"
    initial = game.get("clock", {}).get("initial", 0)
    clocks = game.get("clocks", [])
    board, limit = chess.Board(), chess.engine.Limit(nodes=nodes)
    sans = game["moves"].split()
    info = engine.analyse(board, limit)
    moves = []
    for ply, san in enumerate(sans, 1):
        mine = board.turn == (chess.WHITE if white else chess.BLACK)
        mv = board.parse_san(san)
        before = info
        board.push(mv)
        over = board.is_game_over()
        info = engine.analyse(board, limit) if not over else None
        if not mine:
            continue
        board.pop()
        fen = board.fen()
        best = before.get("pv", [None])[0]
        best_san = board.san(best) if best else None
        best_line = board.variation_san(before["pv"][:6]) if before.get("pv") else ""
        best_is_tactic = bool(best) and (board.is_capture(best) or board.gives_check(best))
        hanging_before = {x for k in ("hanging_pieces", "attacked_by_a_cheaper_piece") for x in facts(board)[k]}
        board.push(mv)
        cp_before = cp_white(before["score"])
        if info is not None:
            cp_after = cp_white(info["score"])
        else:
            cp_after = (MATE_CP if white else -MATE_CP) if board.is_checkmate() else 0
        p_before, p_after = mover_chances(cp_before, white), mover_chances(cp_after, white)
        drop = max(0.0, p_before - p_after)
        g = grade(drop) if best_san != san else None
        left = clocks[ply - 1] / 100 if ply - 1 < len(clocks) else None
        rec = {"ply": ply, "played": san, "best": best_san, "drop": round(drop, 3), "grade": g,
               "phase": phase(board, ply), "clock_left": left, "chances_before": round(p_before, 3)}
        if g in ("mistake", "blunder"):
            tags = []
            if left is not None and initial and left < max(15, 0.1 * initial):
                tags.append("time_trouble")
            if p_before >= 0.5:
                tags.append("threw_win")
            s_after = info["score"].pov(not board.turn) if info else None   # from the player's side
            if s_after is not None and s_after.is_mate() and s_after.mate() < 0:
                tags.append("allowed_mate")
            s_before = before["score"].pov(chess.WHITE if white else chess.BLACK)
            if s_before.is_mate() and s_before.mate() > 0 and not (s_after is not None and s_after.is_mate() and s_after.mate() > 0):
                tags.append("missed_mate")
            reply = info.get("pv", [None])[0] if info else None
            mine_color = chess.WHITE if white else chess.BLACK
            now_hanging = {x for k in ("hanging_pieces", "attacked_by_a_cheaper_piece") for x in facts(board)[k]
                           if x.startswith("White" if white else "Black")} - hanging_before
            if reply is not None and board.is_capture(reply):
                target = board.piece_at(reply.to_square)
                if target and target.color == mine_color and target.piece_type != chess.PAWN and any(
                        x.endswith(chess.square_name(reply.to_square)) for x in now_hanging):
                    tags.append("hung_piece")
            if best_is_tactic and best_san != san:
                tags.append("missed_tactic")
            rec.update(tags=tags, fen=fen, best_line=best_line)
        moves.append(rec)
        if over:
            break
    winner = game.get("winner")
    return {"id": game["id"], "v": VERSION, "site": game.get("site", "lichess"),
            "url": game.get("url", f"https://lichess.org/{game['id']}"), "color": me,
            "speed": game.get("speed"), "created": game["createdAt"], "initial": initial,
            "opening": game.get("opening", {}).get("name", "?"),
            "result": 1.0 if winner == me else 0.0 if winner else 0.5,
            "rating": game["players"][me].get("rating"), "moves": moves}


# ---------- what repeats ----------

def _rate(errors: int, moves: int) -> float | None:
    return round(40 * errors / moves, 2) if moves else None          # errors per 40 of the player's moves


def summarise(games: list[dict], min_games: int = 5) -> dict:
    games = sorted(games, key=lambda g: g["created"])
    errs = [(g, m) for g in games for m in g["moves"] if m["grade"] in ("mistake", "blunder")]
    allm = [(g, m) for g in games for m in g["moves"]]

    def by(key):
        n, e = defaultdict(int), defaultdict(int)
        for g, m in allm:
            n[key(g, m)] += 1
        for g, m in errs:
            e[key(g, m)] += 1
        return {k: {"moves": n[k], "errors": e[k], "per_40_moves": _rate(e[k], n[k])} for k in n}

    tags = defaultdict(int)
    for _, m in errs:
        for t in m["tags"]:
            tags[t] += 1
    pressure = by(lambda g, m: "time_trouble" if m["clock_left"] is not None and g["initial"] and
                  m["clock_left"] < max(15, 0.1 * g["initial"]) else "enough_time")

    def score(gs):
        return {"games": len(gs), "score": round(100 * sum(g["result"] for g in gs) / len(gs)) if gs else None}

    openings = defaultdict(list)
    for g in games:
        openings[(g["color"], g["opening"].split(":")[0])].append(g)
    op = []
    for (color, name), gs in openings.items():
        if len(gs) < min_games:
            continue
        e = sum(1 for g in gs for m in g["moves"] if m["grade"] in ("mistake", "blunder"))
        op.append({"opening": name, "color": color, **score(gs), "errors_per_game": round(e / len(gs), 2)})
    op.sort(key=lambda o: (o["score"], -o["games"]))

    def hour_bucket(g):
        h = datetime.fromtimestamp(g["created"] / 1000).hour
        return "morning (6-12)" if 6 <= h < 12 else "afternoon (12-18)" if 12 <= h < 18 else "evening (18-23)" if 18 <= h < 23 else "night (23-6)"
    hours = defaultdict(list)
    for g in games:
        hours[hour_bucket(g)].append(g)

    after_loss, other = [], []                                # tilt: the next game within 30 minutes of a loss
    for prev, g in zip(games, games[1:]):
        (after_loss if prev["result"] == 0 and g["created"] - prev["created"] < 30 * 60 * 1000 else other).append(g)
    session, prev_t, idx = defaultdict(list), None, 0           # games in a row with gaps under 30 minutes
    for g in games:
        idx = idx + 1 if prev_t and g["created"] - prev_t < 30 * 60 * 1000 else 1
        prev_t = g["created"]
        session["1-3" if idx <= 3 else "4-6" if idx <= 6 else "7+"].append(g)

    return {
        "games": len(games), "first": games[0]["created"] if games else None, "last": games[-1]["created"] if games else None,
        "by_site": {s: score([g for g in games if g.get("site", "lichess") == s])
                    for s in sorted({g.get("site", "lichess") for g in games})},
        "by_speed": {s: score([g for g in games if g["speed"] == s]) for s in sorted({g["speed"] for g in games})},
        "by_color": {c: score([g for g in games if g["color"] == c]) for c in ("white", "black")},
        "errors": len(errs), "per_40_moves": _rate(len(errs), len(allm)),
        "by_phase": by(lambda g, m: m["phase"]), "by_clock": pressure,
        "tags": dict(sorted(tags.items(), key=lambda kv: -kv[1])),
        "untagged": sum(1 for _, m in errs if not set(m["tags"]) - {"threw_win"}),
        "openings": op,
        "by_time_of_day": {k: score(v) for k, v in sorted(hours.items())},
        "after_a_loss": {"next_game_within_30_min": score(after_loss), "other_games": score(other)},
        "by_game_in_session": {k: score(session[k]) for k in ("1-3", "4-6", "7+") if session[k]},
    }


def move_url(game: dict, ply: int) -> str:
    sep = "?move=" if game.get("site") == "chess.com" else "#"
    return f"{game['url']}{sep}{ply}"


def drills(games: list[dict], limit: int = 60) -> list[dict]:
    """The player's own mistakes as training positions: not in time trouble, not already lost, worst first."""
    out = []
    for g in games:
        for m in g["moves"]:
            if m["grade"] in ("mistake", "blunder") and "time_trouble" not in m["tags"] and m["chances_before"] > -0.6:
                out.append({"fen": m["fen"], "best": m["best"], "best_line": m["best_line"], "played": m["played"],
                            "drop": m["drop"], "tags": m["tags"], "phase": m["phase"], "opening": g["opening"],
                            "url": move_url(g, m["ply"]), "created": g["created"]})
    return sorted(out, key=lambda d: -d["drop"])[:limit]


def update(user: str | None, cache: Path, nodes: int = 250_000, threads: int = 8, log=print,
           chesscom: str | None = None, since_ms: int | None = None) -> list[dict]:
    games = {}
    if cache.exists():
        games = {g["id"]: g for g in json.loads(cache.read_text(encoding="utf-8")) if g.get("v") == VERSION}
    fresh = []
    for site, name, get in (("lichess", user, fetch), ("chess.com", chesscom, fetch_chesscom)):
        if name:
            newest = max((g["created"] for g in games.values() if g.get("site", "lichess") == site), default=since_ms)
            fresh += [g for g in get(name, newest) if g["id"] not in games]
    fresh.sort(key=lambda g: -g["createdAt"])
    log(f"{len(games)} games cached, {len(fresh)} new")
    if fresh:
        a = Analyst(threads=threads)
        try:
            for i, g in enumerate(reversed(fresh), 1):                # oldest first, saved as it goes
                games[g["id"]] = analyse_game(a.engine, g, chesscom if g.get("site") == "chess.com" else user, nodes)
                if i % 10 == 0 or i == len(fresh):
                    cache.write_text(json.dumps(list(games.values())), encoding="utf-8")
                    log(f"analysed {i}/{len(fresh)}")
        finally:
            a.close()
    return list(games.values())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--user", help="Lichess username")
    ap.add_argument("--chesscom", help="Chess.com username")
    ap.add_argument("--since", help="only games from this date (YYYY-MM-DD)")
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--nodes", type=int, default=250_000)
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    if not (args.user or args.chesscom):
        ap.error("give --user, --chesscom or both")
    since = int(datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc).timestamp() * 1000) if args.since else None
    games = update(args.user, args.cache, args.nodes, args.threads, chesscom=args.chesscom, since_ms=since)
    if since:
        games = [g for g in games if g["created"] >= since]
    report = {"user": args.user, "chesscom": args.chesscom, "made": datetime.now().isoformat(timespec="seconds"), "nodes_per_position": args.nodes,
              "summary": summarise(games), "drills": drills(games)}
    args.out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(f"{report['summary']['games']} games, {report['summary']['errors']} mistakes and blunders -> {args.out}")


if __name__ == "__main__":
    main()
