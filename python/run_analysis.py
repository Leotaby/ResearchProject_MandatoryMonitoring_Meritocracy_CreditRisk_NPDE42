#!/usr/bin/env python3
"""
RD + DiD/TWFE + credit-risk regressions with publication-style plots.
Outputs to python/output/
"""
from pathlib import Path
import subprocess, numpy as np, pandas as pd, matplotlib.pyplot as plt
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "synthetic_panel.csv"
OUT = Path(__file__).resolve().parent / "output"

def ensure_data():
    if not CSV.exists():
        subprocess.check_call(["python", str(ROOT/"data/generate_synthetic_data.py")])

def binned_rd_plot(df, x, y, c=0.0, bins=35, title="", path=None):
    d = df[[x, y]].dropna().copy()
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for side, color in [(d[d[x]<c], "#2166ac"), (d[d[x]>=c], "#b2182b")]:
        if len(side) < 10: continue
        side = side.copy()
        side["bin"] = pd.qcut(side[x], q=bins, duplicates="drop")
        g = side.groupby("bin", observed=True).agg({x:"mean", y:"mean"}).reset_index(drop=True)
        ax.scatter(g[x], g[y], s=22, color=color, zorder=3)
        X_ = sm.add_constant(g[x].values)
        yhat = sm.OLS(g[y].values, X_).fit().predict(
            sm.add_constant(np.linspace(g[x].min(), g[x].max(), 80)))
        ax.plot(np.linspace(g[x].min(), g[x].max(), 80), yhat, lw=2.2, color=color)
    ax.axvline(c, ls="--", color="grey", lw=0.8)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(f"Running variable (cutoff = {c})")
    ax.set_ylabel(y.replace("_", " ").title())
    fig.tight_layout()
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=200); plt.close(fig)

def twfe(panel, y):
    df = panel.set_index(["firm_id","year"]).copy()
    df["treat_post"] = df["treat_band"] * df["post_reform"]
    exog = df[["treat_post","leverage","bank_dependence","family_control"]]
    return PanelOLS(df[y], exog, entity_effects=True, time_effects=True,
                    drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ensure_data()
    panel = pd.read_csv(CSV)
    cs = panel[panel["year"]==2023].copy()

    # --- RD plots ---
    for yvar, title in [
        ("auditor_dummy", "First stage: Auditor appointment at threshold"),
        ("meritocracy_index", "Reduced form: Meritocracy at threshold"),
        ("interest_rate", "Credit channel: Interest rate at threshold"),
    ]:
        binned_rd_plot(cs, "running", yvar, title=f"{title} (synthetic, 2023)",
                       path=OUT/f"rd_{yvar}_2023.png")

    # --- TWFE regressions ---
    for y in ["meritocracy_index","wage_premium","productivity","interest_rate"]:
        res = twfe(panel, y)
        (OUT/f"twfe_{y}.txt").write_text(res.summary.as_text())

    # --- Credit distress logit ---
    X = sm.add_constant(panel[["auditor_dummy","governance_score","meritocracy_index",
                                "leverage","bank_dependence","family_control"]])
    logit = sm.Logit(panel["distressed"], X).fit(disp=False)
    (OUT/"credit_distress_logit.txt").write_text(logit.summary().as_text())

    # --- Event-study plot ---
    tmp = panel.copy(); tmp["evt"] = tmp["year"] - 2019
    agg = tmp.groupby(["evt","treat_band"])["meritocracy_index"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for g, lbl, c in [(0,"Control","#2166ac"),(1,"Treated (near threshold)","#b2182b")]:
        d = agg[agg["treat_band"]==g]
        ax.plot(d["evt"], d["meritocracy_index"], "o-", label=lbl, color=c)
    ax.axvline(0, ls="--", color="grey", lw=0.8)
    ax.set_title("Event study: Meritocracy index around 2019 reform")
    ax.set_xlabel("Years relative to reform"); ax.set_ylabel("Meritocracy index")
    ax.legend(frameon=False); fig.tight_layout()
    fig.savefig(OUT/"eventstudy_meritocracy.png", dpi=200); plt.close(fig)

    print(f"[OK] Outputs in {OUT}")

if __name__ == "__main__":
    main()
