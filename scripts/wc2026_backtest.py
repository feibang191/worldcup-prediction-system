#!/usr/bin/env python3
"""
世界杯2026投注回测计算器
- 输入：比赛结果（比分或胜平负）
- 输出：投注方案的中奖情况+实际收益
- 支持：SPF/RQSPF/CRS/TTG/BQC + 串关/容错
"""

import json, sys, sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path("./数据")
DB_FILE = BASE / "football_database.sqlite"

# ═══════════════════════════════════════════════════════════
#  体彩竞彩计算规则
# ═══════════════════════════════════════════════════════════

class BettingCalculator:
    """竞彩足球投注计算器"""
    
    # 单注最高奖金
    MAX_SINGLE_PRIZE = 5_000_000
    # 单张彩票最高奖金
    MAX_TICKET_PRIZE = 5_000_000
    # 单注金额
    BET_UNIT = 2
    
    @staticmethod
    def calc_spf(home_goals, away_goals):
        """计算胜平负结果"""
        if home_goals > away_goals:
            return 'H'
        elif home_goals == away_goals:
            return 'D'
        else:
            return 'A'
    
    @staticmethod
    def calc_rqspf(home_goals, away_goals, handicap):
        """计算让球胜平负结果
        handicap: 负数=主队让球, 正数=客队让球
        例: -1 = 主队让1球
        """
        adjusted = home_goals + handicap - away_goals
        # 让球后：adjusted > 0 → 主胜(让球后), =0 → 平, <0 → 主负(让球后)
        # 但竞彩的"让球胜平负"是从主队角度：主队让球后赢=H
        diff = home_goals - away_goals + handicap
        if diff > 0:
            return 'H'  # 让球后主队胜
        elif diff == 0:
            return 'D'  # 让球后平
        else:
            return 'A'  # 让球后主队负
    
    @staticmethod
    def calc_crs(home_goals, away_goals):
        """计算比分结果"""
        if home_goals > away_goals:
            if home_goals >= 6 or away_goals >= 3:
                return '胜其它'
            return f"{home_goals}:{away_goals}"
        elif home_goals == away_goals:
            if home_goals >= 4:
                return '平其它'
            return f"{home_goals}:{away_goals}"
        else:
            if away_goals >= 6 or home_goals >= 3:
                return '负其它'
            return f"{home_goals}:{away_goals}"
    
    @staticmethod
    def calc_ttg(home_goals, away_goals):
        """计算总进球数"""
        total = home_goals + away_goals
        if total >= 7:
            return '7+'
        return str(total)
    
    @staticmethod
    def calc_bqc(home_goals_ht, away_goals_ht, home_goals_ft, away_goals_ft):
        """计算半全场结果
        上半场结果 + 全场结果
        """
        # 上半场
        if home_goals_ht > away_goals_ht:
            ht = '胜'
        elif home_goals_ht == away_goals_ht:
            ht = '平'
        else:
            ht = '负'
        # 全场
        if home_goals_ft > away_goals_ft:
            ft = '胜'
        elif home_goals_ft == away_goals_ft:
            ft = '平'
        else:
            ft = '负'
        return ht + ft
    
    @staticmethod
    def calc_single_payout(stake, odds):
        """计算单注奖金
        stake: 投注金额(元)
        odds: 赔率
        返回: 奖金(元)，已含本金
        """
        payout = stake * odds
        return min(payout, BettingCalculator.MAX_SINGLE_PRIZE)
    
    @staticmethod
    def calc_parlay_payout(stake, odds_list):
        """计算串关奖金
        stake: 每注投注金额(元)
        odds_list: 各场赔率列表
        返回: 奖金(元)
        """
        combined_odds = 1
        for o in odds_list:
            combined_odds *= o
        payout = stake * combined_odds
        return min(payout, BettingCalculator.MAX_SINGLE_PRIZE)
    
    @staticmethod
    def calc_mcn_n(bets, results, m):
        """计算M串N容错投注
        bets: [(name, odds), ...] 投注选项
        results: [True/False, ...] 是否中奖
        m: 串关数
        返回: (中奖注数, 总奖金)
        """
        from itertools import combinations
        n = len(bets)
        total_payout = 0
        winning_tickets = 0
        
        for combo in combinations(range(n), m):
            # 检查这个组合是否全对
            all_correct = all(results[i] for i in combo)
            if all_correct:
                odds_list = [bets[i][1] for i in combo]
                payout = BettingCalculator.calc_parlay_payout(2, odds_list)
                total_payout += payout
                winning_tickets += 1
        
        return winning_tickets, total_payout


# ═══════════════════════════════════════════════════════════
#  投注方案定义（200元方案）
# ═══════════════════════════════════════════════════════════

