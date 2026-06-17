#!/usr/bin/env python3
'''盘口异动检测引擎 v1.0
参考Football-2026的oddsMovement逻辑
检测：亚盘水位变化 ≥ 0.06 触发信号 + 盘口变化
'''
import sqlite3, statistics
from collections import defaultdict

DB_PATH = r'.\football_database.sqlite'

def parse_water(water_str):
    '''解析水位值(带箭头)，返回数值和方向'''
    if not water_str: return None, None
    clean = water_str.replace('↑','').replace('↓','').strip()
    direction = 'up' if '↑' in water_str else ('down' if '↓' in water_str else 'stable')
    try:
        return float(clean), direction
    except:
        return None, None

HANDICAP_MAP = {
    '平手': 0.0, '平手/半球': 0.25, '半球': 0.5, '半球/一球': 0.75,
    '一球': 1.0, '一球/球半': 1.25, '球半': 1.5, '球半/两球': 1.75,
    '两球': 2.0, '两球/两球半': 2.25, '两球半': 2.5, '两球半/三球': 2.75,
    '三球': 3.0
}

def parse_handicap(hc_str):
    if not hc_str: return None
    sign = -1 if '受' in hc_str else 1
    hc = hc_str.replace('受','').replace('降','').replace('升','').strip()
    for cn, val in HANDICAP_MAP.items():
        if cn in hc: return sign * val
    return None

def analyze_odds_movement(match_key, asian_odds_rows):
    '''分析单场比赛的盘口异动，返回信号列表'''
    signals = []
    if not asian_odds_rows: return signals
    
    # 找出水位方向
    for r in asian_odds_rows:
        w_home, dir_home = parse_water(r.get('water_home',''))
        w_away, dir_away = parse_water(r.get('water_away',''))
        
        if not w_home or not w_away:
            continue
        
        if dir_home == 'up' and dir_away == 'down' and abs(w_home - w_away) > 0.06:
            signals.append({
                'company': r.get('company',''),
                'market': '亚盘',
                'signal': f"主水↑客水↓ (主{w_home}→客{w_away})",
                'strength': '强' if abs(w_home - w_away) >= 0.12 else '中',
                'msg': f"资金流向客队 ({r.get('company','')})",
                'impact': '利客'
            })
        elif dir_home == 'down' and dir_away == 'up' and abs(w_home - w_away) > 0.06:
            signals.append({
                'company': r.get('company',''),
                'market': '亚盘',
                'signal': f"主水↓客↑ (主{w_home}→客{w_away})",
                'strength': '强' if abs(w_home - w_away) >= 0.12 else '中',
                'msg': f"资金流向主队 ({r.get('company','')})",
                'impact': '利主'
            })
    
    return signals

def get_unified_movement_report():
    '''全局盘口异动报告'''
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT match_name FROM asian_odds")
    match_names = [r['match_name'] for r in cur.fetchall()]
    
    report = {'matches': [], 'total_signals': 0}
    
    for mk in match_names:
        cur.execute("SELECT * FROM asian_odds WHERE match_name = ? ORDER BY id", (mk,))
        rows = [dict(r) for r in cur.fetchall()]
        
        # 分析水位方向
        water_dirs = {}
        for r in rows:
            wh, dh = parse_water(r.get('water_home',''))
            wa, da = parse_water(r.get('water_away',''))
            hc = parse_handicap(r.get('handicap',''))
            if wh is not None:
                if 'up' not in water_dirs: water_dirs['up_home'] = 0
                if 'down' not in water_dirs: water_dirs['down_home'] = 0
                if dh == 'up': water_dirs['up_home'] = water_dirs.get('up_home', 0) + 1
                elif dh == 'down': water_dirs['down_home'] = water_dirs.get('down_home', 0) + 1
        
        signals = analyze_odds_movement(mk, rows)
        
        match_info = {
            'match': mk,
            'water_movement': water_dirs,
            'signals': signals,
            'signal_count': len(signals),
            'net_flow': (water_dirs.get('up_home',0) - water_dirs.get('down_home',0))
        }
        report['matches'].append(match_info)
        report['total_signals'] += len(signals)
    
    conn.close()
    return report
