# Claude Code 量化交易技能與指令完整指南

> 本文件整合三個主要 Claude Code 擴充資源，針對量化交易與 Freqtrade 使用情境提供完整參考。
>
> 建立日期：2026-03-21

---

## 目錄

1. [資源總覽](#1-資源總覽)
2. [TraderMonty Claude Trading Skills](#2-tradermonty-claude-trading-skills)
3. [wshobson/commands — 57 個斜線指令](#3-wshobsoncommands--57-個斜線指令)
4. [wshobson/agents — 72 個外掛模組](#4-wshobsonagents--72-個外掛模組)
5. [安裝說明](#5-安裝說明)
6. [量化交易 / Freqtrade 最實用推薦](#6-量化交易--freqtrade-最實用推薦)
7. [工作流程範例](#7-工作流程範例)

---

## 1. 資源總覽

| 資源 | 類型 | 數量 | 主要用途 | API 需求 |
|------|------|------|----------|----------|
| [TraderMonty Trading Skills](https://tradermonty.github.io/claude-trading-skills/en/skills/) | 交易專用 Skills | 52 個技能 | 股票/量化分析 | 部分需要 FMP/FINVIZ/Alpaca |
| [wshobson/commands](https://github.com/wshobson/commands) | 斜線指令集 | 57 個指令 | 軟體開發自動化 | 不需要 |
| [wshobson/agents](https://github.com/wshobson/agents) | AI 代理外掛 | 72 個外掛 / 112 個代理 | 多代理協作開發 | 不需要 |

---

## 2. TraderMonty Claude Trading Skills

**網站**：https://tradermonty.github.io/claude-trading-skills/en/skills/
**GitHub**：https://github.com/tradermonty/claude-trading-skills

### 2.1 專案說明

這是專為股票投資者與量化交易者設計的 52 個 Claude Skills 合集，涵蓋從市場篩選、技術分析、策略開發到回測評估的完整工作流程。

標有 ★ 的技能為手寫詳細指南，包含 10 個章節與完整範例，品質較高。

### 2.2 API 需求說明

| API 服務 | 費用 | 需要此 API 的技能 |
|----------|------|------------------|
| **FMP (Financial Modeling Prep)** | 免費版每日 250 次請求 | 14 個以上技能 |
| **FINVIZ Elite** | $39.50/月 或 $299.50/年 | 4 個以上技能（可選） |
| **Alpaca** | 紙幣交易免費 | Portfolio Manager |
| **無 API** | 免費 | Market Breadth Analyzer、Position Sizer、Backtest Expert 等多數技能 |

環境變數設定：
```bash
export FMP_API_KEY="your_key"
export FINVIZ_API_KEY="your_key"
export ALPACA_API_KEY="your_key"
export ALPACA_SECRET_KEY="your_secret"
export ALPACA_PAPER="true"
```

### 2.3 完整技能清單

#### 篩選與偵測（8 個技能）

| 技能名稱 | 說明 | API 需求 |
|----------|------|----------|
| **FinViz Screener** ★ | 從自然語言建立 FinViz 篩選器 URL | FINVIZ（可選） |
| **CANSLIM Screener** ★ | 使用 William O'Neil 成長方法論篩選股票 | FMP |
| **VCP Screener** ★ | Mark Minervini 波動收縮形態篩選 | FMP |
| **Theme Detector** ★ | 跨板塊偵測市場主題 | 無 |
| **FTD Detector** | 使用 O'Neil 方法論確認市場底部 | FMP |
| **Market Top Detector** | 透過派發日與惡化信號偵測市場頂部 | FMP |
| **Dividend Growth Pullback Screener** | 篩選年增長率 12%+ 的高質量股息股回撤 | FMP |
| **Value Dividend Screener** | 篩選本益比低於 20、市淨率與股息組合 | FMP |

#### 分析與研究（15 個技能）

| 技能名稱 | 說明 | API 需求 |
|----------|------|----------|
| **US Stock Analysis** ★ | 基本面、技術面、估值全面分析 | FMP |
| **Market Breadth Analyzer** ★ | 使用公開 CSV 數據量化市場廣度 | 無（本地 CSV）|
| **Market News Analyst** ★ | 分析影響市場的重大新聞事件 | 無 |
| **US Market Bubble Detector** ★ | 數據驅動的泡沫風險評估 | FMP |
| **Technical Analyst** | 股票與指數的週線圖技術分析 | FMP |
| **Sector Analyst** | 板塊輪動與週期定位分析 | 無 |
| **Uptrend Analyzer** | 市場廣度診斷工具 | 無（本地 CSV）|
| **Breadth Chart Analyst** | S&P 500 廣度指數分析 | 無（本地 CSV）|
| **Macro Regime Detector** | 1-2 年視野的結構性轉變偵測 | 無 |
| **Market Environment Analysis** | 綜合市場環境報告 | FMP |
| **Institutional Flow Tracker** | 透過 13F 申報追蹤機構持倉 | FMP |
| **Earnings Calendar** | 獲取即將到來的財報日程 | FMP（必要）|
| **Earnings Trade Analyzer** | 財報後分析（5 因子評分） | FMP（必要）|
| **Economic Calendar Fetcher** | 經濟事件與數據發布日程 | FMP（必要）|
| **PEAD Screener** | 財報後公告漂移型態篩選 | FMP（必要）|

#### 倉位與投資組合管理（5 個技能）

| 技能名稱 | 說明 | API 需求 |
|----------|------|----------|
| **Position Sizer** ★ | 多頭交易的風險基礎倉位計算 | 無 |
| **Portfolio Manager** | 透過 Alpaca MCP Server 進行組合分析 | Alpaca（必要）|
| **Kanchi Dividend SOP** | 將股息投資轉換為可重複流程 | 無 |
| **Kanchi Dividend Review Monitor** | 強制審查觸發器監控 | 無 |
| **Kanchi Dividend US Tax Accounting** | 稅務與帳戶配置工作流程 | 無 |

#### 策略開發（10 個技能）

| 技能名稱 | 說明 | API 需求 |
|----------|------|----------|
| **Backtest Expert** ★ | 系統性回測評估與評分（0-100 分） | 無 |
| **Edge Candidate Agent** | 從日終觀察生成研究票據 | 無 |
| **Edge Concept Synthesizer** | 將提示抽象為可重複使用的概念 | 無 |
| **Edge Hint Extractor** | 從日常觀察與新聞提取交易線索 | 無 |
| **Edge Pipeline Orchestrator** | 從偵測到設計的完整管道 | 無 |
| **Edge Signal Aggregator** | 跨多個邊際發現技能排名信號 | 無 |
| **Edge Strategy Designer** | 將概念轉換為策略草稿 | 無 |
| **Edge Strategy Reviewer** | 審查合理性與過度擬合問題 | 無 |
| **Strategy Pivot Designer** | 生成結構性轉折提案 | 無 |
| **Stanley Druckenmiller Investment** | 整合 8 個上游技能輸出的投資分析 | FMP |

#### 專業工具（7 個技能）

| 技能名稱 | 說明 | API 需求 |
|----------|------|----------|
| **Trade Hypothesis Ideator** | 從數據生成可偽證假說 | 無 |
| **Pair Trade Screener** | 統計套利識別 | FMP |
| **Options Strategy Advisor** | 選擇權分析與模擬 | FMP |
| **Scenario Analyzer** | 將新聞轉換為 18 個月情景分析 | 無 |
| **Trader Memory Core** | 追蹤交易論點全生命週期 | 無 |
| **Data Quality Checker** | 驗證分析文件品質 | 無 |
| **Skill Integration Tester** | 驗證多技能工作流程 | 無 |

#### 技能撰寫工具（3 個技能）

| 技能名稱 | 說明 |
|----------|------|
| **Skill Designer** | 從規格建立新技能 |
| **Skill Idea Miner** | 從會話日誌提取想法 |
| **Dual Axis Skill Reviewer** | 使用決定性檢查進行技能審查 |

### 2.4 重點技能深度說明

#### Backtest Expert（回測專家）★ 強烈推薦

**哲學**：採用對抗性思維，問「什麼會讓這個策略失敗？」而非只關注獲利指標。

**5 維度評分系統（各 20 分，總分 100 分）**：

| 維度 | 評估內容 |
|------|----------|
| 樣本量（Sample Size） | 交易次數是否足夠統計顯著 |
| 期望值（Expectancy） | 正期望值與風險報酬比 |
| 風險管理（Risk Management） | 最大回撤與倉位控制 |
| 穩健性（Robustness） | 參數敏感度與過度擬合測試 |
| 執行真實性（Execution Realism） | 滑點、手續費假設是否合理 |

**判決系統**：
- **Deploy（部署）**：策略可投入實盤
- **Refine（精煉）**：策略需要調整
- **Abandon（放棄）**：策略存在根本性問題

**警告旗標（10 種）**：
- 交易次數不足
- 負期望值
- 參數過度擬合
- 過大回撤
- 未測試執行成本
- 太高的勝率（可能是 look-ahead bias）

**使用範例**：
```bash
python3 skills/backtest-expert/scripts/evaluate_backtest.py \
  --total-trades 150 \
  --win-rate 62 \
  --avg-win-pct 1.8 \
  --avg-loss-pct 1.2 \
  --max-drawdown-pct 15 \
  --years-tested 8 \
  --num-parameters 3 \
  --slippage-tested \
  --output-dir reports/
```

#### Position Sizer（倉位計算器）★ 強烈推薦

**三種計算方法**：

| 方法 | 輸入 | 最適用場景 |
|------|------|------------|
| **Fixed Fractional（固定比例法）** | 進場價、停損價、風險% | 裁量交易，有技術停損 |
| **ATR-Based（ATR 法）** | 進場價、ATR、乘數、風險% | 系統化交易，波動率標準化 |
| **Kelly Criterion（凱利公式）** | 勝率、平均盈虧比 | 已驗證系統的資金配置 |

**最佳實踐**：
- 每筆交易預設風險 1%（波段交易行業標準）
- 永遠向下取整到整數股數
- 使用 Half Kelly（半凱利），不要全凱利
- 所有開放倉位總風險不超過帳戶 6-8%
- 連續虧損後降低至 0.5% 風險

```bash
python3 skills/position-sizer/scripts/position_sizer.py \
  --account-size 100000 \
  --entry 155 \
  --stop 148.50 \
  --risk-pct 1.0 \
  --output-dir reports/
# 結果：153 股，風險 $994.50（帳戶的 0.99%）
```

---

## 3. wshobson/commands — 57 個斜線指令

**GitHub**：https://github.com/wshobson/commands
**Stars**：2,200+，Forks：240+

### 3.1 專案說明

提供 57 個生產就緒的斜線指令（15 個工作流程 + 42 個工具），為 Claude Code 提供智慧自動化與多代理協作能力。主要針對軟體開發場景，但有多個工具對量化策略開發極有幫助。

**執行時間**：
- 工作流程（Workflows）：30-90 秒（多代理協作）
- 工具（Tools）：5-30 秒（單一功能）

### 3.2 安裝方法

```bash
# 方法一：直接克隆（推薦）
cd ~/.claude
git clone https://github.com/wshobson/commands.git

# 使用方式（帶前綴）
/workflows:feature-development OAuth2 authentication
/tools:security-scan vulnerability assessment

# 方法二：複製到根目錄（無前綴使用）
cp ~/.claude/commands/tools/*.md ~/.claude/
cp ~/.claude/commands/workflows/*.md ~/.claude/
/security-scan vulnerability assessment
```

### 3.3 工作流程指令（15 個）

#### 核心開發

| 指令 | 說明 | 使用時機 |
|------|------|----------|
| `/workflows:feature-development` | 端到端功能實現 | 開發新交易功能模組 |
| `/workflows:full-review` | 多視角代碼分析 | 審查策略代碼品質 |
| `/workflows:smart-fix` | 智能問題解決 | 調試策略邏輯錯誤 |
| `/workflows:tdd-cycle` | 測試驅動開發編排 | 為新策略建立測試套件 |

#### 流程自動化

| 指令 | 說明 |
|------|------|
| `/workflows:git-workflow` | 版本控制流程自動化 |
| `/workflows:improve-agent` | 代理優化 |
| `/workflows:legacy-modernize` | 遺留代碼庫現代化 |
| `/workflows:multi-platform` | 跨平台開發 |
| `/workflows:workflow-automate` | CI/CD 管道自動化 |

#### 進階協作

| 指令 | 說明 |
|------|------|
| `/workflows:full-stack-feature` | 多層級功能實現 |
| `/workflows:security-hardening` | 安全優先開發 |
| `/workflows:data-driven-feature` | ML 驅動功能 |
| `/workflows:performance-optimization` | 全系統性能優化 |
| `/workflows:incident-response` | 生產問題解決 |

### 3.4 工具指令（42 個）

#### AI 與機器學習（4 個）

| 指令 | 說明 |
|------|------|
| `/tools:ai-assistant` | LLM 整合與對話管理 |
| `/tools:ai-review` | ML 代碼審查 |
| `/tools:langchain-agent` | LangChain 代理建立 |
| `/tools:prompt-optimize` | 提示工程優化 |

#### 代理協作（3 個）

| 指令 | 說明 |
|------|------|
| `/tools:multi-agent-review` | 多視角代碼審查 |
| `/tools:multi-agent-optimize` | 協調性能優化 |
| `/tools:smart-debug` | 輔助調試 |

#### 架構與代碼品質（4 個）

| 指令 | 說明 |
|------|------|
| `/tools:code-explain` | 代碼文件化說明 |
| `/tools:code-migrate` | 遷移自動化 |
| `/tools:refactor-clean` | 代碼改善 |
| `/tools:tech-debt` | 技術債務評估 |

#### 數據與資料庫（3 個）

| 指令 | 說明 |
|------|------|
| `/tools:data-pipeline` | ETL/ELT 架構 |
| `/tools:data-validation` | 數據品質驗證 |
| `/tools:db-migrate` | 資料庫遷移 |

#### DevOps 與基礎設施（5 個）

| 指令 | 說明 |
|------|------|
| `/tools:deploy-checklist` | 部署前準備清單 |
| `/tools:docker-optimize` | 容器優化 |
| `/tools:k8s-manifest` | Kubernetes 配置 |
| `/tools:monitor-setup` | 可觀測性設置 |
| `/tools:slo-implement` | SLO/SLI 定義 |

#### 測試與開發（6 個）

| 指令 | 說明 |
|------|------|
| `/tools:api-mock` | Mock 生成 |
| `/tools:api-scaffold` | API 端點建立 |
| `/tools:test-harness` | 測試套件生成 |
| `/tools:tdd-red` | 先寫測試（紅燈）|
| `/tools:tdd-green` | 實現邏輯（綠燈）|
| `/tools:tdd-refactor` | 重構優化（重構）|

#### 安全與合規（3 個）

| 指令 | 說明 |
|------|------|
| `/tools:accessibility-audit` | WCAG 合規檢查 |
| `/tools:compliance-check` | 法規合規驗證 |
| `/tools:security-scan` | 漏洞評估 |

#### 調試與分析（4 個）

| 指令 | 說明 |
|------|------|
| `/tools:debug-trace` | 執行期分析 |
| `/tools:error-analysis` | 錯誤模式分析 |
| `/tools:error-trace` | 生產調試 |
| `/tools:issue` | 問題追蹤 |

#### 依賴與配置（3 個）

| 指令 | 說明 |
|------|------|
| `/tools:config-validate` | 配置管理 |
| `/tools:deps-audit` | 依賴分析 |
| `/tools:deps-upgrade` | 版本管理 |

#### 文件與協作（3 個）

| 指令 | 說明 |
|------|------|
| `/tools:doc-generate` | API 文件生成 |
| `/tools:pr-enhance` | PR 優化 |
| `/tools:standup-notes` | 狀態報告 |

#### 操作與上下文（4 個）

| 指令 | 說明 |
|------|------|
| `/tools:cost-optimize` | 資源優化 |
| `/tools:onboard` | 環境設置 |
| `/tools:context-save` | 狀態保存 |
| `/tools:context-restore` | 狀態恢復 |

---

## 4. wshobson/agents — 72 個外掛模組

**GitHub**：https://github.com/wshobson/agents

### 4.1 專案說明

生產就緒的智能自動化系統，包含：
- **72 個專注外掛**（24 個分類）
- **112 個專業代理**（各具領域知識）
- **146 個代理技能**（漸進式知識載入）
- **79 個開發工具**
- **16 個多代理協作工作流程**

每個外掛平均僅載入 3.4 個組件，最小化 token 消耗。

### 4.2 安裝方法

```bash
# 步驟一：加入市場
/plugin marketplace add wshobson/agents

# 步驟二：瀏覽可用外掛
/plugin

# 步驟三：安裝所需外掛
/plugin install python-development
/plugin install data-ml-pipeline
/plugin install quantitative-trading   # 量化交易專用
/plugin install security-scanning
/plugin install comprehensive-review

# 注意：安裝外掛（非個別代理）
# ✅ 正確
/plugin install javascript-typescript@claude-code-workflows
# ❌ 錯誤
/plugin install typescript-pro
```

**快取清除（如遇問題）**：
```bash
rm -rf ~/.claude/plugins/cache/claude-code-workflows
rm ~/.claude/plugins/installed_plugins.json
```

### 4.3 三層模型策略

| 層級 | 模型 | 代理數 | 適用任務 |
|------|------|--------|----------|
| Tier 1 | Opus 4.6 | 42 個 | 關鍵架構、安全、代碼審查 |
| Tier 2 | Inherit（繼承）| 42 個 | 複雜任務（跟隨會話設定）|
| Tier 3 | Sonnet 4.6 | 51 個 | 支援任務（文件、測試、調試）|
| Tier 4 | Haiku 4.5 | 18 個 | 快速操作（SEO、部署、簡單文件）|

```bash
# 設定預設模型
claude --model opus    # 用於複雜分析
claude --model sonnet  # 一般使用
```

### 4.4 主要代理分類

#### 架構與代碼審查
- `architect-review`、`code-reviewer`、`security-auditor`、`performance-auditor`

#### Python 開發
- `python-pro`、`django-pro`、`fastapi-pro`

#### 後端與 API
- `backend-architect`、`database-architect`、`microservices-architect`

#### AI 與機器學習
- `ml-engineer`、`data-scientist`、`ai-architect`、`llm-specialist`、`prompt-engineer`

#### 數據工程
- `data-engineer`、`database-specialist`

#### 基礎設施與 DevOps
- `kubernetes-architect`、`cloud-architect`、`infrastructure-engineer`、`deployment-engineer`、`ci-cd-engineer`

#### 測試與品質
- `test-automator`、`qa-engineer`、`performance-engineer`

#### **量化交易專用外掛**
```bash
/plugin install quantitative-trading
```
描述：「演算法交易與風險管理」— 涵蓋算法交易與量化風險管理能力。

### 4.5 多代理工作流程範例

```bash
# 全棧功能開發（協調 7+ 個代理）
/full-stack-orchestration:full-stack-feature "user authentication with OAuth2"

# 安全強化
/security-scanning:security-hardening --level comprehensive

# Python 項目建立
/python-development:python-scaffold fastapi-microservice

# Kubernetes 部署
/kubernetes-operations:deploy --environment production

# 代理團隊平行審查
/plugin install agent-teams@claude-code-workflows
/team-review src/ --reviewers security,performance,architecture
/team-debug "API returns 500" --hypotheses 3

# Conductor：上下文驅動開發
/plugin install conductor@claude-code-workflows
/conductor:setup          # 建立項目結構
/conductor:new-track      # 生成規格說明
/conductor:implement      # 執行並驗證
/conductor:revert         # 語義撤銷
```

---

## 5. 安裝說明

### 5.1 TraderMonty Trading Skills 安裝

#### Claude Web App
```
1. 下載 skill-packages/ 目錄中的 .skill 壓縮檔
2. 開啟 Claude → 設定 → Skills → 上傳 ZIP 檔
3. 在對話中啟用所需技能
```

#### Claude Code（桌面/CLI）
```bash
# 克隆倉庫
git clone https://github.com/tradermonty/claude-trading-skills.git

# 複製技能資料夾到 Claude Code Skills 目錄
# 路徑通常為 ~/.claude/skills/ 或透過設定 → Skills → 開啟技能資料夾

# 重新啟動 Claude Code 以偵測新技能
```

### 5.2 wshobson/commands 安裝

```bash
cd ~/.claude
git clone https://github.com/wshobson/commands.git

# 驗證安裝
ls ~/.claude/commands/
# 應該看到 workflows/ 和 tools/ 目錄
```

### 5.3 wshobson/agents 安裝

```bash
# 在 Claude Code 中執行
/plugin marketplace add wshobson/agents

# 安裝推薦外掛
/plugin install python-development
/plugin install quantitative-trading
/plugin install data-ml-pipeline
/plugin install comprehensive-review
/plugin install backend-development
```

---

## 6. 量化交易 / Freqtrade 最實用推薦

### 6.1 核心必裝（★★★）

| 技能/指令 | 來源 | 為何重要 |
|-----------|------|----------|
| **Backtest Expert** ★ | TraderMonty | 系統性評估回測品質，防止過度擬合，直接適用 Freqtrade 回測結果分析 |
| **Position Sizer** ★ | TraderMonty | 三種倉位計算方法，自動強制風險管理規則 |
| **Edge Strategy Reviewer** | TraderMonty | 批判性審查策略合理性與過度擬合 |
| **Edge Pipeline Orchestrator** | TraderMonty | 從偵測到設計的完整策略開發管道 |
| `/tools:data-pipeline` | wshobson/commands | 建立行情數據 ETL 管道（OHLCV 數據處理）|
| `/tools:test-harness` | wshobson/commands | 為策略代碼生成完整測試套件 |
| `quantitative-trading` plugin | wshobson/agents | 演算法交易與量化風險管理代理 |
| `data-scientist` agent | wshobson/agents | 數據分析與統計建模 |
| `ml-engineer` agent | wshobson/agents | FreqAI 機器學習模型開發 |

### 6.2 進階推薦（★★）

| 技能/指令 | 來源 | 應用場景 |
|-----------|------|----------|
| **Market Breadth Analyzer** ★ | TraderMonty | 市場環境過濾，決定是否適合交易 |
| **VCP Screener** ★ | TraderMonty | 動量策略候選標的 |
| **Technical Analyst** | TraderMonty | 週線圖技術分析輔助手動選股 |
| **Trade Hypothesis Ideator** | TraderMonty | 生成可偽證的交易假說（對應 Freqtrade 信號邏輯）|
| **Scenario Analyzer** | TraderMonty | 宏觀情景分析（風險管理輸入）|
| `/workflows:performance-optimization` | wshobson/commands | 優化策略計算性能 |
| `/tools:debug-trace` | wshobson/commands | 調試策略執行期問題 |
| `/tools:data-validation` | wshobson/commands | 驗證行情數據品質 |
| `performance-auditor` agent | wshobson/agents | 分析策略回測性能瓶頸 |

### 6.3 策略開發完整工具鏈

```
新策略想法
    │
    ▼
Edge Hint Extractor（從市場觀察提取線索）
    │
    ▼
Trade Hypothesis Ideator（生成可測試假說）
    │
    ▼
Edge Strategy Designer（轉換為策略草稿）
    │
    ▼
[在 Freqtrade 中實現策略]
    │
    ▼
Backtest Expert（評估回測結果）
    │
    ▼
Edge Strategy Reviewer（批判性審查）
    │
    ▼
Position Sizer（計算倉位大小）
    │
    ▼
Trader Memory Core（記錄策略論點與追蹤）
```

### 6.4 Freqtrade 特定使用場景

#### 回測結果分析
```
1. 執行 Freqtrade 回測：
   freqtrade backtesting --strategy MyStrategy --timerange 20230101-20241231

2. 將以下數據輸入 Backtest Expert：
   - 總交易次數
   - 勝率
   - 平均盈利/虧損百分比
   - 最大回撤
   - 測試年數
   - 參數數量
   - 是否測試滑點

3. 獲得 Deploy/Refine/Abandon 判決
```

#### FreqAI 模型開發
```bash
# 安裝 ML 代理
/plugin install data-ml-pipeline@claude-code-workflows

# 請求 ML 工程師代理協助
"使用 ml-engineer 代理幫我設計 FreqAI 的特徵工程管道，
 目標是預測 BTC/USDT 的 4 小時 K 線方向"
```

#### 多時間框架策略開發
```bash
# 使用 TDD 工作流程
/workflows:tdd-cycle "多時間框架動量策略，使用 15 分鐘與 4 小時 K 線"

# 測試套件生成
/tools:test-harness "為 Freqtrade 自訂策略 class 生成單元測試"

# 代碼審查
/tools:multi-agent-review "審查此 Freqtrade 策略的信號邏輯品質"
```

---

## 7. 工作流程範例

### 7.1 新策略完整開發流程

```bash
# 步驟 1：生成策略想法
# （使用 TraderMonty Edge Pipeline）
"使用 Edge Hint Extractor 分析今日 BTC 市場觀察..."

# 步驟 2：設計策略草稿
# （使用 Edge Strategy Designer）
"基於以上線索，用 Edge Strategy Designer 生成策略草稿"

# 步驟 3：實現代碼
/workflows:feature-development "Freqtrade 動量策略，含 RSI + EMA 交叉信號"

# 步驟 4：建立測試
/workflows:tdd-cycle "策略信號邏輯單元測試"

# 步驟 5：回測評估（在 Freqtrade 執行回測後）
"使用 Backtest Expert 評估此回測結果：
 - 總交易：234 筆
 - 勝率：58%
 - 平均盈利：1.6%
 - 平均虧損：1.1%
 - 最大回撤：12%
 - 測試期間：3 年
 - 參數數量：4 個"

# 步驟 6：倉位計算
"使用 Position Sizer 計算：
 帳戶 $50,000，進場 $45,000 BTC，停損 $42,500，風險 1%"

# 步驟 7：保存上下文
/tools:context-save "BTC 動量策略 v1.0 開發進度"
```

### 7.2 市場環境評估工作流程

```bash
# 每日市場評估程序

# 1. 市場廣度分析
"使用 Market Breadth Analyzer 分析今日市場廣度狀況"

# 2. 市場環境判斷
"使用 Market Environment Analysis 生成今日市場環境報告"

# 3. 宏觀情景評估
"使用 Macro Regime Detector 判斷當前宏觀政策環境"

# 4. 根據市場環境調整倉位
"根據市場廣度 Zone，調整 Position Sizer 的風險百分比"
```

### 7.3 策略審查工作流程

```bash
# 代碼品質審查
/tools:multi-agent-review "全面審查此 Freqtrade 策略"

# 性能分析
/workflows:performance-optimization "優化策略指標計算速度"

# 安全性檢查（API 金鑰、敏感數據）
/tools:security-scan "掃描交易系統配置安全漏洞"

# 技術債務評估
/tools:tech-debt "評估策略代碼庫的技術債務"
```

---

## 附錄：快速參考卡

### 最常用的量化交易指令

```bash
# 回測評估
Backtest Expert → 5 維度評分，Deploy/Refine/Abandon 判決

# 倉位計算
Position Sizer → 三種方法（Fixed Fractional / ATR / Kelly）

# 策略開發
Edge Pipeline Orchestrator → 完整策略開發管道

# 代碼品質
/tools:multi-agent-review → 多代理代碼審查
/workflows:tdd-cycle → TDD 開發流程

# 數據管道
/tools:data-pipeline → ETL 數據管道
/tools:data-validation → 數據品質驗證

# ML 策略（FreqAI）
/plugin install data-ml-pipeline → ML 工程師代理
```

### API 金鑰快速設定

```bash
# .env 或 ~/.bashrc 中設定
export FMP_API_KEY="your_fmp_key"          # Financial Modeling Prep
export FINVIZ_API_KEY="your_finviz_key"    # FINVIZ Elite（可選）
export ALPACA_API_KEY="your_alpaca_key"    # Alpaca
export ALPACA_SECRET_KEY="your_secret"
export ALPACA_PAPER="true"                 # 紙幣交易模式
```

---

*本文件基於 2026-03-21 抓取的資料整理。各專案可能持續更新，建議定期查閱原始文件以獲取最新資訊。*

*參考來源：*
- *https://tradermonty.github.io/claude-trading-skills/en/skills/*
- *https://github.com/wshobson/commands*
- *https://github.com/wshobson/agents*
