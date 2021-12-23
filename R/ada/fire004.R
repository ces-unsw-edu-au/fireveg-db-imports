#Set working directory
library(RPostgreSQL)
library(ggplot2)
library(forcats)
library(dplyr)
library(data.table)
library(rpostgis)

#Database URL: http://149.171.173.203/fireveg/web/index.php
# loads the PostgreSQL driver
drv <- dbDriver("PostgreSQL")
# creates a connection to the postgres database
# note that "con" will be used later in each connection to the database
#Those are my user and password information. Sophie you need ask to JR give you your owns
con <- dbConnect(drv, dbname = dbinfo$DBNAME,
                 host = dbinfo$DBHOST, port = dbinfo$DBPORT,
                 user = dbinfo$DBUSER)

#To see the tables in the database
dbGetQuery(con,
           "SELECT table_name FROM information_schema.tables
                   WHERE table_schema='fireveg'")

#Read table from PostgreSQL into R data frame:
qry <- "SELECT * FROM form.quadrat_samples"
my.table<- dbGetQuery(con, qry)
str(my.table)

#Query for fire event dates:
qry2 <- "select v.visit_id,v.visit_date,f.fire_date,v.visit_date-f.fire_date as days_since_fire from form.field_visit v left join form.fire_history f on f.visit_id=v.visit_id"
my.fire<- dbGetQuery(con, qry2)
str(my.fire)

#Close PostgreSQL connection
dbDisconnect(con)

#write.csv(my.table, "fireveg_20200313.csv")
#write.csv(my.fire, "my.fire_20200316.csv")

####
#SPECIES TRAITS
#######
#Resprout organ
# Remove duplicated rows based on species
my.table <- read.csv("fireveg_20200530.csv",sep=",",
                     header=T, dec=".", stringsAsFactors=F, na.strings=c("","NA", "N/A"))

str(my.table)

tmp <- my.table %>% distinct(species, .keep_all = TRUE)

tmp <- tmp[!is.na(tmp$species), ]
dim(tmp) #293
tmp$species

resprout_organ3 <- data.frame(tmp$species, tmp$resprout_organ)
colnames(resprout_organ3)<-c("species1", "resprout_organ")
str(resprout_organ3)

#Seedbank
seedbank3 <- data.frame(tmp$species, tmp$seedbank)
colnames(seedbank3)<-c("species", "seedbank")
str(seedbank3)

#N total live resprouts
tmp$N1<- as.data.frame(aggregate(tmp$resprouts_live, list(tmp$species), sum))
colnames(N1)<-c("species", "N1")
dim(N1)

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
dim(N9)

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
plant.traits$n.reprod.resprout <- plant.traits$N2
plant.traits$reprod.resprout <- (100*plant.traits$N2)/(plant.traits$N2 + plant.traits$N1)
plant.traits$n.reprod.recruit <-plant.traits$N6 # the formula said N5 but this is the number of lives recruits
plant.traits$reprod.recruit <- 100*(plant.traits$N6/plant.traits$N5)
plant.traits$surv.dens <- (plant.traits$N2/625)
plant.traits$recruit.dens <-(plant.traits$N5/625)

str(plant.traits)
plant.traits <- plant.traits[!is.na(plant.traits$resprout_organ), ]
plant.traits <- plant.traits[!is.na(plant.traits$seedbank), ]

write.csv(plant.traits, "plant.traits.csv")

##Box plots
str(plant.traits)
#Resprout survival
plant.traits %>%
  ggplot(aes(x=seedbank,y=n.sprout.surv, fill=seedbank)) +
  geom_boxplot(outlier.shape=NA) + geom_jitter(width=0.1,alpha=0.2) +
  facet_wrap(~resprout_organ, scales="free")

#Recruit survival
plant.traits %>%
  ggplot(aes(x=seedbank,y=n.recruit.surv, fill=seedbank)) +
  geom_boxplot(outlier.shape=NA) + geom_jitter(width=0.1,alpha=0.2) +
  facet_wrap(~resprout_organ, scales="free")

#SEEDER
#Search spp. without reprout organ (seeder)
#create a subseb for seeder
#See number of recruit reproductive
#Calculate time lapse beetween last fire and sampling date

##########
#RESPROUTERS
#For spp. with resprout organ = rhizome
#Calculate % reprout alive (resprout alive/ live + died + kill)

#Some plots
#Live recruit density
plant.traits %>%
  mutate(name = fct_reorder(species1, recruit.dens)) %>%
  ggplot(aes(x=species1, y= recruit.dens, fill = resprout_organ)) +
  geom_bar(stat="identity", alpha=.6, width=.4) +
  coord_flip() + xlab("") +
  ylab("Recruit density") +
  theme_bw()+
  labs(title = "Live recruits density", subtitle = "N5/Area")+
  theme(text = element_text(size=7),
        strip.text.x = element_text(size=30),
        strip.text.y = element_text(size=7))

#Some plots
plant.traits %>%
  mutate(name = fct_reorder(species1, surv.dens)) %>%
  ggplot(aes(x=species1, y=surv.dens, fill = resprout_organ)) +
  geom_bar(stat="identity",  alpha=.6, width=.4) +
  coord_flip() +
  ylab("Survivor density") + xlab("") +
  theme_bw()+
  labs(title = "Resprout survivor density", subtitle = "(N2)/Area")+
  theme(text = element_text(size=12),
        strip.text.x = element_text(size=12),
        strip.text.y = element_text(size=5))

#####
#Dumbbell Plot to vizualice relative positions
#(like growth and decline) between two points in time.
#Now merge with fire information
my.spp<- data.frame(species = my.table$species,
                    visit_id = my.table$visit_id,
                    N2_tf = my.table$resprouts_reproductive,
                    N5_tf = my.table$recruits_live,
                    resprout_organ = my.table$resprout_organ)

str(my.spp)


str(my.fire)
my.fire$visit_id <- as.factor(my.fire$visit_id)
#Lollipop
#Fire frequency
summary(my.fire2$days_since_fire)

ggplot(my.fire, aes(days_since_fire, visit_id)) +
  geom_segment(aes(x = 0, y = visit_id, xend = days_since_fire, yend = visit_id), color = "grey50", size = 0.5) +
  geom_point(size = 1) +
  xlab ("Days since fire")+
  ylab ("")

#Subset only the last fire
my.fire2<-my.fire[c(1,4,5, 10,12,15,18, 22,26,27,34,35,38,43),]

my.time<- merge.data.frame(my.spp, my.fire2, by = "visit_id", all.x = T)
str(my.time)
my.time[1:5,]
####
#SEEDERS SPECIES
####
ggplot(my.time, aes(N5_tf, days_since_fire)) +
  geom_segment(aes(x = 0, y = days_since_fire, xend = N5_tf,
                   yend = days_since_fire), color = "grey50", size = 0.5) +
  geom_point(size = 1) + coord_flip()

table(my.time$species, my.time$N5_tf>1)
#Pultenaea blakelyi
ggplot(subset(my.time, species %in% c("Pultenaea blakelyi")), aes(N5_tf, days_since_fire)) +
  geom_segment(aes(x = 0, y = days_since_fire, xend = N5_tf,
                   yend = days_since_fire), color = "grey50", size = 0.5) +
  geom_point(size = 1) + coord_flip() +
  labs(title = "Pultenaea blakelyi", subtitle = "Total of live recruits")
#Entolasia marginata
ggplot(subset(my.time, species %in% c("Entolasia marginata")), aes(N5_tf, days_since_fire)) +
  geom_segment(aes(x = 0, y = days_since_fire, xend = N5_tf,
                   yend = days_since_fire), color = "grey50", size = 0.5) +
  geom_point(size = 1) + coord_flip() +
  xlab("Total of live recruits (N5)") +
  ylab("Days since fire")+
  labs(title = "Entolasia marginata", subtitle = "Total of live recruits")

#Plectrarnthus parviflorus
ggplot(subset(my.time, species %in% c("Plectranthus parviflorus")), aes(N5_tf, days_since_fire)) +
  geom_segment(aes(x = 0, y = days_since_fire, xend = N5_tf,
                   yend = days_since_fire), color = "grey50", size = 0.5) +
  geom_point(size = 1) + coord_flip() +
  labs(title = "Plectranthus parviflorus", subtitle = "Total of live recruits")

#Resprouters
table(my.time$species, my.time$N2_tf>1)
#Lomandra longifolia
ggplot(subset(my.time, species %in% c("Lomandra longifolia")), aes(N2_tf, days_since_fire)) +
  geom_segment(aes(x = 0, y = days_since_fire, xend = N2_tf,
                   yend = days_since_fire), color = "grey50", size = 0.5) +
  geom_point(size = 1) + coord_flip() +
  ylab("Days since fire") +
  xlab("Resprouts reproductive (N2)")+
  labs(title = "Lomandra longifolia", subtitle = "Resprouts reproductive (N2)")

  #Lepyrodia scariosa
  ggplot(subset(my.time, species %in% c("Lepyrodia scariosa")), aes(N2_tf, days_since_fire)) +
    geom_segment(aes(x = 0, y = days_since_fire, xend = N2_tf,
                     yend = days_since_fire), color = "grey50", size = 0.5) +
    geom_point(size = 1) + coord_flip() +
    ylab("Days since fire") +
    xlab("Resprouts reproductive (N2)")+
    labs(title = "Lepyrodia scariosa", subtitle = "Resprouts reproductive (N2)")


##END
