import schedule
import time
import logging
import configparser
import psycopg2
import datetime
import json
import requests
import os
import uuid

config = configparser.ConfigParser()
if not config.read('config.ini'):
    config.read(os.path.join(os.getcwd(), 'config.ini'))


CONN_STR_QUERIES = f"host={config['QUERIES']['host']} " \
        + f"user={config['QUERIES']['user']} " \
        + f"dbname={config['QUERIES']['dbname']} " \
        + f"password={config['QUERIES']['password']} " \
        + f"sslmode={config['QUERIES']['sslmode']}"
        
CONN_STR_SUB = f"host={config['BILLING']['host']} " \
            + f"user={config['BILLING']['user']} " \
            + f"dbname={config['BILLING']['dbname']} " \
            + f"password={config['BILLING']['password']} " \
            + f"sslmode={config['BILLING']['sslmode']}"


def get_users_to_bill():
    SQL =   """
            select distinct 
                subscription_id, plan_id 
            from 
                queries 
            where
                subscription_id is not null
                and success = true 
                and billed = false 
                and completed >= now() - interval %s
            ;
            """
    billing_horizon = config['BILLING']['billing_horizon']            

    with psycopg2.connect(CONN_STR_QUERIES) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (billing_horizon, ) )
        logging.debug(f'Billing horizon: {billing_horizon}')
        uuids = cur.fetchall()
        cur.close()
        
    return uuids # list of tuples [(sub_id, plan_id), ...]
    

def get_billing_qty(db_cursor, subscription_id, plan_id):

    SQL1 =   """
            update queries
            set 
                billed = True, 
                date_billed = now() 
            where 
                subscription_id = %s 
                and plan_id = %s
                and success = true 
                and billed = false 
                and completed >= now() - interval %s
            returning 
                id ;
            """

    SQL2 =  """
            insert into bills
                (subscription_id, plan_id, units)
            values
                (%s, %s, %s)
            ;
            """

    db_cursor.execute( SQL1, (
        subscription_id, plan_id, config['BILLING']['billing_horizon'] ) )
    query_ids = db_cursor.fetchall()
    
    qty = len(query_ids)
    assert qty > 0
    logging.debug(f'subscription_id: {subscription_id}, units: {qty}')
    
    db_cursor.execute( SQL2, (subscription_id, plan_id, qty) )

    return qty


def process_single_bill(subscription_id, plan_id):
    """Use two stage DB transaction to process bills"""
    try:
        conn = psycopg2.connect(CONN_STR_QUERIES)
        conn.autocommit = False
        cur = conn.cursor()
        
        post_bill_to_API(
            subscription_id, 
            plan_id, 
            get_billing_qty(cur, subscription_id, plan_id))

        conn.commit()
        logging.debug(f'Bill posted successfully: {subscription_id}')
    except:
        conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()


def process_bills():
    users_to_bill = get_users_to_bill() 
    num_bills, n_successful = len(users_to_bill), 0
    logging.info(f'Processing {num_bills} bills')
    
    for subscription_id, plan_id in users_to_bill:
        try:
            process_single_bill(subscription_id, plan_id)
            n_successful += 1
        except:
            logging.exception(f'Error while processing bill: {subscription_id}')

    logging.info(
        f'Processed {num_bills} bills, with {num_bills - n_successful} failures')


def post_bill_to_API(uuid, plan_id, qty):
        url = config['BILLING']['baseURL']
        logging.debug(f'posting a bill to {url}')
        r = requests.post(url,
                data=make_body(uuid, plan_id, qty),
                params={'api-version': '2018-08-31'},
                headers=make_headers(uuid),
                timeout=config['BILLING'].getint('timeout_s'))
        logging.debug(f'Status code: {r.status_code} for UUID: {uuid}')
#        logging.debug(r.json())
        if not r.status_code == 200:
            raise RuntimeError(f'Error while posting bill.\n{r.json()}')

def job():
    try:
        process_bills()
    except:
        logging.exception('Error while running batch billing job')

        
def get_plan_id(uuid):
    SQL3 =   """
            SELECT distinct planid from subscriptiondetails
            where subscriptionid = %s;
            """

    with psycopg2.connect(CONN_STR_SUB) as conn:
        cur = conn.cursor()
        cur.execute( SQL3, (uuid, ) )
        pids = cur.fetchall()
        cur.close()
        
    return([pid[0] for pid in pids])
    

