# Poisson λ 反推算法（2026-06-16 修正版）

## 问题
简单线性公式或固定下限值导致弱队λ=0.1不收敛。

## 正确算法

### 步骤1: 从竞彩SPF赔率去水
```python
implied = [1/o for o in [hw, dr, aw]]
total = sum(implied)
pH, pD, pA = [i/total for i in implied]
```

### 步骤2: 估算总λ
```python
# 平局概率与总λ的关系: pD ≈ exp(-λ_total) * I₀(λ_total)
# 简化: λ_total ≈ -ln(pD) * 1.15
lambda_total = -math.log(pD) * 1.15
```

### 步骤3: 分配主客λ
```python
# 用胜平负概率比估算强弱
ratio = math.sqrt(pH / pA)
lambda_home = lambda_total * ratio / (1 + ratio)
lambda_away = lambda_total / (1 + ratio)
```

### 步骤4: 牛顿迭代精修（20次）
```python
for _ in range(20):
    # 计算当前λ下的比分矩阵
    matrix = gen_matrix(lambda_home, lambda_away)
    pH_new, pD_new, pA_new = calc_spf(matrix)
    
    # 残差
    err_h = pH_new - pH
    err_a = pA_new - pA
    
    # 限制变化幅度
    delta = min(abs(err_h), abs(err_a)) * 0.5
    if err_h > 0: lambda_home -= delta
    else: lambda_home += delta
    if err_a > 0: lambda_away -= delta
    else: lambda_away += delta
    
    # 范围限制
    lambda_home = max(0.3, min(4.0, lambda_home))
    lambda_away = max(0.2, min(4.0, lambda_away))
```

### 步骤5: 验证
```python
# 最终误差应<3%
assert abs(calc_spf(matrix)[0] - pH) < 0.03
assert abs(calc_spf(matrix)[2] - pA) < 0.03
```

## 适用范围
- 竞彩SPF赔率反推
- 适用于强弱分明和势均力敌两种场景
- 不适用于让球盘（需用其他方法）

## 参考
- 会话: 2026-06-16, 竞彩数据模型升级
- 验证: 沙特vs乌拉圭(0.503/1.634), 伊朗vs新西兰(1.282/0.542)
