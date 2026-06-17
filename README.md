# ⚽ World Cup Prediction System

> 基于 Elo + Poisson + 多源赔率融合的量化足球预测系统，专为 FIFA World Cup 2026 设计。

## 📋 系统概述

本系统是一个完整的足球比赛量化预测流水线，覆盖从数据采集到投注策略生成的全流程：

```
数据采集 → 赔率去水修正 → Elo/Poisson 概率模型 → EV 价值分析 → 均值-方差优化投注 → 赛后复盘校准
```

### 核心能力

| 模块 | 功能 | 关键技术 |
|:-----|:-----|:---------|
| 数据采集 | Sporttery API + 500.com + WhoScored + okooo 多源赔率抓取 | HTTP/浏览器自动化 |
| 概率模型 | 胜平负概率 + 比分分布 + 总进球分布 | Elo + Poisson + GBM |
| 赔率修正 | 99家平均欧指去水 → 真实概率 → SP赔率偏差检测 | Overround 去水 |
| EV 分析 | 正EV选项识别 + 凯利指数验证 | Expected Value |
| 投注策略 | 均值-方差优化(Markowitz) + 保本最大化 + 6玩法覆盖 | Kelly Criterion |
| 回测验证 | 5届世界杯384场回测 + 校准曲线 | Log Loss / Brier Score |
| 赛后复盘 | 自动结算 + Elo更新 + 模型校准入库 | 闭环迭代 |

## 🏗️ 项目结构

```
worldcup-prediction-system/
├── SKILL.md                          # 主系统文档（完整方法论+Pitfalls）
├── LICENSE                           # MIT License
├── README.md                         # 本文件
├── .gitignore
│
├── modules/                          # 模块文档
│   ├── data-collection.md            #   数据采集方案
│   ├── model-engine.md               #   Elo/Poisson/xG/GBM/MC 引擎
│   ├── odds-analysis.md              #   赔率分析（竞彩规则/亚盘/大小球）
│   ├── backtest.md                   #   回测框架+校准曲线
│   ├── betting-strategy.md           #   投注策略（均值-方差+竞彩六玩法）
│   ├── report-generation.md          #   报告生成规范
│   └── validation.md                 #   方法论审计
│
├── references/                       # 技术参考文档（46篇）
│   ├── poisson-lambda-solver-v2.md   #   Poisson λ反推算法（牛顿迭代）
│   ├── backtest-results-v6.md        #   v6.0回测结果（5届WC 384场）
│   ├── elo-calibration-20260614.md   #   48队Elo校准表
│   ├── card-layout-standard.md       #   报告排版标准
│   ├── complete-betting-rules.md     #   竞彩完整规则
│   └── ...                           #   更多（数据源/Pitfalls/策略等）
│
├── scripts/                          # 可执行脚本（12个）
│   ├── kelly_engine.py               #   Kelly仓位管理 + EV五级分类
│   ├── multi_bookmaker_engine.py     #   多公司赔率聚合 + 方向矛盾检测
│   ├── odds_movement_engine.py       #   亚盘水位变化检测
│   ├── odds_snapshot_cron.py         #   赔率定时快照
│   ├── settlement_review.py          #   赛后自动复盘
│   ├── age_peak_model.py             #   球员年龄-峰值模型
│   ├── hot_trap_detector.py          #   热门陷阱检测
│   ├── monte-carlo-tournament.py     #   蒙特卡洛锦标赛模拟
│   ├── wc2026_backtest.py            #   世界杯回测引擎
│   ├── wc2026_odds_monitor.py        #   赔率实时监控
│   ├── odds_ev_analysis.py           #   EV分析脚本
│   └── weixin_fetch.py               #   微信文章抓取工具
│
├── sample_data/                      # 示例数据
│   ├── football_database_sample.sqlite  # 脱敏数据库（20张表）
│   └── schema.sql                    #   建表SQL
│
└── config/
    └── calibrated-model.json         # 校准后的模型参数
```

## 📊 数据库 Schema

| 表名 | 行数 | 说明 |
|:-----|:----:|:-----|
| `master_data` | 54 | 世界杯72场比赛主数据（赔率+Elo+FIFA排名） |
| `worldcup_schedule` | 72 | 完整赛程（12组×6场 + 淘汰赛32场） |
| `worldcup_teams` | 48 | 48支参赛队 + 分组 + Elo |
| `team_stats` | 56 | 球队统计（FIFA排名/身价/实力分） |
| `worldcup_odds` | 93 | 赔率历史（含去水概率/亚盘/百家欧赔） |
| `odds_snapshots` | 22 | 赔率定时快照（cron每2小时） |
| `model_calibration` | 37 | 模型校准记录（预测概率 vs 实际结果） |
| `recent_results` | 559 | 球队近期战绩 |
| `historical_matches` | 83 | 历史比赛（含赔率/Kelly） |
| `avg_euro_odds` | 26 | 99家平均欧指 |
| `asian_odds` | 68 | 亚盘赔率 |
| `over_under_odds` | 14 | 大小球赔率 |

