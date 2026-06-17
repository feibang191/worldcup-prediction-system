# Data Sources

| Source | Coverage | Update | Reliability |
|:|:|:|:|
| Titan007 | 71/72 matches, 93-187 companies | Real-time | A |
| The Odds API | 40/72 matches, ~30 companies | Real-time | A |
| Sporttery | 24 matches (round 1) | Pre-match fixed | A |
| 500.com | 20 matches | Pre-match fixed | A- |
| FIFA | 48 teams | Monthly | A+ |
| eloratings.net | 48 teams Elo | Post-match | A+ |
| Transfermarkt | Market values | Seasonal | A |
| FBref/Opta | xG/xT | Post-match | A+ |
| **Footystats Power Rating** | **All 48 teams** | **Pre-tournament** | **A-** |
|   └ `footystats_team_power_rating` | overall_power_score, attack/defense/tempo/control | Cached DB | A- |
|   └ `footystats_team_quant_index` | Detailed stats (goals, xG, win%, btts) | Cached DB | B+ |

### Footystats Power Rating 使用说明

**位置**：`footystats_team_power_rating` 表（SQLite数据库）
**查询key**：`team_slug`（英文slug，如 `canada_national_team`）
**关键字段**：`overall_power_score`（综合实力分）、`rating_tier`（A-E评级）、`attack_score`、`defense_score`

**slug映射**：通过 `worldcup_team_alias_v2.team_name_zh → team_name_en` → 去掉空格+特殊字符+转为snake_case 得到slug（常规模式 `{国家名}_national_team`）

**补数据流程**：当 `worldcup_team_quant_base_v2.footystats_power_score IS NULL` 时，
1. 查 `worldcup_team_alias_v2` 找到 `footystats_team_slug`
2. 查 `footystats_team_power_rating` 获取 `overall_power_score`
3. UPDATE 回 `worldcup_team_quant_base_v2`

**已知问题**：波黑xG数据偏低（xG_for=0.16 vs 进球1.50，可能因数据源差异），综合实力分仍可信（3个赛事来源加权）

### Web数据源

| 站点 | 类型 | 可用数据 | 状态 |
|:|:|:|:|
| **worldcup2026cn.com** | Next.js HTML | **104场完整赛程**（小组72+淘汰32，北京时间/阶段/状态）、A组SSR积分榜、夺冠赔率排行、球队资料、资讯 | ✅ curl直连 |
| **Sporttery Web API** | JSON API | 22+场世界杯赔率（HHAD/HHAF/CRS/TWS），`webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry?clientCode=3001` | ✅ curl直连（Mozilla头+Referer） |
