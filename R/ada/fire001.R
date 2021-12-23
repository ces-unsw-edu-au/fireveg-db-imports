setwd("~/Documentos/Proyectos/Fire database")
library(RPostgreSQL)
library(ggplot2)
library(forcats)
library(dplyr)
library(data.table)

# loads the PostgreSQL driver
drv <- dbDriver("PostgreSQL")
# creates a connection to the postgres database
# note that "con" will be used later in each connection to the database
con <- dbConnect(drv, dbname = dbinfo$DBNAME,
                 host = dbinfo$DBHOST, port = dbinfo$DBPORT,
                 user = dbinfo$DBUSER)

#Read table from PostgreSQL into R data frame:
qry <- "SELECT * FROM form.quadrat_samples"
my.table<- dbGetQuery(con, qry)
str(my.table)
#Close PostgreSQL connection
dbDisconnect(con)

write.csv(my.table, "fireveg_20200313.csv")

####
#SPECIES TRAITS
#######
#Resprout organ
ro<-table(my.table$species, my.table$resprout_organ)
resprout_organ <- as.data.frame.matrix(ro)
resprout_organ2 <-setDT(resprout_organ, keep.rownames = TRUE)[]
resprout_organ3 <- as.data.frame(resprout_organ2)
colnames(resprout_organ3)<-c("plant_species", "basal", "crown", "epicormic",
                             "ligno", "none", "other", "rhizoma",
                             "stolon", "tuber")
str(resprout_organ3)

#Seedbank
sb <-table(my.table$species, my.table$seedbank)
seedbank <- as.data.frame.matrix(sb)
seedbank2 <-setDT(seedbank, keep.rownames = TRUE)[]
seedbank3 <- as.data.frame(seedbank2)
colnames(seedbank3)<-c("plant_species1", "canopy", "non_canopy", "other", "soil_persistent", "transient")
str(seedbank3)

#N total live resprouts
N1<- as.data.frame(aggregate(my.table$resprouts_live, list(my.table$species), sum))
colnames(N1)<-c("species", "N1")

#N reproductive live resprouts
N2<- as.data.frame(aggregate(my.table$resprouts_reproductive, list(my.table$species), sum))
colnames(N2)<-c("species", "N2")

#N total live recruits
N5<- as.data.frame(aggregate(my.table$recruits_live, list(my.table$species), sum))
colnames(N5)<-c("species", "N5")

#N reproductive live recruits
N6<- as.data.frame(aggregate(my.table$recruits_reproductive, list(my.table$species), sum))
colnames(N6)<-c("species", "N6")

#N Dead sprouts
N7<- as.data.frame(aggregate(my.table$resprouts_died, list(my.table$species), sum))
colnames(N7)<-c("species", "N7")

#N dead recruits
N8<- as.data.frame(aggregate(my.table$recruits_died, list(my.table$species), sum))
colnames(N8)<-c("species", "N8")

#N fire killed (resprouts?)
N9<- as.data.frame(aggregate(my.table$resprouts_kill, list(my.table$species), sum))
colnames(N9)<-c("species", "N9")

#Combine in a data frame
plant.traits <-cbind.data.frame(seedbank3, resprout_organ3, N1, N2, N5, N6, N7, N8, N9)
str(plant.traits)
#Delete colunm species
drops <- c("species", "plant_species")
plant.traits <-plant.traits[ , !(names(plant.traits) %in% drops)]
#rhizoma.traits["species"] <- NULL

