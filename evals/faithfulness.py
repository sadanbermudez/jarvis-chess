"""Faithfulness eval: how often are a local model's chess claims true?

Two steps, run in this order:

  python evals/faithfulness.py freeze   fetch the latest standard Lichess games, review each with
                                        Stockfish, write evals/frozen_set.json (commit it before
                                        any scored run, like a held-out set)
  python evals/faithfulness.py run      ask the model to comment on every key moment in two
                                        conditions, score its claims with claims.check/score,
                                        write results under evals/results/

Conditions, on the same moments:
  grounded    the review JSON as review_game returns it (key moments carry facts_before), plus
              the MCP server's instructions
  ungrounded  only the FEN before the move, the move played and the engine's best move

The model writes short commentary and, in the same reply, a JSON block listing the claims it made
in the eight types check_claims supports, plus any other chess statements as free text. Claims of
a supported type are checked against the rules and Stockfish; everything the checker cannot judge
goes to a CSV for hand labelling. The model extracts its own claims, so the commentary is saved
next to the JSON for a human to audit.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import chess

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from jarvis_chess import claims as claim_checker  # noqa: E402
from jarvis_chess import server, sources  # noqa: E402
from jarvis_chess.analysis import Analyst  # noqa: E402

FROZEN = HERE / "frozen_set.json"
RESULTS = HERE / "results"
USER = "dr_namer"
N_GAMES = 5
SECONDS_PER_MOVE = 0.15
KEY_MOMENTS = 5

LLAMA_URL = "http://127.0.0.1:18434/v1/chat/completions"
LLAMA_KEY_FILE = os.path.expandvars(r"%LOCALAPPDATA%\hermes\runtimes\llamacpp\.api_key")
MODEL = "Qwen3.6-35B-A3B-UD-Q4_K_M"
TEMPERATURE = 0.7          # same as argus/evals/run_evals.py
MAX_TOKENS = 2000

CLAIM_TYPES = ("hanging", "attacked_by_cheaper", "pinned", "in_check", "mate_in_one",
               "best_move", "advantage", "material")
SERVER_INSTRUCTIONS = server.mcp.instructions

TASK = """Comment on this moment for a FIDE Master in 3 to 5 sentences: what was wrong with the move played and what the engine's move does instead. Be concrete and name moves in SAN.

