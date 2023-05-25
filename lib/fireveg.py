import openpyxl
from datetime import datetime
import re

# Create field site records
def create_field_site_record(item,sw):
    site_label = item[sw['site_label']].value
    if site_label is not None and site_label != "Site":
        record={'site_label': site_label}
    
        for column in ('elevation','location_description', 'gps_uncertainty_m', 'gps_geom_description'):
            if column in sw.keys():
                val=item[sw[column]].value
                if val is not None and val not in ('na','NA'):
                    record[column] =  val
    
        if 'lons' in sw.keys():
            for xs in sw['lons']:
                xlon = item[xs].value
            for ys in sw['lats']:
                ylat = item[ys].value
            srid = 4326


        if 'xs' in sw.keys():
            for xs in sw['xs']:
                xlon = item[xs].value
            for ys in sw['ys']:
                ylat = item[ys].value

            if 'fixed_utm_zone' in sw.keys():
                utm_zone=sw['fixed_utm_zone']
            else:
                utm_zone=item[sw['utm_zone']].value
            if  utm_zone == 56:
                srid = 28356
            elif utm_zone == 55:
                srid = 28355
            elif utm_zone == 54:
                srid = 28354

   
        if srid is not None and xlon is not None and ylat is not None:
            record['geom'] = "ST_GeomFromText('POINT({xlon} {ylat})', {srid})".format(xlon=xlon,ylat=ylat,srid=srid)

        return(record)

# Create field visit records
def create_field_visit_record(item,sw):
    site_label = item[sw['site_label']].value
    records = list()
    for k in sw['visit_date']:
        visit_date = item[k].value
        if site_label is not None and site_label != "Site":
            if isinstance(visit_date, datetime):
                record = {'visit_id': site_label, 'visit_date': visit_date}
                if 'survey' in sw.keys():
                    record['survey_name'] = sw['survey']
                for column in ('visit_description', 'mainobserver', 'observerlist','replicate_nr'):
                    if column in sw.keys():
                        val=item[sw[column]].value
                        if val is not None and val not in ('na','NA'):
                            if column=='observerlist':
                                val=val.split(',')
                            record[column] =  val
                records.append(record)
    return records

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

## This is a lower level function that will create a field sample record from an `item` (a row in the spreadsheet), using the dictionary or "switch" in `sw`:

def create_field_sample_record(item,sw):
    visit_id=item[sw['visit_id']].value
    if visit_id is not None and visit_id not in ('Site Number'):
        if 'replicate_nr' in sw.keys():
            replicatenr = item[sw['replicate_nr']].value
        elif 'fixed_replicate_nr' in sw.keys():
            replicatenr = sw['fixed_replicate_nr']
        else:
            replicatenr = None
        if 'sample_nr' in sw.keys():
            samplenr = item[sw['sample_nr']].value
        else:
            samplenr = None
        record={'visit_id': visit_id, 'replicate_nr': replicatenr, 'sample_nr': samplenr}
        if 'date' in sw.keys():
            visit_date = item[sw['date']].value 
            if isinstance(visit_date,datetime):
                record['visit_date'] = visit_date.date()

        
        return(record)

def create_quadrat_sample_record(item,sw,lookup,valid_seedbank,valid_organ):
    species = item[sw['species']].value
    spcode = item[sw['spcode']].value
    visit_id =  item[sw['visit_id']].value
    if species is not None:
        record={'visit_id': visit_id, 'sample_nr': item[sw['sample_nr']].value,
                'species': species}
        comms=list()
        if 'workbook' in sw.keys():
            comms.append("Imported from workbook %s using python script" % sw['workbook'])
        if 'worksheet' in sw.keys():
            comms.append("Imported from spreadsheet %s" % sw['worksheet'])
    
        if 'date' in sw.keys():
            visit_date = item[sw['date']].value
        else:
            visit_date = None
            
        if 'replicate_nr' in sw.keys():
            replicate_nr = item[sw['replicate_nr']].value
        elif 'fixed_replicate_nr' in sw.keys():
            replicate_nr = sw['fixed_replicate_nr']
        
        if isinstance(visit_date,datetime):
            record['visit_date'] = visit_date.date()
        else:    
            p=filter(lambda n: n['visit_id'] == visit_id and  n['replicate_nr'] == replicate_nr, lookup)
            found=list(p)
            if len(found)==1 and 'visit_date' in found[0].keys():
                visit_date=found[0]['visit_date']
                if isinstance(visit_date,datetime):
                    record['visit_date'] = visit_date.date()
                    comms.append("visit date not provided, matched by replicate nr %s" % replicate_nr)
                else:
                    record['visit_date'] = visit_date
                    comms.append("matched by replicate nr %s, assuming date object" % replicate_nr)
            else:
                comms.append("neither visit date nor replicate nr was matched ( replicate nr %s ), no date" % replicate_nr)

        if (isinstance(spcode, str) and spcode.isnumeric()) or isinstance(spcode,int):
            record['species_code']=spcode
         
        for k in ('species_notes', 'resprout_organ', 'seedbank', 'adults_unburnt', 'resprouts_live', 'resprouts_died', 'resprouts_kill', 'resprouts_reproductive',
                  'recruits_live', 'recruits_reproductive', 'recruits_died','notes'):
            if k in sw.keys():
                vals=item[sw[k]].value
                if vals is not None and vals not in ('na','NA'):
                    if k == 'resprout_organ':
                        if vals in valid_organ:
                            record[k]=vals
                        elif vals.capitalize() in valid_organ:
                            record[k]=vals.capitalize()
                        else:
                            comms.append("resprout organ written as %s" % vals)
                    elif k == 'seedbank':
                        if vals in valid_seedbank:
                            record[k]=vals
                        elif vals.capitalize() in valid_seedbank:
                            record[k]=vals.capitalize()
                        else:
                            comms.append("seedbank written as %s" % vals)
                    elif k == 'notes':
                        if isinstance(vals,(int, float, complex)):
                            comms.append("Comment column included a numeric value of %s" % vals)
                        else:
                            comms.append(vals)
                    elif k in ('adults_unburnt', 'resprouts_live', 'resprouts_died', 'resprouts_kill', 'resprouts_reproductive',
                  'recruits_live', 'recruits_reproductive', 'recruits_died'):
                        if isinstance(vals,int):
                            record[k]=vals   
                        else:
                            comms.append("%s written as %s" % (k,vals))
                    else:
                        record[k]=vals        
        
        if len(comms)>0:
            record["comments"]=comms
        
        return(record)

