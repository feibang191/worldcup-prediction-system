# 实时比分多源验证

> 2026-06-13教训：美国vs巴拉圭，仅用WhoScored结果2-0，用户纠正为4-1
> **赛后比分必须先搜索确认，不能只信单一数据源**

## 验证优先级

| 优先级 | 来源 | 方法 | 可靠性 |
|:------:|:----|:-----|:------:|
| ① | **用户口述** | 直接录入 | ⭐⭐⭐⭐⭐ |
| ② | **懂球帝** | curl直连首页，正则提取 | ⭐⭐⭐⭐ |
| ③ | RSSSF | curl直连，次日更新 | ⭐⭐⭐ |
| ④ | WhoScored | curl首次200，二次403 | ⭐⭐⭐ |
| ❌ | Wikipedia | 超时/重定向 | — |
| ❌ | 500.com | 无比分页面 | — |

## 懂球帝比分提取方法

```python
import urllib.request, re

url = 'https://www.dongqiudi.com/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=10)
html = resp.read().decode('utf-8', errors='replace')

# 方法1: 找"美国\s+vs\s+巴拉圭"附近的比分
scores = re.findall(r'美国[\s\S]{0,100}?(\d+)[:-](\d+)', html)

# 方法2: 找包含两队名的标题
# 懂球帝首页有图片alt文本含完整比分，如:
# "美国4-1巴拉圭，巴洛贡双响，普利希奇献助攻"
```

## WhoScored一次性提取

```python
# 首次curl一定成功，第二次403
# 必须一次保存完整HTML
req = urllib.request.Request(f'https://www.whoscored.com/Matches/{matchId}/Live', 
                              headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8', errors='replace')

# 搜索比分字段
score_match = re.search(r'"score"\s*:\s*"(\d+\s*:\s*\d+)"', html)
ht_match = re.search(r'"htScore"\s*:\s*"(\d+\s*:\s*\d+)"', html)

# 再尝试提取完整matchCentreData JSON
mcd = re.search(r'matchCentreData\s*:\s*(\{.*?\});', html, re.DOTALL)
```

## 赛后数据入库检查清单

- [ ] 全场比分确认（多源交叉：至少用户口述+懂球帝）
- [ ] 半场比分确认（半全场验证需要）
- [ ] match_results表写入（含半场+全场+技术统计）
- [ ] sporttery_match_postmortem表更新
- [ ] model_calibration表更新（校准参数）
- [ ] 验证追踪表更新
- [ ] 比分偏差分析 → 比分覆盖策略校准