# Independent sensitivity on REAL raw-source-converted CSV, not Stata replication.
# 32 specs = 2 outcomes x 2 horizons x 2 estimators x 2 lags x China in/out.
suppressPackageStartupMessages(library(plm))
options(warn=1)
dir.create("outputs",showWarnings=FALSE)
df <- read.csv("data/processed/model_panel.csv", stringsAsFactors=FALSE)
stopifnot(nrow(df)==270, length(unique(df$ISO3))==30,
          !anyDuplicated(df[c("ISO3","Year")]))
rows <- list()
k <- 0
for (y in c("HighTech_Exports","Unemployment"))
 for (last_year in c(2024,2023))
  for (trans in c("d","ld"))
   for (max_lag in c(2,3))
    for (exclude_china in c(FALSE,TRUE)) {
      k <- k+1
      d <- subset(df, Year<=last_year & (!exclude_china | ISO3!="CHN"))
      spec <- sprintf("%s_%d_%s_lag2_%d_%s",y,last_year,trans,max_lag,
                      ifelse(exclude_china,"exclude_CHN","all_countries"))
      out <- list(spec=spec,outcome=y,end_year=last_year,method=ifelse(trans=="d","difference","system"),
                  instrument_lag_end=max_lag,exclude_CHN=exclude_china,countries=length(unique(d$ISO3)),
                  status="ERROR",nobs=NA_integer_,instrument_columns=NA_integer_,
                  invest_b=NA_real_,patent_b=NA_real_,ar2_p=NA_real_,overid_twosteps_p=NA_real_,
                  overid_df=NA_real_,failure_detail="")
      tryCatch({
        p<-pdata.frame(d,index=c("ISO3","Year"))
        f<-as.formula(paste0(y," ~ lag(",y,",1) + ln1p_invest + ln1p_patent + GDP_Growth",
         " | lag(",y,",2:",max_lag,") + lag(ln1p_invest,2:",max_lag,")",
         " + lag(ln1p_patent,2:",max_lag,") + lag(GDP_Growth,2:",max_lag,")"))
        m<-pgmm(f,data=p,effect="twoways",model="onestep",transformation=trans,collapse=TRUE)
        b<-coef(m)
        out$status<-"ESTIMATED_CONDITIONAL"
        out$nobs<-nobs(m)
        out$instrument_columns<-if(length(m$W))ncol(m$W[[1]]) else NA_integer_
        out$invest_b<-if("ln1p_invest" %in% names(b))unname(b["ln1p_invest"]) else NA_real_
        out$patent_b<-if("ln1p_patent" %in% names(b))unname(b["ln1p_patent"]) else NA_real_
        out$ar2_p<-tryCatch(as.numeric(mtest(m,order=2)$p.value),error=function(e)NA_real_)
        ov<-tryCatch(sargan(m,weights="twosteps"),error=function(e)NULL)
        if(!is.null(ov)) {
          out$overid_df<-as.numeric(unlist(ov$parameter)[1])
          out$overid_twosteps_p<-as.numeric(ov$p.value)
        }
        # Independent, non-overwriting flags. A zero-df over-ID test is
        # NOT a statistically meaningful rejection even if software prints p=0.
        reasons <- character(0)
        if(is.na(out$ar2_p) || !is.finite(out$ar2_p)) {
            reasons <- c(reasons,"AR2_NOT_TESTABLE")
        } else if (out$ar2_p < 0.05) reasons <- c(reasons,"AR2_REJECTED")
        overid_valid <- !is.na(out$overid_df) && is.finite(out$overid_df) &&
            out$overid_df > 0 && !is.na(out$overid_twosteps_p) &&
            is.finite(out$overid_twosteps_p)
        if (!overid_valid) {
            reasons <- c(reasons,"OVERID_NOT_TESTABLE")
        } else if (out$overid_twosteps_p < 0.05) {
            reasons <- c(reasons,"OVERID_REJECTED")
        }
        if (!is.na(out$instrument_columns) && out$instrument_columns>=out$countries)
            reasons <- c(reasons,"INSTRUMENTS_TOO_MANY")
        out$status <- paste(c("ESTIMATED_CONDITIONAL",reasons),collapse=";")
      },error=function(e){out$failure_detail<-conditionMessage(e)})
      rows[[k]]<-as.data.frame(out,stringsAsFactors=FALSE)
      cat("SENSITIVITY_REAL",spec,out$status,"N=",out$nobs,"AR2=",out$ar2_p,
          "OV=",out$overid_twosteps_p,"\n")
    }
stopifnot(length(rows)==32)
out<-do.call(rbind,rows)
write.csv(out,"outputs/r_china_instrument_sensitivity.csv",row.names=FALSE,na="NA")
cat("SENSITIVITY_TOTAL=32 ESTIMATED=",sum(out$status!="ERROR"),
    "FAILED=",sum(out$status=="ERROR"),"\n")
cat("CAUSAL_MODELS_APPROVED=0; R one-step never equals Stata two-step nomata\n")
