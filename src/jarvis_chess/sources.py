"""Recent games from the public Lichess and Chess.com APIs (no account or token needed)."""
from __future__ import annotations

import io
import json
import urllib.request

import chess.pgn

UA = "jarvis-chess/0.1 (personal game review; contact sadanbermudez@gmail.com)"


def _get(url: str, accept: str = "application/json", timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def summarize(pgn: str, site: str, url: str = "") -> dict:
    game = chess.pgn.read_game(io.StringIO(pgn))
    if game is None:
        raise ValueError("not a PGN game")
    h = game.headers
    return {
        "site": site,
        "url": url or h.get("Link") or h.get("Site", ""),
        "date": h.get("UTCDate") or h.get("Date", ""),
        "white": h.get("White", "?"), "white_elo": h.get("WhiteElo", ""),
        "black": h.get("Black", "?"), "black_elo": h.get("BlackElo", ""),
        "result": h.get("Result", "*"),
        "time_control": h.get("TimeControl", ""),
        "opening": h.get("Opening") or h.get("ECOUrl", "").rsplit("/", 1)[-1].replace("-", " "),
        "plies": sum(1 for _ in game.mainline_moves()),
        "pgn": pgn,
    }


def lichess_recent(username: str, count: int = 5) -> list[dict]:
    raw = _get(f"https://lichess.org/api/games/user/{username}?max={count}&pgnInJson=true&opening=true&clocks=false&evals=false",
               accept="application/x-ndjson")
    games = []
    for line in raw.decode("utf-8").splitlines():
        if line.strip():
            g = json.loads(line)
            games.append(summarize(g["pgn"], "lichess", f"https://lichess.org/{g['id']}"))
    return games


def chesscom_recent(username: str, count: int = 5) -> list[dict]:
    archives = json.loads(_get(f"https://api.chess.com/pub/player/{username}/games/archives"))["archives"]
    games: list[dict] = []
    for month in reversed(archives):                 # newest month first, walk back until we have enough
        monthly = json.loads(_get(month))["games"]
        for g in reversed(monthly):
            if g.get("pgn") and g.get("rules", "chess") == "chess":
                games.append(summarize(g["pgn"], "chess.com", g.get("url", "")))
                if len(games) >= count:
                    return games
    return games


def recent(site: str, username: str, count: int = 5) -> list[dict]:
    site = site.lower().replace(".", "").replace(" ", "")
    if site == "lichess":
        return lichess_recent(username, count)
    if site in ("chesscom", "chess"):
        return chesscom_recent(username, count)
    raise ValueError("site must be 'lichess' or 'chesscom'")
