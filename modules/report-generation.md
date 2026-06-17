# Module: Report Generation

> Sources: worldcup-prediction-2026 + worldcup-betting-analyst

## Report Structure

1. Model config - version, weights, data sources
2. Champion probabilities - 48 teams + 95% CI
3. Group qualification - 12 groups detailed
4. Match predictions (by date):
   - Win/Draw/Loss probability + predicted score + confidence
   - Dual-source odds comparison (Titan007 vs Odds API)
   - Asian handicap / Over-Under market sentiment
   - Strength comparison (FIFA rank / value / squad rating)
   - Tactical analysis notes
   - Betting recommendation (SPF/RQSPF/Score/Total Goals)
5. Parlay recommendations - by match day + cross-day
6. Data source notes

## Chinese Team Names

All reports must use Chinese team names. Mapping table in references/team-name-cn.md.

## Visualization

- Desktop widescreen: HTML dashboard
- Mobile (1080px): Vertical HTML
- Full report: Markdown format

## Pitfalls

1. matchupNotes uses English: Must replace before output
2. Never say "gambling": Use "odds analysis" / "market data"
3. FIFA Points != Rank: Points is the score, Rank is position
