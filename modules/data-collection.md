# 模块：数据采集

> 融合来源：500com-sports-scraping + multi-source-sports-data + worldcup-prediction-2026

## 数据源优先级

| 优先级 | 数据源 | 覆盖 | 更新频率 | 可信度 |
|:|:|:|:|:|
| 1 | Titan007(球探网) | 71/72场，93-187家公司 | 实时 | A |
| 2 | The Odds API | 40/72场，~30家公司 | 实时 | A |
| 3 | Sporttery竞彩 | 24场首轮 | 赛前固定 | A |
| 4 | 500.com | 20场(缺让球特殊场次) | 赛前固定 | A- |
| 5 | FIFA官网 | 48队排名 | 月度 | A+ |
| 6 | eloratings.net | 48队Elo | 赛后即时 | A+ |
| 7 | Transfermarkt | 身价 | 季度 | A |
| 8 | FBref/Opta/StatsBomb | xG/xT | 赛后即时 | A+ |

## 赔率抓取

### Titan007（推荐，覆盖最广）

```bash
node scripts/import-titan007-odds.mjs
```

输出：`data/manual/match-odds.csv`（bookmaker=titan007 consensus average）

### The Odds API

需要 `ODDS_API_KEY` 环境变量。

```bash
node scripts/update-realtime-prematch-data.mjs
```

输出：`data/manual/match-odds.csv`（bookmaker=the-odds-api consensus average）

### Sporttery竞彩

浏览器自动化抓取：

```python
# 访问 https://www.sporttery.cn/jc/jsq/zqspf/
# 提取每场的 SPF(胜平负) + RQ(让球胜平负) 赔率
```

输出：`data/manual/match-odds.csv`（bookmaker=sporttery）

### 500.com

```bash
# 访问 https://trade.500.com/jczq/
# 提取 SPF + RQ 赔率
# 注意：让球特殊的场次（+2/-3）可能未开售
```

## 赔率去水（去除overround）

```python
def remove_overround(h_odds, d_odds, a_odds):
    """赔率→去overround后隐含概率"""
    ph, pd, pa = 1/h_odds, 1/d_odds, 1/a_odds
    overround = ph + pd + pa
    return ph/overround, pd/overround, pa/overround
```

## 双源合并规则

`match-odds.csv` 同时存放多源赔率，通过 `bookmaker` 字段区分：
- `titan007 consensus average` — Titan007数据
- `the-odds-api consensus average` — Odds API数据
- `sporttery` — 竞彩数据

**合并模式写入**，key = `date|homeTeam|awayTeam|bookmaker`，同key新行覆盖旧行。

## Elo计算

```bash
node scripts/build-elo-form.mjs --input data/results.csv --outDir data/processed
```

参数：
- K值：世界杯60，洲际杯50，预选赛40，友谊赛30
- 主场优势：非中立场+65（中立场+0）
- 输出：`data/processed/elo-history.json`

## xG数据

来源：Footystats（`footystats_team_quant_wide`表）

```python
# 70% xG + 30% 实际进球
mu = 0.7 * xg_for_avg + 0.3 * goals_per_match
```

## 关键Pitfalls

1. **500.com编码**：页面用gb2312，需 `decode('gb2312', errors='ignore')`
2. **Sporttery反爬**：需要用浏览器自动化，直接API被403
3. **Titan007无日期列**：需从赛程文件反查
4. **赔率更新时机**：24小时内最有价值，3小时内更强
