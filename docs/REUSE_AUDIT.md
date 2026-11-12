# BEIE Reuse Audit (Phase 1 Blueprint Compliance)

| Component | Decision | Reason & Justification |
|---|---|---|
| **Python 3.11+** | KEEP | Core analytics, high-performance vectorized operations. |
| **NumPy & SciPy** | KEEP | Matrix operations for Leontief inverse and Monte Carlo distribution draws. |
| **DuckDB + Parquet**| KEEP | Fast local columnar analytics, SQL queries on disk without heavy DB server. |
| **Pydantic v2** | KEEP | Strict runtime request and response contracts. |
| **Streamlit** | KEEP | High-velocity, responsive UI supporting custom CSS, session state, and multi-page flows. |
| **Plotly** | KEEP | Interactive SVG/WebGL charts (fan charts, histograms, waterfalls, pies). |
| **pytest & Ruff** | KEEP | Automated testing, linting, and regression verification from day one. |
| **Local LLM / Heavy Weights** | REJECT / DEFER | Avoid multi-GB memory overheads on standard laptops. Standard templates provide zero-latency multilingual accuracy. |
| **OpenBB** | DEFER | Direct Indian official data adapters (MoSPI, PPAC, RBI) provide authoritative provenance. |