BETTING_PLAN = {
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
        # (名称, [(比赛, 玩法, 选项, 赔率), ...], 类型, 金额)
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
        # (名称, [(比赛, 玩法, 选项, 赔率), ...], 类型, 金额)
        ('墨西哥RQSPF+韩国RQSPF(容错)', [
            ('墨西哥vs南非', 'RQSPF', 'H', 2.00),
            ('韩国vs捷克', 'RQSPF', 'H', 5.90),
        ], '2串3', 6),
    ]
}


# ═══════════════════════════════════════════════════════════
#  回测计算
# ═══════════════════════════════════════════════════════════

def run_backtest(results):
    """
    results: {
        '墨西哥vs南非': {'home_goals': int, 'away_goals': int, 
                       'home_goals_ht': int, 'away_goals_ht': int,
                       'handicap': -1},
        '韩国vs捷克': {...}
    }
    """
    calc = BettingCalculator()
    
    # 计算每场比赛的各种结果
    match_results = {}
    for match, r in results.items():
        hg, ag = r['home_goals'], r['away_goals']
        hg_ht, ag_ht = r.get('home_goals_ht', hg//2), r.get('away_goals_ht', ag//2)
        handicap = r.get('handicap', -1)
        
        match_results[match] = {
            'SPF': calc.calc_spf(hg, ag),
            'RQSPF': calc.calc_rqspf(hg, ag, handicap),
            'CRS': calc.calc_crs(hg, ag),
            'TTG': calc.calc_ttg(hg, ag),
            'BQC': calc.calc_bqc(hg_ht, ag_ht, hg, ag),
            'score': f"{hg}:{ag}",
            'ht_score': f"{hg_ht}:{ag_ht}",
            'handicap': handicap,
        }
    
    # ── 计算单场投注 ──
    single_results = []
    total_single_cost = 0
    total_single_payout = 0
    
    for name, match, play_type, option, odds, stake in BETTING_PLAN['singles']:
        total_single_cost += stake
        mr = match_results[match]
        
        if play_type == 'RQSPF':
            actual = mr['RQSPF']
            is_win = (actual == option)
        elif play_type == 'BQC':
            actual = mr['BQC']
            # BQC选项映射：HH→胜胜, HD→胜平, HA→胜负, DH→平胜, DD→平平, DA→平负, AH→负胜, AD→负平, AA→负负
            bqc_map = {'HH':'胜胜','HD':'胜平','HA':'胜负','DH':'平胜','DD':'平平','DA':'平负','AH':'负胜','AD':'负平','AA':'负负'}
            expected = bqc_map.get(option, option)
            is_win = (actual == expected)
        elif play_type == 'SPF':
            actual = mr['SPF']
            is_win = (actual == option)
        elif play_type == 'CRS':
            actual = mr['CRS']
            is_win = (actual == option)
        elif play_type == 'TTG':
            actual = mr['TTG']
            is_win = (actual == option)
        else:
            actual = '?'
            is_win = False
        
        payout = calc.calc_single_payout(stake, odds) if is_win else 0
        total_single_payout += payout
        
        single_results.append({
            'name': name,
            'match': match,
            'play': play_type,
            'option': option,
            'odds': odds,
            'stake': stake,
            'actual': actual,
            'is_win': is_win,
            'payout': payout,
            'profit': payout - stake if is_win else -stake,
        })
    
    # ── 计算串关 ──
    parlay_results = []
    total_parlay_cost = 0
    total_parlay_payout = 0
    
    for name, legs, ptype, stake in BETTING_PLAN['parlays']:
        total_parlay_cost += stake
        all_correct = True
        odds_list = []
        
        for match, play_type, option, odds in legs:
            mr = match_results[match]
            if play_type == 'RQSPF':
                actual = mr['RQSPF']
            elif play_type == 'BQC':
                actual = mr['BQC']
                bqc_map = {'HH':'胜胜','HD':'胜平','HA':'胜负','DH':'平胜','DD':'平平','DA':'平负','AH':'负胜','AD':'负平','AA':'负负'}
                option = bqc_map.get(option, option)
            else:
                actual = mr.get(play_type, '?')
            
            if actual != option:
                all_correct = False
            odds_list.append(odds)
        
        if all_correct:
            payout = calc.calc_parlay_payout(stake, odds_list)
        else:
            payout = 0
        
        total_parlay_payout += payout
        
        parlay_results.append({
            'name': name,
            'legs': legs,
            'type': ptype,
            'stake': stake,
            'is_win': all_correct,
            'payout': payout,
            'profit': payout - stake if all_correct else -stake,
            'combined_odds': 1,
        })
        if all_correct:
            parlay_results[-1]['combined_odds'] = stake and payout / stake or 0
    
    # ── 计算容错 ──
    tolerance_results = []
    total_tolerance_cost = 0
    total_tolerance_payout = 0
    
    for name, legs, ttype, stake in BETTING_PLAN['tolerance']:
        total_tolerance_cost += stake
        
        bets = []
        results_list = []
        for match, play_type, option, odds in legs:
            mr = match_results[match]
            if play_type == 'RQSPF':
                actual = mr['RQSPF']
            elif play_type == 'BQC':
                actual = mr['BQC']
                bqc_map = {'HH':'胜胜','HD':'胜平','HA':'胜负','DH':'平胜','DD':'平平','DA':'平负','AH':'负胜','AD':'负平','AA':'负负'}
                option = bqc_map.get(option, option)
            else:
                actual = mr.get(play_type, '?')
            
            bets.append((f"{match}-{play_type}-{option}", odds))
            results_list.append(actual == option)
        
        m = int(ttype.split('串')[1]) if '串' in ttype else 2
        # 2串3 = C(2,2) + C(2,1)*2 = 1 + 2*2 = 不对
        # 2串3 = 所有2场组合 + 所有1场组合 = 1个2串1 + 2个单关 = 3注
        # 实际上2串3就是3注
        from itertools import combinations
        
        # 计算所有组合
        n = len(bets)
        total_winning = 0
        total_payout = 0
        
        # 单关（1串1）
        for i in range(n):
            if results_list[i]:
                payout = calc.calc_single_payout(2, bets[i][1])
                total_payout += payout
                total_winning += 1
        
        # 2串1
        for combo in combinations(range(n), 2):
            if all(results_list[i] for i in combo):
                odds_list = [bets[i][1] for i in combo]
                payout = calc.calc_parlay_payout(2, odds_list)
                total_payout += payout
                total_winning += 1
        
        total_tolerance_payout += total_payout
        
        tolerance_results.append({
            'name': name,
            'legs': legs,
            'type': ttype,
            'stake': stake,
            'winning_tickets': total_winning,
            'payout': total_payout,
            'profit': total_payout - stake,
        })
    
    # ── 汇总 ──
    total_cost = total_single_cost + total_parlay_cost + total_tolerance_cost
    total_payout = total_single_payout + total_parlay_payout + total_tolerance_payout
    total_profit = total_payout - total_cost
    roi = total_profit / total_cost * 100 if total_cost > 0 else 0
    
    return {
        'match_results': match_results,
        'single_results': single_results,
        'parlay_results': parlay_results,
        'tolerance_results': tolerance_results,
        'total_cost': total_cost,
        'total_payout': total_payout,
        'total_profit': total_profit,
        'roi': roi,
        'total_single_cost': total_single_cost,
        'total_single_payout': total_single_payout,
        'total_parlay_cost': total_parlay_cost,
        'total_parlay_payout': total_parlay_payout,
        'total_tolerance_cost': total_tolerance_cost,
        'total_tolerance_payout': total_tolerance_payout,
    }


# ═══════════════════════════════════════════════════════════
#  报告输出
# ═══════════════════════════════════════════════════════════

def generate_report(result):
    """生成标准格式报告"""
    mr = result['match_results']
    
    lines = []
    lines.append("═" * 72)
    lines.append("  ⚽ 投注回测报告 | " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    lines.append("═" * 72)
    
    # 比赛结果
    lines.append("")
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
    
    # 串关投注
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
    
    # 容错投注
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


# ═══════════════════════════════════════════════════════════
#  主函数
# ═══════════════════════════════════════════════════════════

def main():
    """主函数 - 支持命令行输入比分或从JSON读取"""
    
    # 示例：墨西哥2:1南非，韩国1:1捷克
    if len(sys.argv) >= 5:
        # python3 backtest.py 墨西哥 2 1 南非 韩国 1 1 捷克
        results = {
            '墨西哥vs南非': {
                'home_goals': int(sys.argv[2]),
                'away_goals': int(sys.argv[4]),
                'handicap': -1,
            },
            '韩国vs捷克': {
                'home_goals': int(sys.argv[6]),
                'away_goals': int(sys.argv[8]),
                'handicap': -1,
            }
        }
    else:
        # 默认示例比分
        results = {
            '墨西哥vs南非': {
                'home_goals': 2,
                'away_goals': 1,
                'home_goals_ht': 1,
                'away_goals_ht': 0,
                'handicap': -1,
            },
            '韩国vs捷克': {
                'home_goals': 1,
                'away_goals': 1,
                'home_goals_ht': 0,
                'away_goals_ht': 0,
                'handicap': -1,
            }
        }
        print("  ⚠️ 使用示例比分，实际使用请传入：")
        print("  python3 backtest.py 墨西哥 2 1 南非 韩国 1 1 捷克")
        print()
    
    result = run_backtest(results)
    report = generate_report(result)
    print(report)
    
    # 保存报告
    report_file = BASE / "backtest_latest.txt"
    report_file.write_text(report, encoding='utf-8')
    print(f"  💾 报告已保存：{report_file}")


if __name__ == "__main__":
    main()
