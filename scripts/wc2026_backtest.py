#!/usr/bin/env python3
"""
世界杯2026投注回测计算器
- 输入：比赛结果（比分）
- 输出：投注方案的中奖情况+实际收益
- 支持：SPF/RQSPF/CRS/TTG/BQC + 串关/容错

用法：
  python3 wc2026_backtest.py 墨西哥 2 1 南非 韩国 1 1 捷克
  python3 wc2026_backtest.py  # 使用示例比分
"""

import json, sys, sqlite3
from datetime import datetime
from pathlib import Path
from itertools import combinations

BASE = Path("./数据")

# ═══════════════════════════════════════════════════════════
#  体彩竞彩计算规则
# ═══════════════════════════════════════════════════════════

# BQC中英文映射（关键：赔率用英文，比赛结果返回中文）
BQC_MAP = {
    'HH': '胜胜', 'HD': '胜平', 'HA': '胜负',
    'DH': '平胜', 'DD': '平平', 'DA': '平负',
    'AH': '负胜', 'AD': '负平', 'AA': '负负'
}
BQC_MAP_REVERSE = {v: k for k, v in BQC_MAP.items()}


def calc_spf(home_goals, away_goals):
    if home_goals > away_goals: return 'H'
    elif home_goals == away_goals: return 'D'
    else: return 'A'


def calc_rqspf(home_goals, away_goals, handicap=-1):
    diff = home_goals - away_goals + handicap
    if diff > 0: return 'H'
    elif diff == 0: return 'D'
    else: return 'A'


def calc_crs(home_goals, away_goals):
    if home_goals > away_goals:
        if home_goals >= 6 or away_goals >= 3: return '胜其它'
        return f"{home_goals}:{away_goals}"
    elif home_goals == away_goals:
        if home_goals >= 4: return '平其它'
        return f"{home_goals}:{away_goals}"
    else:
        if away_goals >= 6 or home_goals >= 3: return '负其它'
        return f"{home_goals}:{away_goals}"


def calc_ttg(home_goals, away_goals):
    total = home_goals + away_goals
    return '7+' if total >= 7 else str(total)


def calc_bqc(home_goals_ht, away_goals_ht, home_goals_ft, away_goals_ft):
    ht = '胜' if home_goals_ht > away_goals_ht else ('平' if home_goals_ht == away_goals_ht else '负')
    ft = '胜' if home_goals_ft > away_goals_ft else ('平' if home_goals_ft == away_goals_ft else '负')
    return ht + ft


def match_bet(bet_option, actual_result, play_type):
    """判断投注是否中奖，处理BQC中英文映射"""
    if play_type == 'BQC':
        expected = BQC_MAP.get(bet_option, bet_option)
        return actual_result == expected
    return bet_option == actual_result


# ═══════════════════════════════════════════════════════════
#  投注方案定义（默认200元方案，可自定义）
# ═══════════════════════════════════════════════════════════

