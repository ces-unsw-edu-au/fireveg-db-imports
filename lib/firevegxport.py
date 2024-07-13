import pandas as pd

def summarise_values(x,w):
    if None in x:
        sfx = " * "
    else:
        sfx = ""
    df=pd.concat({"value": pd.Series(x),"weight": pd.Series(w)},axis=1)
    res = df.groupby(by="value").sum() / df.weight.sum()
    res = res.sort_values(by="weight",ascending=[0])
    val = ""
    glue = ""
    for index, row in res.iterrows():
        if row['weight'] > 0.1:
            val = val + glue + index 
            glue = " / "
        elif row['weight'] > 0.05:
            val = val + glue + ("(%s)" % index) 
            glue = " / "
        else:
            val = val + glue + ("[%s]" % index)
            glue = " / "
    return (val + sfx).strip(" ")

def summarise_triplet(x,y,z,w):
    df=pd.concat({"best": pd.Series(x),"lower": pd.Series(y),"upper": pd.Series(z),"weight": pd.Series(w)},axis=1)
    val="%0.1f (%0.1f -- %0.1f)" % (df['best'].mean(),df['lower'].min(),df['upper'].max())
    if val=="nan (nan -- nan)":
        val="*"
    elif val.find("nan")==0:
        val=val.replace("nan (","(")
    elif val.find("nan")>0:
        val=val.replace(" (nan -- nan)","")
    if val.find("nan")>0:
        val=val.replace("nan","?")
    return val 

def unique_taxa(row,slc):
    ss=[col.find(slc)>0 for col in row.index.tolist()]
    record=row[ss]
    records=record.values.tolist()
    valid=list()
    for x in records:
        if type(x)==list:
            valid=valid+x
    z=list(set(valid))
    z="; ".join(z)
    return(z)



def extract_refs(row,slc):
    ss=[col.find(slc)>0 for col in row.index.tolist()]
    record=row[ss]
    records=record.values.tolist()
    valid=list()
    for x in records:
        if type(x)==list:
            valid=valid+x
    z=list(set(valid))
    return(z)