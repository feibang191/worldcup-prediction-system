"""规则化复盘系统 v1.0
赛后自动验证预测命中 + 模型校准 + 盈亏记录
"""
import json, sqlite3, os
from datetime import datetime

DB_PATH = r".\football_database.sqlite"
REVIEW_PATH = r".\verify\review_log.json"

def settle_match(match_key, home_score, away_score):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if home_score > away_score:
        result = "主胜"
    elif home_score == away_score:
        result = "平局"
    else:
        result = "客胜"

    cur.execute(
        "SELECT had_win,had_draw,had_loss,true_win,true_draw,true_loss FROM worldcup_odds WHERE match_name=?",
        (match_key,)
    )
    row = cur.fetchone()

    review = {
        "match": match_key,
        "score": f"{home_score}:{away_score}",
        "result": result,
        "predictions": []
    }

    if row:
        tests = [
            ("主胜", row[3], home_score > away_score),
            ("平局", row[4], home_score == away_score),
            ("客胜", row[5], home_score < away_score)
        ]
        for label, prob, hit in tests:
            review["predictions"].append({
                "label": label,
                "prob": prob,
                "hit": hit
            })
            if prob:
                band = "高" if prob > 0.4 else ("中" if prob > 0.2 else "低")
                cur.execute(
                    "INSERT INTO model_calibration (match_key,predicted_prob,actual_outcome,confidence_band,settled_at) VALUES (?,?,?,?,datetime('now','+8 hours'))",
                    (match_key, prob, 1 if hit else 0, band)
                )

    conn.commit()
    conn.close()

    os.makedirs(os.path.dirname(REVIEW_PATH), exist_ok=True)
    if os.path.exists(REVIEW_PATH):
        with open(REVIEW_PATH, "r", encoding="utf-8") as f:
            reviews = json.load(f)
    else:
        reviews = []
    reviews.append(review)
    with open(REVIEW_PATH, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

    return review