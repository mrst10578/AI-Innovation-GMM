# Real R plm exploratory panel and limited-instrument GMM. Never fabricate diagnostics.
suppressPackageStartupMessages(library(plm))
suppressPackageStartupMessages(library(lmtest))
suppressPackageStartupMessages(library(sandwich))
options(warn=1)
dir.create("outputs",showWarnings=FALSE)
sink("outputs/r_models_log.txt",split=TRUE)
on.exit(sink(),add=TRUE)
cat("R_VERSION:",R.version.string,"\n")
for (p in c("plm","lmtest","sandwich")) cat("PACKAGE:",p,as.character(packageVersion(p)),"\n")
d <- read.csv("data/processed/model_panel.csv",stringsAsFactors=FALSE)
stopifnot(all(c("ISO3","Year","ln1p_invest","ln1p_patent","HighTech_Exports","Unemployment","GDP_Growth") %in% names(d)))
stopifnot(anyDuplicated(d[c("ISO3","Year")])==0)
d <- d[order(d$ISO3,d$Year),]
d$ISO3 <- as.factor(d$ISO3)
cat("DATA",nrow(d),"COUNTRIES",length(unique(d$ISO3)),"\n")
fields <- c("ln1p_invest","ln1p_patent","HighTech_Exports","Unemployment","GDP_Growth")
pfull <- pdata.frame(d,index=c("ISO3","Year"),drop.index=FALSE)
cat("=== Unit roots T<=9: diagnostic low power ===\n")
for (v in fields) for (test in c("ips","madwu")) {
    tag <- paste(v,test,sep=":")
    tryCatch({
        u<-purtest(pfull[[v]],test=test,exo="intercept",lags=0)
        cat("UNIT_ROOT",tag,"stat",as.numeric(u$statistic),
            "p",as.numeric(u$p.value),"lag=0 intercept no trend\n")
    },error=function(e)cat("UNIT_ROOT_NOT_AVAILABLE",tag,conditionMessage(e),"\n"))
}
cat("=== Models, 2016-2024 vs 2016-2023 ===\n")
for (last_year in c(2024,2023)) {
 sub<-d[d$Year<=last_year,]
 pdata<-pdata.frame(sub,index=c("ISO3","Year"))
 for (y in c("HighTech_Exports","Unemployment")) {
    basic<-as.formula(paste(y,"~ ln1p_invest + ln1p_patent + GDP_Growth"))
    for (method in c("pooling","within")) {
       tryCatch({
         m<-plm(basic,data=pdata,model=method,effect=if(method=="within") "twoways" else "individual")
         se<-sqrt(diag(vcovHC(m,method="arellano",type="HC1",cluster="group")))
         co<-coef(m)
         cat("BASELINE",y,last_year,method,"n",nobs(m),"coef",
             paste(names(co),format(co,digits=5),sep="=",collapse=";"),"cluster_se",
             paste(names(se),format(se,digits=5),sep="=",collapse=";"),"\n")
       },error=function(e) cat("BASELINE_FAILED",y,last_year,method,conditionMessage(e),"\n"))
    }
    for (tr in c("d","ld")) for (maxlag in c(2,3)) {
      spec<-paste(y,last_year,tr,paste0("lag2:",maxlag),sep="_")
      # y and AI variables endogenous; GDP growth conservatively instrumented as potentially predetermined.
      f<-as.formula(paste0(y," ~ lag(",y,",1) + ln1p_invest + ln1p_patent + GDP_Growth",
          " | lag(",y,",2:",maxlag,") + lag(ln1p_invest,2:",maxlag,")",
          " + lag(ln1p_patent,2:",maxlag,") + lag(GDP_Growth,2:",maxlag,")"))
      tryCatch({
        m<-pgmm(f,data=pdata,effect="twoways",model="onestep",transformation=tr,collapse=TRUE)
        ninst<-if(length(m$W))ncol(m$W[[1]]) else NA_integer_
        cat("GMM",spec,"n",nobs(m),"groups",length(unique(sub$ISO3)),
            "instr_cols_per_group",ninst,"\n")
        cat("GMM_COEFFICIENTS",spec,
            paste(names(coef(m)),format(coef(m),digits=6),sep="=",collapse=";"),"\n")
        if (is.finite(ninst) && ninst>=length(unique(sub$ISO3))) {
            cat("GMM_FLAG",spec,"instrument proliferation, do not certify\n")
        }
        s<-summary(m,robust=TRUE)
        print(s$coefficients)
        # 'sargan' is plm's Sargan-Hansen test; no assertion of robust Hansen equivalence.
        for (w in c("onestep","twosteps")){
          tryCatch({ j<-sargan(m,weights=w); cat("OVERID",spec,w,
                       as.numeric(j$statistic),as.numeric(j$p.value),"df",
                       as.numeric(j$parameter),"\n")
                   },error=function(e)cat("OVERID_NOT_AVAILABLE",spec,w,conditionMessage(e),"\n"))
        }
        for (order in c(1,2)){
          tryCatch({a<-mtest(m,order=order);cat("AB_SERIAL",spec,"AR",order,
                       as.numeric(a$statistic),as.numeric(a$p.value),"\n")
                   },error=function(e)cat("AB_SERIAL_NOT_AVAILABLE",spec,order,conditionMessage(e),"\n"))
        }
        cat("DIFF_IN_HANSEN_NOT_EXECUTED",spec,"plm::pgmm does not automatically provide verified nested subset test\n")
      },error=function(e)cat("GMM_FAILED",spec,conditionMessage(e),"\n"))
    }
 }
}
cat("FINISHED_REAL_R_ANALYSIS\n")
