# 500.com 世界杯数据提取方法

## 数据源概览

### 1. 500.com 主站（www.500.com）
- **比分数据**：info-title 含比分（`世界杯：美国 4-1 巴拉圭`）
- **赛程结构**：team_1/team_2 行含 title 属性（完整队名）+ display text（可能被截断）
- **提取方法**：
  ```python
  # 比分：info-title 匹配
  for m in re.finditer(r'info-title[^>]*>(.*?)</span>', html):
      line = m.group(1)
      if '世界杯' in line:
          score_m = re.search(r'(.+?)\s+(\d+)-(\d+)\s+(.+)', line)
  
  # 未开赛：team_1/team_2 结构
  for m in re.finditer(r'<td><span class="team_1"[^>]*>.*?</td>', html, re.DOTALL):
      teams = re.findall(r'title="([^"]+)"', m.group(0))
  ```

### 2. 竞彩赔率页（trade.500.com）
- **5种玩法**：胜平负(269)、让球(270)、比分(271)、进球数(272)、半全场(312)
- **队名**：`data-homesxname` / `data-awaysxname`（真实队名）
- **赔率**：`data-sp` 属性（逗号分隔多个赔率）
- **让球**：`data-rangqiu` 属性（如 `-1`, `+2`）
- **时间**：`data-matchdate` + `data-matchtime`
- **提取方法**：
  ```python
  for m in re.finditer(r'<tr class="bet-tb-tr"[^>]*>(.*?)</tr>', html, re.DOTALL):
      row = m.group(0)
      if '世界杯' not in row: continue
      home = re.search(r'data-homesxname="([^"]+)"', row)
      away = re.search(r'data-awaysxname="([^"]+)"', row)
      odds = re.findall(r'data-sp="([^"]+)"', row)
      rangqiu = re.search(r'data-rangqiu="([^"]+)"', row)
  ```

### 3. 亚盘页
- **结构**：`tr.tr1` / `tr.tr2` 行（非标准 tr）
- **公司名**：脱敏显示（"威**尔"）
- **盘口**：`<td onclick>` 标签中
- **水位**：带 `row="1"` 属性的 `<td>`

### 4. 晶报赛程文章
- **URL**：晶报体育频道（jb.sznews.com）
- **格式**：`01:00K葡萄牙VS乌兹别克斯坦`（时间+小组+队名）
- **提取**：正则 `r'(\d{2}:\d{2})([A-L])(.+?)VS(.+)'`
- **覆盖**：48队×3轮=96场（小组赛96场+淘汰赛）

## 2026世界杯48队完整分组

```
A组: 墨西哥 南非 韩国 捷克
B组: 加拿大 波黑 卡塔尔 瑞士
C组: 巴西 摩洛哥 海地 苏格兰
D组: 美国 巴拉圭 澳大利亚 土耳其
E组: 德国 库拉索 科特迪瓦 厄瓜多尔
F组: 荷兰 日本 瑞典 突尼斯
G组: 比利时 埃及 伊朗 新西兰
H组: 西班牙 佛得角 沙特阿拉伯 乌拉圭
I组: 法国 塞内加尔 伊拉克 挪威
J组: 阿根廷 阿尔及利亚 奥地利 约旦
K组: 葡萄牙 民主刚果 乌兹别克斯坦 哥伦比亚
L组: 英格兰 克罗地亚 加纳 巴拿马
```

## 数据库表结构

- `worldcup_schedule`：72场小组赛赛程
- `worldcup_teams`：48队+分组归属
- `worldcup_odds`：5玩法×18场=89条赔率
