# 中国体育数据站反爬模式与应对

## 2026-06-14 更新

## 各站点 curl 可用性

| 站点 | curl 直连 | 浏览器 | 备注 |
|:--|:--|:--|:--|
| **500.com** | ✅ 可靠 | 备用 | gb2312编码，无Cloudflare，唯一curl可直连的竞彩数据源 |
| **懂球帝(dongqiudi.com)** | ❌ 403/302 | 备用 | 首页curl返回302重定向，API返回403。赛后比分用用户口述最可靠 |
| **直播吧(zhibo8.cc)** | ❌ SSL错误 | 备用 | curl返回SSL handshake失败，非标准证书 |
| **新浪体育(sina.com.cn)** | ❌ 404 | 备用 | 比赛详情页面返回404 |
| **虎扑(hupu.com)** | ❌ 403 | 备用 | 反爬严格 |
| **WHOSCORED** | ⚠️ 首次成功 | 主要 | 首次curl 200(514K HTML)，第二次立即403。必须一次拉取完整数据 |
| **Transfermarkt** | ❌ 403 | 备用 | Cloudflare保护 |
| **FlashScore** | ❌ 空 | 备用 | curl返回空内容 |
| **Bet365/OddsPortal** | ❌ 404/空 | 备用 | 世界杯专用URL全部404 |
| **Sporttery(store.sporttery.cn)** | ❌ DNS失败 | 备用 | 本机DNS解析失败，依赖本地SQLite快照 |

## 应对策略

### 1. 500.com是唯一curl可直连的竞彩数据源
- 竞彩赔率：`trade.500.com/jczq/?playid={id}&g=2`
- 亚盘：`odds.500.com/fenxi/yazhi-{fid}.shtml`
- 分析页：`odds.500.com/fenxi/shuju-{fid}.shtml`
- 资料页：`odds.500.com/fenxi/youliao-{fid}.shtml`
- 编码：gb2312，必须 `decode('gb2312')`

### 2. 赛后比分验证优先级
1. **用户口述**（最可靠）
2. **懂球帝首页**（curl 302重定向但正文含比分标题）
3. **RSSSF**（curl直连，次日更新）
4. **WhoScored**（首次curl 200，第二次403，一次成功）
5. **夸克体育**（浏览器方案）

### 3. WhoScored 特殊处理
- 首次请求返回完整HTML(~514K)，含所有72场赛程+赔率
- 第二次请求立即403（session/fingerprint限制）
- **对策**：首次成功后立即完整保存HTML+解析，不重试
- matchCentreData赛后数据：字段直达搜索 `"score":"X : X"` 比完整JSON解析更快

### 4. 浏览器方案（kimi-webbridge / browser-use）
- 用于：懂球帝实时比分、Transfermarkt球员身价、FlashScore赔率
- **限制**：远程浏览器网络不稳定，单次只开1-2个标签页
- **并发上限**：不超过5个标签页，否则502
- **间隔**：串行抓取，每次间隔5-10秒

## Pitfall

1. **curl返回200≠有数据**：页面可访问不代表目标场次数据在正文中。正文不含目标场次只能标缺失。
2. **SSL错误不等于站点不可用**：zhibo8的SSL错误是证书问题，浏览器可正常访问。
3. **404不一定代表站点挂了**：OddsPortal世界杯专用URL全404是正常的——赛事太早，盘口未上线。
4. **懂球帝curl 302是正常重定向**：首页curl返回302到移动端页面，但正文仍含比赛比分标题，可直接解析。
