#!/usr/bin/env python3
"""多公司赔率聚合引擎 v1.0
整合竞彩官方(500.com/Sporttery) + 17家博彩公司亚盘数据
输出：去水概率、亚盘共识、盘口矛盾检测
"""
import statistics, sqlite3
from collections import defaultdict

HANDICAP_MAP = {
    '平手': 0.0, '平手/半球': 0.25, '半球': 0.5, '半球/一球': 0.75,
    '一球': 1.0, '一球/球半': 1.25, '球半': 1.5, '球半/两球': 1.75,
    '两球': 2.0, '两球/两球半': 2.25, '两球半': 2.5, '两球半/三球': 2.75,
    '三球': 3.0
}

def parse_handicap(hc_str):
    """简体中文盘口转数值，负值=客让"""
    if not hc_str:
        return 0
    sign = -1 if '受' in hc_str else 1
    hc = hc_str.replace('受', '').replace('降', '').replace('升', '').strip()
    for cn, val in HANDICAP_MAP.items():
        if cn in hc:
            return sign * val
    return None

def de_margin(odds):
    """赔率去水: p_i = (1/o_i) / sum(1/o_j)"""
    imp = [1 / v for v in odds if v and v > 1]
    total = sum(imp)
    if total <= 0:
        return None
    keys = ['win', 'draw', 'loss']
    return {
        'probs': {k: v / total for k, v in zip(keys, imp)},
        'overround': total
    }

def asian_aggregate(odds_rows):
    """多公司亚盘聚合: 均值/标准差/公司数"""
    waters_h, waters_a, hcs = [], [], []
    for r in odds_rows:
        try:
            wh = float(r.get('water_home', '0').rstrip('\u2191\u2193').strip())
            wa = float(r.get('water_away', '0').rstrip('\u2191\u2193').strip())
            waters_h.append(wh)
            waters_a.append(wa)
            hc = parse_handicap(r.get('handicap', ''))
            if hc is not None:
                hcs.append(hc)
        except (ValueError, TypeError):
            pass
    if not waters_h:
        return None
    return {
        'water_h_mean': round(statistics.mean(waters_h), 3),
        'water_a_mean': round(statistics.mean(waters_a), 3),
        'water_h_std': round(statistics.stdev(waters_h), 3) if len(waters_h) > 1 else 0,
        'handicap_mean': round(statistics.mean(hcs), 3) if hcs else None,
        'bookmaker_count': len(waters_h)
    }

def detect_conflict(sporttery_probs, asian_consensus, home, away):
    """检测竞彩vs亚盘方向矛盾"""
    if not sporttery_probs or not asian_consensus:
        return None
    sp = sporttery_probs
    hm = asian_consensus.get('handicap_mean')
    if hm is None:
        return None
    if hm < -1 and sp.get('win', 0) > sp.get('loss', 0):
        return {
            'level': '矛盾',
            'msg': f"竞彩{home}偏优(sp={sp['win']:.0%})，但亚盘受{abs(hm):.1f}球极度支持{away} — 方向矛盾"
        }
    if hm > 1 and sp.get('loss', 0) > sp.get('win', 0):
        return {
            'level': '矛盾',
            'msg': f"竞彩{away}偏优(sp={sp['loss']:.0%})，但亚盘让{hm:.1f}球极度支持{home} — 方向矛盾"
        }
    return {'level': '一致', 'msg': f"方向一致，亚盘盘口{hm:.1f}与竞彩方向同步"}