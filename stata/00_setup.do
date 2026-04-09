* Setup: install required packages
clear all
set more off
cap mkdir "stata/output"
foreach pkg in rdrobust reghdfe ftools ivreghdfe xtabond2 {
    cap which `pkg'
    if _rc ssc install `pkg', replace
}
di "OK: setup done."
