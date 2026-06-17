# 500.com指数中心百家欧赔抓取 (2026-06-16)

## 背景
500.com主站DNS无法解析，curl不可用。但通过kimi-webbridge浏览器可访问指数中心页面，获取百家欧赔数据。

## 前提
- kimi-webbridge daemon已启动且extension_connected=true
- 使用独立session名称隔离

## 步骤

### 1. 导航到指数中心
```python
call("navigate", {"url": "https://500.com/odds/zhishu/"}, "500_odds")
```

### 2. 等待页面加载
```python
time.sleep(3)
call("wait", {"seconds": 2}, "500_odds")
```

### 3. 提取比赛数据
```python
call("evaluate", {
    "code": "document.body.innerText"
}, "500_odds")
```

### 4. 解析返回数据
返回格式: 比赛编号 TAB 赛事 TAB 阶段 TAB 时间 TAB 主队 TAB VS TAB 客队 TAB 公司 TAB 亚盘 TAB 亚水 TAB SPF主队 TAB SPF平 TAB SPF客 TAB 返还率

### 5. 关闭session
```python
call("close_session", {}, "500_odds")
```

## Pitfall
- 不要用kimi-daemon.py evaluate脚本
- 不要重复使用同一个session名称
- 每次抓取用独立session名称
- 抓取完成后立即关闭session

## 数据库入库
- euro_odds_detail: 明细表(company/home_win/draw_odds/away_win/return_rate/source)
- avg_euro_odds: 聚合平均值表(AVG home_win/draw_odds/away_win)