DEFAULT_BETTING_PLAN = {
    'total_budget': 200,
    'singles': [
        # (名称, 比赛, 玩法, 选项, 赔率, 金额)
        ('墨西哥RQSPF让1胜', '墨西哥vs南非', 'RQSPF', 'H', 2.00, 44),
        ('墨西哥BQC胜胜', '墨西哥vs南非', 'BQC', 'HH', 3.00, 53),
        ('韩国RQSPF让1胜', '韩国vs捷克', 'RQSPF', 'H', 5.90, 18),
        ('韩国BQC胜胜', '韩国vs捷克', 'BQC', 'HH', 3.80, 36),
        ('韩国RQSPF让1平', '韩国vs捷克', 'RQSPF', 'D', 4.00, 40),
        ('韩国BQC负平', '韩国vs捷克', 'BQC', 'AD', 11.00, 10),
    ],
    'parlays': [
        ('墨西哥RQSPF让1胜×韩国RQSPF让1胜', [
            ('墨西哥vs南非', 'RQSPF', 'H', 2.00),
            ('韩国vs捷克', 'RQSPF', 'H', 5.90),
        ], '2串1', 2),
        ('墨西哥BQC胜胜×韩国BQC胜胜', [
            ('墨西哥vs南非', 'BQC', 'HH', 3.00),
            ('韩国vs捷克', 'BQC', 'HH', 3.80),
        ], '2串1', 2),
        ('墨西哥RQSPF×韩国BQC(混合)', [
            ('墨西哥vs南非', 'RQSPF', 'H', 2.00),
            ('韩国vs捷克', 'BQC', 'HH', 3.80),
        ], '2串1', 2),
        ('墨西哥BQC×韩国RQSPF(混合)', [
            ('墨西哥vs南非', 'BQC', 'HH', 3.00),
            ('韩国vs捷克', 'RQSPF', 'H', 5.90),
        ], '2串1', 2),
    ],
    'tolerance': [
        ('墨西哥RQSPF+韩国RQSPF(容错)', [
            ('墨西哥vs南非', 'RQSPF', 'H', 2.00),
            ('韩国vs捷克', 'RQSPF', 'H', 5.90),
        ], '2串3', 6),
    ]
}


# ═══════════════════════════════════════════════════════════
#  回测计算
# ═══════════════════════════════════════════════════════════

