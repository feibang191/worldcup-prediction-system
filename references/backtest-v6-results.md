# v6.0 Backtest Results (5 World Cups, 384 matches)

> Backtested: 2026-06-11
> Training: 5058 matches (continental cups + internationals)
> Test: 2002/2006/2010/2014/2018/2022 World Cups

## Core Metrics

| Metric | Value | Target |
|:|:|:|
| Accuracy | 212/384 (55.2%) | >55% |
| Log Loss | 0.9735 | <0.95 |
| Brier Score | 0.1925 | <0.18 |
| EV (5% overround) | +3.20% | >0% |
| Draw predictions | 25 (11 correct, 44%) | >0% |
| High confidence (>=60%) | 110 matches, 72.7% accuracy | >70% |

## Confidence Tiers

| Threshold | Matches | Accuracy | LogLoss |
|:|:|:|:|
| >=45% | 272 | 61.4% | 0.931 |
| >=50% | 215 | 63.3% | 0.921 |
| >=55% | 162 | 65.4% | 0.885 |
| >=60% | 110 | **72.7%** | 0.794 |
| >=65% | 62 | 69.4% | 0.832 |

## By Tournament

| Year | Accuracy | LogLoss | Note |
|:|:|:|:|
| 2002 | 54.7% | 1.027 | Many upsets |
| 2006 | **64.1%** | **0.865** | Strong teams stable |
| 2010 | 48.4% | 1.014 | Most upsets |
| 2014 | 51.6% | 0.989 | — |
| 2018 | 57.8% | 0.966 | — |
| 2022 | 54.7% | 0.981 | — |

## Version Evolution

| Version | Accuracy | LogLoss | Brier | EV | Draws |
|:|:|:|:|:|:|
| v5.0 Elo+Poisson | 53.1% | 1.042 | 0.202 | -0.63% | 0 |
| v5.1 Fixed Elo | 56.2% | 1.024 | 0.200 | +3.60% | 0 |
| v5.4 Three-source | 56.2% | 0.987 | 0.198 | +10.89% | 0 |
| v5.8 Dynamic+Env+GBM | 55.7% | 0.974 | 0.198 | +5.84% | 32 |
| **v6.0 Unified** | **55.2%** | **0.974** | **0.193** | **+3.20%** | **25** |

## Key Learnings

1. Market odds fusion (LogLoss -6.7%) is the single biggest improvement
2. xG data boosts EV from -2.45% to +10.89%
3. GBM draw filter converts 0 draw predictions to 25 (44% accuracy)
4. Environment correction minimal for 2022 Qatar (AC stadiums), significant for 2026
5. Elo difference 100-300 has best prediction accuracy (70.8%)
6. 2006 Germany WC had strongest accuracy (64.1%) — strong teams performed stably
