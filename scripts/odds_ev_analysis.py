#!/usr/bin/env python3
"""
竞彩投注模型 v7 — 参考实现
用途: 从 all_matches_odds_data.json → 市场共识 → 逐公司EV → 凯利验证 → 投注单
输入: Desktop/all_matches_odds_data.json (来自合并Excel)
输出: 终端表格 + odds_model_final_v7.json
"""

import json, re, math

# ===== 解析函数 =====
def parse_oude(rows):
    """欧赔：每行=公司名+赔率+胜率+返还率+凯利"""
    cs = []
    for row in rows:
        if not isinstance(row, list) or not row: continue
        c0 = str(row[0]).strip() if row[0] else ''
        if not c0 or len(c0) < 2 or c0 in ('最高值','最低值','平均值','离散值'): continue
        try:
            w=float(row[1]); d=float(row[2]); l=float(row[3])
            rr=float(row[7]) if len(row)>7 and row[7] else None
            kl=[None,None,None]
            for j in range(8,11):
                if len(row)>j and row[j]:
                    try: kl[j-8]=float(row[j])
                    except: pass
            ti = 1/w+1/d+1/l
            cs.append({'name':c0,'win':w,'draw':d,'lose':l,
                       'ret_rate':rr,'keli':kl,
                       'prob_w':(1/w)/ti,'prob_d':(1/d)/ti,'prob_l':(1/l)/ti})
        except: continue
    return cs

def parse_yapan(rows):
    es = []
    for row in rows:
        if not isinstance(row, list) or not row: continue
        c0 = str(row[0]).strip() if row[0] else ''
        if not c0 or c0 in ('最高值','最低值','平均值','离散值','全部公司','赔率公司'): continue
        try:
            es.append({
                'name': c0,
                'up_water': float(row[1]) if len(row)>1 and isinstance(row[1],(int,float)) else None,
                'handicap': str(row[2]).strip() if len(row)>2 else '',
                'dn_water': float(row[3]) if len(row)>3 and isinstance(row[3],(int,float)) else None,
                'time': str(row[4]).strip() if len(row)>4 else '',
            })
        except: continue
    return es

def parse_daxiao(rows):
    es = []
    for row in rows:
        if not isinstance(row, list) or not row: continue
        c0 = str(row[0]).strip() if row[0] else ''
        if not c0 or c0 in ('最高值','最低值','平均值','离散值','全部公司','赔率公司'): continue
        try:
            es.append({
                'name': c0,
                'big_water': float(row[1]) if len(row)>1 and isinstance(row[1],(int,float)) else None,
                'handicap': str(row[2]).strip() if len(row)>2 else '',
                'small_water': float(row[3]) if len(row)>3 and isinstance(row[3],(int,float)) else None,
            })
        except: continue
    return es

# ===== EV计算 =====
def calc_evs(oude):
    # 市场共识
    aw=sum(c['win'] for c in oude)/len(oude)
    ad=sum(c['draw'] for c in oude)/len(oude)
    al=sum(c['lose'] for c in oude)/len(oude)
    tot=1/aw+1/ad+1/al
    mp_w=(1/aw)/tot; mp_d=(1/ad)/tot; mp_l=(1/al)/tot
    fw=1/mp_w; fd=1/mp_d; fl=1/mp_l

    ev_ops = []
    for co in oude:
        for outcome, col, mp, f_odd in [
            ('主胜','win',mp_w,fw),('平局','draw',mp_d,fd),('客胜','lose',mp_l,fl)]:
            odds=co[col]; ev=round((odds*mp-1)*100,2)
            keli=co['keli'][0 if outcome=='主胜' else 1 if outcome=='平局' else 2]
            if ev>0:
                ev_ops.append({
                    'outcome':outcome,'ev':ev,'odds':odds,
                    'fair_odd':round(f_odd,2),'company':co['name'],'kelly':keli,
                    'prob':round(mp*100,1)})

    ev_ops.sort(key=lambda x:x['ev'], reverse=True)
    return {'mp':{'win':round(mp_w,3),'draw':round(mp_d,3),'lose':round(mp_l,3)},
            'fair_odds':{'win':round(fw,2),'draw':round(fd,2),'lose':round(fl,2)},
            'avg_odds':{'win':round(aw,2),'draw':round(ad,2),'lose':round(al,2)},
            'ev_ops':ev_ops}

# ===== 主入口 =====
if __name__ == '__main__':
    # 加载数据
    with open(r'C:/Users/Administrator/Desktop/all_matches_odds_data.json') as f:
        all_data = json.load(f)

    matches = {}
    for mk in all_data:
        m = all_data[mk]
        r0 = m.get('oude',[])
        r1 = m.get('yapan',[])
        r2 = m.get('daxiao',[])
        matches[mk] = {
            'match': m.get('match', mk),
            'oude': parse_oude(r0[0]['rows']) if r0 else [],
            'yapan': parse_yapan(r1[0]['rows']) if r1 else [],
            'daxiao': parse_daxiao(r2[0]['rows']) if r2 else [],
        }

    results = {}
    for mk, m in matches.items():
        r = calc_evs(m['oude'])
        r['match'] = m['match']
        r['n'] = len(m['oude'])
        results[mk] = r
        print(f"\n  {m['match']}: {len(m['oude'])}家公司, EV>0: {len(r['ev_ops'])}条")

    # 保存
    with open(r'C:/Users/Administrator/Desktop/odds_model_ev_results.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)