def make_body(uuid, plan_id, qty):
    now = datetime.datetime.utcnow()
    effectiveStartTime = now.strftime('%Y-%m-%dT%H:%M:%S')
    body = {'resourceId': uuid,
            'quantity': qty,
            'dimension': config['BILLING']['dimension'],
            'effectiveStartTime': effectiveStartTime,
            'planId': plan_id}
    return json.dumps(body)


def make_headers(uuid):
    headers = {'Content-type': 'application/json',
                'x-ms-requestid': uuid,
                'x-ms-correlationid': 'orxagrid_lcapp2',
                'authorization': 'Bearer ' + get_authorization_token()}
    return headers


def get_authorization_token():
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    body = {'grant_type': 'client_credentials',
            'client_id': config['TOKEN']['client_id'],
            'client_secret': config['TOKEN']['client_secret'],
            'resource':config['TOKEN']['resource']}
    r = requests.get(config['TOKEN']['end_point'],
                     data = body,
                     headers=headers)
    assert r.status_code == 200
    res = json.loads(r.content.decode())
    return(res['access_token'])
    
    
def make_tables(conn_str):

    SQL =   """
            CREATE TABLE
            IF NOT EXISTS bills (
                id SERIAL PRIMARY KEY,
                subscription_id UUID NOT NULL,
                plan_id TEXT NOT NULL, 
                units INT NOT NULL,
                created TIMESTAMPTZ NOT NULL DEFAULT NOW()
            ) ;
            """
    
    success = False
    while not success:
        logging.info('Trying to make bills table if not exist')
        try:
            with psycopg2.connect(conn_str) as conn:
                        
                cur = conn.cursor()
                cur.execute(SQL)
                conn.commit()
                cur.close()

            success = True

        except Exception as err:
                logging.info(err)
                time.sleep(5)


def run_service():
    make_tables(CONN_STR_QUERIES)

    schedule.every(
        config['BILLING'].getint('query_interval_seconds')).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


def make_test_data(conn_str):
    logging.debug('Inserting test data into DB')
    SQL1 =   """
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
            """

    SQL2 =  """
            INSERT INTO queries
            (subscription_id, object_id, plan_id)
            VALUES (%s, %s, %s) 
            RETURNING id;
            """

    SQL3 =  """
            UPDATE queries
            SET 
            success = true,
            completed = NOW()
            WHERE id = %s 
            ;
            """            

    subscription_id, oid, plan_id = str(uuid.uuid4()), str(uuid.uuid4()), 'foo'

    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute(SQL1)
        cur.execute( SQL2, (subscription_id, oid, plan_id) )   
        query_id = cur.fetchone()[0]     
        time.sleep(0.1)
        cur.execute( SQL3, (query_id, ) )        
        conn.commit()
        cur.close()



if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    logging.warning('Starting inline TEST MODE for billing service.'
                    ' Ensure a postgres instance is running on localhost.')

    CONN_STR_QUERIES = f"host=localhost " \
            + f"user=postgres " \
            + f"dbname=postgres " \
            + f"password=password " \
            + f"sslmode=allow"
            
    CONN_STR_SUB = CONN_STR_QUERIES

    config['BILLING']['baseURL'] = 'https://postman-echo.com/post'
    config['BILLING']['query_interval_seconds'] = '5'

    logging.debug('Job should run every 5 seconds')
    make_test_data(CONN_STR_QUERIES)
    run_service()



# https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/marketplace-metering-service-apis
"""
{
  "resourceId": <guid>, // unique identifier of the resource against which usage is emitted. 
  "quantity": 5.0, // how many units were consumed for the date and hour specified in effectiveStartTime, must be greater than 0, can be integer or float value
  "dimension": "dim1", // custom dimension identifier
  "effectiveStartTime": "2018-12-01T08:30:14", // time in UTC when the usage event occurred, from now and until 24 hours back
  "planId": "plan1", // id of the plan purchased for the offer
}
"""


# https://www.getpostman.com/collections/8aa190ce9bb7da1e85d8

# https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/saas-metered-billing

# https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-saas-fulfillment-api-v2

