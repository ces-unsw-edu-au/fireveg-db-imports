require("RPostgreSQL")
require(sf)

if (file.exists("secrets/dbinfo")) {
  tmp <- readLines("secrets/dbinfo")
  tmp <- data.frame(strsplit(tmp,"="))
  dbinfo <- tmp[2,]
  names(dbinfo) <- tmp[1,]
   rm(tmp)
} else {
  exit("No database information found")
}


drv <- dbDriver("PostgreSQL") ## remember to update .pgpass file
con <- dbConnect(drv, dbname = dbinfo$DBNAME,
                 host = dbinfo$DBHOST, port = dbinfo$DBPORT,
                 user = dbinfo$DBUSER)

qry <- "select visit_id,visit_date,ST_Transform(geom,4326) as geom from form.field_visit"

locs <- read_sf(con,query=qry)

require(leaflet)
leaflet() %>%
  addTiles() %>%
  addMarkers(data=locs,label=~visit_id)



 prg <- 'select * from form.field_visit';
field_visit <- dbGetQuery(con,prg)



require(dplyr)
res %>% filter(!is.na(min)) %>% transmute(qry=sprintf("UPDATE form.quadrat_samples SET species_code=%s WHERE species='%s' AND species_code is NULL", min, ScientificName)) %>% pull(qry) -> qries

for (qry in qries)
   dbSendQuery(con,qry)

 spcode <- 3574
 spname <- "Thysanotus tuberosis"
qry <- sprintf("UPDATE form.quadrat_samples SET species_code=%s WHERE species='%s' AND species_code is NULL",spcode,spname)
   dbSendQuery(con,qry)

dbDisconnect(con)
