import re
import copy
r = re.compile("[A-Z][a-z]+")
def create_ref_code(x):
    
    if x.__contains__("personal communication"):
        y = x[0:x.find(" personal")].replace(",","")
        year = "pers. comm."
    elif x.__contains__("unpublished"):
        y = x[0:x.find("unpublished")].replace(",","")
        year = "unpub."
    else:
        y = x[0:x.find(")")].replace(",","")
        year = ''.join(re.findall("\d+", y))
    z = list(filter(r.match, y.split()))
    author = ' '.join(z)
    final_code =  "%s %s" % (author, year)
    if (len(final_code)>50):
        final_code=final_code[0:50]
    return(final_code)

def create_ref_code_RP(x):
    if x.__contains__("^RFA"):
        final_code = x
    else:
        final_code = "RP %s" % x
    if (len(final_code)>50):
        final_code=final_code[0:50]
    return(final_code)

def extract_link(target,ref1,ref2, ref3, ref4):
    p=re.compile('[,;\s]+')
    assert (target.hyperlink is not None),"Only works when cell has a hyperlink!"
    hlink = target.hyperlink.location
    hlink = hlink.split("!")
    if (hlink[0] != "References"): #"Expecting hyperlink to 'References' sheet"
        return None
    else:
        column=hlink[1][0:1]
        # use this to fix error with one hyperlink 'C84\\' at 'SpeciesData'.AE2080
        cell=hlink[1].replace("\\","") 
        refcodes=ref1[cell].value
        refinfo=list()
        if refcodes is not None:
            if isinstance(refcodes,int):
                for elem in filter(lambda x: x['refcode'] == refcodes, ref2):
                    refinfo.append(elem['refstring'])
            else:
                for refcode in p.split(refcodes):
                    refcode=refcode.strip(" ")
                    refcode=re.sub("[abc]$","",refcode)
                    if refcode.isnumeric():
                        for elem in filter(lambda x: x['refcode'] == int(refcode), ref2):
                            refinfo.append(elem['refstring'])
                    else:
                        for elem in filter(lambda x: x['refcode'] == refcode, ref3):
                            refinfo.append(elem['refstring'])
                        for elem in filter(lambda x: x['refcode'] == refcode, ref4):
                            refinfo.append(elem['refstring'])
            return (refcodes,refinfo)
        else:
            return None

def extract_value(target, switcher, varname, ref1, ref2, ref3, ref4,
                  splitstring="&|;|,| or | and "):
    assert (target.value is not None),"Only works whith non-empty cells"
    assert isinstance(switcher,dict),"Switcher argument must be a dictionary"
    assert isinstance(varname,str),"Variable name argument must be a string"
    p=re.compile('[,;\s]+')
    val = target.value
    rslts = list()
    note = list()
    if target.font.color != None:
        note.append('Cell color index %s' % target.font.color.indexed)
    if target.font.strike != None:
        note.append('Cell text has strikethrough')
    if isinstance(val,int) or isinstance(val,float):
        record={"raw_value":[varname,str(val)]}
        if len(note)>0:
            record["original_notes"]=note                
        rslts.append(record)
    else:
        for w in val.split('/'):
            transvalue=None
            oref=list()
            method=None
            w=w.strip(" ")
            start=0
            end=len(w)
            if w.find("(")>0:
                for refs in re.findall("\(([\w\d, ]+)\)",w):
                    for ref in p.split(refs):
                        ref=ref.strip(" ")
                        ref=re.sub("[abc]$","",ref)
                        if ref.isnumeric():
                            for elem in filter(lambda x: x['refcode'] == int(ref), ref2):
                                oref.append(elem['refstring'])
                        else:
                            for elem in filter(lambda x: x['refcode'] == ref, ref3):
                                oref.append(elem['refstring'])
                            for elem in filter(lambda x: x['refcode'] == ref, ref4):
                                oref.append(elem['refstring'])
                end=w.index("(")
            if w.find("a-")==0:
                method='Inferred from plant morphology'
                start=2
            if w.find("?")>0:
                note.append("uncertain")
                
                
            sw=w[start:end].strip(" ").replace("?","")
            
            for sv in re.split(splitstring,sw):
                newnote=copy.deepcopy(note)
                sv=sv.strip(" ")
                transvalue=switcher.get(sv, None)
                record={"raw_value":[varname,w],"main_source":"NSWFFRDv2.1"}
                if sw != w:
                    record["raw_value"].extend(['->',sw])
                    newnote.append("original record split into multiple entries, prob. different sources")
                if sv != sw:
                    record["raw_value"].extend(['->',sv])
                    newnote.append("original record split into multiple entries separated by and/or")
                if transvalue is not None:
                    record["norm_value"]=transvalue
                if method is not None:
                    newnote.append(method)
                    #record["method_of_estimation"]=method
                if len(oref)>0:
                    record["original_sources"]=oref                
                if len(newnote)>0:
                    record["original_notes"]=newnote                
                rslts.append(record)
    return(rslts)

