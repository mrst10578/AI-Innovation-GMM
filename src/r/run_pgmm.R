# INDEPENDENT R sensitivity; do not call these Stata results.
# Usage from repository root after python -m src.python.research_audit
suppressPackageStartupMessages(library(plm))
infile <- "data/processed/panel_for_r.csv"
if (!file.exists(infile)) stop("Run python -m src.python.research_audit first")
d <- read.csv(infile, stringsAsFactors=FALSE)
dir.create("outputs/r", recursive=TRUE, showWarnings=FALSE)
con <- file("outputs/r/run_pgmm.log", open="wt")
sink(con, split=TRUE)
on.exit <- function() { sink(); close(con) } # scripts run at top level: close explicitly below
cat("Independent R pgmm execution; NOT Stata; not a causal validation\n")
cat("R:", R.version.string, "plm:", as.character(packageVersion("plm")), "\n")
cat("Run input:", infile, "rows", nrow(d), "\n")
res <- list()
for (dep in c("HighTech_Exports","Unemployment")) {
 for (lastyear in c(2024L,2023L)) {
  for (transform in c("d","ld")) {
   for (steps in c("onestep","twosteps")) {
    tag <- paste(dep,lastyear,transform,steps,sep="__")
    dd <- d[d$Year<=lastyear,]
    form <- as.formula(paste0(dep,
     " ~ lag(",dep,",1) + ln_ai_investment + ln_ai_patents + GDP_Growth",
     " | lag(",dep,",2:2) + lag(ln_ai_investment,2:2) + lag(ln_ai_patents,2:2)",
     " | GDP_Growth"))
    w <- character()
    fit <- withCallingHandlers(tryCatch(
      pgmm(form, data=dd, index=c("ISO3","Year"),
           model=steps, transformation=transform, effect="twoways", collapse=TRUE),
      error=function(e)e),
      warning=function(z){w <<- c(w,conditionMessage(z));invokeRestart("muffleWarning")})
    cat("\nRUN:",tag,"\n")
    if(inherits(fit,"error")) {
     cat("FAILED:", conditionMessage(fit),"\n")
     res[[length(res)+1]] <- data.frame(run=tag,outcome=dep,last_year=lastyear,
       estimator=transform,steps=steps,status="failed",term=NA_character_,
       estimate=NA_real_,std_error=NA_real_,p_value=NA_real_,
       ar1_p=NA_real_,ar2_p=NA_real_,sargan_p=NA_real_,
       instrument_columns=NA_integer_,groups=NA_integer_,
       warnings=conditionMessage(fit),stringsAsFactors=FALSE)
     next
    }
    s <- tryCatch(summary(fit,robust=TRUE),error=function(e)e)
    coefmat <- if(inherits(s,"error")) NULL else coef(s)
    a <- tryCatch(mtest(fit,order=1),error=function(e)e)
    b <- tryCatch(mtest(fit,order=2),error=function(e)e)
    j <- tryCatch(sargan(fit),error=function(e)e)
    pval <- function(o) if(inherits(o,"error")) NA_real_ else as.numeric(o$p.value)
    nar <- length(fit$W)
    ni <- ncol(fit$W[[1]])
    if(inherits(s,"error")) w <- c(w,paste("summary:",conditionMessage(s)))
    if(inherits(a,"error")) w <- c(w,paste("AR1:",conditionMessage(a)))
    if(inherits(b,"error")) w <- c(w,paste("AR2:",conditionMessage(b)))
    if(inherits(j,"error")) w <- c(w,paste("Sargan:",conditionMessage(j)))
    cat("Groups",nar,"instrument columns",ni,
        "AR1 p",pval(a),"AR2 p",pval(b),"Sargan p",pval(j),"\n")
    cat("NOTE: Sargan here is NOT a robust Hansen test.\n")
    if(!is.null(coefmat)) {
      print(coefmat)
      for(i in seq_len(nrow(coefmat))) {
       res[[length(res)+1]] <- data.frame(run=tag,outcome=dep,last_year=lastyear,
        estimator=transform,steps=steps,status="fitted_unvalidated",
        term=rownames(coefmat)[i], estimate=coefmat[i,1],std_error=coefmat[i,2],
        p_value=coefmat[i,ncol(coefmat)],ar1_p=pval(a),ar2_p=pval(b),
        sargan_p=pval(j),instrument_columns=ni,groups=nar,
        warnings=paste(w,collapse=" | "),stringsAsFactors=FALSE)
      }
    }
   }
  }
 }
}
if(length(res)==0)stop("No estimator attempts recorded")
out <- do.call(rbind,res)
write.csv(out,"outputs/r/pgmm_results.csv",row.names=FALSE,na="")
cat("\nRecords written:",nrow(out),"\n")
cat("WARNING: no difference-in-Hansen nor independently validated robust Hansen result supplied.\n")
cat("Panel dimensions and weak identification require critical review.\n")
sink()
close(con)
