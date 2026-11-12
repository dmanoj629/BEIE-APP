# BEIE Model Assumptions & Calibration Note

## 1. Macroeconomic Transmission & Leontief Cost-Push
- **Leontief Price Equation**:
  $$\Delta p = (I - A^{\top})^{-1} a_c \Delta c$$
  where $A$ is the domestic input-output coefficients matrix (15 aggregated sectors derived from the national input-output tables), $a_c$ is sector-level direct crude/energy cost intensity, and $\Delta c$ is the percentage crude shock.
- **Crude Import Dependency**: Over 85% of India's crude consumption is imported (Source: PPAC / RBI Bulletin). We evaluate $a_c$ on total input absorption.

## 2. Policy Buffer & Fuel Price Decisions
Because pump prices in India are administered by Oil Marketing Companies (OMCs) under government guidance, pump prices do not move 1:1 with international crude on day one.
BEIE models three explicit policy regimes:
1. **Prices Held**: $\Delta r = 0$ (OMCs absorb under-recoveries or excise cuts buffer prices, as seen during 2022–2024).
2. **Partial Pass-Through**: Default 50% pass-through over 3–4 months.
3. **Full Pass-Through**: Full economic cost passed to retail petrol and diesel.

## 3. Monte Carlo Parameter Distributions
In accordance with Blueprint Section 10:
- **Pass-through share $\theta_g$**: Modeled as triangular distributions per consumption group:
  - Transport & Fuel: $\text{Triangular}(\text{low}=0.70, \text{mode}=0.85, \text{high}=1.00)$
  - Food & Beverages: $\text{Triangular}(\text{low}=0.25, \text{mode}=0.40, \text{high}=0.55)$
  - Manufactured Goods: $\text{Triangular}(\text{low}=0.30, \text{mode}=0.45, \text{high}=0.65)$
  - Housing & Services: $\text{Triangular}(\text{low}=0.10, \text{mode}=0.20, \text{high}=0.35)$
- **Transmission Completion Lag**: Uniform integer draw between 2 and 4 months, consistent with empirical findings that freight transport cost pass-through completes within 60–90 days (Source: RBI Bulletin / Outlook Business).
- **Simulation Parameters**: 5,000 to 10,000 draws using a fixed pseudo-random seed (`seed=42`) for full determinism and auditability.

## 4. Empirical Anchor & Calibration Note
- **RBI Anchor**: RBI Bulletin (July 2025, Kundu, Tewari & Bhattacharyya) finds that a **10% increase in Indian crude basket prices leads to approximately a 20 basis points (0.20 pp) increase in headline CPI**.
- Under our partial pass-through calibration, a +10% crude shock results in a median headline impact of +0.19 to +0.22 pp, aligning with RBI empirical bounds.
- For a +25% shock, the benchmark median CPI impact lands near +0.50 pp (+48 to +54 bps). Any deviation beyond $\pm 25\%$ triggers an automated sanity alert in the engine run record.