After the commentary, output one fenced ```json block and nothing after it. It must list every factual chess statement your commentary makes:
{"claims": [...], "other_claims": [...]}

"claims" holds each statement that fits one of these eight types, as a dict:
  {"type": "hanging", "square": "e5"}             a piece on that square is attacked and undefended
  {"type": "attacked_by_cheaper", "square": "d4"} a piece on that square is attacked by a cheaper piece
  {"type": "pinned", "square": "c6"}              the piece on that square is pinned to its own king
  {"type": "in_check"}                            the side to move is in check
  {"type": "mate_in_one", "move": "Qh7#"}         the side to move has this mate in one
  {"type": "best_move", "move": "Nf3"}            this is the best move for the side to move
  {"type": "advantage", "side": "white"}          that side is better (engine evaluation)
  {"type": "material", "side": "white"}           that side is ahead on material
Add "position": "before" if the statement is about the position before the move played, or "position": "after" if it is about the position after the move played (where the other side is to move).

"other_claims" holds every other factual chess statement in your commentary (plans, threats, tactics, structure, evaluations of lines) as short plain sentences.

List only statements your commentary actually makes. Do not add claims that are not in the commentary."""


# ── freeze ───────────────────────────────────────────────────────────────────
def freeze(args) -> None:
    if FROZEN.exists() and not args.force:
        sys.exit(f"{FROZEN} exists; it is the frozen set. Use --force only to rebuild it on purpose.")
    games = [g for g in sources.lichess_recent(USER, args.fetch)
             if _header(g["pgn"], "Variant", "Standard") == "Standard"][:N_GAMES]
    if len(games) < N_GAMES:
        sys.exit(f"only {len(games)} standard games in the last {args.fetch}; raise --fetch")
    a = Analyst()
    out = []
    try:
        for g in games:
            t0 = time.time()
            r = a.review(g["pgn"], SECONDS_PER_MOVE, KEY_MOMENTS)
            # what review_game hands the model: per-move list trimmed to six fields
            r["moves"] = [{k: m[k] for k in ("ply", "side", "played", "best", "eval_after", "grade")}
                          for m in r["moves"]]
            gid = g["url"].rsplit("/", 1)[-1]
            print(f"{gid}: {g['plies']} plies, {len(r['key_moments'])} key moments, {time.time() - t0:.1f} s")
            out.append({
                "game_id": gid, "url": g["url"], "date": g["date"], "white": g["white"], "black": g["black"],
                "result": g["result"], "time_control": g["time_control"], "plies": g["plies"],
                "key_moments": [{"ply": m["ply"], "side": m["side"], "fen_before": m["fen_before"],
                                 "played": m["played"], "best": m["best"], "grade": m["grade"]}
                                for m in r["key_moments"]],
                "pgn": g["pgn"], "review": r,
            })
    finally:
        a.close()
    doc = {"about": "Frozen test set for evals/faithfulness.py. Commit before any scored run.",
           "user": USER, "site": "lichess", "frozen_at": datetime.now().isoformat(timespec="seconds"),
           "engine": out[0]["review"]["engine"] if out else "", "seconds_per_move": SECONDS_PER_MOVE,
           "key_moments_per_game": KEY_MOMENTS, "games": out}
    FROZEN.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    n = sum(len(g["key_moments"]) for g in out)
    print(f"wrote {FROZEN}: {len(out)} games, {n} key moments")


def _header(pgn: str, name: str, default: str = "") -> str:
    m = re.search(rf'^\[{name} "([^"]*)"\]', pgn, re.M)
    return m.group(1) if m else default


# ── prompts ──────────────────────────────────────────────────────────────────
def prompts(game: dict, moment: dict, condition: str) -> list[dict]:
    if condition == "grounded":
        system = SERVER_INSTRUCTIONS
        user = (f"review_game returned this for game {game['url']}:\n```json\n"
                f"{json.dumps(game['review'], indent=1, ensure_ascii=False)}\n```\n\n"
                f"Moment: ply {moment['ply']}, {moment['side']} played {moment['played']}; "
                f"the engine preferred {moment['best']}. It is listed in key_moments with its facts. "
                f"No tools are available in this conversation; use the review above.\n\n{TASK}")
    elif condition == "ungrounded":
        system = "You are a chess commentator."
        user = (f"Position (FEN, before the move): {moment['fen_before']}\n"
                f"{moment['side']} played {moment['played']}. The engine's best move was {moment['best']}.\n\n{TASK}")
    else:
        raise ValueError(condition)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def ask(messages: list[dict], key: str) -> tuple[str, int, float]:
    body = {"model": MODEL, "messages": messages, "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
            "chat_template_kwargs": {"enable_thinking": False}}
    req = urllib.request.Request(LLAMA_URL, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        data = json.loads(r.read())
    tokens = (data.get("usage") or {}).get("completion_tokens", 0)
    return (data["choices"][0]["message"].get("content") or "").strip(), tokens, round(time.time() - t0, 1)


# ── parsing ──────────────────────────────────────────────────────────────────
FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S | re.I)


def parse_reply(reply: str) -> dict:
    """Split a reply into commentary and the claims block.

    Returns {"commentary", "claims", "other_claims", "error"}. The claims block is the last fenced
    JSON object; failing that, the last balanced {...} that parses. Each claim gets a "position"
    of "before" or "after"; a missing or unknown value becomes "before" with "position_defaulted".
    Claims that are not dicts are dropped and counted in the error field.
    """
    out = {"commentary": reply.strip(), "claims": [], "other_claims": [], "error": None}
    blob, start = None, None
    fences = list(FENCE.finditer(reply))
    if fences:
        blob, start = fences[-1].group(1), fences[-1].start()
    else:
        for i in range(len(reply) - 1, -1, -1):
            if reply[i] == "{":
                cand = _balanced(reply, i)
                obj = _loads(cand) if cand else None
                # the claims block itself, not one of the claim dicts nested inside it
                if isinstance(obj, dict) and ("claims" in obj or "other_claims" in obj):
                    blob, start = cand, i
                    break
    if blob is None:
        out["error"] = "no JSON block"
        return out
    data = _loads(blob)
    if not isinstance(data, dict):
        out["error"] = "JSON block does not parse"
        out["commentary"] = reply[:start].strip()
        return out
    out["commentary"] = reply[:start].strip()
    raw = data.get("claims") or []
    dropped = 0
    for c in raw if isinstance(raw, list) else []:
        if not isinstance(c, dict):
            dropped += 1
            continue
        c = dict(c)
        pos = str(c.get("position", "")).strip().lower()
        if pos not in ("before", "after"):
            c["position"] = "before"
            c["position_defaulted"] = True
        else:
            c["position"] = pos
        out["claims"].append(c)
    other = data.get("other_claims") or []
    out["other_claims"] = [str(x) for x in other] if isinstance(other, list) else [str(other)]
    if dropped:
        out["error"] = f"{dropped} claim(s) were not objects and were dropped"
    return out


