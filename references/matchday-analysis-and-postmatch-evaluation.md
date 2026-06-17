# Match-Day Analysis & Post-Match Evaluation Workflow

Date: 2026-06-13

## Trigger

User says "今天有什么推荐" / "分析这场比赛" / "跑一组推荐" / 赛后复盘要求。

## Match-Day Analysis Flow

### Step 1: Identify Today's Matches

Query all sources simultaneously:

```python
# Sporttery matches
SELECT id, match_num_str, home_team, away_team, match_date, match_time
FROM sporttery_matches WHERE match_date = 'YYYY-MM-DD'

# WhoScored fixtures
SELECT ws_match_id, home_team, away_team, start_time, odds_h, odds_d, odds_a, stage_name
FROM worldcup_fixtures WHERE start_time LIKE 'YYYY-MM-DD%'
```

### Step 2: Pull Odds from All Sources

| Source | Query/Path | Notes |
|:--|:--|:--|
| Sporttery (`sporttery_pool_odds`) | `pool_code='had'`, `odds_json` | H/D/A values |
| WhoScored (`worldcup_fixtures`) | `odds_h/d/a` or raw `full_browser.json` | Multi-provider B3/SK/PIN/PIT/KN |
| FootyStats (`footystats_team_power_rating`) | `overall_power_score` | 实力分0-100 |
| Quant (`worldcup_team_quant_base_v2`) | `footystats_power_score` | 同实力分不同表 |
| Candidate Scorecard (`sporttery_candidate_scorecard_v1`) | `base_score, decision, risk_tags_json` | 推荐评分 |

### Step 3: Team Name Resolution

**Critical**: Team names differ across databases. Use multiple LIKE patterns:

```python
for zh, en in [('加拿大', 'Canada'), ('波黑', 'Bosnia')]:
    cur.execute("SELECT ... WHERE team_name LIKE ?", (f'%{en[:4]}%',))
    # AND fallback
    cur.execute("SELECT ... WHERE team_name_zh LIKE ?", (f'%{zh[:2]}%',))
```

### Step 4: Compute EV

Core formula: **WhoScored去水概率 × Sporttery 赔率 = EV**

```python
ws_total = 1/ws_h + 1/ws_d + 1/ws_a
ws_imp_h = 1/ws_h / ws_total  # WhoScored去水概率
ev_h = ws_imp_h * st_h - 1     # EV vs Sporttery赔率
```

Why this works: WhoScored (B3 specifically) has lower抽水 (~5-6%) versus Sporttery (~12-15%). Using WhoScored probability × Sporttery odds captures the pricing difference.

### Step 5: Incorporate FootyStats Power Rating

Signal: When FootyStats power score and Sporttery odds disagree strongly (>20 point gap), flag it:

```python
if abs(power_a - power_h) > 20:
    if (sp_h < 2.0 and power_a > power_h) or (sp_a < 2.0 and power_h > power_a):
        print("⚠️ 实力分与赔率方向不一致——潜在正EV机会")
```

### Step 6: Output Format

Use `═══` bordered format with sections:
- 比赛名称+时间
- Sporttery赔率 + 隐含概率 + 抽水
- WhoScored对比赔率
- EV分析 (✅/❌ for each outcome)
- FootyStats实力分析
- 最终提示

Verdict guidance:
- 三项全负EV → "跳过，观望"
- 单项正EV且>+2% → "可小注尝试"
- 实力分与赔率分歧 → "重点关注，低注验证"

## Post-Match Evaluation Flow

### Step 1: Fetch Live Data

WhoScored is the best source for completed match data:

```python
mid = 1976989  # From worldcup_fixtures.ws_match_id
url = f'https://www.whoscored.com/Matches/{mid}/Live'

# WhoScored will 403 on second request — use single-shot approach
# Cache the HTML immediately on success
```

### Step 2: Extract Match Data

Parse `matchCentreData` from the Live page:

Key fields:
| Field | Path | Example |
|:--|:--|:--|
| Score | `data['score']` | "1 : 1" |
| HT Score | `data['htScore']` | "0 : 1" |
| Status | `data['statusCode']` | 6=finished |
| Team data | `data['home']`, `data['away']` | Dicts |
| Stats | `data['home']['stats']` | Per-minute dicts |
| Events | `data['events']` | List of goal/card/sub events |
| Referee | `data.get('referee', {})` | `name`, `officialId` |
| Venue | `data.get('venueName')` | "Toronto Stadium" |
| Attendance | `data.get('attendance')` | 43002 |

Stats are per-minute time series — sum all values for match totals.

### Step 3: Compare with Pre-Match Predictions

Compare Sporttery odds, WhoScored odds, FootyStats power vs actual score.

### Step 4: Update Model Calibration

```sql
INSERT INTO model_calibration 
(match_key, actual, power_h, power_a, odds_h, odds_d, odds_a, result_h, result_a, notes)
VALUES ('加拿大vs波黑_20260613', '1-1', 42, 72, 1.59, 3.38, 4.90, 1, 1,
        'FootyStats实力差30分，主场扳平，主胜溢价0.21')
```

### Step 5: Derive Calibration Rules

1. Power gap > 20 → stronger team undervalued by ~0.15-0.20 odds points
2. Home advantage: Default 15% → 10% when home team is weaker
3. Sporttery主胜 premium ~0.20 over WhoScored for weak-home vs strong-away

## Saved Results

| Item | Path |
|:--|:--|
| Raw match data (JSON) | `数据/realTime/{match}_ft.json` |
| Post-match report (MD) | `报告/赛后复盘_{team1}vs{team2}_{date}.md` |
| Pre-match analysis | `报告/{date}比赛推荐.md` |

## Key Pitfalls

- **WhoScored 403 on second request**: First curl always succeeds, second immediately fails. Save HTML immediately.
- **matchCentreData JSON size**: 1MB+. Full parsing may fail on large JSON.
- **Stats are per-minute dicts**: Sum all minute values for totals.
- **Team name mismatch**: Different formats across sources.
- **BOM encoding**: WhoScored JSON files use utf-8-sig encoding.
- **World Cup 2026 has 12 groups (A-L)**: 48 teams in expanded format.