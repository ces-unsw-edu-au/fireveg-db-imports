import openpyxl
from datetime import datetime
import re
# Create fire history records
# This is a lower level function that will create a field sample record from an item (a row in the spreadsheet), using the dictionary or "switch" in col_dicts:

def create_fire_history_record(item,col_dicts):
    records=list()
    for sw in col_dicts:
        record=dict()
        comms=list()
        if item[sw['site_label']].value == 'Site':
            continue
        for k in sw.keys():
            vals=item[sw[k]].value
            if vals is not None:
                if k == 'fire_date':
                    if isinstance(vals,datetime):
                        record['fire_date']=str(vals.date())
                        record['earliest_date']=vals.date()
                        record['latest_date']=vals.date()
                    elif isinstance(vals,int):
                        record['fire_date']=str(vals)
                        if vals>0:
                            record['earliest_date']=datetime(vals,1,1).date()
                            record['latest_date']=datetime(vals,12,31).date()
                        else:
                            comms.append('Fire date is missing or empty')
                    elif vals.isnumeric():
                        record['fire_date']=str(vals)
                        record['earliest_date']=datetime(int(vals),1,1).date()
                        record['latest_date']=datetime(int(vals),12,31).date()
                    else:
                        record['fire_date']=vals
                        comms.append('Fire date given as: %s' % vals)
                        found=re.findall("[<>]",vals)
                        for i in found:
                            comms.append('max/min value given')
                            vals=vals.replace(i,"")
                        ws=vals.split("-")
                        if len(ws)==2:
                            if len(ws[0])==4 and ws[0].isnumeric():
                                record['earliest_date']=datetime(int(ws[0]),1,1).date()
                            if len(ws[1])==4 and ws[1].isnumeric():
                                record['latest_date']=datetime(int(ws[1]),12,31).date()
                            elif len(ws[1])==2 and ws[1].isnumeric():
                                fch2=ws[0][0:2]+ws[1]
                                record['latest_date']=datetime(int(fch2),12,31).date()
    
                            
                else:
                    record[k]=vals
        if len(comms)>0:
            record['notes'] = comms
        if len(record)>1:
            records.append(record)
    return records

def import_records_from_workbook(filepath, workbook, worksheet, col_dictionary, create_record_function, **kwargs):
    wb = openpyxl.load_workbook(filepath / workbook, data_only=True)
    ws=wb[worksheet]
    row_count = ws.max_row+1
    records=list()
    for k in range(2,row_count):
        item=ws[k]
        record=create_record_function(item,col_dictionary,**kwargs)
        if record is not None:
            if type(record)==list:
                records.extend(record)
            elif type(record)==dict:
                records.append(record)
    return records
