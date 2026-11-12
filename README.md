# BEIE — Bharat Economic Intelligence Engine
### *A computational map of India's economy: from macroeconomic signals to household and business impact*

**Theme:** FinTech & Financial Inclusion · Viksit Bharat 2047  
**Event:** Bharat Innovation Challenge 2.0 (BIC 2.0) — Lovely Professional University (LPU)  
**Team:** D. Manoj · Dhruva · Suresh Maladhar | **Mentor:** Varun Sagar D (Shikaripura, Karnataka)  
**Origin:** Karnataka, India  
**Tagline:** *"Understand the Economy. Anticipate Change. Make Better Decisions."*

---

## 1. Executive Summary & Product Mission
When global economic events strike (such as a 25% surge in crude oil, unseasonal summer heatwaves, or monetary policy repo rate revisions), Indian citizens and small business owners see the painful outcome—higher diesel prices, climbing grocery bills, dearer loan EMIs, and compressed operating margins—without being able to see the causal transmission chain behind it.

**BEIE (Bharat Economic Intelligence Engine)** solves this by bridging verified public economic data (RBI, MoSPI, PPAC, IMD, CSO, AGMARKNET) through a transparent **15-sector Leontief input-output cost-push model**, **administered fuel pricing policy logic**, and **vectorized Monte Carlo simulations** returning P10/P50/P90 uncertainty intervals.

### Non-Negotiable Engineering Principles (The Blueprint Rules)
1. **Provenance on Every Number:** Every observation cites its source agency, official URL, observation date, retrieval date, license, and cryptographic SHA-256 sidecar.
2. **No Invented Statistics or Silent Synthetic Fallbacks:** Missing or stale data produces an honest, visible blocker in mode `limited`. Missing data is never treated as zero.
3. **Python Controls All Calculations:** AI is strictly quarantined to interpreting verified structured JSON results. AI never calculates or invents economic numbers.
4. **Number Verification Gate:** Every numerical token in an AI-generated explanation is verified against the structured result JSON. Any ungrounded number triggers an automated discard and safe multilingual template fallback.
5. **No Regulated Stock Tips:** Strictly adheres to SEBI retail risk disclosure guidelines—no personal stock recommendations or buy/sell calls.
6. **Zero Cloud Lock-in / Works Offline:** BEIE operates 100% reliably without requiring an external AI API key or GPU, utilizing its deterministic multilingual template engine.

---

## 2. Architecture & System Loop

```
EVENT / SEASON / SHOCK (e.g. Crude Oil +25%, Heatwave, Repo Rate +50 bps)
                     │
                     ▼
OFFICIAL GROUND TRUTH DATA (MoSPI, PPAC, RBI, IMD, CSO Input-Output Tables)
                     │
                     ▼
15-SECTOR LEONTIEF TRANSMISSION: Δp = (I - Aᵀ)⁻¹ · a_c · Δc
                     │
                     ▼
REGIONAL TRANSMISSION (Karnataka State CPI & Bengaluru Pump Baselines)
                     │
                     ▼
USER PROFILE & EXPOSURE (Farmer, Salaried, Shopkeeper, MSME, Student)
                     │
                     ▼
NUMPY MONTE CARLO SIMULATION (5,000–10,000 draws, fixed seeds)
                     │
                     ▼
P10 / P50 / P90 UNCERTAINTY BANDS & PLOTLY INTERACTIVE CHARTS
                     │
                     ▼
GROUNDED AI ANALYST (Gemini / OpenAI / Multilingual Templates)
                     │
                     ▼
INFORMED HOUSEHOLD & BUSINESS DECISION
```

---

## 3. Platform Modules & Capabilities

