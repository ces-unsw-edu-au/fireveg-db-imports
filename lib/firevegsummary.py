import pandas as pd
from IPython.display import display, Markdown
from lib.firevegdb import dbquery
def show_trait_info(trait_name,trait_df,params):
    # Check comments on vocabularies
    qry_vocabulary = "SELECT pg_catalog.obj_description(t.oid, 'pg_type')::json from pg_type t where typname = '%s';" 

    # Number of records per source
    qry_source = 'SELECT main_source,count(*) FROM litrev.%s GROUP BY main_source'
    # Number of records per value of categorical variable
    qry_values = ' select norm_value,count(*),count(distinct species),count(distinct species_code) from litrev.%s group by norm_value;'

    # Number of records per value of numerical variable
    qry_triplet = ' select best is NOT NULL as b, lower is NOT NULL as l, upper is NOT NULL as u,count(*),count(distinct species),count(distinct species_code) from litrev.%s group by b,l,u;'

    # Raw values when norm value is NULL 
    qry_nulls = ' select raw_value,count(*),count(distinct species),count(distinct species_code) from litrev.%s where norm_value is NULL group by raw_value;'
    # Raw values when best/lower/upper are all NULL 
    qry_triplet_nulls = 'select raw_value,count(*),count(distinct species),count(distinct species_code) from litrev.%s where best is NULL and lower is NULL and upper is NULL group by raw_value;'

    elem = trait_df[trait_df["Trait code"]==trait_name]
    msg = "***{}***: {}.\n\n_Life Stage_: {} / _Life history process_: {}" .format(
        elem.iloc[0]['Trait name'],
        elem.iloc[0]['Description'] ,
        elem.iloc[0]['Life stage'] ,
        elem.iloc[0]['Life history process'] )                
    display(Markdown(msg))
    # display(elem.transpose())
    cat_vocab = elem.iloc[0]['category_vocabulary']
    if cat_vocab is not None:
        cat_table = dbquery(qry_vocabulary % cat_vocab , params)
        display(Markdown("##### Vocabulary for trait"))
        display(pd.DataFrame(cat_table[0]).transpose())
    met_vocab = elem.iloc[0]['method_vocabulary']
    if met_vocab is not None:
        met_table = dbquery(qry_vocabulary % met_vocab,params)
        display(Markdown("##### Vocabulary for the methods"))
        display(pd.DataFrame(met_table[0]).transpose())
    display(Markdown("#### Summary of data"))
    if elem.iloc[0]['Value type'] == 'categorical':
        res = dbquery(qry_values % trait_name,params)
        data=pd.DataFrame(res,
                      columns=["Value","Nr. records","Nr. taxa","Nr. valid"])
        display(data)
        display(Markdown("Transcription errors"))
        res=dbquery(qry_nulls % trait_name,params)
        nulldata=pd.DataFrame(res,
                      columns=["Value","Nr. records","Nr. taxa","Nr. valid"])
        display(nulldata)
    if elem.iloc[0]['Value type'] == 'numerical':
        res = dbquery(qry_triplet % trait_name,params)
        data=pd.DataFrame(res,
                      columns=["best","lower","upper","Nr. records","Nr. taxa","Nr. valid"])
        display(data)
        display(Markdown("Transcription errors"))
        res=dbquery(qry_triplet_nulls % trait_name,params)
        nulldata=pd.DataFrame(res,
                      columns=["Value","Nr. records","Nr. taxa","Nr. valid"])
        display(nulldata)