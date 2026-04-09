* Main analysis: RD + DiD/TWFE + System-GMM
clear all
set more off
cap mkdir "stata/output"

import delimited "data/synthetic_panel.csv", clear
gen post_reform = (year >= 2019)

* Baseline 2018 size for treatment
preserve
keep if year == 2018
keep firm_id log_assets
rename log_assets log_assets_2018
tempfile base
save `base'
restore
merge m:1 firm_id using `base', nogen
gen treat_band = (log_assets_2018 >= 13.80 & log_assets_2018 < 14.00)
gen treat_post = treat_band * post_reform

xtset firm_id year

* ---- RD (2023 cross-section) ----
preserve
keep if year == 2023
rdrobust auditor_dummy running, c(0)
rdrobust meritocracy_index running, c(0)
rdplot auditor_dummy running, c(0) ///
    graph_options(title("First stage: auditor at threshold") ///
    ytitle("auditor_dummy") xtitle("running"))
graph export "stata/output/rd_auditor_2023.png", replace width(1600)
rdplot meritocracy_index running, c(0) ///
    graph_options(title("Reduced form: meritocracy at threshold") ///
    ytitle("meritocracy_index") xtitle("running"))
graph export "stata/output/rd_meritocracy_2023.png", replace width(1600)
restore

* ---- TWFE with reghdfe ----
reghdfe meritocracy_index treat_post leverage bank_dependence family_control, ///
    absorb(firm_id year) vce(cluster firm_id)
estimates store M_mer
reghdfe wage_premium treat_post leverage bank_dependence family_control, ///
    absorb(firm_id year) vce(cluster firm_id)
estimates store M_wage
reghdfe interest_rate treat_post governance_score leverage bank_dependence, ///
    absorb(firm_id year) vce(cluster firm_id)
estimates store M_ir

* ---- System-GMM demo ----
gen ln_prod = ln(productivity)
xtabond2 ln_prod L.ln_prod auditor_dummy governance_score leverage ///
    bank_dependence i.year, ///
    gmm(L.ln_prod leverage, lag(2 .)) ///
    iv(auditor_dummy governance_score bank_dependence i.year, eq(level)) ///
    twostep robust small

di "OK: outputs in stata/output/"
