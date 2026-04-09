# Mandatory Monitoring, Meritocracy, and Credit Risk in Italian Private Firms

**Replication package for NPDE 42° cycle PhD proposal**
*Hatef Tabbakhian — University of Naples Federico II (DISES / CSEF)*

---

## Live Demo

**[→ Open Interactive Dashboard](https://npde-proposal-preview.vercel.app)**


## Overview

This repository is a fully reproducible mini-research project that previews the empirical core of my PhD proposal:

> **Mandatory Monitoring, Meritocracy, and Credit Risk in Italian Private Firms: Evidence from Statutory-Auditor Thresholds**

It implements the main identification strategies on **realistic synthetic data** mimicking Italian S.r.l. firms around statutory-auditor appointment thresholds:

| Method | What it tests |
|--------|--------------|
| **Regression Discontinuity (RD)** | Jump in auditor appointment and meritocracy outcomes at the size threshold |
| **Difference-in-Differences (DiD)** | Effect of the 2019 threshold reform on near-threshold firms |
| **Two-Way Fixed Effects (TWFE)** | Panel estimates of monitoring → meritocracy, productivity, credit terms |
| **System-GMM** | Dynamic panel with persistence in productivity (Stata demo) |
| **Credit-risk models** | Interest rate, leverage, and distress regressions |
| **C++17 Monte Carlo** | Fast simulation of governance → meritocracy → productivity dynamics |

> **All data are synthetic.** The purpose is to demonstrate methods, reproducibility, and feasibility.

## Theoretical foundations

- **Pagano, M. & Picariello, L. (2025).** *Corporate Governance, Meritocracy and Careers.* Review of Finance, 29(2), 349–385. [Link](https://academic.oup.com/rof/article/29/2/349/7905828)
- **Coraggio, D., Pagano, M., Scognamiglio, A., & Tåg, J. (2025).** *JAQ of All Trades: Job Mismatch, Firm Productivity and Managerial Quality.* Journal of Financial Economics. [Link](https://www.sciencedirect.com/science/article/pii/S0304405X24002150)
- **Altavilla, C., Ellul, A., Pagano, M., Polo, A., & Vlassopoulos, T. (2025).** *Loan Guarantees, Bank Lending and Credit Risk Reallocation.* Journal of Financial Economics. [Link](https://www.sciencedirect.com/science/article/abs/pii/S0304405X2500145X)
- **Bank of Italy (2026).** Discussion Paper on statutory-auditor thresholds and credit conditions. [Link](https://www.bancaditalia.it/pubblicazioni/temi-discussione/2026/2026-1517/index.html)

## Repository structure

```
├── README.md
├── LICENSE
├── .gitignore
├── data/
│   ├── README.md
│   └── generate_synthetic_data.py
├── python/
│   ├── requirements.txt
│   └── run_analysis.py          # RD + DiD + TWFE + credit-risk + plots
├── r/
│   ├── install_packages.R
│   └── run_analysis.R           # rdrobust + fixest + plm + ggplot2
├── stata/
│   ├── 00_setup.do
│   └── 01_run_analysis.do       # rdrobust + reghdfe + xtabond2
├── cpp/
│   ├── CMakeLists.txt
│   └── src/main.cpp             # Monte Carlo simulation
└── docs/
    └── index.html               # Interactive dashboard (open in browser)
```

## Quick start

### 1. Generate synthetic data
```bash
cd data
python generate_synthetic_data.py --n_firms 3000 --seed 42
```

### 2. Python analysis
```bash
pip install -r python/requirements.txt
python python/run_analysis.py
```

### 3. R analysis
```r
source("r/install_packages.R")
source("r/run_analysis.R")
```

### 4. Stata analysis
```stata
do stata/00_setup.do
do stata/01_run_analysis.do
```

### 5. C++ simulation
```bash
mkdir -p cpp/build && cd cpp/build
cmake .. && cmake --build . --config Release
./sim
```

### 6. Interactive dashboard
Open `docs/index.html` in any browser — no server required.

## Interactive dashboard

The `docs/index.html` file provides a self-contained interactive exploration tool:

- **RD plots** with adjustable bandwidth and polynomial order
- **DiD event-study** visualization with draggable reform year
- **Credit-risk channel** scatter plots with real-time parameter controls
- **Monte Carlo simulation** running directly in the browser

All computation happens client-side using synthetic data generated on page load.

## Author

**Hatef Tabbakhian** — tabbakhianhatef@gmail.com
[GitHub](https://github.com/leotaby) · [LinkedIn](https://linkedin.com/in/hateftaby)

## License

MIT — see [LICENSE](LICENSE).