| Module | Core Functionality | Primary Engine | Status |
|---|---|---|---|
| **⚡ Universal Scenario Simulator** | Model multi-shock scenarios (crude, diesel, electricity, freight, raw materials, repo rate) with natural language extraction | `beie.domains.energy`, `beie.model.costpush` | ✅ Operational |
| **🎯 Problems We Solve** | Computational directory of 33+ real-world economic problems with search, filtering, and custom problem NLP analyzer | `app.views.problems_we_solve` | ✅ Operational |
| **👥 Citizen Intelligence** | Personalized dashboard for Farmers, Salaried employees, Students, and Shopkeepers with living cost radars | `app.views.citizen_home` | ✅ Operational |
| **🏢 Business Intelligence** | 8 MSME tools: Input shock calculator, margin simulator, seasonality, working capital stress, corridor freight, surplus cash, and weekly digest | `app.views.business_tools` | ✅ Operational |
| **🛡️ Portfolio Risk Engine** | Aladdin-inspired multi-asset portfolio and loan-book stress testing with Monte Carlo VaR, CVaR, and what-if holding removal | `beie.risk.engine` | ✅ Operational |
| **🛍️ Purchase Timing Advisor** | Evaluates festival sale calendars, product launch cycles, and budget to recommend Buy Now vs Wait | `beie.domains.purchase` | ✅ Operational |
| **📊 Stock Risk & SEBI Education** | Verified SEBI individual investor loss statistics, transaction cost breakdown, and illustrative asset allocations | `beie.domains.markets` | ✅ Operational |
| **📜 Data & Provenance Registry** | Audited raw and normalized datasets with true SHA-256 hashes, retrieval dates, and OGDL license terms | `beie.ingest` | ✅ Operational |
| **⚙️ AI Intelligence Settings** | Dedicated portal for Google Gemini & OpenAI API keys with real connection testing, status badges, and key masking | `beie.llm.adapter` | ✅ Operational |

---

## 4. Quickstart & Installation (Windows / Linux / macOS)

### Prerequisites
- Python 3.11+ or 3.12+ (tested on Python 3.11.9)
- Standard PC / Laptop (no GPU required, optimized for modest hardware)

### 1. Navigate to Project Directory
```powershell
cd "c:\Users\D MANOJ\Downloads\final bic yes"
```

### 2. Install Required Dependencies
```powershell
py -3.11 -m pip install -r requirements.txt openai
```

### 3. Run Automated Engineering Test Suite
```powershell
py -3.11 -m pytest
```
*Guaranteed Result:* **All 70 automated tests pass in ~15 seconds**, validating contracts, Leontief matrix mathematics, Monte Carlo quantiles, provenance SHA-256 hashes, AI number verifiers, and failure paths.

### 4. Code Quality & Lint Check
```powershell
py -3.11 -m ruff check .
```
*Guaranteed Result:* `All checks passed!`

### 5. Launch the BEIE Web Platform
```powershell
py -3.11 -m streamlit run app/streamlit_app.py --server.port=8501
```
Open your browser to: **`http://localhost:8501`**

---

## 5. BIC 2026 Live Competition Demonstration Script

### Demonstration A — Citizen / Farmer Walkthrough (3 Minutes)
1. Open the platform at `http://localhost:8501`.
2. Click **"🚀 Get Started"** and select **"👤 Citizen & Worker Hub"**.
3. Complete the step-by-step onboarding:
   - Select Preferred Language: English, Kannada, or Hindi.
   - Enter Indian PIN Code: `577427` (Shikaripura) or `560001` (Bengaluru) — watch BEIE instantly auto-resolve district and state.
   - Select Occupation: **🌾 Farmer** (or select **"Other"** and type: *"I grow paddy and sugarcane in Mandya using electric borewell and hired tractor"* — observe the smart context extraction badge on the dashboard).
4. On the Citizen Dashboard, set the **Crude Oil Shock slider to +25%**:
   - Observe the **15-Sector Leontief Transmission Chain**: Global Crude ($74.10) → Refined Diesel (+₹4.53/L) → Freight (+3.0%) → Food CPI (+0.41 pp) → Total Karnataka Headline CPI (+0.51 pp).
   - View the interactive **Plotly P10/P50/P90 Fan Chart** and **Monte Carlo Draw Histogram**.
   - Note the **RBI July 2025 empirical sanity anchor** badge (+10% crude ≈ +20 bps headline CPI).
   - Open the **"Why this result?" Drawer** to inspect the seed (`42`), run ID, and exact formulas.

### Demonstration B — Universal Scenario Simulator (2 Minutes)
1. From the navigation sidebar, select **"⚡ Universal Scenario Simulator"**.
2. Type a natural language scenario into the input bar:
   *"What happens if diesel rises 15%, electricity tariffs increase 8%, and freight increases 12%?"*
3. Click **"🔍 Extract Parameters"** — watch BEIE extract and align the numeric percentage sliders.
4. Run the simulation:
   - Inspect the **15-Sector Leontief Inter-Industry Price Escalation horizontal bar chart**.
   - Compare baseline CPI (5.86%) vs stressed CPI (6.37%).
   - Review the MSME margin compression and household monthly outflow change.

