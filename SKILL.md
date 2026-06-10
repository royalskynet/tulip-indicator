---
name: tulip-indicator
description: >
  鬱金香指標（Tulip Indicator, TI）——泡沫崩解型大回調傳導鏈監測系統。
  合成四層指標（A 倉位→B 邊緣流動性→C 信貸→D 結構確認）為 0–100 的鬱金香值。
  觸發：「跑一次鬱金香指標」「今天 TI 多少」「鬱金香日報」「TI 更新」「bubble check」
metadata:
  emoji: "🌷"
  type: rigid
---

# 鬱金香指標執行 Skill

**這是 RIGID skill。觸發後立即執行全部步驟，不要先描述你要做什麼，不要詢問確認，直接開始搜尋。**

## 觸發詞

**指令**：`!ti`（精確比對，立即執行）

**自然語言**：「跑一次鬱金香指標」「鬱金香指標」「TI 日報」「鬱金香日報」「今天 TI 多少」「TI 更新」「bubble check」「鬱金香值」

---

## 執行步驟（觸發後立即按順序執行，不跳步）

### STEP 1：立刻執行以下 15 次搜尋，拿到即時數值

用 web_search 逐一搜尋，每項都要拿到實際數字，抓不到的標「未驗證」：

```
A1: "NAAIM Exposure Index latest 2026"
A2a: "AAII asset allocation survey stock allocation latest 2026"
A2b: "AAII sentiment survey bearish percentage latest 2026"
A3: "BofA Global Fund Manager Survey cash level latest 2026"
A4: "FINRA margin debt statistics YoY 2026"
A5: "台股融資餘額最新"
B1: "ARKK SPY 3 month performance comparison 2026"
B2: "Bitcoin dominance BTC.D latest June 2026"
B3: "IPO withdrawn pulled 2026" + "junk bond deal pulled 2026"
B4a: "台股當沖比例最新"
B4b: "台股新開戶數最新 2026"
C1: "ICE BofA US high yield OAS spread basis points 2026"
C2: "CoreWeave AI data center bond financing 2026"
C3: "BDC price to NAV discount average 2026"
D1: "S&P 500 percent stocks above 200 day moving average 2026"
D2: "VIX VIX3M current value June 2026"
D3: "initial jobless claims 4 week moving average 2026"
```

### STEP 2：套入計分規則（每項 0=綠 / 1=黃 / 2=紅）

| 層 | 代碼 | 🟡（1分） | 🔴（2分） |
|---|---|---|---|
| A 倉位（/10） | A1 | NAAIM >90 持續四週 | 四週內從 >90 急降至 <60 |
| | A2 | 股票配置 >70% | >70% 且現金 <15% 且空頭情緒 >40% |
| | A3 | BofA 現金 <4% | 單月從 <4% 跳升 >0.5pp |
| | A4 | YoY >+25% | YoY 由正轉負 |
| | A5 | 融資創高且增速 > 大盤 | 大盤距高點 <5% 但融資連兩週降 |
| B 邊緣（/8） | B1 | ARKK/SPY 見頂回落而 SPY 創新高 | 背離 >2 個月 |
| | B2 | BTC.D 上升且山寨普跌 | 持續 >1 個月 |
| | B3 | 當月 ≥1 起流標 | 當月 ≥3 起 |
| | B4 | 當沖 >40% 或 新開戶創高 | 兩者同時 |
| C 信貸（/6） | C1 | HY OAS >400bp | >500bp 且四週不回落 |
| | C2 | 利差走闊或評級展望轉負 | 大型借款方再融資失敗 |
| | C3 | BDC 折價 >10% | >15% 且持續擴大 |
| D 結構（/6） | D1 | <50% 站上 200DMA | <40% 且指數距高點 <5% |
| | D2 | VIX > VIX3M 出現 | 倒掛持續 ≥3 日 |
| | D3 | 初領 >260k | >300k 且趨勢向上 |

**各層正規化：**
- A_score = (A實得 / 10) × 100
- B_score = (B實得 / 8) × 100
- C_score = (C實得 / 6) × 100
- D_score = (D實得 / 6) × 100

**TI 公式：**
```
TI_base = 0.20×A_score + 0.30×B_score + 0.30×C_score + 0.20×D_score
```

**組合加成：**
- A1=🔴 且 C1≥🟡 → +10
- A2=🔴 且 B層任一=🔴 → +5
- C2=🔴 → +8
- B3=🔴 → +5

```
TI = min(100, TI_base + 加成)
```

### STEP 3：輸出固定格式報告

```
## 🌷 鬱金香指標 | YYYY-MM-DD
TI = XX（前次 XX，YYYY-MM-DD）　狀態：[平靜/累積期/引信備妥/點火/進行中]

| 層 | 原始分 | 層分 | 亮燈 |
|---|---|---|---|
| A 倉位 | x/10 | xx | A3🟡 ... |
| B 邊緣流動性 | x/8 | xx | ... |
| C 信貸 | x/6 | xx | ... |
| D 結構確認 | x/6 | xx | — |
組合加成：+0（無觸發）/ +xx（條件）
未驗證：...

### 各層明細
[每個亮燈項寫一句說明實際數值與觸發條件]

### 分析（3–5 句）
- 與前次比較
- 當前最值得盯的單一斷點
- 條件時間框架（必須附「歷史類比 n≤5」免責）

### 建議動作
[對應區間的一條建議，不多給]
```

## 區間對照

| TI | 狀態 | 建議 |
|---|---|---|
| 0–20 | 平靜 | 正常配置，每月查 |
| 20–40 | 累積期 | 停止加碼風險，確認組合能扛 -35% |
| 40–60 | 引信備妥 | 現金墊高，B/C 改週查 |
| 60–80 | 點火 | 防禦完成，最後主動窗口 |
| 80–100 | 進行中 | 控損，不在底部被迫賣出 |

## 判讀紀律

- 不得給具體日期預測
- 狀態遷移需連續兩期確認，單期跳區先標「待確認」
- 時間框架只以區間 + 歷史類比（n≤5）表述
- 最高原則：**不被迫在底部賣出**，非精準擇時