## 🔧 核心算法

### 1. Elo → 胜平负概率（含Elo差距自适应平局修正）

```python
expected_home = 1 / (1 + 10 ** ((elo_away - elo_home) / 400))
p_home = expected_home * 0.85
p_away = (1 - expected_home) * 0.85
p_draw = 1 - p_home - p_away

# 平局修正因子随Elo差距递减（非一刀切）
# 教训：法国(1810) vs 塞内加尔(1580) Elo差230
#       全局x1.44高估平局，实际3-1法国胜
if elo_gap < 50:    draw_factor = 1.44
elif elo_gap < 100:  draw_factor = 1.25
elif elo_gap < 150:  draw_factor = 1.10
elif elo_gap < 200:  draw_factor = 1.00
else:                draw_factor = 0.85
```

### 2. Poisson 比分分布（λ反推 + 牛顿迭代）

```python
# 从胜平负概率反推 lambda
lambda_total = -math.log(p_draw) * 1.15
ratio = math.sqrt(p_home / p_away)
lambda_home = lambda_total * ratio / (1 + ratio)
lambda_away = lambda_total / (1 + ratio)

# 比分概率
P(i, j) = poisson(i, lambda_home) * poisson(j, lambda_away)
```

### 3. 赔率去水修正

```python
# SP赔率（含13%前水） vs 99家平均欧指（含~4%前水）
# 用99Avg去水概率作为真实概率基准
true_prob = (1 / odds_99avg) / overround_99avg

# 修正EV = 真实概率 x SP赔率 - 1
ev = true_prob * sp_odds - 1
# ev > 0 → 正EV，值得投注
```

### 4. 均值-方差优化投注（Markowitz）

```python
# 最大化: L = sum(b_i * edge_i) - (lambda/2) * sum(b_i^2 * sigma_i^2)
# 约束: sum(b_i) = B (预算)
# 解: b_i = (edge_i - mu) / (lambda * sigma_i^2)
# lambda=2.0(默认), 1.5(高信心), 3.0(低信心), 5.0(止损)
```

## 📈 回测结果（v6.0，5届世界杯 384场）

| 指标 | 数值 | 说明 |
|:-----|:----:|:-----|
| 准确率 | 55.2% | 全版本最高 |
| Log Loss | 0.9735 | 全版本最低 |
| Brier Score | 0.1925 | 首次跌破0.20 |
| EV (+5% overround) | +3.20% | 正EV |
| 平局预测准确率 | 44% | 25场（GBM过滤有效） |
| 高确信(>=60%)准确率 | 72.7% | 110场，投注核心区间 |

## ⚠️ 已知 Pitfalls（57条已验证踩坑记录）

本系统在开发过程中积累了57条已验证的Pitfalls，涵盖：

- **模型类**：Poisson平局结构性缺陷、Elo-xG不相关、平局修正不能一刀切
- **数据源类**：WhoScored二次403、500.com gb2312编码、Sporttery日期时区错位
- **投注类**：同场不同玩法不能混串、比分串关ROI最差(-85.7%)
- **抓取类**：正则3次失败换思路、zgzcw三层WAF无法突破

完整Pitfalls列表见 `SKILL.md` 底部。

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_GITHUB_USERNAME/worldcup-prediction-system.git
cd worldcup-prediction-system

# 2. 查看示例数据库
sqlite3 sample_data/football_database_sample.sqlite
> SELECT * FROM worldcup_teams LIMIT 10;

# 3. 运行赔率监控
python scripts/wc2026_odds_monitor.py

# 4. 运行回测
python scripts/wc2026_backtest.py
```

### 依赖

- Python 3.8+
- SQLite 3
- requests（HTTP抓取）
- 标准库：json, re, math, sqlite3, datetime, collections

## 🎯 适用场景

- FIFA World Cup 2026 预测（48队、104场、16场馆）
- 中国体彩竞彩投注策略优化
- Elo/Poisson 足球建模学习
- 赔率去水与EV价值分析
- 蒙特卡洛锦标赛模拟
- 多源赔率聚合与异动检测

## 📝 免责声明

本项目仅供教育和研究目的。不构成任何赌博建议。体育投注涉及财务风险，使用者需自行承担所有风险。作者不对通过使用本系统造成的任何财务损失负责。请理性投注，遵守当地法律法规。

## 📄 License

[MIT](LICENSE) - 自由使用、修改、分发。
