#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鬱金香指標 (Tulip Indicator) v2.0 計分引擎
- 輸入：每個代理對自身歷史窗的百分位 (0-100, 泡沫極端=高)
- 處理：代理 -> 機制(均值) -> 原始加權composite -> 顯示刻度TI
- 顯示刻度：內部raw 70 對應顯示 90 (引信備妥/危險線)，raw 70-100 壓進顯示 90-100(脈衝段)
- 輸出：顯示TI、區間、三組摘要(放大器/領先引信/確認)、寫入 history
用法：把 PROXIES 換成當期百分位後 `python3 score.py`
"""
import csv, os, datetime, json

# ---- 七機制權重 (2026 AI資料中心情境；隨時代浮動見 METHODOLOGY §8) ----
WEIGHTS = {'M1':0.25,'M2':0.18,'M3':0.14,'M4':0.10,'M5':0.10,'M6':0.15,'M7':0.08}
NAMES = {'M1':'信貸計價','M2':'資本支出轉折','M3':'邊際買家枯竭',
         'M4':'槓桿','M5':'集中度/偽分散','M6':'結構確認','M7':'情緒/全民化'}

# ---- 三組(對外摘要層) ----
GROUPS = {
    '放大器(乾柴多高)':   ['M4','M5','M7'],   # 槓桿+集中度+情緒：嚴重度，可維持數年
    '領先引信(火星點了沒)':['M1','M2','M3'],   # 信貸+capex+邊際買家：領先轉折
    '確認(燒起來沒)':     ['M6'],             # 結構確認：同步脈衝源
}

# ---- 區間 (顯示刻度) ----
BANDS = [
    (0,  50,  '平靜',            '正常配置，每月查'),
    (50, 75,  '累積',            '停止加碼風險，壓力測試組合能否扛 -35% 不被迫賣'),
    (75, 90,  '警戒/逐步退場',   '防禦準備並逐步減碼，目標 90 前退完；改週查 M1/M2/M6'),
    (90, 101, '進行中/太晚',     '脈衝/cascade 已啟動，控損模式，不在底部被迫賣'),
]

def to_display(raw):
    """內部raw -> 顯示刻度。raw70->90(慢爬拉伸), raw70-100->90-100(脈衝壓縮)。"""
    if raw <= 70:
        return raw * 90.0/70.0
    return 90.0 + (raw - 70.0) * 10.0/30.0

def band(disp):
    for lo,hi,name,act in BANDS:
        if lo <= disp < hi:
            return name, act
    return BANDS[-1][2], BANDS[-1][3]

def mechanism_scores(proxies):
    M, used, missing = {}, {}, {}
    for m, ps in proxies.items():
        vals = [v for v in ps.values() if v is not None]
        miss = [k for k,v in ps.items() if v is None]
        M[m] = round(sum(vals)/len(vals),1) if vals else None
        used[m], missing[m] = len(vals), miss
    return M, missing

def composite(M):
    avail = {m:s for m,s in M.items() if s is not None}
    wsum = sum(WEIGHTS[m] for m in avail)            # 缺機制則重新正規化
    raw = sum(WEIGHTS[m]*avail[m] for m in avail)/wsum if wsum else 0
    return round(raw,1)

def group_scores(M):
    out={}
    for g,ms in GROUPS.items():
        avail=[(WEIGHTS[m],M[m]) for m in ms if M.get(m) is not None]
        out[g]=round(sum(w*s for w,s in avail)/sum(w for w,_ in avail),1) if avail else None
    return out

def run(proxies, date=None, history='history/ti_history_v2.csv', note=''):
    date = date or datetime.date.today().isoformat()
    M, missing = mechanism_scores(proxies)
    raw = composite(M)
    disp = round(to_display(raw))
    name, act = band(disp)
    groups = group_scores(M)

    print(f"\n🌷 鬱金香指標 v2.0 ｜ {date}")
    print(f"   TI = {disp} / 100   狀態：{name}")
    print(f"   (內部raw {raw} → 顯示刻度；顯示90=raw70=引信備妥)")
    print(f"   行動：{act}\n")
    print("   三組摘要：")
    for g,s in groups.items():
        print(f"     {g:<18} {s}")
    print("\n   七機制(底層)：")
    for m in WEIGHTS:
        flag = f"  ⚠未驗證:{missing[m]}" if missing[m] else ""
        print(f"     {m} {NAMES[m]:<10} 權重{int(WEIGHTS[m]*100):>2}%  分 {M[m]}{flag}")

    # 寫入 history (含每代理原始百分位，供日後算轉折/累積窗)
    os.makedirs(os.path.dirname(history), exist_ok=True)
    flat = {f"{m}.{p}":v for m,ps in proxies.items() for p,v in ps.items()}
    header = ['date','TI_display','TI_raw','state'] + list(WEIGHTS) + \
             list(GROUPS) + sorted(flat) + ['unverified','note']
    row = {'date':date,'TI_display':disp,'TI_raw':raw,'state':name,
           **{m:M[m] for m in WEIGHTS}, **groups, **flat,
           'unverified':';'.join(f"{m}:{','.join(v)}" for m,v in missing.items() if v),
           'note':note}
    newfile = not os.path.exists(history)
    with open(history,'a',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=header)
        if newfile: w.writeheader()
        w.writerow(row)
    return disp, raw, name, groups, M


# ================= 當期輸入 (2026-06-22；百分位為首次bootstrap估計) =================
if __name__ == '__main__':
    PROXIES = {
        'M1': {'hy_oas': 10, 'hy_ig': 30, 'bdc_navdisc_gate': 80},
        'M2': {'hyperscaler_capex_trigger_x_gate': 30, 'ai_credit_fast': 25},
        'M3': {'ipo_withdrawal_rate': 15, 'inflow_decel': 45},
        'M4': {'margin_debt_yoy': 88, 'ai_debt_growth': 85},
        'M5': {'mag7_share': 88, 'xasset_corr': 68},
        'M6': {'breadth_200dma': 30, 'vix_term': 20, 'drawdown_ath': 18},
        'M7': {'ipo_first_day_pop_fomo': 88, 'us_sentiment_positioning': 80},
    }
    run(PROXIES, date='2026-06-22',
        note='首次v2 live;百分位bootstrap;放大器滿/引信冷/確認趴;單一火星=BDC')