def create_record(spreadsheet,target_col,row_index,switcher,
                  ref1,ref2,ref3,ref4,
                  sp_col='A',spcode_col='B',
                  **kwarg):
    target=spreadsheet[target_col][row_index]
    varname=spreadsheet[target_col][1].value
    if (target.value is not None):
        records=list()
        if (target.hyperlink is not None):
            ref=extract_link(target,ref1,ref2,ref3,ref4)
        else:
            ref=None
        if (target.value is not None):
            spname=spreadsheet[sp_col][row_index].value
            spcode=spreadsheet[spcode_col][row_index].value
            rec=extract_value(target,switcher,varname,
                              ref1,ref2,ref3,ref4,
                              **kwarg)
            for record in rec:
                record["species"]=spname
                record["species_code"]=spcode
                if 'original_sources' not in record and ref is not None:
                    record['original_sources'] = ref[1]
                records.append(record)
        return(records)

def extract_numeric_value(target,varname,ref1,ref2,ref3,ref4):
    assert (target.value is not None),"Only works whith non-empty cells"
    p=re.compile('[,;\s]+')
    val = target.value
    note = list()
    if target.font.color != None:
        note.append('Cell color index %s' % target.font.color.indexed)
    if target.font.strike != None:
        note.append('Cell text has strikethrough')
  
    rslts = list()
    if isinstance(val,int) or isinstance(val,float):
        record={"raw_value":[varname,str(val)],"best":val,"main_source":"NSWFFRDv2.1"}
        if len(note)>0:
            record["original_notes"]=note 
        rslts.append(record)
    else:
        for w in val.split('/'):
            newnote=copy.deepcopy(note)
            w=w.strip(" ")
            record={"raw_value":[varname,w],"main_source":"NSWFFRDv2.1"}
            if w.find("?")>0:
                newnote.append("uncertain")
                w=w.replace("?","")
            end=len(w)
            if w.find("(")>0:
                record["original_sources"]=list()
                for refs in re.findall("\(([\w\d, ]+)\)",w):
                    for ref in p.split(refs):
                        ref=ref.strip(" ")
                        ref=re.sub("[abc]$","",ref)
                        if ref.isnumeric():
                            for elem in filter(lambda x: x['refcode'] == int(ref), ref2):
                                record["original_sources"].append(elem['refstring'])
                        else:
                            for elem in filter(lambda x: x['refcode'] == ref, ref3):
                                record["original_sources"].append(elem['refstring'])
                            for elem in filter(lambda x: x['refcode'] == ref, ref4):
                                record["original_sources"].append(elem['refstring'])
                end=w.index("(")
            sw=w[0:end].strip(" ")
            if sw.isnumeric():
                record["best"]=sw
            elif sw.find("-")>0:
                val = sw.split("-")
                if val[0].isnumeric():
                    record["lower"]=val[0]
                if val[1].isnumeric():
                    record["upper"]=val[1]
            elif sw.find(">")==0:
                val=sw[1:]
                if val.isnumeric():
                    record["lower"]=val
            elif sw.find("<")==0:
                val=sw[1:]
                if val.isnumeric():
                    record["upper"]=val
            else:
                val=sw    
            
            if len(newnote)>0:
                record["original_notes"]=newnote  
            rslts.append(record)
    return(rslts)

def create_numeric_record(spreadsheet,target_col,row_index,
                         ref1,ref2,ref3,ref4,
                        sp_col='A',spcode_col='B'):
    records = list()
    target=spreadsheet[target_col][row_index]
    if (target.hyperlink is not None):
        ref=extract_link(target,ref1,ref2,ref3,ref4)
    else:
        ref=None
    if (target.value is not None):
        spname=spreadsheet[sp_col][row_index].value
        spcode=spreadsheet[spcode_col][row_index].value
        varname=spreadsheet[target_col][1].value
        rec=extract_numeric_value(target,varname,
                              ref1,ref2,ref3,ref4)
        for record in rec:
            record["main_source"]="NSWFFRDv2.1"
            record["species"]=spname
            record["species_code"]=spcode
            record["weight"]=1
            record["weight_notes"]=['automatic assignment of weight by python script','default value of 1']
            if 'original_sources' not in record and ref is not None:
                record['original_sources'] = ref[1]
            records.append(record)
    return(records)

