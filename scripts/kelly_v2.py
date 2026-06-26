#!/usr/bin/env python3
"""
Kelly 投注策略 v2 — 使用 Dixon-Coles + Shin 隐含概率
"""
import json, os, sys

sys.path.insert(0, r"E:\MyBrain\WIKI\球赛专属\scripts")
from hybrid_model_v2 import *
from shin_implied_prob import ShinMethod

def kelly_fraction(prob, odds):
    """Kelly: f = (p*o - 1) / (o - 1)"""
    if prob * odds <= 1:
        return 0
    return (prob * odds - 1) / (odds - 1)

def load_dc_results():
    """加载 DC 修正版结果"""
    path = r"E:\MyBrain\WIKI\球赛专属\数据\hybrid_model_v2_dc_results.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_kelly_v2():
    print("=" * 100)
    print("  Kelly 投注策略 v2 — Dixon-Coles + Shin 隐含概率")
    print("=" * 100)
    
    results = load_dc_results()
    odds_data = load_official_odds()
    
    recommendations = []
    
    for r in results:
        match = r['match']
        evs = r.get('evs', [])
        
        best = None
        best_ev = -999
        
        for ev in evs:
            outcome, odds, prob, ev_val = ev['outcome'], ev['odds'], ev['prob'], ev['ev']
            
            if ev_val <= 0:
                continue
            
            # 使用模型概率计算 Kelly
            kelly = kelly_fraction(prob, odds)
            half_kelly = kelly * 0.5
            
            # 使用 Shin 方法计算公平赔率
            if outcome == '胜':
                h_odds, d_odds, a_odds = odds, 0, 0
            elif outcome == '平':
                h_odds, d_odds, a_odds = 0, odds, 0
            else:
                h_odds, d_odds, a_odds = 0, 0, odds
            
            # 找到原始赔率
            for o in odds_data:
                if o['home'] in match and o['away'] in match:
                    spf = o.get('spf', [1,1,1])
                    h_odds, d_odds, a_odds = spf[0], spf[1], spf[2]
                    break
            
            if h_odds > 0 and d_odds > 0 and a_odds > 0:
                shin = ShinMethod(h_odds, d_odds, a_odds)
                fair_h, fair_d, fair_a = shin.fair_probs
                margin = shin.margin * 100
                
                # 公平赔率下的 EV
                if outcome == '胜':
                    fair_odds = 1.0 / fair_h
                    ev_fair = prob * fair_odds - 1
                elif outcome == '平':
                    fair_odds = 1.0 / fair_d
                    ev_fair = prob * fair_odds - 1
                else:
                    fair_odds = 1.0 / fair_a
                    ev_fair = prob * fair_odds - 1
            else:
                fair_odds = odds
                ev_fair = ev_val
            
            if kelly > best_ev:
                best_ev = kelly
                best = {
                    'match': match,
                    'outcome': outcome,
                    'odds': odds,
                    'prob': prob,
                    'ev': ev_val,
                    'kelly': kelly,
                    'half_kelly': half_kelly,
                    'fair_odds': round(fair_odds, 2) if 'fair_odds' in dir() else 0,
                    'margin': round(margin, 1) if 'margin' in dir() else 0,
                }
        
        if best:
            recommendations.append(best)
    
    # 按 Kelly 排序
    recommendations.sort(key=lambda x: x['kelly'], reverse=True)
    
    # 输出结果
    print(f"\n{'#':<3} {'比赛':<30} {'推荐':<5} {'赔率':>5} {'概率':>7} {'EV%':>7} {'Kelly%':>7} {'½Kelly%':>8}")
    print("  " + "─" * 90)
    
    for i, rec in enumerate(recommendations[:15], 1):
        print(f"  {i:<3} {rec['match']:<30} {rec['outcome']:<5} {rec['odds']:>5.2f} {rec['prob']:>6.1%} {rec['ev']*100:>6.1f}% {rec['kelly']*100:>6.1f}% {rec['half_kelly']*100:>7.1f}%")
    
    print(f"\n  共 {len(recommendations)} 场正EV")
    
    # 预算方案
    print(f"\n{'='*100}")
    print("  预算方案 (½ Kelly)")
    print("="*100)
    
    for bankroll in [500, 1000, 2000]:
        print(f"\n  💰 总预算 {bankroll} 元:")
        total_stake = sum(rec['half_kelly'] * bankroll for rec in recommendations[:10])
        total_ev = sum(rec['prob'] * rec['odds'] * rec['half_kelly'] * bankroll for rec in recommendations[:10])
        profit = total_ev - total_stake
        
        print(f"    推荐注数: {min(10, len(recommendations))} 场")
        print(f"    总投入: {total_stake:.0f}元 ({total_stake/bankroll*100:.0f}%)")
        print(f"    总期望回报: {total_ev:.0f}元")
        print(f"    总期望盈利: +{profit:.0f}元 ({profit/total_stake*100:.1f}%)")

if __name__ == "__main__":
    run_kelly_v2()
