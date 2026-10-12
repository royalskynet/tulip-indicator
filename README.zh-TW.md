# 鬱金香指標（Tulip Indicator, TI）v2.1

> 泛用的「內生型經濟泡沫破滅計」。單一指數 0–100，偵測榮景尾端的**脆弱度累積與點火**——不是估值高低，不是擇時倒數。

[English](README.md) | **繁體中文**

方法論寫在 [`METHODOLOGY.md`](METHODOLOGY.md)（方法論 v2.0），程式碼版本為 v2.1.0。

---

## 快速安裝

純 Python 3.9+ 標準函式庫——不需要任何第三方相依套件，也不用編譯。

```bash
git clone https://github.com/royalskynet/tulip-indicator && cd tulip-indicator && ./tulip.py
```

這一行就完成：抓下程式、算出指數、印出完整報告（顯示刻度 TI、區間與行動建議、三組摘要、七機制分數），並把這次執行追加到 `history/ti_history_v2.csv`。

**想要直接用 `tulip` 指令？**

```bash
pip install "tulip-indicator @ git+https://github.com/royalskynet/tulip-indicator" && tulip --version
```

**想當成 Claude skill 來跑？** repo 內附 `SKILL.md`（RIGID 觸發詞與逐步執行流程），把 clone 放進你的 skills 目錄即可：

```bash
git clone https://github.com/royalskynet/tulip-indicator ~/.claude/skills/tulip-indicator
```

