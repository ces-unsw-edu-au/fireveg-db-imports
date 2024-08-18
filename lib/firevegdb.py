# Function to batch process insert or update queries:
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import AsIs

## shortcut for running simple database queries
def dbquery(query,dbparams, useconn=None):
    if useconn is None:
        conn = psycopg2.connect(**dbparams)
    else:
        conn = useconn
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query)
    res = cur.fetchall()
    cur.close()
    if useconn is None and conn is not None:
        conn.close()
    return res

## Batch update or insert
def batch_upsert(params,table,records,keycol,idx, execute=False, useconn=None):
    if useconn is None:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
    else:
        conn = useconn
    cur = conn.cursor()
    updated_rows=0

    for record in records:
        if len(record.keys())>len(keycol):
            if 'geom' in record.keys():
                the_geom=record['geom']
                record['geom']='GEOMSTR'
            if idx is not None:
                qrystr = "INSERT INTO %s (%s) values %s ON CONFLICT ON CONSTRAINT %s DO UPDATE SET %s"
                upd=list()
                for k in record.keys():
                    if k not in keycol:
                        upd.append("{col}=EXCLUDED.{col}".format(col=k))
                qry = cur.mogrify(qrystr, (AsIs(table),
                                AsIs(','.join(record.keys())),
                                tuple(record.values()),
                                AsIs(idx),
                                AsIs(','.join(upd))
                               ))
            else:
                qrystr = "INSERT INTO %s (%s) values %s ON CONFLICT DO NOTHING"
                qry = cur.mogrify(qrystr, (AsIs(table),
                                AsIs(','.join(record.keys())),
                                tuple(record.values())
                               ))

            if 'geom' in record.keys():
                qry=qry.decode('utf-8')
                qry=qry.replace("'GEOMSTR'",the_geom)
                record['geom']=the_geom

            if execute:
                cur.execute(qry)
                if cur.rowcount > 0:
                    updated_rows = updated_rows + cur.rowcount
            else:
                print(qry)
            
    conn.commit()        
    cur.close()
    print("%s rows updated" % (updated_rows))
        
    if useconn is None and conn is not None:
        conn.close()
        print('Database connection closed.')

### This function filters a list of `records` to find unique records and then validate them against the information in table `field_visit` (visit_id, visit_date and replicate_nr). Any valid but missing records are inserted in table `field_visit` and the samples are inserted in table `field_sample`.
def validate_and_update_site_records(records, useconn=None):
    if useconn is None:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
    else:
        conn = useconn

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