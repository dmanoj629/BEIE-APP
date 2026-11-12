# BEIE Scope & Boundary Definition

## 1. Problem Statement
When macroeconomic shocks occur (e.g. global crude oil rising 25%), Indian citizens and MSMEs experience the immediate financial distress (higher diesel and food prices, tighter margins, rising loan EMIs) without visibility into the transmission mechanism. India's rich economic, climate, and geographic datasets exist in silos.

## 2. Target Users
1. **Citizens**: Farmers, salaried employees, small shopkeepers, gig workers seeking to understand how national shocks affect their household budget, food prices, fuel bills, and EMIs.
2. **MSMEs & Regional Businesses**: Manufacturing units, transporters, retailers needing regional and sector-specific cost foresight, break-even simulation, and supply chain vulnerability analysis.
3. **Researchers & Institutions**: Exploring transparent regional economic transmission models without opaque black boxes.

## 3. The Core Demo Question
> **"What happens to a Karnataka household and MSME if crude oil rises 25%?"**
Outputs:
- Month-by-month CPI impact range (P10, P50, P90 bands via Monte Carlo simulation).
- Rupee impact breakdown across household budget items and MSME input costs.
- Transparent causal transmission chain from crude basket -> refinery/pump -> transport/freight -> manufactured goods & food -> consumer price index.
- Sourced observations, explicit assumptions, and honest limitations.

## 4. What Counts as Evidence
- Official statistical releases from MoSPI (CPI 2024=100 series, Annexures I–IV).
- Official energy and pricing bulletins from PPAC (Petroleum Planning & Analysis Cell, Ministry of Petroleum & Natural Gas).
- Empirical research from Reserve Bank of India (RBI Bulletin July 2025: *Revisiting the Oil Price and Inflation Nexus in India*).
- Official commodity and mandi data from AGMARKNET / data.gov.in.
- Every observation carries its exact source URL, retrieval timestamp, unit, and geographic boundary.

## 5. Explicit Non-Goals
- BEIE is **not** a general-purpose conversational LLM that hallucinates answers.
- BEIE is **not** an autonomous trading bot or provider of personalized stock recommendations.
- BEIE does **not** predict single future price numbers; it generates distribution bands under explicit scenarios.
- BEIE does **not** replace enterprise risk engines (e.g., BlackRock Aladdin or Moody's); it acts as an interpretable cross-domain public intelligence layer.
