"""年龄-峰值模型引擎 v1.0"""
def peak_score(age, is_first=False):
    if age < 18: return 0.1
    elif age < 22:
        base = 0.3 + (age-18)*0.05
        return base * (0.7 if is_first else 1.0)
    elif age < 25: return 0.6 + (age-22)*0.10
    elif age < 28: return 0.9 + (age-25)*0.03
    elif age < 31: return 0.95 - (age-28)*0.05
    elif age < 34: return 0.75 - (age-31)*0.05
    elif age < 38: return max(0.4, 0.60 - (age-34)*0.07)
    else: return max(0.15, 0.50 - (age-38)*0.05)

POS_WEIGHTS = {
    '1GK': 1.0, '2DF': 1.0, '3MF': 1.2, '4FW': 1.5,
    'CB': 1.0, 'FB': 0.9, 'DM': 1.1, 'CM': 1.2,
    'AM': 1.3, 'WG': 1.2, 'ST': 1.5
}

def analyze_team(players):
    import statistics
    if not players:
        return None
    ages = [p.get('age', 25) for p in players]
    caps = [p.get('caps', 0) for p in players]
    peak_sum = sum(
        peak_score(p.get('age', 25), p.get('caps', 0) < 10) *
        POS_WEIGHTS.get(p.get('position', '').split()[-1] if p.get('position') else '3MF', 1.0)
        for p in players
    )
    exp_idx = sum(
        min(c / 50, 1) * 0.7 + (0.3 if c >= 10 else 0)
        for c in caps
    ) / max(len(caps), 1)
    avg_age = statistics.mean(ages)
    peak_idx = peak_sum / len(players)
    tier = '黄金期' if 25 < avg_age < 29 else ('年轻' if avg_age <= 25 else '老化')
    if tier == '黄金期' and peak_idx > 1.0:
        tier = '巅峰期'
    return {
        'avg_age': round(avg_age, 1),
        'peak_index': round(peak_idx, 3),
        'experience_index': round(exp_idx, 2),
        'tier': tier,
        'player_count': len(players)
    }