#Species characteristics
plant.traits$n.fire.mortality <- (plant.traits$N1 + plant.traits$N7 + plant.traits$N9)
plant.traits$fire.mortality <- (100*plant.traits$N9)/(plant.traits$N1 + plant.traits$N7 + plant.traits$N9)
plant.traits$n.sprout.surv <-(plant.traits$N1 + plant.traits$N7)
plant.traits$sprout.surv <- (100*plant.traits$N1)/(plant.traits$N1 + plant.traits$N7)
plant.traits$seed_adult <- (plant.traits$N5 + plant.traits$N8)/(plant.traits$N1 + plant.traits$N7)
plant.traits$n.recruit.surv <- (plant.traits$N5 + plant.traits$N8)
plant.traits$recruit.surv <- (100*plant.traits$N5)/(plant.traits$N5 + plant.traits$N8)
plant.traits$n.reprod.resprout <- plant.traits$N1
#rhizoma.traits$reprod.resprout <- 100*N2/N12
plant.traits$n.reprod.recruit <-plant.traits$N6 # the formula said N5 but this is the number of lives recruits
plant.traits$reprod.recruit <- 100*(plant.traits$N6/plant.traits$N5)
plant.traits$surv.dens <- (plant.traits$N2/625)
plant.traits$recruit.dens <-(plant.traits$N5/625)

str(plant.traits)
write.csv(plant.traits, "plant.traits.csv")


#SEEDER
#Search spp. without reprout organ (seeder)
#create a subseb for seeder
#See number of recruit reproductive
#Calculate time lapse beetween las fire and sampling date

#Crate a new data frame subsetting plant without reprout organ
seeders <- subset(plant.traits, none == 1)
str(seeders)
data.frame(seeders$plant_species1, seeders$none, seeders$rhizoma)

#Some plots
#Number of reproductive recruits
seeders %>%
  mutate(name = fct_reorder(plant_species1, n.reprod.recruit)) %>%
  ggplot(aes(x=plant_species1, y=n.reprod.recruit)) +
  geom_bar(stat="identity", fill="#f68060", alpha=.6, width=.4) +
  coord_flip() +
  xlab("") +
  theme_bw()
#There is none reproductive recruits is too soon I guess because there are
#live recruits
#Live recruit density
seeders %>%
  mutate(name = fct_reorder(plant_species1, recruit.dens)) %>%
  ggplot(aes(x=plant_species1, y= recruit.dens)) +
  geom_bar(stat="identity", fill="#f68060", alpha=.6, width=.4) +
  coord_flip() +
  xlab("") +
  theme_bw()

#Type of seedbank
str(my.table)

#Seed bank for seeders
myplot<-ggplot(my.table, aes(species, seedbank, fill=seedbank)) +
  geom_bar(stat="identity", position=position_dodge()) +
  coord_flip()

myplot %+% subset(my.table, resprout_organ %in% c("none"))

seeders %>%
  mutate(name = fct_reorder(plant_species1, soil_persistent)) %>%
  ggplot(aes(x=plant_species1, y=  soil_persistent)) +
  geom_bar(stat="identity", fill="#f68060", alpha=.6, width=.4) +
  coord_flip() +
  xlab("") +
  theme_bw()

##########
#RESPROUTERS
#For spp. with resprout organ = rhizome
#Calculate % reprout alive (resprout alive/ live + died + kill)

table(plant.traits$rhizoma)
my.rhizoma <- subset(plant.traits, rhizoma ==1)
str(my.rhizoma)
#14 obs. of  34 variables
table(my.rhizoma$plant_species1, my.rhizoma$rhizoma)
str(my.rhizoma)
write.csv(my.rhizoma, "my.rhizoma.csv")

#Some plots
my.rhizoma %>%
  mutate(name = fct_reorder(plant_species1, surv.dens)) %>%
  ggplot(aes(x=plant_species1, y=surv.dens)) +
  geom_bar(stat="identity", fill="#f68060", alpha=.6, width=.4) +
  coord_flip() +
  xlab("") +
  theme_bw()

rhizoma.traits %>%
  mutate(name = fct_reorder(plant_species, n.reprod.resprout)) %>%
  ggplot(aes(x=plant_species, y= n.reprod.resprout)) +
  geom_bar(stat="identity", fill="#f68060", alpha=.6, width=.4) +
  coord_flip() +
  xlab("") +
  theme_bw()

##END
