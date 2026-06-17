# Module: Validation and Audit

> Sources: sports-model-validation + betting-model-methodology-audit

## When to Use

- Adding new features to the model
- Comparing model versions (A/B test)
- Evaluating feature effectiveness
- Auditing methodology from external sources

## Validation Workflow

1. Define hypothesis (e.g., "xG improves Log Loss by >0.01")
2. Build control (current) and experiment (new feature)
3. Run both on same test set (5 WC backtest)
4. Compare metrics: Log Loss, accuracy, EV, calibration
5. Keep feature only if improvement is statistically significant

## Feature Validation Checklist

- [ ] Feature available pre-match (no time leakage)
- [ ] Feature has sufficient coverage (>80% matches)
- [ ] Feature improves Log Loss by >0.01
- [ ] Feature doesn't increase overfitting risk
- [ ] Feature is interpretable

## External Methodology Audit

When evaluating external prediction methods:
1. Extract verifiable claims (probabilities, weights, accuracy)
2. Compare against our backtest on same dataset
3. Identify unique insights we can adopt
4. Flag unverifiable claims

## Pitfalls

1. Multiple testing: Testing many features increases false positives
2. Survivorship bias: Only reporting successful features
3. Data snooping: Repeatedly adjusting to same test set
