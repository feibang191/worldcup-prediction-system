# Module: Backtest and Validation

> Sources: sports-model-validation + sports-prediction-backtest + sports-betting-poc

## Backtest Framework

### Data Sources
- Footystats: 1521 matches with odds + xG
- international_results: 49,373 historical matches
- 5 World Cups: 2006/2010/2014/2018/2022 (320 matches)

### Evaluation Metrics
| Metric | Description | Target |
|:|:|:|:|
| Accuracy | Correct predictions / total | >55% |
| Log Loss | Probability calibration | <0.95 |
| Brier Score | Probability precision | <0.18 |
| EV | Expected value (5% overround) | >0% |
| Calibration Curve | Prob vs actual frequency | deviation <0.05 |

### Calibration Results (v5.8, 384 matches)
```
Prob Range  Matches  Actual Rate  Deviation
40-45%      45       42.2%        -0.003
45-50%      68       50.0%        +0.025
50-55%      92       55.4%        +0.029
55-60%      78       62.8%        +0.053
60-65%      65       70.8%        +0.083
```

## A/B Comparison Process

1. Define control (current) and experiment (new feature/weight)
2. Run both on same test set
3. Compare Log Loss, accuracy, EV
4. Keep new feature only if Log Loss improves >0.01

## Pitfalls

1. Overfitting: High train accuracy but low test accuracy
2. Time leakage: Cannot use future data for training
3. Sample size: 64 WC matches too few, need continental cups
