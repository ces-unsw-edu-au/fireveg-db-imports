require(austraits)
require(dplyr)rec
require(tidyr)
require(sf)
require(readr)
require(galah)
require(taxize)

## shared by Will
will.data <- read_csv("data/blue_table.csv", col_types="cccccccccccc")
will.data$trait_name %>% table()

will.data %>% distinct(trait_name) %>% pull -> slc_traits
# almost the same as the ones included here:
austraits <- load_austraits()

## summary
austraits$traits%>% summarise(taxa=n_distinct(taxon_name),traits=n_distinct(trait_name),datasets=n_distinct(dataset_id))

mi.tkn <- readLines("~/.IUCNAPItoken")
qry <- get_iucn("Eidothea hardeniana",key=mi.tkn)
attr(qry,"uri")


austraits$traits %>% filter(grepl("fire",trait_name ) | trait_name %in% slc_traits) %>% group_by(trait_name,unit,value_type) %>% summarise(total=n(),refs=n_distinct(dataset_id),nspp=n_distinct(taxon_name)) %>% print.AsIs()

austraits$traits %>% filter(trait_name %in% "fire_response_juvenile") %>% select(value,unit,replicates,taxon_name,original_name) 

austraits$traits %>% filter(trait_name %in% "fire_response_juvenile") %>% group_by(value) %>% summarise(total=n(),refs=n_distinct(dataset_id),nspp=n_distinct(taxon_name)) 

austraits$traits %>% filter(trait_name %in% "fire_cued_seeding") %>% group_by(value) %>% summarise(total=n(),refs=n_distinct(dataset_id),nspp=n_distinct(taxon_name)) 

austraits$traits %>% filter(trait_name %in% "fire_cued_seeding") %>% group_by(value) %>% summarise(total=n(),refs=n_distinct(dataset_id),nspp=n_distinct(taxon_name)) 

sites <- austraits$sites %>%  filter(site_property %in% c("longitude (deg)", "latitude (deg)")) %>% mutate(value=as.numeric(value)) %>% filter(!is.na(value)) %>% pivot_wider(names_from = site_property, values_from = value)

sites.ll <- st_as_sf(sites,
                 coords = c("longitude (deg)", "latitude (deg)"),
                 crs = 4326)

plot(sites.ll)


austraits$traits %>% filter(trait_name %in% "fire_cued_seeding") %>% distinct(dataset_id,site_name) 

fire_risk <- read_csv("data/Appendix_S2.csv")


austraits$traits %>% filter(taxon_name %in% "Actinotus helianthi") %>% group_by(trait_name,unit,value_type) %>% summarise(total=n(),refs=n_distinct(dataset_id),nspp=n_distinct(taxon_name)) %>% print.AsIs()


austraits$traits %>% filter(taxon_name %in% "Actinotus helianthi")