def run_backtest(results, plan=None):
    if plan is None:
        plan = DEFAULT_BETTING_PLAN

    # 计算每场比赛的各种结果
    match_results = {}
    for match, r in results.items():
        hg, ag = r['home_goals'], r['away_goals']
        hg_ht = r.get('home_goals_ht', hg // 2)
        ag_ht = r.get('away_goals_ht', ag // 2)
        handicap = r.get('handicap', -1)

        match_results[match] = {
            'SPF': calc_spf(hg, ag),
            'RQSPF': calc_rqspf(hg, ag, handicap),
            'CRS': calc_crs(hg, ag),
            'TTG': calc_ttg(hg, ag),
            'BQC': calc_bqc(hg_ht, ag_ht, hg, ag),
            'score': f"{hg}:{ag}",
            'ht_score': f"{hg_ht}:{ag_ht}",
            'handicap': handicap,
        }

    # ── 单场投注 ──
    single_results = []
    total_single_cost = total_single_payout = 0

    for name, match, play_type, option, odds, stake in plan['singles']:
        total_single_cost += stake
        mr = match_results[match]
        actual = mr[play_type]
        is_win = match_bet(option, actual, play_type)
        payout = min(stake * odds, 5_000_000) if is_win else 0
        total_single_payout += payout
        single_results.append({
            'name': name, 'match': match, 'play': play_type,
            'option': option, 'odds': odds, 'stake': stake,
            'actual': actual, 'is_win': is_win, 'payout': payout,
            'profit': payout - stake if is_win else -stake,
        })

    # ── 串关 ──
    parlay_results = []
    total_parlay_cost = total_parlay_payout = 0

    for name, legs, ptype, stake in plan['parlays']:
        total_parlay_cost += stake
        all_correct = True
        odds_list = []
        for match, play_type, option, odds in legs:
            actual = match_results[match][play_type]
            if not match_bet(option, actual, play_type):
                all_correct = False
            odds_list.append(odds)

        payout = min(stake * (odds_list[0] * odds_list[1]), 5_000_000) if all_correct else 0
        total_parlay_payout += payout
        parlay_results.append({
            'name': name, 'type': ptype, 'stake': stake,
            'is_win': all_correct, 'payout': payout,
            'profit': payout - stake if all_correct else -stake,
        })

    # ── 容错 ──
    tolerance_results = []
    total_tolerance_cost = total_tolerance_payout = 0

    for name, legs, ttype, stake in plan['tolerance']:
        total_tolerance_cost += stake
        bets, results_list = [], []
        for match, play_type, option, odds in legs:
            actual = match_results[match][play_type]
            bets.append((f"{match}-{play_type}-{option}", odds))
            results_list.append(match_bet(option, actual, play_type))

        n = len(bets)
        winning = payout_total = 0

        # 单关
        for i in range(n):
            if results_list[i]:
                payout_total += min(2 * bets[i][1], 5_000_000)
                winning += 1

        # 2串1
        for combo in combinations(range(n), 2):
            if all(results_list[i] for i in combo):
                combined = bets[combo[0]][1] * bets[combo[1]][1]
                payout_total += min(2 * combined, 5_000_000)
                winning += 1

        total_tolerance_payout += payout_total
        tolerance_results.append({
            'name': name, 'type': ttype, 'stake': stake,
            'winning_tickets': winning, 'payout': payout_total,
            'profit': payout_total - stake,
        })

    total_cost = total_single_cost + total_parlay_cost + total_tolerance_cost
    total_payout = total_single_payout + total_parlay_payout + total_tolerance_payout

    return {
        'match_results': match_results,
        'single_results': single_results,
        'parlay_results': parlay_results,
        'tolerance_results': tolerance_results,
        'total_cost': total_cost, 'total_payout': total_payout,
        'total_profit': total_payout - total_cost,
        'roi': (total_payout - total_cost) / total_cost * 100 if total_cost > 0 else 0,
        'total_single_cost': total_single_cost,
        'total_single_payout': total_single_payout,
        'total_parlay_cost': total_parlay_cost,
        'total_parlay_payout': total_parlay_payout,
        'total_tolerance_cost': total_tolerance_cost,
        'total_tolerance_payout': total_tolerance_payout,
    }


def generate_report(result):
    """生成标准排版报告（═══/┌─┐/│格式）"""
    mr = result['match_results']
    lines = []
    lines.append("═" * 72)
    lines.append("  ⚽ 投注回测报告 | " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    lines.append("═" * 72)
    lines.append("")

    # 比赛结果
    lines.append("  比赛结果")
    lines.append("  " + "─" * 60)
    for match, r in mr.items():
        lines.append(f"  {match}  {r['score']} (半场{r['ht_score']})")
        lines.append(f"    SPF:{r['SPF']} | RQSPF:{r['RQSPF']} | CRS:{r['CRS']} | TTG:{r['TTG']} | BQC:{r['BQC']}")
    lines.append("")

    # 单场投注
    lines.append("  " + "─" * 60)
    lines.append("  一、单场投注")
    lines.append("  " + "─" * 60)
    lines.append(f"  {'#':<3} {'投注选项':<18} {'玩法':<6} {'选项':<6} {'赔率':>6} {'金额':>6} {'实际':>6} {'结果':>4} {'奖金':>8}")
    lines.append("  " + "─" * 60)
    for i, sr in enumerate(result['single_results'], 1):
        status = "✅" if sr['is_win'] else "❌"
        payout_str = f"{sr['payout']:.0f}元" if sr['is_win'] else "0元"
        lines.append(f"  {i:<3} {sr['name']:<18} {sr['play']:<6} {sr['option']:<6} {sr['odds']:>6.2f} {sr['stake']:>5}元 {sr['actual']:>6} {status:>4} {payout_str:>8}")
    lines.append("  " + "─" * 60)
    lines.append(f"  小计：投入{result['total_single_cost']}元 | 奖金{result['total_single_payout']:.0f}元 | 盈亏{result['total_single_payout']-result['total_single_cost']:+.0f}元")
    lines.append("")

    # 串关
    lines.append("  " + "─" * 60)
    lines.append("  二、串关投注")
    lines.append("  " + "─" * 60)
    lines.append(f"  {'#':<3} {'串关组合':<35} {'类型':<6} {'金额':>6} {'结果':>4} {'奖金':>8}")
    lines.append("  " + "─" * 60)
    for i, pr in enumerate(result['parlay_results'], 1):
        status = "✅" if pr['is_win'] else "❌"
        payout_str = f"{pr['payout']:.0f}元" if pr['is_win'] else "0元"
        lines.append(f"  {i:<3} {pr['name']:<35} {pr['type']:<6} {pr['stake']:>5}元 {status:>4} {payout_str:>8}")
    lines.append("  " + "─" * 60)
    lines.append(f"  小计：投入{result['total_parlay_cost']}元 | 奖金{result['total_parlay_payout']:.0f}元 | 盈亏{result['total_parlay_payout']-result['total_parlay_cost']:+.0f}元")
    lines.append("")

    # 容错
    lines.append("  " + "─" * 60)
    lines.append("  三、容错投注")
    lines.append("  " + "─" * 60)
    lines.append(f"  {'#':<3} {'容错组合':<35} {'类型':<6} {'金额':>6} {'中奖':>4} {'奖金':>8}")
    lines.append("  " + "─" * 60)
    for i, tr in enumerate(result['tolerance_results'], 1):
        lines.append(f"  {i:<3} {tr['name']:<35} {tr['type']:<6} {tr['stake']:>5}元 {tr['winning_tickets']:>3}注 {tr['payout']:>7.0f}元")
    lines.append("  " + "─" * 60)
    lines.append(f"  小计：投入{result['total_tolerance_cost']}元 | 奖金{result['total_tolerance_payout']:.0f}元 | 盈亏{result['total_tolerance_payout']-result['total_tolerance_cost']:+.0f}元")
    lines.append("")

    # 总账
    lines.append("═" * 72)
    lines.append("  总账")
    lines.append("═" * 72)
    lines.append(f"  {'类别':<20} {'投入':>8} {'奖金':>8} {'盈亏':>8}")
    lines.append("  " + "─" * 60)
    lines.append(f"  {'单场投注':<20} {result['total_single_cost']:>7}元 {result['total_single_payout']:>7.0f}元 {result['total_single_payout']-result['total_single_cost']:>+7.0f}元")
    lines.append(f"  {'串关投注':<20} {result['total_parlay_cost']:>7}元 {result['total_parlay_payout']:>7.0f}元 {result['total_parlay_payout']-result['total_parlay_cost']:>+7.0f}元")
    lines.append(f"  {'容错投注':<20} {result['total_tolerance_cost']:>7}元 {result['total_tolerance_payout']:>7.0f}元 {result['total_tolerance_payout']-result['total_tolerance_cost']:>+7.0f}元")
    lines.append("  " + "─" * 60)
    lines.append(f"  {'合计':<20} {result['total_cost']:>7}元 {result['total_payout']:>7.0f}元 {result['total_profit']:>+7.0f}元")
    lines.append("")
    lines.append(f"  ROI：{result['roi']:+.1f}%")
    lines.append("")
    lines.append("═" * 72)
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) >= 9:
        results = {
            sys.argv[1]+'vs'+sys.argv[3]: {
                'home_goals': int(sys.argv[2]), 'away_goals': int(sys.argv[4]), 'handicap': -1
            },
            sys.argv[5]+'vs'+sys.argv[7]: {
                'home_goals': int(sys.argv[6]), 'away_goals': int(sys.argv[8]), 'handicap': -1
            }
        }
    else:
        results = {
            '墨西哥vs南非': {'home_goals': 2, 'away_goals': 1, 'home_goals_ht': 1, 'away_goals_ht': 0, 'handicap': -1},
            '韩国vs捷克': {'home_goals': 1, 'away_goals': 1, 'home_goals_ht': 0, 'away_goals_ht': 0, 'handicap': -1}
        }
        print("  ⚠️ 使用示例比分，实际用法：python3 wc2026_backtest.py 墨西哥 2 1 南非 韩国 1 1 捷克\n")

    result = run_backtest(results)
    print(generate_report(result))
