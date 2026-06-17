# Backtest Results: 2018-2022 World Cups

## v5.8 Model (Dynamic Weights + Environment + GBM Draw Filter)

### 5 World Cups Combined (384 matches)

| Metric | Value |
|:|:|:|
| Accuracy | 214/384 (55.7%) |
| Log Loss | 0.9736 |
| Brier Score | 0.198 |
| EV (5% overround) | +5.84% |
| Draw predictions | 14/32 (43.8%) |
| High confidence (>=60%) | 77/109 (70.6%) |

### Per-Tournament Breakdown

| World Cup | Accuracy | Note |
|:|:|:|:|
| 2002 Korea/Japan | 53.1% | Many upsets |
| 2006 Germany | 68.8% | Strong teams stable |
| 2010 South Africa | 50.0% | Many upsets |
| 2014 Brazil | 53.1% | Mixed |
| 2018 Russia | 57.8% | Good |
| 2022 Qatar | 59.4% | Best recent |

### Confidence Tier Performance

| Confidence | Matches | Accuracy | ROI |
|:|:|:|:|
| >=60% | 109 | 70.6% | +21% |
| 55-60% | 78 | 73.7% | +16% |
| 50-55% | 92 | 62.5% | +3% |
| <50% | 105 | 42.2% | Negative |

### Elo Range Performance

| Elo Diff Range | Matches | Accuracy |
|:|:|:|:|
| [-500, -100) | 19 | 42.1% |
| [-100, 0) | 8 | 75.0% |
| [0, +100) | 11 | 36.4% |
| [+100, +300) | 24 | 70.8% |
| [+300, +600) | 2 | 50.0% |

### Key Finding
Elo difference 100-300 has the best accuracy (70.8%). These are the "clear favorite but not a blowout" matches - exactly the type that appears most in World Cup group stages.

### Calibration Curve (v5.8)

| Predicted Prob | Actual Rate | Deviation |
|:|:|:|:|
| 40-45% | 42.2% | -0.003 |
| 45-50% | 50.0% | +0.025 |
| 50-55% | 55.4% | +0.029 |
| 55-60% | 62.8% | +0.053 |
| 60-65% | 70.8% | +0.083 |

Model is well-calibrated in the 40-55% range but slightly overconfident in 55-70% range.
