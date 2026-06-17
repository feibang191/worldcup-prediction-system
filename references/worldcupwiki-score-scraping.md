# worldcupwiki.com 比分抓取模式（2026-06-16 新增）

## 触发条件
- 所有HTTP抓取源返回空/403/超时（Flashscore/500.com/sporttery/ESPN/Wikipedia/RSS/thesportsdb/livescores/goal247/sportsdaquan）
- 需要获取已赛世界杯比赛比分

## 完整抓取链

```
1. browser_navigate → https://worldcupwiki.com/schedule
2. browser_console(expression="document.body.innerText.indexOf('June XX')") → 定位日期位置
3. browser_console(expression="document.body.innerText.substring(start, start + 2000)") → 截取比赛结果
4. 正则提取比分: re.match(r'(.*?)\s+vs\.\s+(.*?)\s+([✔✅\s]*)\s*([\d-]+)', line)
```

## 关键技巧

- 页面按日期分组: "Thursday, June 11 (Completed)", "Friday, June 12 (Completed)" 等
- 已赛比赛在 `<table>` 中有 `Group/Matchup/Result/Venue` 四列
- 未赛比赛只有 `Group/Matchup/Time (ET)/Venue`
- 比分格式: "Mexico 2-0", "South Korea 2-1", "1-1 Draw", "USA 4-1"
- 比赛描述文本也包含比分: "Germany routed debutants Curaçao 7-1"

## Pitfall

- 页面初始渲染只显示到最近几个日期，需用 `browser_scroll` 或 `substring` 定位更早期日期
- `browser_console` 的 `expression` 参数中不要使用 `return` 语句（会导致 SyntaxError）
- 使用 `const` 而非 `let` 声明变量，避免重复声明错误

## 适用场景
- 世界杯小组赛/淘汰赛比分
- 大型锦标赛赛程和结果
- 需要精确到场的赛后复盘
