# 500.com 竞彩数据抓取实战指南

## 触发条件
当需要从500.com抓取竞彩赔率、亚盘、胜负彩、北京单场、篮球竞彩等数据时使用。

## 核心原则
**500.com页面用gb2312编码，必须用`decode('gb2312', errors='ignore')`读取。**
**所有数据都是服务端渲染的HTML，不需要模拟AJAX。**

## 标准URL模式

### 竞彩足球赔率（已完成）
```
https://trade.500.com/jczq/?playid={playid}&g=2
```
- playid=269: 胜平负
- playid=270: 让球胜平负
- playid=271: 比分
- playid=272: 进球数
- playid=312: 半全场
- playid=313: 混合过关

解析方法：找 `<tr class="bet-tb-tr">` 行，提取 `title` 属性中的球队名，`data-sp` 属性中的赔率。

### 竞彩分析页（欧赔+历史交锋）
```
https://odds.500.com/fenxi/shuju-{fid}.shtml
```
- fid: 比赛ID（从竞彩赔率页URL或搜索结果获取）
- 包含：历史交锋记录、平均欧指、凯利指数、历史赔率

解析方法：
- 表格含 `平均欧指` 或 `威**尔` 的是数据表
- 球队名在 `<span class="dz-l">` 和 `<span class="dz-r">` 中
- 比分在 `<em>` 标签中
- 赔率在 `<span>` 标签中（3个数字=胜平负赔率）

### 竞彩亚盘页
```
https://odds.500.com/fenxi/yazhi-{fid}.shtml
```
- 包含17家主流公司的亚盘赔率（即时+历史）

解析方法：
- 找所有 `<tr class="tr1">` 或 `<tr class="tr2">` 行
- 公司ID在 `row="数字"` 属性中
- 公司名在 `title="..."` 属性中
- **主队水位**在第一个 `<td row="1" class="ying/.ping">` 中
- **盘口**在 `<td onclick="javascript:openPl(this)">` 中（如"受球半/两球"）
- **客队水位**在 `<td row="1" width="58" class="ying/.ping">` 中
- 每家公司可能有多个盘口（即时+历史），用 `<table class="pl_table_data">` 分组

**关键正则**：
```python
# 找所有tr数据行
re.findall(r'<tr[^>]*class="tr[12]"[^>]*>(.*?)</tr>', html, re.S)
# 主队水位
re.search(r'<td[^>]*row="1"[^>]*class="([^"]*)">(.*?)</td>', row)
# 盘口
re.search(r'<td[^>]*onclick[^>]*row="1"[^>]*>(.*?)</td>', row)
# 客队水位
re.findall(r'<td row="1"[^>]*width="58"[^>]*class="([^"]*)">(.*?)</td>', row)
```

### 竞彩资料页
```
https://odds.500.com/fenxi/youliao-{fid}.shtml
```
- 包含：近期战绩、交锋记录、近期赛程

### 胜负彩(sfc)
```
https://trade.500.com/sfc/
```
- 每场格式：`场次 赛事 时间 主队 VS 客队 3/1/0 全包 分析`
- **赔率可能尚未开售**（显示为 `3 1 0` 占位符）
- 队名在 `<span class="dz-l zhu">` 和 `<span class="dz-r">` 中

### 北京单场(bjdc)
```
https://trade.500.com/bjdc/
```
- 格式：`场次 联赛 时间 [排名] 主队 -让球 客队 [排名] 赔率1 赔率2 赔率3 -- -- -- 让球盘口 历史比分`
- 赔率直接在td文本中，不需要特殊属性
- 让球盘口格式：`-1` `0` `受平手/半球`

### 篮球竞彩(jclq)
```
https://trade.500.com/jclq/
```
- 格式：`编号 赛事 时间 客队 VS 主队 赔率1 让分 赔率2 赔率3 总分 赔率4 赔率5`
- 让分格式：`-5.5`（负数=主队让客队）
- 胜分差赔率在下一行（客胜行+主胜行）

