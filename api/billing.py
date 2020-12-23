import logging
import time
import random
from flask import current_app
import config as cfg
import psycopg2

import subscription


def check_subscription(object_id, SSO_type, dom):
    
    sub_id, plan_id,used_no,max_no = None, None, None, None
    if not current_app.config['APPLY_BILLING']:
      return sub_id, plan_id
    
    if SSO_type == 'ad':
        sub_id, plan_id, used_no, max_no = subscription.check_user_subscribed(object_id) #str(sid)
        return sub_id, plan_id, used_no, max_no

    elif SSO_type == 'b2c':
        if dom == "orxagrid.com":
            used_no=0
        else:            
            used_no=check_free_query_quota(object_id)
            
        return sub_id, plan_id,used_no,cfg.MAX_FREE_CALLS

    assert False, '500 Unexpected SSO type'
 


def check_free_query_quota(object_id):
    free_queries_so_far =  get_unbillable_queries(
        current_app.config['BILLING_DB_CONN_STR'],
        object_id)
    logging.info('Free queries used so far: ' + str(free_queries_so_far) + \
    ' by user: ' + str(object_id))
        
    if free_queries_so_far <= current_app.config['MAX_FREE_CALLS']:
        return free_queries_so_far

    assert False, '402 Free quota query limits exceeded for user'


def make_tables(conn_str):

    success = False
    while not success:
        logging.info('Trying to make query table if not exist')
        try:
            with psycopg2.connect(conn_str) as conn:
                SQL =   """
                        CREATE TABLE
                        IF NOT EXISTS queries (
                            id SERIAL PRIMARY KEY,
                            started TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            success BOOLEAN NOT NULL DEFAULT FALSE,
                            subscription_id UUID,
                            plan_id TEXT,
                            object_id UUID,
                            completed TIMESTAMPTZ,
                            billed BOOLEAN NOT NULL DEFAULT FALSE,
                            date_billed TIMESTAMPTZ 
                        );
                        
                         --   CREATE TABLE
                         --   IF NOT EXISTS bills (
                         --     id SERIAL PRIMARY KEY,
                         --     subscription_id UUID NOT NULL,
                         --     plan_id TEXT NOT NULL, 
                         --     units INT NOT NULL,
                         --     created TIMESTAMPTZ NOT NULL DEFAULT NOW()
                         -- ) ;
                        """
                        

                cur = conn.cursor()
                cur.execute(SQL)
                conn.commit()
                cur.close()

            logging.info('Success')
            success = True

        except Exception as err:
                logging.info(err)
                time.sleep(5)



def query_started(subscription_id, oid, plan_id):
    
    if not current_app.config['APPLY_BILLING']:
        subscription_id = None

    conn_str = current_app.config['BILLING_DB_CONN_STR']
    logging.info('Registering query started')
    
    SQL =  """
            INSERT INTO queries
            (subscription_id, object_id, plan_id)
            VALUES (%s, %s, %s) 
            RETURNING id;
            """

    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (subscription_id, oid, plan_id) )
        conn.commit()
        id = cur.fetchone()[0]
        cur.close()

    logging.info(f'Got query id: {id}')

    return id


def query_successful(query_id):

    if not current_app.config['APPLY_BILLING']:
        pass # mark as successful
        #TODO: check that suscription_id is Null
        # return # TODO - mark as successful but do not bill

    conn_str = current_app.config['BILLING_DB_CONN_STR']
    logging.info('Registering successful query')
    
    SQL1 =  """
            UPDATE queries
            SET 
            success = true,
            completed = NOW()
            WHERE id = %s 
            -- RETURNING subscription_id 
            ;
            """

    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL1, (query_id, ) )
        conn.commit()
        cur.close()


def get_unbillable_queries(conn_str, oid=''):

     if oid:
         SQL =   """
                 SELECT count(*) 
                 FROM queries 
                 WHERE object_id = %s 
                 AND success = True;
                 """
         with psycopg2.connect(conn_str) as conn:
             cur = conn.cursor()
             cur.execute( SQL, (oid, ) )
             rv = cur.fetchone()[0]
             cur.close()
         return rv
     
def get_billed_queries(conn_str,sid='',stdt='',enddt='',plan_id=''):

     if sid:
         SQL =   """
                 SELECT count(*)
                 FROM queries 
                 WHERE subscription_id = %s
                 AND to_date(to_char(date_billed,'YYYY-MM-DD'),'YYYY-MM-DD') >= %s
                 AND to_date(to_char(date_billed,'YYYY-MM-DD'),'YYYY-MM-DD') <= %s
                 AND success = True
                 AND billed = True
                 AND plan_id = %s;
                 """
         with psycopg2.connect(conn_str) as conn:
             cur = conn.cursor()
             cur.execute( SQL, (sid,stdt,enddt,plan_id) )
             rv = cur.fetchone()[0]
             cur.close()
         return rv

if __name__ != '__main__':

    if cfg.APPLY_BILLING:
        make_tables(cfg.BILLING_DB_CONN_STR)

else: #run inline tests

    class CurrentApp():
        pass

    current_app = CurrentApp
    current_app.config = {}

    logging.basicConfig(level=logging.DEBUG)

    logging.debug('Running inline test for billing.py')
    
    current_app.config['BILLING_DB_CONN_STR'] = \
        'postgres://postgres:password@localhost:5432/postgres'
    current_app.config['APPLY_BILLING'] = True

    make_tables(current_app.config['BILLING_DB_CONN_STR'])


    logging.debug('Creating query entry with subscription_id for AAD')
    id1 = query_started(
            subscription_id='6b71cfa4-fa75-3540-fc41-b72fd8ef2555',
            oid='5995EBF0-D3D8-4C3F-8921-DC59DB7E5280',
            plan_id='m1')
    time.sleep(random.random()/2)
    query_successful(id1)


    logging.debug('Creating query entry with object_id for B2C')
    id2 = query_started(
            subscription_id=None,
            oid='9e5ffe58-9a55-41d4-ad25-3d1f45b544dc',
            plan_id=None)
    time.sleep(random.random()/2)
    query_successful(id2)


    logging.debug('Creating query entry with subscription_id but billing off')
    current_app.config['APPLY_BILLING'] = False    
    id3 = query_started(
            subscription_id='69a7c491-88d5-4a51-ab28-abc351234fe9',
            oid=None,
            plan_id='m1')
    time.sleep(random.random()/2)
    query_successful(id3)    

    
    logging.debug("Checking correct subscription_id's were put into DB")

    conn_str = 'postgres://postgres:password@localhost:5432/postgres'
    SQL =   """
            SELECT subscription_id
            FROM queries
            WHERE id = %s
            """

    logging.debug('Checking AAD query entry')
    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (id1, ) )
        rv = cur.fetchone()[0]
        cur.close()
    assert rv == '6b71cfa4-fa75-3540-fc41-b72fd8ef2555', f'Query ID {id1} failed'
    logging.debug(f'Query ID {id1} test passed')
    
    logging.debug('Checking B2C query entry')
    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (id2, ) )
        rv = cur.fetchone()[0]
        cur.close()
    assert rv is None, f'Query ID {id2} failed'
    logging.debug(f'Query ID {id2} test passed')

    logging.debug('Checking unbilled query entry')
    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (id2, ) )
        rv = cur.fetchone()[0]
        cur.close()
    assert rv is None, f'Query ID {id3} failed'
    logging.debug(f'Query ID {id3} test passed')


    logging.debug('Inline test passed')