### This function filters a list of `records` to find unique records and then validate them against the information in table `field_visit` (visit_id, visit_date and replicate_nr). Any valid but missing records are inserted in table `field_visit` and the samples are inserted in table `field_sample`.
def validate_and_update_site_records(records, useconn=None):
    if useconn is None:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
    else:
        conn = useconn
    conn = psycopg2.connect(**params)

    cur = conn.cursor(cursor_factory=DictCursor)
    unique_records = list()
    sites = list()
    for record in records:
        if record not in unique_records:
            unique_records.append(record)
            if record['visit_id'] not in sites:
                sites.append(record['visit_id'])
    #alternative
    #from psycopg2 import sql
    #qry= sql.SQL('SELECT DISTINCT visit_id,visit_date,replicate_nr FROM form.field_visit WHERE visit_id IN ({}) ORDER by visit_id, visit_date;').format(
    #    sql.SQL(',').join(map(sql.Literal, sites))
    #)
    qryvisits= cur.mogrify('SELECT DISTINCT visit_id,visit_date,replicate_nr FROM form.field_visit WHERE visit_id IN %s ORDER by visit_id, visit_date;',(tuple(sites),))
    cur.execute(qryvisits)
    ##print(qry)
    visits = cur.fetchall()
    updated_rows=0
    for record in unique_records:
        if any(d['visit_id'] == record['visit_id'] for d in visits):
            if 'visit_date' in record.keys():
                p=filter(lambda n: n['visit_id'] == record['visit_id'] and  n['visit_date'] == record['visit_date'], visits)
                found=list(p)
                record['found']=len(found)
            elif 'replicate_nr' in record.keys():
                p=filter(lambda n: n['visit_id'] == record['visit_id'] and  n['replicate_nr'] == record['replicate_nr'], visits)
                found=list(p)
                #print(found)
                record['found']=len(found)
                if (len(found)>0):
                    record['visit_date']=found[0][1]
   
            if 'visit_date' in record.keys():
                cur.execute('INSERT INTO form.field_visit(visit_id,visit_date) values %s ON CONFLICT DO NOTHING',
                            (tuple([record['visit_id'],record['visit_date']]),))
                if cur.rowcount > 0:
                    updated_rows = updated_rows + cur.rowcount
                cur.execute('INSERT INTO form.field_samples(visit_id,visit_date,sample_nr) values %s ON CONFLICT DO NOTHING',
                        (tuple([record['visit_id'],record['visit_date'],record['sample_nr']]),))
                if cur.rowcount > 0:
                    updated_rows = updated_rows + cur.rowcount        
            else:
                print("record for %s is incomplete" % record['visit_id'])
        else:
            print("%s not found" % record['visit_id'])
            record['found']=0

    print("%s rows updated" % updated_rows)
    conn.commit()
    
    cur.execute(qryvisits)
    ##print(qry)
    updated_visits = cur.fetchall()

    cur.close()

    if useconn is None and conn is not None:
        conn.close()
        print('Database connection closed.')
    return(updated_visits)



### Functions to read records in a workbook
# We need a wrapping function to apply a lower level function (`create_record_function`) to all rows in a `worksheet` of the selected `workbook` using a dictionary `col_dictionary`, we add a `**kwargs` to pass additional arguments to the lower level function:

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
