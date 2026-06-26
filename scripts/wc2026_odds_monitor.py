#!/usr/bin/env python3
"""World Cup 2026 Odds Monitor."""

import json
import sys
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/mnt/e/MyBrain/WIKI/球赛专属/数据")
DATA_FILE = DATA_DIR / "sporttery_official_odds.json"
SNAPSHOT_DIR = DATA_DIR / "monitor" / "snapshots"
THRESHOLD = 0.05

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def latest_snapshot():
    if not SNAPSHOT_DIR.exists():
        return None
    snaps = sorted(SNAPSHOT_DIR.glob("odds_*.json"))
    if not snaps:
        return None
    raw = load(snaps[-1])
    # Handle wrapper format {'matches': [...], 'fetch_time': ...}
    if isinstance(raw, dict) and "matches" in raw:
        return raw["matches"]
    return raw

def compare(curr, prev):
    changes = []
    cm = {(m["home"], m["away"]): m for m in curr}
    pm = {(m["home"], m["away"]): m for m in prev} if prev else {}
    
    for key, m in cm.items():
        if key not in pm:
            changes.append(("new", m, []))
            continue
        mc = []
        spf_c = m.get("spf") or []
        spf_p = pm[key].get("spf") or []
        for i, lab in enumerate(["主胜", "平局", "客胜"]):
            cv = spf_c[i] if i < len(spf_c) else 0
            pv = spf_p[i] if i < len(spf_p) else 0
            if pv and pv > 0:
                pc = abs(cv - pv) / pv
                if pc > THRESHOLD:
                    mc.append(("spf", lab, pv, cv, pc*100, "up" if cv > pv else "down"))
        rq_c = m.get("rq") or []
        rq_p = pm[key].get("rq") or []
        for i, lab in enumerate(["让胜", "让平", "让负"]):
            cv = rq_c[i] if i < len(rq_c) else 0
            pv = rq_p[i] if i < len(rq_p) else 0
            if pv and pv > 0:
                pc = abs(cv - pv) / pv
                if pc > THRESHOLD:
                    mc.append(("rq", lab, pv, cv, pc*100, "up" if cv > pv else "down"))
        if mc:
            changes.append(("changed", m, mc))
    return changes

def main():
    print("=" * 60)
    print("WC2026 Odds Monitor")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    if not DATA_FILE.exists():
        print(f"Not found: {DATA_FILE}")
        sys.exit(1)
    
    curr = load(DATA_FILE)
    print(f"Loaded {len(curr)} matches")
    
    prev = latest_snapshot()
    print(f"Historical baseline: {'found' if prev else 'none'}")
    
    ch = compare(curr, prev)
    
    if ch:
        print(f"\nChanges found: {len(ch)} matches\n")
        for typ, m, details in ch:
            tid = m.get("id","?")
            teams = f"{m['home']} vs {m['away']}"
            if typ == "new":
                print(f"  NEW: {tid} {teams} ({m['date']} {m['time']})")
                if m.get("spf"): print(f"     SPF: {m['spf']}")
                if m.get("rq"): print(f"     RQ: {m['rq']}")
            else:
                print(f"  CHANGED: {tid} {teams} ({m['date']} {m['time']})")
                for field, lab, pv, cv, pct, dr in details:
                    arrow = "UP" if dr == "up" else "DOWN"
                    print(f"     {field.upper()}-{lab}: {pv:.2f}->{cv:.2f} ({arrow}{pct:.1f}%)")
    else:
        print("\nNo significant changes. Odds stable.")
    
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sf = SNAPSHOT_DIR / f"odds_{ts}.json"
    save(curr, sf)
    print(f"\nSnapshot saved: {sf}")
    
    nc = sum(1 for t,_,_ in ch if t=="changed")
    nn = sum(1 for t,_,_ in ch if t=="new")
    tc = sum(len(d) for _,_,d in ch if _=="changed")
    print(f"Summary: {nc} changed, {nn} new, {tc} individual changes")
    print("=" * 60)

if __name__ == "__main__":
    main()
