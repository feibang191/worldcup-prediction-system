#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界杯竞彩投注质量门

1. 拆分理论最高奖金 / 数学期望 / 实际结算。
2. 用 Poisson 比分矩阵计算胜平负、让球胜平负概率。
3. 重算每张票的命中概率、理论最高奖金、数学期望、EV。
4. 输出修正版归档与 Markdown 自检报告。

注意：本脚本不抓实时赔率。实时赔率必须由 500.com / 网易彩票 / SPdex 页面核验后写入归档。
"""

from __future__ import annotations

import argparse
import json
import math
import os
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple

OUTCOME_MAP = {
    "主胜(H)": "H", "平局(D)": "D", "客胜(A)": "A",
    "主胜": "H", "平局": "D", "客胜": "A",
    "H": "H", "D": "D", "A": "A",
}


def poisson_pmf(lam: float, max_goals: int) -> List[float]:
    probs = [math.exp(-lam)]
    for goal in range(1, max_goals + 1):
        probs.append(probs[-1] * lam / goal)
    total = sum(probs)
    return [p / total for p in probs]


def score_matrix(home_lambda: float, away_lambda: float, max_goals: int = 8) -> Dict[Tuple[int, int], float]:
    home_probs = poisson_pmf(max(home_lambda, 0.05), max_goals)
    away_probs = poisson_pmf(max(away_lambda, 0.05), max_goals)
    return {(h, a): hp * ap for h, hp in enumerate(home_probs) for a, ap in enumerate(away_probs)}


def outcome_from_score(home_goals: int, away_goals: int, handicap: float = 0) -> str:
    adjusted_home = home_goals + handicap
    if adjusted_home > away_goals:
        return "H"
    if adjusted_home == away_goals:
        return "D"
    return "A"


def outcome_probabilities(home_lambda: float, away_lambda: float, handicap: float = 0) -> Dict[str, float]:
    probs = {"H": 0.0, "D": 0.0, "A": 0.0}
    for (home_goals, away_goals), prob in score_matrix(home_lambda, away_lambda).items():
        probs[outcome_from_score(home_goals, away_goals, handicap)] += prob
    total = sum(probs.values())
    return {key: val / total for key, val in probs.items()}


def normalize_option(option: str) -> str:
    normalized = OUTCOME_MAP.get(option)
    if not normalized:
        raise ValueError(f"无法识别投注方向: {option}")
    return normalized


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def build_prediction_index(predictions: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {row["cn_match"]: row for row in predictions}


def probability_for_selection(prediction: Dict[str, Any], option: str, handicap: float) -> float:
    outcome = normalize_option(option)
    home_lambda = float(prediction.get("home_goals_est") or prediction.get("xg_h") or 1.2)
    away_lambda = float(prediction.get("away_goals_est") or prediction.get("xg_a") or 1.2)
    return outcome_probabilities(home_lambda, away_lambda, handicap)[outcome]


def evaluate_bet(bet: Dict[str, Any], prediction_index: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    result = deepcopy(bet)
    if "combo_odds" in bet:
        legs = [
            {"match": bet["match1"], "handicap": float(bet.get("handicap1", 0)), "option": bet["option1"], "odds": float(bet["odds1"])},
            {"match": bet["match2"], "handicap": float(bet.get("handicap2", 0)), "option": bet["option2"], "odds": float(bet["odds2"])},
        ]
        hit_probability = 1.0
        leg_details = []
        for leg in legs:
            prediction = prediction_index.get(leg["match"])
            if not prediction:
                raise ValueError(f"缺少预测数据: {leg['match']}")
            leg_prob = probability_for_selection(prediction, leg["option"], leg["handicap"])
            hit_probability *= leg_prob
            leg_details.append({**leg, "probability": leg_prob})
        odds = float(bet["combo_odds"])
        amount = float(bet["amount"])
        max_payout = amount * odds
        expected_value = max_payout * hit_probability
        result.update({
            "legs": leg_details,
            "hit_probability": hit_probability,
            "max_payout_if_hit": max_payout,
            "expected_value": expected_value,
            "expected_profit": expected_value - amount,
            "ev_rate": expected_value / amount - 1,
            "field_warning": "expected_value uses Poisson handicap matrix, not theoretical max payout",
        })
    else:
        prediction = prediction_index.get(bet["match"])
        if not prediction:
            raise ValueError(f"缺少预测数据: {bet['match']}")
        amount = float(bet["amount"])
        odds = float(bet["odds"])
        handicap = float(bet.get("handicap", 0))
        hit_probability = probability_for_selection(prediction, bet["option"], handicap)
        max_payout = amount * odds
        expected_value = max_payout * hit_probability
        result.update({
            "hit_probability": hit_probability,
            "max_payout_if_hit": max_payout,
            "expected_value": expected_value,
            "expected_profit": expected_value - amount,
            "ev_rate": expected_value / amount - 1,
        })
    return result


def evaluate_plan(plan: Dict[str, Any], prediction_index: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    evaluated = deepcopy(plan)
    evaluated_bets = [evaluate_bet(bet, prediction_index) for bet in plan.get("bets", [])]
    total_invest = sum(float(bet.get("amount", 0)) for bet in evaluated_bets)
    max_payout = sum(float(bet.get("max_payout_if_hit", 0)) for bet in evaluated_bets)
    expected_value = sum(float(bet.get("expected_value", 0)) for bet in evaluated_bets)
    evaluated.update({
        "bets": evaluated_bets,
        "total_invest": total_invest,
        "max_payout_if_all_hit": max_payout,
        "expected_value": expected_value,
        "expected_profit": expected_value - total_invest,
        "expected_roi": (expected_value / total_invest - 1) * 100 if total_invest else 0,
        "legacy_total_expected": plan.get("total_expected"),
        "legacy_expected_profit": plan.get("expected_profit"),
        "quality_gate_status": "PASS" if total_invest > 0 else "FAIL",
    })
    return evaluated


def markdown_report(evaluated_plans: Dict[str, Any]) -> str:
    lines = []
    lines.append("═══════════════════════════════════════════════════════════════")
    lines.append("  🧯 投注质量门修正报告")
    lines.append("═══════════════════════════════════════════════════════════════")
    lines.append("")
    lines.append("【结论】已把理论最高奖金和数学期望拆开，EV重新按 Poisson 比分矩阵计算。")
    lines.append("")
    lines.append("【方案汇总】")
    lines.append("| 方案 | 状态 | 投入 | 理论全中奖金 | 数学期望回收 | 期望盈亏 | EV |")
    lines.append("|:--|:--|--:|--:|--:|--:|--:|")
    for name, plan in evaluated_plans.items():
        lines.append(
            f"| {name} | {plan.get('status')} | {plan['total_invest']:.0f}元 | "
            f"{plan['max_payout_if_all_hit']:.1f}元 | {plan['expected_value']:.1f}元 | "
            f"{plan['expected_profit']:+.1f}元 | {plan['expected_roi']:+.1f}% |"
        )
    lines.append("")
    lines.append("【硬规则】")
    lines.append("  · max_payout_if_all_hit：全部命中时理论最高奖金。")
    lines.append("  · expected_value：按模型概率计算的数学期望回收。")
    lines.append("  · expected_profit：expected_value - total_invest。")
    lines.append("  · 让球胜平负概率来自 Poisson 比分矩阵，不再直接套1X2概率。")
    lines.append("")
    lines.append("【赛后结算字段】")
    lines.append("  · actual_score_home / actual_score_away")
    lines.append("  · handicap_result / bet_won / actual_payout / actual_profit")
    lines.append("")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("═══════════════════════════════════════════════════════════════")
    return "\n".join(lines)


def run(archive_path: str, predictions_path: str, output_path: str, report_path: str) -> None:
    archive = load_json(archive_path)
    predictions = load_json(predictions_path)
    prediction_index = build_prediction_index(predictions)
    fixed = deepcopy(archive)
    fixed["quality_gate"] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "probability_method": "Poisson score matrix, max_goals=8",
        "field_policy": "max_payout_if_all_hit / expected_value / expected_profit are separate fields",
        "requires_realtime_odds_before_ticket": True,
    }
    fixed_plans = {name: evaluate_plan(plan, prediction_index) for name, plan in archive.get("plans", {}).items()}
    fixed["plans"] = fixed_plans
    fixed.setdefault("settlement", {})["status"] = "pending"
    fixed["settlement"]["requires_actual_ticket"] = True
    fixed["settlement"]["actual_ticket_plan"] = None
    write_json(output_path, fixed)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(markdown_report(fixed_plans))


def main() -> None:
    parser = argparse.ArgumentParser(description="竞彩投注质量门")
    parser.add_argument("--archive", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    run(args.archive, args.predictions, args.output, args.report)


if __name__ == "__main__":
    main()
