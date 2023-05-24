# Function to batch process insert or update queries:
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import AsIs

def batch_upsert(params,table,records,keycol,idx, execute=False,useconn=None):
    if useconn is None:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
    else:
        conn = useconn
    cur = conn.cursor()
    #postgis.register(cur)
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