### 开奖公告
```
https://zx.500.com/jczq/
```
- 找包含比分 `X-Y` 的行

## 常用辅助URL
```
https://odds.500.com/fenxi/yazhi_same.php?cid={company_id}&cp={handicap}&id={fid}&s1={h}&s2={a}  # 同赔查询
https://liansai.500.com/zuqiu-{fid}/  # 比赛详情
https://liansai.500.com/team/{team_id}/  # 球队页面
```

## Pitfall

1. **gb2312编码**：所有500.com页面都是gb2312，`requests.get(url).content.decode('gb2312')`
2. **球队名被隐藏**：公司名如"威**尔"、"*门"是脱敏显示，完整名在 `title` 属性中
3. **亚盘盘口中文**："受球半/两球"=客队让1.75球，"受两球"=客队让2球，"受半球"=客队让0.5球
4. **胜负彩赔率未开售**：显示为 `3 1 0` 占位符，不代表真实赔率
5. **500.com 6/13-6/16 无竞彩赔率**：足彩对阵从6/17起才有赔率，早期赔率需本地Excel
6. **北京单场和篮球竞彩的赔率格式不同**：bjdc用 `data-sp` 属性，jclq直接在文本中
7. **亚盘页表格结构特殊**：数据在 `tr.tr1/tr.tr2` 行中，每行一个公司，不是标准行列结构
8. **500.com分析页的历史交锋**：只包含双方直接交锋记录，不是各自近期战绩
9. **正则匹配要宽松**：中文内容用 `[\\u4e00-\\u9fa5]` 模式比精确队名匹配更可靠

## 2026-06-14 扩展：资料页(战绩)与批量入库

### 资料页（战绩/赛程）
```
https://odds.500.com/fenxi/youliao-{fid}.shtml
```
- 2026-06-13实测：资料页返回的"近期战绩"为 **template占位模板**，无真实数据（只显示固定格式的占位表格）
- 资料页历史交锋表格 **有真实数据**，可从 `<table class="hz_jl_new_1">` 中提取
- 解析历史交锋：用正则 `r'<tr[^>]*class="[^"]*(?:hz_jl[^"]*)"[^>]*>(.*?)</tr>'` 匹配数据行
- 队名在 `data-home`/`data-away` 属性或 `<span>` 标签中
- 比分在比分列 `<td>` 文本中（格式如 `2-0`）

### 批量入库建议（2026-06-13）
抓取500.com竞彩数据需经过6个页面（赔率5种玩法+亚盘+分析+资料），每个页面URL模式和解析逻辑不同。
**最佳实践**：先建表+写入库脚本，再跑批量抓取，避免多次重复抓取。
需要4张表：`jczq_odds`(竞彩赔率)、`asian_odds`(亚盘)、`historical_matches`(历史交锋)、`team_profiles`(球队资料)。
建表前用 `PRAGMA table_info(TABLE)` 确认列名。

### 已验证的SQLite表结构
- `jczq_odds`: match_id, play_type, match_name, home, away, odds_h, odds_d, odds_a, odds_qh, odds_ql, odds_qy, odds_hh, odds_hd, odds_ha, odds_ht, odds_dt, odds_at, odds_0, odds_1, odds_2, odds_3, odds_4, odds_5_plus, odds_1_0, odds_1_1, odds_1_2, odds_2_0, odds_2_1, odds_2_2, odds_3_0, odds_3_1, odds_3_2, odds_4_0, odds_4_1, odds_4_2, odds_5_0, odds_5_1, odds_b, odds_qh_jd, odds_ql_jd, odds_qy_jd, match_date
- `asian_odds`: company_id, company_name, handicap, home_odds, away_odds, match_name, home_team, away_team
- `historical_matches`: match_date, home_team, away_team, home_score, away_score, match_type, source
- `team_profiles`: team_name, team_type, nationality, confederation, fifa_rank, base_value, stadium, coach
