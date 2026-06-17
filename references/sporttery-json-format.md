# Sporttery 赔率数据格式 & 监控脚本

## JSON格式（sporttery_official_odds.json）

```json
[
  {
    "id": "2026001",
    "date": "2026-06-12",
    "time": "03:00",
    "league": "世界杯",
    "home": "墨西哥",
    "away": "南非",
    "handicap": "-1",
    "spf": [1.26, 4.45, 9.0],
    "rq": [2.0, 3.25, 3.11],
    "status": "已开售"
  }
]
```

**字段说明：**
- `spf`: [主胜H, 平D, 客胜A] — 胜平负赔率
- `rq`: [让球主胜H, 让球平D, 让球负A] — 让球胜平负赔率（空数组=未开售）
- `handicap`: 让球数（负数=主队让球）
- `status`: "已开售" | "未开售" | "已截止"

## 监控脚本

`.\scripts\wc2026_odds_monitor.py`

功能：
1. 读取当前赔率文件
2. 与上次数据对比，检测变化（阈值>5%）
3. 保存到SQLite `odds_snapshots` 表
4. 保存到历史目录 `odds_history/odds_{timestamp}.json`
5. 记录变化日志 `odds_changes.log`

## 抓取方法

### 方法1：Web API直达 ✅（推荐，2026-06-14验证）

Sporttery官方API可直接curl：

```
GET https://webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry?clientCode=3001
Headers: User-Agent=Mozilla, Referer=https://www.sporttery.cn/, Accept=application/json
```

返回JSON，结构：
```json
{
  "value": {
    "matchInfoList": [{
      "businessDate": "2026-06-13",
      "subMatchList": [{
        "homeTeamAllName": "卡塔尔",
        "awayTeamAllName": "瑞士",
        "matchDate": "2026-06-14",
        "matchTime": "03:00",
        "matchNumStr": "周六005",
        "matchStatus": "Selling",
        "oddsList": [
          {"poolCode": "HHAD", "h": "2.35", "d": "3.42", "a": "2.43"},
          {"poolCode": "HHAF", "h": "2.35", "d": "3.42", "a": "2.43", "goalLine": "+2.00"}
        ]
      }]
    }]
  }
}
```

### 方法2：浏览器自动化（备用）

如API不可用，回退：
browser_navigate("https://www.sporttery.cn/jsl/jczq/")
browser_vision(question="提取所有世界杯比赛的赔率数据")
```

然后手动整理为JSON格式保存。

## Cron定时监控

Job ID: YOUR_JOB_ID
Schedule: every 2h