需求：Python 3.9 以上、`git`，以及連網才能自動抓 FRED（可選，見[更新代理數值](#更新代理數值)）。`tulip.py` 在 git 裡就帶執行權限，clone 之後不必再 `chmod`。

---

## 這是什麼

TI 把跨所有內生泡沫都成立的因果鏈拆成**七個機制（M1–M7）**，每個機制用當代最貼切的代理變數量測，對各自的歷史分佈取**連續百分位**，再加權合成 0–100 的「鬱金香值」。100 ＝ 泡沫破滅的傳導正在發生（1637 鬱金香、1929、2000、2008 那一刻）。

> 不在範圍：外生衝擊（疫情、開戰、天災）。那是另一類事件，本指標不混入、不設 override。

---

## 七機制

| 代碼 | 機制（不變骨架） | 2026 權重 | 角色 |
|---|---|---|---|
| **M1** | 信貸計價 · Credit pricing（影子銀行錯配） | 25% | 領頭＋脈衝源 |
| **M2** | 資本支出轉折 · Capex inflection（實體產能） | 18% | 領頭 |
| **M3** | 邊際買家枯竭 · Marginal-buyer exhaustion | 14% | 領頭 |
| **M4** | 槓桿 · Leverage／信用擴張 | 10% | 嚴重度放大器 |
| **M5** | 集中度／偽分散 · Concentration | 10% | 結構 |
| **M6** | 結構確認 · Structural confirmation（同步點火） | 15% | 脈衝源／確認 |
| **M7** | 情緒／全民化 · Sentiment／retail mania | 8% | 油表 |

機制是**不變骨架**，代理隨時代替換（1929 券商 call loan → 2000 dot-com IPO → 2008 房貸證券化 → 2026 AI capex × 私募信貸 × 被動 ETF 集中）。權重隨當代主流泡沫結構浮動，規則見 `METHODOLOGY.md` §8。

---

## 三組摘要

七機制在底層計算，報告層收斂成三組，一眼看懂「柴、火、燒」。

| 組 | 含機制 | 讀什麼 |
|---|---|---|
| 放大器（乾柴多高） | M4 + M5 + M7 | 結構多脆、爆了多慘（可高位盤旋數年） |
| 領先引信（火星點了沒） | M1 + M2 + M3 | 領先轉折是否開始——**這組才是計時器** |
| 確認（燒起來沒） | M6 | 災難是否正在傳導，亮即 90→100 那一哩 |

**判讀口訣：** 放大器高＋引信低＋確認趴 ＝ 滿地汽油、火柴未劃（累積期）。最該盯的是「領先引信」由低轉高那一刻，而非總分絕對值。

---

## 顯示刻度與區間

內部 raw 危險線在 70，對外做單調映射把危險線推到直覺的 **90**。顯示 90 ＝ 引信備妥／危險線；90–100 ＝ 那段幾天的脈衝。

| TI（顯示） | 狀態 | 行動 |
|---|---|---|
| 0–50 | 平靜 | 正常配置，每月查 |
| 50–75 | 累積 | 停止加碼風險，壓力測試組合能否扛 −35% |
| 75–90 | 警戒／逐步退場 | **逐步退場窗口，90 前退完**；改每週查 |
| 90–100 | 進行中／太晚 | 控損，不在底部被迫賣 |

**關於跳機點：** 不要把跳傘設在 90。看到 90，那一哩已在進行、你是賣在下殺裡。**理想是 75 起分批退、90 前退完。** 75–90 是行動線，90 之後是描述線。

---

## 執行方式

```
./tulip.py                      # 單檔入口（只用標準函式庫）
./tulip.py --no-fred            # 跳過 FRED 自動抓取
./tulip.py --show               # 印出本次採用的代理百分位後結束
./tulip.py --set M1.hy_oas=45 --set M4.margin_debt_yoy=92
./tulip.py --selftest           # 內建自我檢查
./tulip.py --version

python3 -m tulip                # 裝成套件後的另一種呼叫方式
```

| 參數 | 作用 |
|---|---|
| `--no-fred` | 跳過 FRED 自動抓取，只用內附的手動百分位計分 |
| `--set MECH.PROXY=PCT` | 覆寫單一代理百分位（可重複）；填 `none` 標為未驗證 |
| `--show` | 印出解析後的代理 JSON 後結束，不計分 |
| `--date YYYY-MM-DD` | 指定執行日期（預設今天） |
| `--history PATH` | 歷史 CSV（預設 `history/ti_history_v2.csv`，不存在會自動建立） |
| `--note TEXT` | 隨該筆記錄一起存下的自由註記 |
| `--window N` | 百分位視窗天數（預設 756） |
| `--version` | 印出版本 |
| `--selftest` | 只有 `tulip.py` 有：跑內建斷言 |

煙霧測試（smoke test）：

```bash
PYTHONPATH=. python3 tests/test_smoke.py
```

（若已安裝 pytest，`python3 -m pytest tests/` 也可以。）

### 更新代理數值

只要環境變數或工作目錄下的 `.env` 有 `FRED_API_KEY`，下列兩項會自動從 FRED 抓：

- `M1.hy_oas` —— FRED 序列 `BAMLH0A0HYM2`（高收益債 OAS）
- `M1.hy_ig` —— FRED 序列 `BAMLH0A0HYM2` − `BAMLC0A0CM`，即高收益減投資等級的利差

其餘代理都是**手動百分位**，記在 `tulip/proxies.json`（單檔版 `tulip.py` 內嵌同樣數值）。每次跑之前要更新，也可以交給 `SKILL.md` 裡的 Claude skill 去抓數與計分；單項覆寫用 `--set M1.hy_oas=45`。沒有 API key 也跑得動，只是用內附數值，並且會在 stderr 提醒你。

```bash
echo "FRED_API_KEY=你的key" > .env
```

`.env` 已在 .gitignore 裡，絕對不要把 key 提交上去。

### 交給 AI 代理執行

對 Claude 說：「跑一次鬱金香指標」／`!ti`／"run the Tulip Indicator"。代理會依 `indicators.yaml` 的清單逐項抓數、對各自歷史窗取百分位、加權七機制、輸出顯示 TI ＋ 三組摘要、追加到 `history/ti_history_v2.csv`，並依 `SKILL.md` 的格式產出紅黃綠燈報告。`CLAUDE.md` 是同一套流程更完整的版本，任何型號（含 Sonnet）都能接手。

**頻率：** TI < 50 每月；50–75 每週查領先引信；> 75 全表每週，M6 可每日。

---

## 檔案

| 檔案 | 說明 |
|---|---|
| `tulip.py` | 單檔、純標準函式庫入口——clone 完就能跑 |
| `tulip/cli.py` | CLI：抓 FRED、`--set` 覆寫、產報告、寫歷史 |
| `tulip/score.py` | 計分引擎：代理百分位 → 機制 → raw → 顯示 TI ＋ 三組摘要 |
| `tulip/fred.py` | FRED 取數與百分位／利差換算 |
| `tulip/proxies.json` | 未自動抓取之代理的手動百分位 |
| `METHODOLOGY.md` | 完整 v2 方法論：七機制、百分位計分、權重、顯示刻度、否證測試 |
| `indicators.yaml` | 機讀規格：每個代理的抓數指令、transform、視窗、閾值 |
| `SKILL.md` | RIGID skill 觸發與步驟 |
| `CLAUDE.md` | AI 代理執行指令（任何型號含 Sonnet 可接手） |
| `history/ti_history_v2.csv` | v2 歷次讀數紀錄（每代理原始值＋百分位） |
| `history/ti_history.csv` | 已棄用的 v1.1 紀錄（schema 不同，保留為歷史） |
| `CHANGELOG.md` | 版本／權重修訂紀錄——防止為了分數好看而調規則 |
| `tests/test_smoke.py` | 百分位、利差對齊、合併、覆寫與區間的煙霧測試 |

---

## 判讀紀律

- **不為過去擬合：** 2000/2008 只當否證抓壞代理，禁止為了命中歷史而調權重（n≤5，擬合＝自欺）。
- **連續兩期確認遷移：** 單期跳區先標「待確認」。
- **不給具體日期：** 時間框架只以區間 ＋ 歷史類比表述。
- **分數不為情緒讓步：** 不得因讀者的倉位或情緒調整任何代理分數。

---

## 免責

本指數刻意偏領先（M1+M2+M3 共 57% 權重），會提前示警、有空頭假訊號、會在高位卡很久——這是特性不是失靈。時間框架基於 n≤5 的歷史類比，是條件區間而非預測。最高原則：**不被迫在底部賣出**，而非精準擇時。本專案不構成投資建議。