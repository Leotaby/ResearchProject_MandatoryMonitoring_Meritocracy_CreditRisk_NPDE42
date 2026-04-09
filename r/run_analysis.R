library(data.table); library(ggplot2); library(fixest); library(rdrobust)
root <- normalizePath("..", winslash="/")
df <- fread(file.path(root,"data","synthetic_panel.csv"))
outdir <- file.path(root,"r","output"); dir.create(outdir, showWarnings=FALSE, recursive=TRUE)
cs <- df[year==2023]

# RD estimates
sink(file.path(outdir,"rdrobust_summary.txt"))
cat("=== Auditor dummy ===\n"); print(rdrobust(cs$auditor_dummy, cs$running, c=0))
cat("\n=== Meritocracy ===\n"); print(rdrobust(cs$meritocracy_index, cs$running, c=0))
cat("\n=== Interest rate ===\n"); print(rdrobust(cs$interest_rate, cs$running, c=0))
sink()

# RD plots
for (yvar in c("auditor_dummy","meritocracy_index","interest_rate")) {
  png(file.path(outdir, paste0("rd_",yvar,"_2023.png")), width=1400, height=840, res=200)
  rdplot(cs[[yvar]], cs$running, c=0, title=paste("RD:", yvar, "(2023)"),
         x.label="Running variable", y.label=yvar)
  dev.off()
}

# TWFE
df[, treat_post := treat_band * post_reform]
m1 <- feols(meritocracy_index ~ treat_post + leverage + bank_dependence + family_control | firm_id + year, data=df, cluster="firm_id")
m2 <- feols(interest_rate ~ treat_post + governance_score + leverage + bank_dependence | firm_id + year, data=df, cluster="firm_id")
sink(file.path(outdir,"twfe_fixest.txt"))
cat("=== Meritocracy ===\n"); print(summary(m1))
cat("\n=== Interest rate ===\n"); print(summary(m2))
sink()

# Distress logit
logit <- glm(distressed ~ auditor_dummy + governance_score + meritocracy_index + leverage + bank_dependence + family_control, family=binomial, data=df)
sink(file.path(outdir,"credit_logit.txt")); print(summary(logit)); sink()

cat("OK: outputs in", outdir, "\n")
