# Poisson λ 求解算法

## 背景
从竞彩SPF赔率反推Poisson分布参数λ，用于生成比分概率矩阵和EV分析。

## 算法步骤

### Step 1: 赔率去水
```python
imp_h = 1/hw
imp_d = 1/dr  
imp_a = 1/aw
total = imp_h + imp_d + imp_a
pH = imp_h / total
pD = imp_d / total
pA = imp_a / total
```

### Step 2: 初始λ估计
```python
lambda_total = -math.log(pD) * 1.15  # 从平局概率反推总期望进球
ratio = math.sqrt(pH / pA)           # 主客胜比例
lambda_h = lambda_total * ratio / (1 + ratio)
lambda_a = lambda_total / (1 + ratio)
```

### Step 3: 牛顿迭代(20次)
```python
for _ in range(20):
    # 计算当前λ下的概率
    pH_calc = 0; pD_calc = 0; pA_calc = 0
    for i in range(8):
        for j in range(8):
            pi = exp(-λh) * λh^i / i!
            pj = exp(-λa) * λa^j / j!
            if i > j: pH_calc += pi*pj
            elif i == j: pD_calc += pi*pj
            else: pA_calc += pi*pj
    
    # 按比例调整λ
    if pH_calc > 0.001: λh *= (pH / pH_calc) ** 0.15
    if pA_calc > 0.001: λa *= (pA / pA_calc) ** 0.15
    
    # 限制范围
    λh = max(0.3, min(4.0, λh))
    λa = max(0.2, min(4.0, λa))
```

### Step 4: 验证
```python
# 最终pH/pD/pA应与去水概率误差<3%
# 如果>5%，检查迭代次数或初始估计
```

## Pitfall
- ❌ 不要用固定下限(如λa=0.1)代替求解
- ❌ 不要只用sqrt(pH/pA)估算而不迭代
- ❌ λ范围限制很重要，避免发散
- ✅ 验证标准: 最终概率与去水概率误差<3%

## 参考
- 2026-06-16 session: 西班牙vs佛得角 λh=1.440, λa=0.995
- 2026-06-16 session: 比利时vs埃及 λh=1.485, λa=0.573
- 2026-06-16 session: 沙特vs乌拉圭 λh=0.503, λa=1.634
- 2026-06-16 session: 伊朗vs新西兰 λh=1.282, λa=0.542