def _balanced(s: str, i: int) -> str | None:
    depth, in_str, esc = 0, False, False
    for j in range(i, len(s)):
        ch = s[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[i:j + 1]
    return None


def _loads(s: str):
    try:
        return json.loads(s)
    except ValueError:
        return None


# ── scoring ──────────────────────────────────────────────────────────────────
def boards(moment: dict) -> dict[str, chess.Board]:
    before = chess.Board(moment["fen_before"])
    after = before.copy()
    after.push_san(moment["played"])
    return {"before": before, "after": after}


class CachedEngine:
    """One checker search per (position, multipv), reused by every later claim on that position.

    Multi-threaded Stockfish is not deterministic: in the smoke run, two 0.5 s searches of the same
    FEN returned different top-2 moves, so the same best_move claim was true in one condition and
    false in the other. Caching makes both conditions face the identical engine verdict.
    claims.check() is unchanged; it only sees an object with analyse().
    """

    def __init__(self, engine):
        self.engine, self.cache = engine, {}

    def analyse(self, board, limit, multipv=None):
        k = (board.fen(), multipv)
        if k not in self.cache:
            self.cache[k] = self.engine.analyse(board, limit, multipv=multipv)
        return self.cache[k]


def check_moment(moment: dict, parsed: dict, engine) -> list[dict]:
    b = boards(moment)
    results = []
    for pos in ("before", "after"):
        mine = [c for c in parsed["claims"] if c["position"] == pos]
        if mine:
            for r in claim_checker.check(b[pos], mine, engine):
                r["fen"] = b[pos].fen()
                results.append(r)
    return results


def wilson(k: int, n: int, z: float = 1.959964) -> list[float] | None:
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def summarise(rows: list[dict]) -> dict:
    results = [r for row in rows for r in row["results"]]
    s = claim_checker.score(results)
    s["wilson_95"] = wilson(s["true"], s["checkable"])
    s["moments"] = len(rows)
    s["structured_claims"] = len(results)
    s["unverifiable_structured_claims"] = sum(1 for r in results if r["verdict"] is None)
    s["other_claims"] = sum(len(row["other_claims"]) for row in rows)
    s["parse_errors"] = sum(1 for row in rows if row["parse_error"])
    s["call_errors"] = sum(1 for row in rows if row.get("call_error"))
    by_type = {}
    for r in results:
        t = r["claim"].get("type", "?") if r["claim"].get("type") in CLAIM_TYPES else "other/unknown"
        d = by_type.setdefault(t, {"checkable": 0, "true": 0, "false": 0, "unverifiable": 0})
        if r["verdict"] is None:
            d["unverifiable"] += 1
        else:
            d["checkable"] += 1
            d["true" if r["verdict"] else "false"] += 1
    s["by_type"] = dict(sorted(by_type.items()))
    # the review (0.15 s) and the checker (0.5 s, top 2) are separate searches and can disagree:
    # count best_move claims that repeat the review's best move for the position before the move
    # and were still judged false, so that disagreement is visible instead of hidden in the score
    s["best_move_equals_review_best_but_false"] = sum(
        1 for row in rows for r in row["results"]
        if r["claim"].get("type") == "best_move" and r["claim"].get("position") == "before"
        and str(r["claim"].get("move", "")).rstrip("#+!?") == (row["best"] or "").rstrip("#+")
        and r["verdict"] is False)
    s["seconds_total"] = round(sum(row["seconds"] for row in rows), 1)
    return s


# ── run ──────────────────────────────────────────────────────────────────────
def run(args) -> None:
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    key = Path(LLAMA_KEY_FILE).read_text(encoding="utf-8").strip()
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    moments = [(g, m) for g in frozen["games"] for m in g["key_moments"]]
    if args.limit:
        moments = moments[:args.limit]
    stamp = datetime.now()
    rows = []
    analyst = Analyst()
    checker_engine = CachedEngine(analyst.engine)
    t_start = time.time()
    try:
        for cond in conditions:
            print(f"\n== {cond}")
            for g, m in moments:
                row = {"condition": cond, "game_id": g["game_id"], "url": g["url"], "ply": m["ply"],
                       "side": m["side"], "fen_before": m["fen_before"], "played": m["played"],
                       "best": m["best"], "grade": m["grade"], "call_error": None}
                try:
                    reply, tokens, secs = ask(prompts(g, m, cond), key)
                except Exception as e:  # noqa: BLE001 - recorded, never silently dropped
                    reply, tokens, secs = "", 0, 0.0
                    row["call_error"] = f"{type(e).__name__}: {e}"[:300]
                parsed = parse_reply(reply) if reply else {"commentary": "", "claims": [], "other_claims": [],
                                                          "error": "empty reply"}
                results = check_moment(m, parsed, checker_engine)
                row.update({"reply": reply, "commentary": parsed["commentary"], "parse_error": parsed["error"],
                            "claims": parsed["claims"], "other_claims": parsed["other_claims"],
                            "results": results, "score": claim_checker.score(results),
                            "completion_tokens": tokens, "seconds": secs})
                rows.append(row)
                sc = row["score"]
                print(f"  {g['game_id']} ply {m['ply']:>3} {m['played']:<7} {secs:>5}s  "
                      f"claims {len(results)} checkable {sc['checkable']} true {sc['true']}"
                      f"{'  PARSE: ' + parsed['error'] if parsed['error'] else ''}")
    finally:
        analyst.close()
    wall = round(time.time() - t_start, 1)
    summary = {c: summarise([r for r in rows if r["condition"] == c]) for c in conditions}
    RESULTS.mkdir(exist_ok=True)
    base = RESULTS / f"faithfulness-{stamp:%Y%m%d-%H%M%S}"
    meta = {"model": MODEL, "temperature": TEMPERATURE, "thinking": False, "max_tokens": MAX_TOKENS,
            "checker": {"seconds": 0.5, "tolerance": 2, "engine": analyst.name},
            "frozen_set": str(FROZEN.relative_to(HERE.parent)), "frozen_at": frozen["frozen_at"],
            "games": [g["game_id"] for g in frozen["games"]], "moments": len(moments),
            "conditions": conditions, "started": stamp.isoformat(timespec="seconds"), "wall_seconds": wall}
    Path(f"{base}.json").write_text(json.dumps({"meta": meta, "summary": summary, "rows": rows},
                                               indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    write_labels(rows, Path(f"{base}-to-label.csv"))
    write_commentary(rows, Path(f"{base}-commentary.md"))
    print(f"\nwall {wall} s")
    for c, s in summary.items():
        print(f"{c}: checkable {s['checkable']} true {s['true']} false {s['false']} "
              f"faithfulness {s['faithfulness']} wilson95 {s['wilson_95']} "
              f"(unverifiable {s['unverifiable_structured_claims']}, other {s['other_claims']}, "
              f"parse errors {s['parse_errors']})")
    print(f"results: {base}.json")


def write_labels(rows: list[dict], path: Path) -> None:
    """Everything the checker could not judge, one row per statement, with an empty label column."""
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["condition", "game_id", "ply", "played", "best", "fen_before", "kind", "statement",
                    "checker_reason", "label_true_false_unclear", "note"])
        for r in rows:
            base = [r["condition"], r["game_id"], r["ply"], r["played"], r["best"], r["fen_before"]]
            for x in r["results"]:
                if x["verdict"] is None:
                    w.writerow(base + ["structured claim the checker cannot judge",
                                       json.dumps(x["claim"], ensure_ascii=False), x["why"], "", ""])
            for s in r["other_claims"]:
                w.writerow(base + ["other claim (no checker type)", s, "", "", ""])


def write_commentary(rows: list[dict], path: Path) -> None:
    """Each commentary next to its extracted claims and verdicts, so a human can audit the extraction."""
    v = {True: "TRUE", False: "FALSE", None: "cannot check"}
    lines = ["# Commentary and extracted claims", "",
             "Check that every claim below appears in the commentary above it, and that the commentary "
             "makes no checkable statement missing from the list.", ""]
    for r in rows:
        lines += [f"## {r['condition']} · {r['url']} · ply {r['ply']} · {r['side']} played {r['played']}, "
                  f"engine best {r['best']}", "", f"FEN before: `{r['fen_before']}`", ""]
        if r.get("call_error"):
            lines += [f"Call error: {r['call_error']}", ""]
        if r["parse_error"]:
            lines += [f"Parse problem: {r['parse_error']}", ""]
        lines += ["> " + (r["commentary"] or "(empty)").replace("\n", "\n> "), ""]
        for x in r["results"]:
            lines.append(f"- {v[x['verdict']]}: `{json.dumps(x['claim'], ensure_ascii=False)}` ({x['why']})")
        for s in r["other_claims"]:
            lines.append(f"- to label by hand: {s}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze", help="build evals/frozen_set.json")
    f.add_argument("--fetch", type=int, default=20, help="how many recent games to scan for standard ones")
    f.add_argument("--force", action="store_true")
    r = sub.add_parser("run", help="score the model on the frozen set")
    r.add_argument("--conditions", default="grounded,ungrounded")
    r.add_argument("--limit", type=int, default=0, help="first N moments only (smoke test, not a result)")
    a = ap.parse_args()
    freeze(a) if a.cmd == "freeze" else run(a)
