#!/usr/bin/env python3
"""
Extract ALL 竞彩 data from trade.500.com/jczq/
Returns: list of matches with full odds (SPF, RQ, BJDC, etc.)
"""
import re, json, os, sys
from urllib.request import Request, urlopen

def crawl_500_jczq():
    url = 'https://trade.500.com/jczq/index.php?playid=272'
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
    resp = urlopen(req, timeout=15)
    html = resp.read().decode('gb2312', errors='replace')
    print(f"HTML size: {len(html)}")
    
    # Strategy: extract all matches from the table
    # The page has a structured table with matches
    # Each match row has: 赛事编号, 开赛时间, 主队 VS 客队, SPF赔率, RQ赔率
    
    # Find all match blocks - pattern: match_id followed by team names and odds
    # The table structure uses <tr> with cells
    
    matches = []
    current_date = ""
    
    # Find all table rows
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.I)
    
    for row in rows:
        text = re.sub(r'<[^>]+>', ' ', row).strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Check for date headers like "周日 2026-06-14"
        date_match = re.search(r'(周[一二三四五六日])\s*(\d+-\d+-\d+)', text)
        if date_match:
            current_date = f"2026-{date_match.group(2)}"
            continue
        
        # Check for match line - needs VS and odds numbers
        if 'VS' not in text or not re.search(r'\d+\.\d+', text):
            continue
        
        # Extract match ID (e.g., "周日001", "周一002")
        mid_match = re.search(r'(周[一二三四五六日]\d+)', text)
        if not mid_match:
            continue
        match_id = mid_match.group(1)
        
        # Extract teams
        teams_match = re.search(r'([\u4e00-\u9fa5a-zA-Z]+)\s*VS\s*([\u4e00-\u9fa5a-zA-Z]+)', text)
        if not teams_match:
            continue
        home = teams_match.group(1).strip()
        away = teams_match.group(2).strip()
        
        # Extract league (世界杯, etc.)
        league_match = re.search(r'世界杯|国际赛|中北美|南美', text)
        league = league_match.group(0) if league_match else "未知"
        
        # Extract all odds numbers (X.XX format)
        all_odds = re.findall(r'(\d+\.\d+)', text)
        valid_odds = [float(n) for n in all_odds if 1.0 <= float(n) <= 100.0]
        
        # Filter to reasonable odds range (1.0-20.0 for main odds)
        main_odds = [o for o in valid_odds if o <= 20.0]
        
        if len(main_odds) >= 6:
            spf = main_odds[:3]  # 胜平负
            rq = main_odds[3:6]  # 让球胜平负
            handicap = "0"
        elif len(main_odds) >= 3:
            spf = main_odds[:3]
            rq = []
        else:
            continue
        
        matches.append({
            'id': match_id,
            'date': current_date,
            'home': home,
            'away': away,
            'league': league,
            'spf': spf,
            'rq': rq,
            'all_valid_odds': valid_odds
        })
    
    return matches

if __name__ == '__main__':
    matches = crawl_500_jczq()
    print(f"Extracted {len(matches)} matches")
    
    for m in matches:
        spf = f"SPF:{m['spf']}"
        rq = f"RQ:{m['rq']}"
        print(f"  {m['id']} {m['home']} VS {m['away']} | {spf} | {rq}")
    
    # Save
    out_path = r"E:\MyBrain\WIKI\球赛专属\数据\500_jczq_raw.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to: {out_path}")
