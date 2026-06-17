# Sporttery Browser Automation

## When to Use

Fetching live odds from sporttery.cn (Chinese sports lottery official site).

## Method

Direct API access returns 403 Forbidden. Must use browser automation.

```python
# Navigate to the SPF page
browser_navigate("https://www.sporttery.cn/jc/jsq/zqspf/")

# Extract data via browser_vision (screenshot analysis)
# The page shows: match number, teams, handicap, SPF odds (H/D/A), RQ odds

# Example extracted data:
# 001 | Mexico vs South Africa | -1 | 1.26/4.45/9.00 | 2.00/3.25/3.11
```

## Data Format

```json
{
  "id": "2026001",
  "date": "2026-06-12",
  "home": "墨西哥",
  "away": "南非",
  "handicap": "-1",
  "spf": [1.26, 4.45, 9.00],
  "rq": [2.00, 3.25, 3.11]
}
```

## Pitfalls

1. **API 403**: Direct urllib/curl to sporttery.cn API returns 403 Forbidden
2. **Must use browser**: Navigate + screenshot + vision extraction
3. **Handicap special matches**: Let +2/-3 matches may show "未开售" (not on sale)
4. **Update time**: Page shows "竞彩奖金更新时间：YYYY-MM-DD HH:MM:SS"
5. **Overround**: Sporttery has ~15-20% overround (much higher than international 5-6%)
6. **500.com identical**: 500.com odds are the same source as Sporttery (Chinese lottery)
