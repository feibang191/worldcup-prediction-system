# GBM Draw Prediction

## Problem

Standard Poisson/Elo models NEVER predict draws because p_Draw is always lower
than p_Home or p_Away. In the 2022 World Cup, 15/64 matches (23.4%) were draws.

## Solution: GBM Supplementary Filter

Train a GradientBoostingClassifier on historical matches to predict draw probability.
Use it as a FILTER, not a replacement for the main model.

```python
from sklearn.ensemble import GradientBoostingClassifier
import numpy as np

# Training data: all international matches with results
# Features: [elo_diff, elo_home, elo_away, expected_win_prob]
X_train = []
y_train = []
for match in historical_matches:
    elo_h, elo_a = get_elo(match)
    diff = elo_h - elo_a
    exp_win = 1 / (1 + 10**(-diff/400))
    X_train.append([diff, elo_h, elo_a, exp_win])
    y_train.append(0 if match.hs > match.as else (1 if match.hs == match.as else 2))

gbm = GradientBoostingClassifier(
    n_estimators=300, max_depth=3, learning_rate=0.05, random_state=42
)
gbm.fit(np.array(X_train), np.array(y_train))

# Prediction logic
gbm_proba = gbm.predict_proba([[diff, elo_h, elo_a, exp_win]])[0]
gbm_draw_prob = gbm_proba[1]  # class 1 = draw

# FILTER: only override main model when GBM strongly suggests draw
if gbm_draw_prob > 0.35 and main_model_draw_prob > 0.22:
    prediction = 'D'  # predict draw
else:
    prediction = main_model_prediction  # use main model (H or A)
```

## Results (2022 World Cup backtest)

| Approach | Draw Predicted | Draw Correct | Draw Accuracy |
|:|:|:|:|
| No GBM | 0/64 | 0 | N/A |
| GBM filter (threshold=0.35) | 8/64 | 3/8 | 37.5% |
| GBM filter (expanded training) | 5/64 | 3/5 | 60.0% |

## Pitfalls

1. **GBM alone has worse overall accuracy** (51.6% vs 56.2% for v5.4)
   - Use ONLY as supplementary filter, not primary predictor
2. **Training data must include continental cups** (Euro/Copa/AFCON)
   - World Cup alone (320 matches) is too few for 19-feature GBM
   - With 5058 training samples, draw prediction improves to 60%
3. **Feature count matters**: 4 features > 19 features (less overfitting)
4. **Threshold tuning**: 0.35 is optimal for 2022 WC; may need recalibration for 2026
