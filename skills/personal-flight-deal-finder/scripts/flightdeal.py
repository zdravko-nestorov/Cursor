#!/usr/bin/env python3
"""Date-pair enumeration and baseline state for the personal-flight-deal-finder skill.

Standard library only. The state directory is resolved next to this script's parent,
so the command works from any working directory.

  pairs --window 2026-09-05..2026-09-27 --stay 10-12
  load  --trip-id sof-nbo-sep2026
  save  --trip-id sof-nbo-sep2026 --payload run.json   (use - for stdin)
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime, timedelta

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(SKILL_DIR, "state")
HISTORY_LIMIT = 24
DEAL_BAND = 0.10
TYPICAL_BAND = 0.75


def fail(message):
    sys.exit("error: " + message)


def state_path(trip_id):
    if not trip_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_." for c in trip_id):
        fail("trip_id must be lowercase letters, digits, hyphen, underscore or dot")
    return os.path.join(STATE_DIR, trip_id + ".json")


def read_state(trip_id):
    path = state_path(trip_id)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write_state(trip_id, data):
    os.makedirs(STATE_DIR, exist_ok=True)
    path = state_path(trip_id)
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    os.replace(tmp, path)
    return path


def cmd_pairs(args):
    try:
        start_text, end_text = args.window.split("..")
        start = date.fromisoformat(start_text.strip())
        end = date.fromisoformat(end_text.strip())
    except ValueError:
        fail("window must look like 2026-09-05..2026-09-27")
    if end <= start:
        fail("window end must be after window start")

    stay = args.stay.split("-") if "-" in args.stay else [args.stay, args.stay]
    try:
        low, high = int(stay[0]), int(stay[-1])
    except ValueError:
        fail("stay must look like 10-12 or 11")
    if low < 1 or high < low:
        fail("stay range is not valid")

    rows = []
    for length in range(low, high + 1):
        day = start
        while day + timedelta(days=length) <= end:
            rows.append((day, day + timedelta(days=length), length))
            day += timedelta(days=1)
    rows.sort(key=lambda row: (row[0], row[2]))

    print("window %s..%s  stay %d-%d days  pairs %d" % (start, end, low, high, len(rows)))
    for depart, back, length in rows:
        print("%s %s  ->  %s %s   %2dd" % (depart, depart.strftime("%a"), back, back.strftime("%a"), length))


def cmd_load(args):
    state = read_state(args.trip_id)
    if not state:
        print(json.dumps({"trip_id": args.trip_id, "status": "empty",
                          "note": "first run, no baseline stored"}, indent=2))
        return
    print(json.dumps(state, indent=2, ensure_ascii=False))


def cmd_save(args):
    if args.payload == "-":
        payload = json.load(sys.stdin)
    else:
        with open(args.payload, encoding="utf-8") as handle:
            payload = json.load(handle)

    lowest = payload.get("lowest")
    if not isinstance(lowest, dict) or "total" not in lowest:
        fail("payload needs a lowest object with a total")
    try:
        total = float(lowest["total"])
    except (TypeError, ValueError):
        fail("lowest.total must be a number")
    currency = lowest.get("currency", "")

    old = read_state(args.trip_id)
    previous = (old.get("lowest") or {}).get("total")

    prices = [total]
    for value in payload.get("prices_seen", []):
        try:
            prices.append(float(value))
        except (TypeError, ValueError):
            fail("every prices_seen entry must be a number")

    old_range = old.get("observed_range") or {}
    low = min(prices + ([old_range["min"]] if "min" in old_range else []))
    high = max(prices + ([old_range["max"]] if "max" in old_range else []))
    samples = int(old_range.get("samples", 0)) + len(prices)

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    history = list(old.get("history", []))
    history.append({"checked": now, "lowest": total, "currency": currency})
    history = history[-HISTORY_LIMIT:]

    state = {
        "trip_id": args.trip_id,
        "trip": payload.get("trip", old.get("trip", {})),
        "lowest": lowest,
        "options_seen": payload.get("options_seen", []),
        "observed_range": {"min": low, "max": high, "samples": samples, "currency": currency},
        "notes": payload.get("notes", ""),
        "last_check": now,
        "runs": int(old.get("runs", 0)) + 1,
        "history": history,
    }
    path = write_state(args.trip_id, state)

    print("STATE SAVED: lowest=%.2f %s, checked=%s" % (total, currency, now))
    print("file: %s  (run %d)" % (path, state["runs"]))

    if previous is None:
        print("VS BASELINE: no baseline, this is the first recorded run")
    else:
        previous = float(previous)
        delta = total - previous
        pct = (delta / previous * 100) if previous else 0.0
        word = "unchanged" if abs(delta) < 0.005 else ("down" if delta < 0 else "up")
        print("VS BASELINE: %s %.2f %s (%.1f%%), previous lowest %.2f %s"
              % (word, abs(delta), currency, abs(pct), previous, currency))

    print("OBSERVED RANGE: %.2f to %.2f %s over %d quoted prices" % (low, high, currency, samples))

    # The verdict compares today's lowest against the lowest of earlier runs, never
    # against the spread of dates inside one run. One run alone proves nothing.
    tracked = [float(entry["lowest"]) for entry in history]
    floor, ceiling = min(tracked), max(tracked)
    span = ceiling - floor
    print("TRACKED LOWEST: %.2f to %.2f %s over %d runs" % (floor, ceiling, currency, len(tracked)))
    if len(tracked) < 3 or span <= 0:
        print("SUGGESTED VERDICT: insufficient history, decide from the cited price-history sources")
        return
    position = (total - floor) / span
    if position <= DEAL_BAND:
        verdict = "DEAL, in the lowest %d%% of the tracked range" % int(DEAL_BAND * 100)
    elif position <= TYPICAL_BAND:
        verdict = "FAIR, inside the typical part of the tracked range"
    else:
        verdict = "WAIT, above the typical part of the tracked range"
    print("SUGGESTED VERDICT: %s (position %.0f%% of range)" % (verdict, position * 100))
    print("note: apply the trend override from Step 5 before printing the verdict")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_pairs = sub.add_parser("pairs", help="list every departure and return pair in the window")
    p_pairs.add_argument("--window", required=True, help="2026-09-05..2026-09-27")
    p_pairs.add_argument("--stay", required=True, help="10-12 or 11")
    p_pairs.set_defaults(func=cmd_pairs)

    p_load = sub.add_parser("load", help="print the stored baseline for a trip")
    p_load.add_argument("--trip-id", required=True)
    p_load.set_defaults(func=cmd_load)

    p_save = sub.add_parser("save", help="store the run and print delta, range and verdict")
    p_save.add_argument("--trip-id", required=True)
    p_save.add_argument("--payload", required=True, help="path to the run JSON, or - for stdin")
    p_save.set_defaults(func=cmd_save)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
