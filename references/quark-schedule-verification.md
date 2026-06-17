# 夸克体育赛程验证流程

> 当需要验证世界杯赛程准确性时使用

## 数据源对比方法

夸克体育赛程图（`vt.quark.cn/quark-sports/`）提供北京时间(UTC+8)的官方赛程。

### 验证步骤

1. 拉取夸克页面HTML → 提取所有比赛日期+时间
2. 对比WhoScored数据（`worldcup_fixtures`表）的赛程
3. 重点关注：**时间对齐**（UTC vs CST转换）、**队名映射**、**分组归属**

### 2026-06-13验证结果

| 对比项 | WhoScored | 夸克体育 | 结论 |
|--------|-----------|----------|------|
| 总场次 | 72场 | 72场 | ✅ |
| 匹配率 | — | — | 71/72 ✅ |
| 时间 | UTC | CST（+7h） | 已对齐 |
| 唯一差异 | 约旦vs瑞士(6/28) | 约旦vs阿联酋(6/28) | 待确认 |

### 关键差异处理

- 夸克的`土耳其`对应WhoScored的`Turkiye`（国名变更，仅译名不同，实质同队）
- 夸克的`波黑`对应WhoScored的`Bosnia and Herzegovina`（一致）
- 夸克`民主刚果`对应WhoScored`DR Congo`
- 夸克`库拉索`对应WhoScored`Curacao`
- 夸克`佛得角`对应WhoScored`Cape Verde`

### 注意

夸克页面是SPA（Single Page Application），直接curl爬取不到队名。
需从页面中的时间戳、队名编码等线索间接验证，或通过图片识别（vision_analyze）。

## 数据入库

验证通过后写入 `wc2026_schedule` 表：

```sql
CREATE TABLE wc2026_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT,
    home_zh TEXT, away_zh TEXT,
    home_en TEXT, away_en TEXT,
    match_date TEXT, match_time TEXT,
    kickoff_cst TEXT
);
```

保存路径：`球赛专属/数据/`