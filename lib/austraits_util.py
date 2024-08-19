from IPython.display import display, Markdown
def extract_reflabel(x,refid):
    authors=list()
    year=x.entries[refid].fields['year']
    for person in x.entries[refid].persons['author']:
        authors.extend(person.last_names)
    reflabel = "%s %s" % (" ".join(authors),year)
    if len(reflabel)>50:
        reflabel=reflabel[0:47]+"..."
    return(reflabel)

def extract_refinfo(x,refid):
    year=x.entries[refid].fields['year']
    title=x.entries[refid].fields['title']
    persons = x.entries[refid].persons['author']
    if len(persons)==1:
        refcitation = "%s (%s) %s" % (persons[0],year, title)
    else:
        authors=list()
        for person in persons:
            authors.append(person.__str__())
        refcitation = "%s (%s) %s" % ("; ".join(authors),year, title)
    for f in ('journal','volume','doi'):
        if f in x.entries[refid].fields.keys():
            refcitation = refcitation + " " + x.entries[refid].fields[f]
    return refcitation 

def match_spcode(row, taxlist):
    spname=row['taxon_name']
    altname=row['original_name']
    result={'species':spname}
    if altname!=spname:
        result['original_notes']=['original_name:',altname]
    spp_info = taxlist[taxlist['scientificName'] == spname] 
    spcode=None
    if len(spp_info)==1 and spp_info.speciesCode_Synonym is not None:
        spcode=spp_info.speciesCode_Synonym.values[0]
        result['species_code']=spcode
    elif spname != altname:
        spp_info = taxlist[taxlist['scientificName'] == altname]
        if len(spp_info)==1 and spp_info.speciesCode_Synonym is not None:
            spcode=spp_info.speciesCode_Synonym.values[0]
            result['species_code']=spcode
            result['original_notes'].append('original name used to match with BioNET names')
 
    return result

def create_record(row, refs, vocab, taxlist):
    refid=row['dataset_id']
    if refid in list(refs.entries.keys()):
        reflabel = extract_reflabel(refs,refid)
    else:
        reflabel=refid
    
    transvalue=vocab.get(row['value'], None)
    
    record={'main_source': 'austraits-6.0.0',
            'additional_notes': ['Values reclassified by JRFP',
                                'Automatic extraction with python script'],
            'raw_value': [row['trait_name'],row['value'],row['value_type']],
            'original_notes': ['observation_id',str(row['observation_id']),],
           'original_sources':[reflabel,]}
    spinfo=match_spcode(row, taxlist)
    for key in spinfo.keys():
        record[key]=spinfo[key]
    if row['source_id'] != "nan":
        for srcid in row['source_id'].split(','):
            srcid=srcid.strip()
            if srcid in list(refs.entries.keys()):
                srclabel = extract_reflabel(refs,srcid)
            else:
                srclabel=srcid
            record['original_sources'].append(srclabel)
        record['additional_notes'].append('Austraits (v6.0.0) record with source_id as well as dataset_id')
    if reflabel=='NSWFRD_2014':
        record['weight'] = 0
        record['weight_notes'] = ["python-script import","default of 0 for redundant records"]
    else:
        record['weight'] = 1
        record['weight_notes'] = ["python-script import","default of 1"]
    if transvalue is not None:   
        record["norm_value"]=transvalue
    if row['location_id'] != "nan":
        record['original_notes'].append('location id:')
        record['original_notes'].append(str(row['location_id']))
    return(record)

def trait_summary(definitions, traits, trait_name):
    description = definitions[trait_name]['description']
    allowed_values = definitions[trait_name]['allowed_values_levels']
    ss = (traits['trait_name']==trait_name)
    plainstr = "**Description**: %s\n\n**Records in Austraits**: %s.\n\n**Allowed values**:" % (description, traits[ss].shape[0])
    display(Markdown(plainstr))
    for k,v in allowed_values.items():
        display(Markdown("*{}*:\n{}\n".format(k,v)))
    display(Markdown("Frequency of values in this version of Austraits:\n"))
    res = traits[ss]['value'].value_counts()
    print(res)