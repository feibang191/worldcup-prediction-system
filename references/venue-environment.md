# 2026世界杯场馆环境数据

来源: Open-Meteo API 实时抓取 | 2026-06-13

## 关键发现

| 因子 | 场馆数 | 影响 |
|:--|:--:|:--|
| 高海拔(>1000m) | 2 | 墨西哥城2254m、瓜达拉哈拉1672m - 球速↑10%，体能↓ |
| 中海拔(200-500m) | 3 | 亚特兰大307m、堪萨斯城269m、蒙特雷493m |
| 高温(>30°C) | 6 | 阿灵顿33°C、休斯顿33°C、亚特兰大30°C、迈阿密33°C、圣克拉拉30°C、蒙特雷33°C |
| 高降水(>40mm/周) | 4 | 迈阿密49mm、费城59mm、墨西哥城45mm、瓜达拉哈拉56mm |

## 全部16场馆

| 场馆 | 城市 | 海拔(m) | 6月高温(°C) | 6月低温(°C) | 降水(mm) |
|:--|:--|:--:|:--:|:--:|:--:|
| MetLife Stadium | East Rutherford | 7 | 29.4 | 18.8 | 25.7 |
| SoFi Stadium | Inglewood | 49 | 23.9 | 18.0 | 0.0 |
| AT&T Stadium | Arlington | 167 | 32.7 | 23.7 | 20.6 |
| NRG Stadium | Houston | 17 | 33.4 | 25.6 | 19.7 |
| Mercedes-Benz Stadium | Atlanta | 307 | 30.3 | 21.4 | 29.4 |
| Hard Rock Stadium | Miami | 2 | 33.4 | 26.7 | 48.7 |
| Lincoln Financial Field | Philadelphia | 5 | 29.7 | 19.0 | 59.1 |
| Lumen Field | Seattle | 17 | 27.4 | 12.9 | 0.0 |
| Levi's Stadium | Santa Clara | 5 | 30.5 | 16.5 | 0.0 |
| Gillette Stadium | Foxborough | 79 | 28.2 | 16.3 | 3.7 |
| Arrowhead Stadium | Kansas City | 269 | 27.9 | 16.6 | 10.4 |
| BMO Field | Toronto | 81 | 21.9 | 13.0 | 29.9 |
| BC Place | Vancouver | 27 | 22.4 | 13.9 | 0.0 |
| **Estadio Azteca** | **Mexico City** | **2254** | **22.7** | **12.8** | **44.5** |
| Estadio BBVA | Monterrey | 493 | 32.6 | 23.7 | 34.8 |
| **Estadio Akron** | **Guadalajara** | **1672** | **25.8** | **15.9** | **55.5** |

## 应用建议

- **高海拔修正**: 墨西哥城/瓜达拉哈拉比赛时，欧洲/低海拔球队实力分下调8-12%，高原球队上调5-8%
- **高温修正**: 阿灵顿/休斯顿/迈阿密/亚特兰大/蒙特雷比赛时，下半场体能下降明显→0-0/1-1概率上升
- **降水修正**: 费城/瓜达拉哈拉降水多→场地湿滑→传球成功率↓→小球概率↑

## 数据文件

- `数据/worldcup_venues.json` — 完整16场馆JSON
- 入库表: `worldcup_venues` (SQLite)
