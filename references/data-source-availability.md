# 数据源可用性状态总表 (2026-06-16更新)

## 可用源 (4个)

| 源 | 方式 | 说明 |
|:--|:--|:--|
| Sporttery API | curl直连 | `webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry?clientCode=3001`，Mozilla头+Referer |
| 500.com主表 | curl+gb2312 | 竞彩SPF赔率+让球赔率，非分析页 |
| worldcupwiki.com | browser_navigate | 比分/赛程，无反爬 |
| 500.com指数中心 | kimi-webbridge | 百家欧赔，需daemon启动+独立session |

## 不可用源 (16个)

| 源 | 错误 | 原因 |
|:--|:--|:--|
| 500.com分析页 | 404 | URL已废弃 |
| zgzcw.com | CloudWAF | 三层防护无法突破 |
| Wikipedia | SSL handshake fail | 网络问题 |
| 懂球帝 | 403 | 反爬 |
| Flashscore | 403/空 | 反爬 |
| Goal.com | 403 | 反爬 |
| TheSportsDB | 404 | API端点失效 |
| worldfootball.net | Cloudflare | JS挑战 |
| Kimi-webbridge daemon | 脚本丢失 | 需重新安装 |
| FootyStats | 403 | 付费墙 |
| Transfermarkt | 反爬 | JS挑战 |
| WhoScored | 首次200二次403 | 需一次拉完 |
| OddsPortal | 404 | 无WC2026专用页 |
| SPdex | cookie过期 | ASP.NET_SessionId需刷新 |
| RSSSF | UTF-16编码 | 需特殊解码 |
| 微信文章 | r.jina.ai 403 | 需weixin_fetch.py |

## 更新日志

- 2026-06-16: 新增500.com指数中心(kimi-webbridge)确认可用
- 2026-06-16: 500.com主站DNS无法解析，curl不可用
- 2026-06-16: 确认Sporttery API curl直连可用
- 2026-06-16: worldcupwiki.com是唯一可靠的比分源
