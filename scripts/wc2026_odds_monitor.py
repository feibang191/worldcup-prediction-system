#!/usr/bin/env python3
"""
世界杯2026赔率监控脚本
- 抓取Sporttery最新赔率
- 与上次数据对比，检测变化（>5%触发警报）
- 保存到JSON + SQLite + 历史存档
- 输出变化报告

用法：python3 wc2026_odds_monitor.py
"""

import json, os, sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path("./数据")
ODDS_FILE = BASE / "sporttery_official_odds.json"
ODDS_HISTORY = BASE / "odds_history"
DB_FILE = BASE / "football_database.sqlite"
CHANGE_LOG = BASE / "odds_changes.log"

os.makedirs(ODDS_HISTORY, exist_ok=True)


def load_previous():
    if ODDS_FILE.exists():
        try:
            data = json.loads(ODDS_FILE.read_text(encoding='utf-8-sig'))
            if isinstance(data, list):
                return {m['id']: m for m in data}
        except:
            pass
    return {}


def save_current(matches):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ODDS_FILE.write_text(json.dumps(matches, ensure_ascii=False, indent=2), encoding='utf-8')
    history_file = ODDS_HISTORY / f"odds_{ts}.json"
    history_file.write_text(json.dumps(matches, ensure_ascii=False, indent=2), encoding='utf-8')
    return ts


def detect_changes(old, new, threshold=0.05):
    changes = []
    for mid, new_m in new.items():
        if mid in old:
            old_m = old[mid]
            for i, key in enumerate(['H', 'D', 'A']):
                old_val = old_m['spf'][i] if i < len(old_m.get('spf', [])) else None
                new_val = new_m['spf'][i] if i < len(new_m.get('spf', [])) else None
                if old_val and new_val and abs(old_val - new_val) > threshold:
                    changes.append({
                        'match': f"{new_m['home']} vs {new_m['away']}",
                        'type': 'SPF', 'option': key,
                        'old': old_val, 'new': new_val,
                        'pct': (new_val - old_val) / old_val * 100,
                    })
            for i, key in enumerate(['H', 'D', 'A']):
                old_rq = old_m.get('rq', [])
                new_rq = new_m.get('rq', [])
                if i < len(old_rq) and i < len(new_rq) and old_rq[i] and new_rq[i]:
                    if abs(old_rq[i] - new_rq[i]) > threshold:
                        changes.append({
                            'match': f"{new_m['home']} vs {new_m['away']}",
                            'type': 'RQ', 'option': key,
                            'old': old_rq[i], 'new': new_rq[i],
                            'pct': (new_rq[i] - old_rq[i]) / old_rq[i] * 100,
                        })
        else:
            changes.append({
                'match': f"{new_m['home']} vs {new_m['away']}",
                'type': 'NEW', 'option': '',
                'old': 0, 'new': 0, 'pct': 0,
            })
    return changes


def save_to_sqlite(matches, ts):
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS odds_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id TEXT, snapshot_time TEXT,
        home TEXT, away TEXT, match_date TEXT, match_time TEXT,
        spf_h REAL, spf_d REAL, spf_a REAL,
        rq_h REAL, rq_d REAL, rq_a REAL,
        handicap TEXT, status TEXT
    )''')
    for m in matches:
        spf = m.get('spf', [None, None, None])
        rq = m.get('rq', [None, None, None])
        c.execute('''INSERT INTO odds_snapshots
            (match_id, snapshot_time, home, away, match_date, match_time,
             spf_h, spf_d, spf_a, rq_h, rq_d, rq_a, handicap, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (m['id'], ts, m['home'], m['away'], m['date'], m['time'],
             spf[0] if len(spf) > 0 else None, spf[1] if len(spf) > 1 else None,
             spf[2] if len(spf) > 2 else None, rq[0] if len(rq) > 0 else None,
             rq[1] if len(rq) > 1 else None, rq[2] if len(rq) > 2 else None,
             m.get('handicap', ''), m.get('status', '')))
    conn.commit()
    conn.close()


def main():
    print("═" * 60)
    print(f"  ⚽ 世界杯2026赔率监控 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)

    old = load_previous()
    print(f"\n  📊 上次数据：{len(old)}场比赛")

    if not ODDS_FILE.exists():
        print("  ❌ 未找到赔率数据文件")
        return

    current_data = json.loads(ODDS_FILE.read_text(encoding='utf-8-sig'))
    if not isinstance(current_data, list):
        print("  ❌ 数据格式错误")
        return

    new = {m['id']: m for m in current_data}
    print(f"  📊 当前数据：{len(new)}场比赛")

    changes = detect_changes(old, new)

    if changes:
        print(f"\n  🔔 检测到 {len(changes)} 项赔率变化：")
        print("  " + "─" * 55)
        for c in changes:
            if c['type'] == 'NEW':
                print(f"  🆕 {c['match']} - 新增比赛")
            else:
                arrow = "↑" if c['pct'] > 0 else "↓"
                print(f"  {arrow} {c['match']} | {c['type']}-{c['option']} | {c['old']:.2f} → {c['new']:.2f} ({c['pct']:+.1f}%)")

        with open(CHANGE_LOG, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n时间: {datetime.now().isoformat()}\n")
            for c in changes:
                if c['type'] != 'NEW':
                    f.write(f"  {c['match']} | {c['type']}-{c['option']} | {c['old']:.2f} → {c['new']:.2f} ({c['pct']:+.1f}%)\n")
    else:
        print("\n  ✅ 赔率无变化")

    ts = save_current(current_data)
    save_to_sqlite(current_data, ts)
    print(f"\n  💾 已保存到 SQLite + 历史文件 (snapshot: {ts})")

    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = [m for m in current_data if m['date'] >= today]
    if upcoming:
        print(f"\n  📅 即将开赛 ({len(upcoming)}场)：")
        for m in upcoming[:10]:
            spf = m.get('spf', [])
            rq = m.get('rq', [])
            spf_str = f"SPF:{spf[0]:.2f}/{spf[1]:.2f}/{spf[2]:.2f}" if len(spf) == 3 else "SPF:--"
            rq_str = f"RQ:{rq[0]:.2f}/{rq[1]:.2f}/{rq[2]:.2f}" if len(rq) == 3 else "RQ:--"
            print(f"  {m['date']} {m['time']} | {m['home']} vs {m['away']} | {spf_str} | {rq_str}")

    print("\n" + "═" * 60)


if __name__ == "__main__":
    main()
