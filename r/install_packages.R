pkgs <- c("data.table","ggplot2","fixest","plm","rdrobust","broom")
to_install <- pkgs[!pkgs %in% installed.packages()[,"Package"]]
if (length(to_install) > 0) install.packages(to_install, repos="https://cloud.r-project.org")
cat("OK: packages ready.\n")
