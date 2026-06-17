"""热门陷阱检测 v1.0"""
def check_team_trap(team_name, elo_rating, fifa_ranking, market_value):
    signals = []
    severity = 0
    if elo_rating and elo_rating > 1600 and fifa_ranking <= 3:
        signals.append("盛极而衰: Elo={:.0f} FIFA#{}".format(elo_rating, fifa_ranking))
        severity += 2
    elif elo_rating and elo_rating > 1500 and fifa_ranking <= 8:
        signals.append("高位预警: Elo={:.0f} FIFA#{}".format(elo_rating, fifa_ranking))
        severity += 1
    if market_value and market_value > 8 and fifa_ranking > 5:
        signals.append("身价溢价: {:.1f}亿但FIFA#{}".format(market_value, fifa_ranking))
        severity += 1
    return {'team': team_name, 'severity': severity, 'signals': signals}

def get_hot_traps(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT team_name, fifa_ranking, elo_rating, transfermarkt_value FROM team_stats ORDER BY elo_rating DESC")
    traps = []
    for name, fifa, elo, val in cur.fetchall():
        r = check_team_trap(name, elo, fifa, val)
        if r['severity'] > 0:
            traps.append(r)
    conn.close()
    return sorted(traps, key=lambda x: -x['severity'])