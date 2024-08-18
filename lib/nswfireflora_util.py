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
        cell=hlink[1]
        refcodes=ref1[hlink[1]].value
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