def read_rows_resprouting(sheet,row,reg_cats,ref1,ref2):
    sp_col='A'
    code_col='B'
    fireresponse_col='J'
    comment_col='K'
    NFRR_col='BN'
    oref_col='BO'

    switcher={
        "S": "None",
        "Sr": "Few",
        "S/R": "Half",
        "Rs": "Most",
        "R": "All"
    }
    
    varname=sheet[fireresponse_col][1].value
    
    spname=sheet[sp_col][row].value
    spcode=sheet[code_col][row].value
    varvalue=sheet[fireresponse_col][row].value
    origcomment=sheet[comment_col][row].value
    NFRRraw=sheet[NFRR_col][row].value
    otherraw=sheet[oref_col][row].value

    records=list()
    
    
    record={"raw_value":[varname, varvalue], 
            "original_sources":list(), 
            "main_source":"NSWFFRDv2.1", 
            "additional_notes":["Values reclassified following rules proposed by D. Keith et al.",
                                "Automatic extraction with python script"],
           "weight_notes":["python-script import","default of 1"],
           "weight":1, 
            "original_notes":list()}

    if varvalue is not None:
        # we won't record the original or attempt transforming the value
        transvalue=switcher.get(varvalue, "Unknown")
        record["norm_value"]=transvalue
        if origcomment is not None:
            record["original_notes"].append(origcomment)
            record["additional_notes"].append("See comments in NSWFFRDv2.1 entry")
        if spcode is not None:
            record["species_code"]=spcode
        if spname is not None:
            record["species"]=spname
        newrecord=copy.deepcopy(record)
        if len(newrecord["original_sources"])==0:
            newrecord.pop("original_sources")
        if len(newrecord["original_notes"])==0:
            newrecord.pop("original_notes")
        newrecord["weight"]=10
        newrecord["weight_notes"][1]="default of 10 for summary value"
        records.append(newrecord)
        if NFRRraw is not None:
            NFRRval=NFRRraw.replace('FO(1)','FOI')
            NFRRval=NFRRval.strip(" ")
            for item in NFRRval.split(" "):
                newrecord=copy.deepcopy(record)
                newrecord["additional_notes"].append("Raw values extracted from notes/comments in NSWFFRDBv2.1")
                newrecord["raw_value"].append("Overall value of fireresponse column is %s" % varvalue)
                qry = re.findall("\d+", item)
                if len(qry)==1:
                    group = list(filter(lambda x: x['NFRRcode'] == int(qry[0]), reg_cats))
                    if len(group)==1:
                        newrecord["raw_value"][0]=("VA Group %s" % qry[0])
                        newrecord["raw_value"][1]=group[0]['category']
                    if qry[0] in ('1','2','3','8'):
                        newrecord["norm_value"] = 'None'
                    elif qry[0] in ('4','5','6','7','9','11'):
                        newrecord["norm_value"] = 'All'
                    else:
                        newrecord["norm_value"] = 'Unknown'
                qry = re.findall("[A-Z]+", item)
                if len(qry)==1:
                    ref = list(filter(lambda x: x['refcode'] == qry[0], ref1))
                    if len(ref)==1:
                        newrecord["original_sources"].append(ref[0]['refstring'])
                if sheet[NFRR_col][row].font.color is not None:
                    newrecord["additional_notes"].append("NFRR record(s) might have been ammended in NSWFFRDv2.1")
                if sheet[NFRR_col][row].font.strike is not None:
                    newrecord["additional_notes"].append("NFRR record(s) might have been discarded in NSWFFRDv2.1")
                if len(newrecord["original_sources"])==0:
                    newrecord.pop("original_sources")
                if len(newrecord["original_notes"])==0:
                    newrecord.pop("original_notes")
                records.append(newrecord)
        if otherraw is not None:
            otherval=otherraw
            for item in otherval.split(" "):
                newrecord=copy.deepcopy(record)
                newrecord["additional_notes"].append("Raw values extracted from notes/comments in NSWFFRDBv2.1")
                newrecord["raw_value"].append("Overall value of fireresponse column is %s" % varvalue)
                qry = re.findall("[IVX]+", item)
                if len(qry)==1:
                    group = list(filter(lambda x: x['othercode'] == qry[0], reg_cats))[0]
                    newrecord["raw_value"][0]=("VA Group %s" % qry[0])
                    newrecord["raw_value"][1]=group['category']
                    if qry[0] in ('I','II','III','VIII'):
                        newrecord["norm_value"] = 'None'
                    elif qry[0] in ('IV','V','VI','VII','IX','XI'):
                        newrecord["norm_value"] = 'All'
                    else:
                        newrecord["norm_value"] = 'Unknown'
                qry = re.findall("\d+", item)
                if len(qry)==1:
                    ref = list(filter(lambda x: x['refcode'] == int(qry[0]), ref2))[0]
                    newrecord["original_sources"].append(ref['refstring'])
                if len(newrecord["original_sources"])==0:
                    newrecord.pop("original_sources")
                if len(newrecord["original_notes"])==0:
                    newrecord.pop("original_notes")
                records.append(newrecord)

        return(records)
    else:
        print("empty row")
        return(None)