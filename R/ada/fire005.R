setwd("~/Documentos/Proyectos/Fire database")
library(RPostgreSQL)
library(ggplot2)
library(forcats)
library(dplyr)
library(data.table)
library(rpostgis)

#Database URL: http://terra.ad.unsw.edu.au/fireveg/web/index.php
# loads the PostgreSQL driver
drv <- dbDriver("PostgreSQL")
# creates a connection to the postgres database
# note that "con" will be used later in each connection to the database
con <- dbConnect(drv, dbname = dbinfo$DBNAME,
                 host = dbinfo$DBHOST, port = dbinfo$DBPORT,
                 user = dbinfo$DBUSER)

#To see the tables in the database
dbGetQuery(con,
           "SELECT table_name FROM information_schema.tables
                   WHERE table_schema='form'")

#       table_name
  #1     field_visit
    #2      observerid
#3   field_samples
  #4    fire_history
#5 quadrat_samples

#See colums names for a given table
dbGetQuery(con, "SELECT column_name
  FROM information_schema.columns
 WHERE table_schema = 'form'
   AND table_name   = 'quadrat_samples'")

#Read table from PostgreSQL into R data frame:
qry <- "SELECT * FROM form.quadrat_samples"
my.table<- dbGetQuery(con, qry)
str(my.table)
write.csv(my.table, "quadrat_samples_20210211.csv")

######
#ADD NEW RECORDS IN YHE DB
#####
#read the table with updates (this table only has the uodate records)
data_new <- read.csv("quadrat_samples_20210222.csv",sep=",",
                     header=T, dec=".", stringsAsFactors=F)
str(data_new)
table(data_new$resprout_organ)

# add records one by one:

#BFEH_4_UNSW ERROR:   invalid input value for enum seedbank_type: "soil_persistent" LINE 1: ...UNSW','1','Ceratopetalum apetalum','2271','basal','soil_pers.
#CANU_1_UNSW   ERROR:  invalid input value for enum seedbank_type: "soil_persistent"LINE 1: ...('CANU_1_UNSW','1','Solanum torvum','6113','none','soil_pers..
#COOM_1_UNSW ERROR:  invalid input value for enum seedbank_type: "non_canopy"LINE 1: ...','1','Argyrodendron trifoliolatum','8401','none','non_canop.
#GGRR_01_UNSW ERROR:  ERROR:  invalid input value for enum seedbank_type: "soil_persistent" LINE 1: ...R_01_UNSW','1','Solanum ditrichum','12298','none','soil_pers...
#HORT_1_UNSW ERROR:  invalid input value for enum seedbank_type: "non_canopy" LINE 1: ..._UNSW','1','Mallotus philippensis','2735','basal','non_canop...
#HUON_1_UNSW ERROR:  invalid input value for enum seedbank_type: "non_canopy" LINE 1: ...NSW','1','Cryptocarya glaucescens','3479','basal','non_canop.
#SAS002B ERROR:  invalid input value for enum seedbank_type: " root"LINE 1: ...SAS002B','1','Celastrus australis','2026','basal',' root','n...
#SASrf1 ERROR:  invalid input value for enum seedbank_type: " basal"LINE 1: ...rf1','1','Doryphora sassafras','3913','epicormic',' basal','
#SCCJB13 ERROR:  invalid input value for enum seedbank_type: "soil_persistent" LINE 1: ...ES('SCCJB13','1','Acacia maidenii','3821','basal','soil_pers...
#SCCJB37-Near ERROR:  invalid input value for enum seedbank_type: "non_canopy"LINE 1: ...-Near','1','Alectryon subcinereus','5875','basal','non_canop.
#T_01_UNSW
#T_02_UNSW
#TOOL_1_UNSW

table(data_new$visit_id == 'BFEH_4_UNSW')

slc_vst <- 'BFEH_4_UNSW'
## & data_new$resprout_organ %in% c("basal")
for (k in seq(along=data_new$visit_id)[data_new$visit_id %in% slc_vst ]) {
  newrow <- data_new[k,]
  ins <- sprintf("INSERT INTO form.quadrat_samples(%s) VALUES('%s') ON CONFLICT DO NOTHING",
                 paste(colnames(newrow)[!is.na(newrow) & newrow != ""],collapse=','),
                 paste(newrow[!is.na(newrow) & newrow != ""],collapse="','")
  )
  dbSendQuery(con,ins)
}

prg <- sprintf("SELECT * FROM form.quadrat_samples WHERE visit_id='%s'", slc_vst)
dbGetQuery(con,prg)
head(subset(data_new,visit_id %in% slc_vst))

##END
