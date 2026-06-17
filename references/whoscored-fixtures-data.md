# WhoScored 世界杯赛程+赔率数据

## 数据来源
WhoScored 通过浏览器抓取获取 `full_browser.json` 文件，包含世界杯全部 72 场小组赛数据。

## 文件位置
`数据/whoscored/worldcup_2026_20260609/worldcup_2026_fixtures_full_browser.json`

## 数据结构

### 顶层
| 键 | 类型 | 说明 |
|:--|:--|:--|
| fixtures | list[dict] | 72 场小组赛 |
| teams | list[dict] | 48 支队伍 |
| tournaments | list[dict] | 赛事信息 |
| createdAt | str | 数据生成时间 (UTC) |
| version | str | 数据版本号 |

### fixture 结构
```python
{
    'tournamentId': 36,
    'stageId': 23753,
    'stageName': 'World Cup Grp. A',  # 小组名
    'matchId': 1953853,
    'status': 1,  # 1=未开始, 2=进行中, 3=已结束
    'startTime': '2026-06-11T20:00:00',
    'startTimeUtc': '2026-06-11T19:00:00Z',
    'homeTeamId': 972,
    'homeTeamName': 'Mexico',
    'awayTeamId': 485,
    'awayTeamName': 'South Africa',
    'homeScore': None,   # 赛后有比分
    'awayScore': None,
    'home_best_1': 1.42,  # 主胜最优赔率
    'draw_best_x': 4.5,   # 平局最优赔率
    'away_best_2': 9.0,   # 客胜最优赔率
    'home_offers': [  # 多家提供商赔率
        {'oddsDecimal': 1.42, 'provider': 'B3', 'providerId': 23, 'oddsFractional': '21/50', 'oddsUS': '-239'},
        ...
    ],
    'draw_offers': [...],
    'away_offers': [...],
}
```

### 提供商列表 (provider)
| ID | 名称 | 说明 |
|:--|:--|:--|
| 23 | B3 | Bet365 |
| 134 | SK | SkyBet |
| 1001 | PIT | Pinnacle |
| 1002 | PIN | Pinnacle (备用) |
| 1003 | KN | Kambi Network |

## 数据库映射
SQLite 表 `worldcup_fixtures`:
```sql
CREATE TABLE worldcup_fixtures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ws_match_id INTEGER UNIQUE,   -- WhoScored matchId
    stage_name TEXT,               -- 小组名
    stage_id INTEGER,
    home_team TEXT,                -- 主队(英文)
    away_team TEXT,                -- 客队(英文)
    start_time TEXT,               -- 开赛时间
    start_utc TEXT,                -- UTC时间
    status INTEGER,                -- 比赛状态
    odds_h REAL,                   -- 主胜最优赔率
    odds_d REAL,                   -- 平局最优赔率
    odds_a REAL,                   -- 客胜最优赔率
    created_at TEXT
);
```

## 已知分组
WhoScored 使用 12 组 (A-L)，每组 4 队，每组内 6 场比赛。

## 读取注意
- 文件使用 UTF-8 BOM 编码 → `encoding='utf-8-sig'`
- teams 是 list 不是 dict → 需构建 {teamId: teamName} 映射
- 赛程时间用 startTime 本地时间 (时区不明)，startTimeUtc 为 UTC
