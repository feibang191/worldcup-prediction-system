# Module: Model Engine

> Sources: hybrid-model-sports + sports-prediction-methodology + worldcup-prediction-2026

## v6.0 Architecture

### Three-Source Fusion
- Elo probability (20-40%)
- xG Poisson (15%)
- Market odds implied probability (30-50%)

### Dynamic Weights
| Stage | Elo | xG | Odds |
|:|:|:|:|
| Group Stage | 20% | 15% | 50% |
| Knockout | 40% | 15% | 30% |

### Elo to Probability
```python
def elo_probs(diff):
    p_win = 1/(1+10**(-diff/400))
    draw_pct = 0.24 * exp(-(abs(diff)/500)**1.5)
    remaining = 1 - draw_pct
    return p_win * remaining, draw_pct, (1-p_win) * remaining
```

### GBM Draw Filter
- Training: 5058 matches (continental cups 3601 + internationals 1457)
- Features: [elo_diff, elo_home, elo_away, expected_win_prob]
- Logic: gbm_draw_prob > 0.35 AND p_D > 0.22 -> predict draw

### Environment Correction
- Altitude >1500m: High-altitude countries +8%, European -5~15%
- Temperature >30C: Heat-adapted +3%, others -3~10%
- High temp + high humidity (>70%): Extra -3% for non-adapted

### QDR Squad Index
QDR = Quality*0.5 + Depth*0.3 + Reliability*0.2

### Monte Carlo Full Tournament Path
```bash
node scripts/simulate-tournament.mjs --iterations 50000
```

## Pitfalls

1. Draw prediction = 0: Structural Poisson defect, needs GBM supplement
2. Elo diff 0-100 worst accuracy: Low differentiation when close
3. European teams underestimated: Elo can't capture squad depth + tournament pedigree
