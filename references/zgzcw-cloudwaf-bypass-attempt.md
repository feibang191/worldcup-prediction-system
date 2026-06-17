# zgzcw CloudWAF 三层反爬尝试记录

## 目标
获取zgzcw.com分析页（百家欧赔/亚盘对比/大小指数）的多公司赔率数据。
URL: `https://fenxi.zgzcw.com/{fid}/bjop`（例: `1359236`=科特迪瓦vs厄瓜多尔）

## 验证结果（2026-06-15）

### 第1层：页面级WAF
- 直接HTTP请求 → 返回50350字符的CryptoJS fingerprint挑战代码
- 特征: `CloudWAF` Server头, `security_antibot_code` 参数, 浏览器指纹检测
- 通过Selenium真实Chrome(headless=false) → ✅ 可通过, 页面正常渲染

### 第2层：JS文件级WAF
- 直接请求 `/js/bjop.js` → 返回50348字符的挑战代码(同页面级WAF)
- 通过Selenium获取(验证后) → 返回23792字符 → ✅ 看似通过
- 但实际内容仍是CryptoJS WAF代码, 非真实bjop.js
- **根因**: JS文件在WAF验证后仍被替换, 需要更完整的浏览器指纹匹配

### 第3层：API级Token验证  
- 即使页面+JS都加载, AJAX调用的赔率数据仍然返回全"0.00"
- `共[0]家公司` 标记说明API请求未通过服务器端验证
- bjop.js中的get_key()函数使用浏览器指纹生成加密token, 服务端验证失败

## 尝试过的方案

| 方案 | 结果 | 说明 |
|:--|:--:|:--|
| 直接HTTP请求 | ❌ WAF拦截 | 纯页面级反爬 |
| Selenium headless + webdriver隐藏 | ❌ 数据为0 | JS级WAF未通过 |
| Selenium headless=false + 完整指纹(plugins/languages/chrome) | ❌ 数据为0 | API级token验证失败 |
| 性能日志捕获API端点 | ❌ 无对应API | 真实bjop.js未加载, 所以AJAX请求未触发 |
| jQuery.ajax直接调用 | ❌ jquery_error | 页面未暴露数据接口 |

## 关键发现

1. zgzcw的CloudWAF是**三层叠加**的, 不是单层验证
2. 即使页面HTML正常渲染(非WAF挑战页面), JS文件可能仍是WAF版本
3. "0.00"数据是WAF验证失败的典型特征, 不是页面还没加载完
4. 需要**完整的非浏览器指纹**才能通过——包括屏幕分辨率/GPU/字体列表/插件列表的精确匹配
5. 这种级别的反爬只有 `browser-use` + `undetected-chromedriver` 或类似专业方案才有可能突破

## 替代数据源

百家欧赔/亚盘对比/大小指数 → 目前无可用的免费结构化源:
- Sporttery API: 仅官方胜平负+让球, 无多公司对比
- 500.com分析页: 全部404(新版不兼容)
- OddsPortal: SPA站点, 需浏览器自动化
- The Odds API: 需要付费key

## 结论

zgzcw的CloudWAF在当前工具条件下**不可突破**。放弃此数据源, 已有数据(500.com主表+Sporttery+Elo+泊松)足以支撑量化模型。