# 赔率监控与回测自动化

## 脚本清单

| 脚本 | 路径 | 功能 |
|:|:|:|
| 赔率监控 | `.\scripts\wc2026_odds_monitor.py` | 抓取Sporttery赔率→对比变化→SQLite+历史JSON |
| 回测计算 | `.\scripts\wc2026_backtest.py` | 传入比分→计算中奖+收益→标准格式报告 |

## 赔率监控脚本

### 功能
1. 加载上次赔率数据
2. 读取当前数据
3. 检测赔率变化（阈值>5%）
4. 保存到SQLite(odds_snapshots表) + 历史JSON
5. 输出变化报告

### 调用
```bash
cd ./scripts
python3 wc2026_odds_monitor.py
```

### 输出
- SQLite: `football_database.sqlite` → `odds_snapshots` 表
- 历史: `.\数据\odds_history\odds_{timestamp}.json`
- 变化日志: `.\数据\odds_changes.log`

## 回测计算脚本

### 功能
1. 输入比分（命令行或代码）
2. 计算所有投注选项的中奖情况
3. 支持SPF/RQSPF/CRS/TTG/BQC全部6种玩法
4. 支持串关(2串1)和容错(2串3)
5. 输出标准格式报告

### 调用
```bash
cd ./scripts
python3 wc2026_backtest.py 墨西哥 2 1 南非 韩国 1 1 捷克
```

### 关键实现
- BQC匹配必须做中英文映射（HH→胜胜, HD→胜平 等）
- 让球计算：`diff = home_goals - away_goals + handicap`
- 串关奖金：`赔率1 × 赔率2 × ... × 赔率n × 投注金额`
- 单注上限：500万元

## Cron定时任务

| 任务 | 频率 | 说明 |
|:|:|:|
| 赔率监控 | 每2小时 | 自动抓取+对比+报告 |
| 赛前最终赔率 | 赛前1小时(一次性) | 锁定前最后推送 |
| 赛后回测 | 赛后30分钟(一次性) | 自动计算投入收益 |

### Cron Prompt模板

**赔率监控：**
```
你是世界杯2026赔率监控助手。请执行：
1. 用浏览器访问 https://www.sporttery.cn/jsl/jczq/ 获取最新竞彩足球赔率
2. 提取所有世界杯比赛的SPF和RQSPF赔率
3. 保存到 ./数据/sporttery_official_odds.json
4. 运行 python3 ./scripts/wc2026_odds_monitor.py 检测变化
```

**赛后回测：**
```
你是世界杯2026赛后回测助手。请执行：
1. 搜索今天世界杯比赛结果
2. 用浏览器访问比分网站获取最终比分
3. 执行回测计算器（传入实际比分）
4. 输出标准格式报告
```