### Demonstration C — Problems We Solve (1.5 Minutes)
1. Select **"🎯 Problems We Solve"** from the navigation sidebar.
2. Explore the directory of 33+ real problems categorized by Household, Farmer, MSME, and Researcher.
3. Test the interactive filter chips (e.g. click *Farmer* or *Supply chain*).
4. Scroll to **"Describe a Problem Not Listed Here"** and enter a custom challenge:
   *"I operate a small cold-storage unit in Hassan. If electricity tariffs increase by 10% and diesel generator costs rise by 15%, how will it impact my monthly operating margins?"*
5. Click **"🚀 Analyze Problem Feasibility"**:
   - Watch BEIE's engine analyzer map the query to the Energy & Macro Transmission domain, verify that public data is ingested, and confirm calculation feasibility with zero synthetic data.

### Demonstration D — Business Console & Weekly Intelligence Digest (2 Minutes)
1. In the sidebar, click **"🔄 Switch Track"** to enter the **Enterprise & Business Console**.
2. Select **Manufacturing / MSME** in **Bengaluru Urban**.
3. Explore the 7 business simulators:
   - **Tool 1 (Input-Cost Shock):** Run sliders to see margin waterfall decomposition.
   - **Tool 4 (Cash Runway):** Simulate 6-month cash trajectory under a 30-day customer debtor delay.
   - **Tool 5 (Logistics Corridors):** Inspect fuel sensitivity across the Bengaluru–Mangaluru NH-75 corridor (52% fuel share).
   - **Tool 8 (Weekly Business Digest):** Review the synthesized executive intelligence briefing and click **"📥 Download Executive Business Intelligence Digest"** to save the evidence-backed markdown report.

### Demonstration E — Aladdin Portfolio Risk Engine (1.5 Minutes)
1. Select **"🛡️ Portfolio Risk (Aladdin-Engine)"**.
2. Inspect the multi-asset portfolio: sector exposure pie chart, daily 95% Monte Carlo VaR & CVaR, and crude shock stress P&L.
3. Perform a **What-If Holding Removal** on energy holdings to see diversification benefits and tail risk shifts.

### Demonstration F — AI Settings & Offline Reliability (1 Minute)
1. Navigate to **"⚙️ AI Intelligence Settings"**.
2. Switch between **Google Gemini** and **OpenAI**.
3. Click **"🧪 Test Connection"** — observe real-time health verification (latency in milliseconds or clear credential diagnostics).
4. Explain to the judges: BEIE operates with full intelligence even with no API key, powered by its verified deterministic multilingual template library.
5. In the sidebar, click **"📦 Download Clean Project ZIP"** to download the clean, self-contained project archive directly in-browser.

---

## 6. Project Materials & Provenance Integrity

All raw files are stored in `data/raw/` with verified cryptographic SHA-256 sidecars in `*.provenance.json`:

| File | Size (Bytes) | SHA-256 Checksum | Source Authority |
|---|---|---|---|
| `mospi_cpi_2026.json` | 1,694 | `4c4159e4b7158e3b512fd6ac3301c510370c2f12a0fcb82f43478cf6f3f648bf` | MoSPI Annexures III & IV |
| `ppac_crude_basket_2026.csv` | 406 | `ac22ee3c074f1173085da85cfa3251026ffe94e99f4a2a390f46df9a9bb65e87` | Petroleum Planning & Analysis Cell |
| `ppac_pump_prices_2026.csv` | 635 | `d82ebfeed5370b4fcff4c405583e148b50fc3574b531b156d8487af4ac0d4179` | PPAC / IOCL Daily Notifications |
| `io_matrix_15sector.json` | 3,913 | `5349c2a232a63e33c5937f3512c7e2b129b6203ebe3e8942c95298d1958d7eac` | CSO / MoSPI Supply & Use Tables |
| `cpi_weights_karnataka.json` | 766 | `552d9ca032d3a7dcc82afd6dc301abf9bb3d1cb7be41424134041d9f4d8ccb78` | MoSPI HCES Weighting Diagram |

*(Audited and verified by `tests/test_provenance_audit.py`)*

---

## 7. License & Compliance
Built strictly for the **Bharat Innovation Challenge 2.0 (BIC 2026)** at Lovely Professional University.  
All data ingested from official government repositories complies with the **Open Government Data License - India (OGDL)** and public fair-use disclosure research exemptions.
