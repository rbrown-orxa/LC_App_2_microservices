import psycopg2
import logging
import time
import random
from flask import current_app
import config as cfg

import subscription



def check_subscription(object_id, SSO_type):
    
    sub_id, plan_id = None, None
    if not current_app.config['APPLY_BILLING']:
      return sub_id, plan_id
    
    if SSO_type == 'ad':
        sub_id, plan_id = subscription.check_user_subscribed(object_id) #str(sid)
        return sub_id, plan_id

    elif SSO_type == 'b2c':
        check_free_query_quota(object_id)
        return sub_id, plan_id

    assert False, '500 Unexpected SSO type'


def check_free_query_quota(object_id):
    free_queries_so_far =  get_unbillable_queries(
        current_app.config['BILLING_DB_CONN_STR'],
        object_id)
    logging.info('Free queries used so far: ' + str(free_queries_so_far) + \
    ' by user: ' + str(object_id))

    assert free_queries_so_far < current_app.config['MAX_FREE_CALLS'], \
    '402 Free quota query limits exceeded for user'


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
                        
                           CREATE TABLE
                           IF NOT EXISTS bills (
                             id SERIAL PRIMARY KEY,
                             subscription_id UUID NOT NULL,
                             plan_id TEXT NOT NULL, 
                             units INT NOT NULL,
                             created TIMESTAMPTZ NOT NULL DEFAULT NOW()
                         ) ;
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
        # return None
        pass # log the query in DB even though subscription_id will be empty

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
        return

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

if __name__ == '__main__':
    class CurrentApp():
        pass

    current_app = CurrentApp
    current_app.config = {}

    logging.basicConfig(level=logging.DEBUG)
    
    current_app.config['APPLY_BILLING'] = True
    current_app.config['BILLING_DB_CONN_STR'] = \
        'postgres://postgres:password@localhost:5432/postgres'

    make_tables(current_app.config['BILLING_DB_CONN_STR'])


    id2 = query_started(
            subscription_id='6b71cfa4-fa75-3540-fc41-b72fd8ef2555',
            oid='5995EBF0-D3D8-4C3F-8921-DC59DB7E5280',
            plan_id='m1')
    time.sleep(random.random()/2)
    query_successful(id2)

    # id2 = query_started(
    #         subscription_id='CEF06856-837B-4661-A627-6B20FD268A5C')
    # time.sleep(random.random()/2)
    # query_successful(id2)

    # id4 = query_started(
    #         subscription_id='2EF06856-837B-4661-A627-6B20FD268A5B')
    # time.sleep(random.random()/2)
    # query_successful(id4)




    # bill = get_billing_quantities(current_app.config['BILLING_DB_CONN_STR'])
    # print(f'Unbilled units: {bill}')

    # time.sleep(random.random()) # simulate API billing request being sent

    # register_billed_quantities(current_app.config['BILLING_DB_CONN_STR'], bill)
