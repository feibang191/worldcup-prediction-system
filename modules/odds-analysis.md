# Module: Odds Analysis

> Sources: soccer-lottery + worldcup-betting-analyst + soccer-betting-master-system

## Three-Dimension Weighted Model

| Dimension | Weight | Description |
|:|:|:|:|
| Motivation Analysis | 40% | Relegation/title/nothing to play for |
| Odds Movement | 35% | Market consensus + money flow |
| Recent Form | 25% | Last 10 matches + home/away |

## China Sports Lottery Rules

1. **SPF (Win/Draw/Loss)**: Standard 1X2
2. **RQSPF (Handicap)**: With handicap line
3. **CRS (Correct Score)**: Exact score
4. **TTG (Total Goals)**: 0/1/2/3/4/5/6/7+
5. **BQC (HT/FT)**: Half-time + Full-time combo
6. **Mixed Parlay**: Multi-match combo

## Dual-Source Odds Comparison

Each match shows Titan007 (93-187 companies) vs The Odds API (~30 companies).
Differences >5% need special attention.

## Recommendation Logic

- SPF: Give direction when highest prob >= 50%
- RQSPF: Recommend when prob >= 65%
- Score: Top 3 most likely scores
- Total Goals: Predicted count + over/under
- Parlay: Only highest confidence matches

## Pitfalls

1. Odds != Probability: Must remove overround first
2. Sporttery margin 15-20%: Much higher than international (5-6%)
3. Dual source divergence >5%: Market not formed, bet cautiously
