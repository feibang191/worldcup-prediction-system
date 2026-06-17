# 弱主vs强客投注策略

**加拿大(42) vs 波黑(72)** 复盘验证 | 2026-06-13 | 实际结果 1-1

---

## 场景定义

- **弱主**: FootyStats 实力分 < 50
- **强客**: FootyStats 实力分 > 65
- **实力差**: 客队 - 主队 ≥ 25分

## 三步信号检测

### 第1步: 实力背离

```
FootyStats实力分: 客队比主队高≥25分
  ↓
Sporttery主胜赔率 <1.70 (隐含概率>52%)
  ↓
背离信号: 市场实力与定价方向不一致
```

### 第2步: 赔率套利

```
WhoScored(B3)主胜赔率 - Sporttery主胜赔率 ≥ 0.15 → 定价偏差
去水概率: WS_p_h = (1/WS_h) / (1/WS_h + 1/WS_d + 1/WS_a)
客胜EV: WS_p_a × SP_a - 1
```

**为什么用 WhoScored?**
- WhoScored(B3)抽水约5-6%，Sporttery约12-15%
- WhoScored概率更接近真实市场概率
- Sporttery主胜溢价0.15-0.20→对应的客胜赔率偏肥→正EV机会

### 第3步: 交叉验证 (可选)

```
✓ SPdex交易量: 客队占比 >25%
✓ 凯利方差: 客队 <10.0
✓ 临场赔率: 客胜走低
```

## 信号强度分级

| 级别 | 条件 | 行动 |
|:--|:--|:--|
| ⭐⭐⭐⭐⭐ | 实力差≥25 + 价差≥0.15 + SPdex客队>25% | 满仓推 |
| ⭐⭐⭐⭐ | 实力差≥25 + 价差≥0.15 | 主力仓位 |
| ⭐⭐⭐ | 仅实力差≥25 | 轻仓 |
| ❌ | 实力差<20 或 主胜>2.00 或 价差<0.10 | 跳过 |

## 仓位方案 (200元)

| 方案 | 玩法 | 金额 | 比例 | 说明 |
|:--|:--|:--:|:--:|:--|
| A | 客队受让(+0.5) | 100元 | 50% | 主力，客队不败即赢 |
| B | 客胜 | 60元 | 30% | 高风险，正EV驱动 |
| C | 1-1比分 | 40元 | 20% | 精确打击 |

## 模型校准参数

| 参数 | 原值 | 新值 | 依据 |
|:--|:--:|:--:|:--|
| 主场加成 | 15% | **10%** | 加拿大42+15%=48<72→仍被半场领先 |
| 客队实力权重 | 1.0x | **1.05-1.08x** | 实力差30时覆盖概率更高 |
| Sporttery主胜溢价 | — | **0.15-0.20** | 弱主vs强客固定价差 |
| Poisson平局概率 | 原公式 | **+3%** | 主场扳平动力被低估 |

## 决策树

```
实力差≥25 + SP主胜<1.70 + 背离信号                  → ✅ 可下
实力差≥25 + WS-SP价差≥0.15                         → ✅ 高置信
以上两条 + SPdex客队量>25%                          → ✅ 强信号
实力差<20 或 SP主胜>2.00                           → ❌ 跳过
WS-SP价差<0.10                                     → ❌ 无价值
```

## 延伸应用: 极弱主vs超强客 (变体)

当Sporttery比WhoScored更看衰弱主时(SP H > WS H)：

- 海地(25) vs 苏格兰(59): SP H=7.65 vs WS H=6.50
- 海地主胜EV=+15.8% (14.17%×7.65)
- 但海地实力25实际赢球概率极低
- 建议: 海地受让(+2)更合理，而非直接主胜

## 案例库

| 比赛 | 实力差 | SP H | WS-SP价差 | EV信号 | 结果 | 方案A | B | C |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 加拿大42 vs 波黑72 | 30 | 1.59 | +0.21 | 客胜+2.1% | 1-1 | ✅ | ❌ | ✅ |

## 赛前检查清单

- [ ] 双方 FootyStats 实力分 (footystats_team_power_rating)
- [ ] Sporttery vs WhoScored 主胜赔率差
- [ ] 客队 EV (去水概率×赔率-1)
- [ ] 场地海拔/温度 (高海拔=主队优势↓)
- [ ] 裁判出牌尺度 (影响身体对抗)
- [ ] 两队近5场状态

## 数据库表

```sql
-- 校准参数存储
CREATE TABLE IF NOT EXISTS model_calibration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_key TEXT UNIQUE,
    actual TEXT,          -- 实际比分
    power_h REAL,         -- 主队实力分
    power_a REAL,         -- 客队实力分
    odds_h REAL,          -- SP主胜
    odds_d REAL,          -- SP平局
    odds_a REAL,          -- SP客胜
    result_h INTEGER,     -- 主队进球
    result_a INTEGER,     -- 客队进球
    notes TEXT
);

-- 赛后数据
INSERT OR REPLACE INTO sporttery_match_postmortem
(match_num_str, home_team, away_team, actual_score, source_url, created_at)
VALUES (?, ?, ?, ?, ?, ?);

INSERT OR REPLACE INTO match_results
(match_id, home, away, home_goals, away_goals, snapshot_time)
VALUES (?, ?, ?, ?, ?, ?);
```
