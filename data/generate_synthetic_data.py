#!/usr/bin/env python3
"""
Generate realistic synthetic panel data (Italian S.r.l. firms 2015-2023)
around statutory-auditor thresholds.

Channels modeled:
  1. Governance -> meritocracy -> talent allocation -> productivity
  2. Governance -> opacity reduction -> credit terms / risk-taking

Output: data/synthetic_panel.csv
"""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def generate_panel(seed=42, n_firms=3000, start_year=2015, end_year=2023):
    rng = np.random.default_rng(seed)
    years = np.arange(start_year, end_year + 1)
    firm_id = np.arange(1, n_firms + 1)

    # --- Latent firm characteristics (time-invariant) ---
    family_control = rng.binomial(1, 0.55, n_firms)
    bank_dependence = rng.beta(2.0, 5.0, n_firms)
    manager_quality = rng.normal(0.0, 1.0, n_firms)
    firm_fe = rng.normal(0.0, 0.4, n_firms)
    growth = rng.normal(0.03, 0.02, n_firms)

    regions = rng.choice(
        ["NW", "NE", "Center", "South", "Islands"],
        size=n_firms, p=[0.25, 0.20, 0.20, 0.25, 0.10]
    )
    industries = rng.choice(
        ["Manufacturing", "Trade", "Services", "Construction", "ICT"],
        size=n_firms, p=[0.30, 0.20, 0.30, 0.15, 0.05]
    )
    base_log_assets = rng.normal(14.0, 0.6, n_firms)

    rows = []
    for year in years:
        t = year - start_year
        # Threshold reform: pre-2019 at 14.00, post-2019 lowered to 13.80
        threshold = 14.00 if year <= 2018 else 13.80

        log_assets = base_log_assets + growth * t + rng.normal(0, 0.15, n_firms)
        running = log_assets - threshold
        assets = np.exp(log_assets) * 1e6
        revenue = np.exp(log_assets - 0.15 + rng.normal(0, 0.20, n_firms)) * 1e6
        employees = np.clip(
            np.round(np.exp(log_assets - 13.0) * 45 + rng.normal(0, 4, n_firms)),
            1, None
        ).astype(int)

        # Fuzzy compliance: sharp jump in P(auditor) at running=0
        p_audit = np.clip(0.10 + 0.75 * sigmoid(4.0 * running), 0.02, 0.98)
        auditor = rng.binomial(1, p_audit)

        # Governance score (monitoring + firm characteristics)
        governance = (
            0.20 * firm_fe + 0.85 * auditor - 0.45 * family_control
            + 0.10 * manager_quality + rng.normal(0, 0.60, n_firms)
        )

        # Meritocracy index
        meritocracy = (
            0.55 * governance - 0.35 * family_control
            + 0.20 * manager_quality + rng.normal(0, 0.70, n_firms)
        )

        # Managerial turnover (governance disciplines low-quality incumbents)
        p_turn = sigmoid(-1.1 + 0.55 * governance - 0.30 * manager_quality
                         + rng.normal(0, 0.20, n_firms))
        turnover = rng.binomial(1, np.clip(p_turn, 0.01, 0.99))

        # Wage premium (favoritism proxy: lower = more meritocratic)
        wage_premium = np.clip(
            0.25 - 0.08 * meritocracy + 0.05 * family_control
            + rng.normal(0, 0.08, n_firms), -0.10, 0.60
        )

        # Productivity
        productivity = np.exp(
            2.0 + 0.22 * meritocracy + 0.05 * governance
            + 0.20 * firm_fe + rng.normal(0, 0.25, n_firms)
        )

        # Credit-risk channel
        leverage = np.clip(
            0.35 + 0.10 * bank_dependence - 0.03 * governance
            + rng.normal(0, 0.08, n_firms), 0.05, 0.95
        )
        interest_rate = np.clip(
            0.045 - 0.0045 * governance - 0.003 * meritocracy
            + 0.030 * leverage + 0.007 * bank_dependence
            + rng.normal(0, 0.006, n_firms), 0.005, 0.25
        )
        lin_def = (
            -3.2 + 2.2 * leverage + 7.5 * interest_rate
            - 0.35 * governance - 0.10 * np.log(productivity)
            + rng.normal(0, 0.40, n_firms)
        )
        default_risk = sigmoid(lin_def)
        distressed = rng.binomial(1, np.clip(default_risk, 0.001, 0.999))

        df_y = pd.DataFrame({
            "firm_id": firm_id, "year": year,
            "region": regions, "industry": industries,
            "family_control": family_control,
            "bank_dependence": np.round(bank_dependence, 4),
            "threshold_log_assets": threshold,
            "log_assets": np.round(log_assets, 4),
            "running": np.round(running, 4),
            "assets": np.round(assets, 0),
            "revenue": np.round(revenue, 0),
            "employees": employees,
            "auditor_dummy": auditor,
            "governance_score": np.round(governance, 4),
            "meritocracy_index": np.round(meritocracy, 4),
            "managerial_turnover": turnover,
            "wage_premium": np.round(wage_premium, 4),
            "productivity": np.round(productivity, 4),
            "leverage": np.round(leverage, 4),
            "interest_rate": np.round(interest_rate, 4),
            "default_risk": np.round(default_risk, 4),
            "distressed": distressed,
        })
        rows.append(df_y)

    panel = pd.concat(rows, ignore_index=True)
    panel["post_reform"] = (panel["year"] >= 2019).astype(int)

    # Baseline 2018 size for DiD treatment assignment
    base = panel.loc[panel["year"] == 2018, ["firm_id", "log_assets"]].copy()
    base.columns = ["firm_id", "log_assets_2018"]
    panel = panel.merge(base, on="firm_id", how="left")
    panel["treat_band"] = (
        (panel["log_assets_2018"] >= 13.80) & (panel["log_assets_2018"] < 14.00)
    ).astype(int)

    return panel


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n_firms", type=int, default=3000)
    args = parser.parse_args()

    panel = generate_panel(seed=args.seed, n_firms=args.n_firms)
    out = Path(__file__).parent / "synthetic_panel.csv"
    panel.to_csv(out, index=False)
    print(f"[OK] {out}  ({len(panel)} rows, {panel['firm_id'].nunique()} firms)")
