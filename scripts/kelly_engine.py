import json, math

def kelly(prob: float, decimal_odds: float, fraction: float = 0.25) -> dict:
    '''Kelly Criterion仓位计算'''
    if not (0 < prob < 1) or decimal_odds <= 1:
        return {'ok': False, 'full_kelly': None, 'suggested_pct': None}
    b = decimal_odds - 1; q = 1 - prob
    full = (b * prob - q) / b
    suggested = max(0.0, full * fraction)
    if suggested <= 0: tier = '不投'
    elif suggested < 0.05: tier = '轻仓'
    elif suggested < 0.15: tier = '中仓'
    elif suggested < 0.25: tier = '重仓'
    else: tier = '超重仓⚠️'
    return {'ok': True, 'full_kelly': round(full, 4), 'suggested_pct': round(suggested, 4), 'tier': tier}

def evaluate_bet(label: str, model_prob: float, decimal_odds: float) -> dict:
    '''EV + Kelly 联合评估'''
    market_implied = 1 / decimal_odds
    edge = model_prob - market_implied
    ev = model_prob * (decimal_odds - 1) - (1 - model_prob)
    if edge >= 0.08: value_tier = '高价值 🔥'
    elif edge >= 0.04: value_tier = '中高价值 ⭐'
    elif edge >= 0.01: value_tier = '中价值'
    elif edge >= -0.02: value_tier = '中性 ℹ️'
    else: value_tier = '低价值'
    k = kelly(model_prob, decimal_odds)
    return {'label': label, 'model_prob': round(model_prob, 4), 'edge': round(edge, 4), 'ev': round(ev, 6), 'value_tier': value_tier, 'kelly': k, 'recommend': edge > 0.01 and k['suggested_pct'] > 0.03}
