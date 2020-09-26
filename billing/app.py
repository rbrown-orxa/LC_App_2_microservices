import schedule
import time
import logging
import configparser
import psycopg2
import datetime
import json
import requests
import os

config = configparser.ConfigParser()
if not config.read('config.ini'):
    config.read(os.path.join(os.getcwd(), 'config.ini'))


loglevel = getattr(logging, config['DEBUG']['loglevel'].upper())
logging.basicConfig(level=loglevel)

CONN_STR = f"host={config['DB']['host']} " \
        + f"user={config['DB']['user']} " \
        + f"dbname={config['DB']['dbname']} " \
        + f"password={config['DB']['password']} " \
        + f"sslmode={config['DB']['sslmode']}"
        
CONN_STR_SUB = f"host={config['DB']['host']} " \
            + f"user={config['DB']['user']} " \
            + f"dbname={config['DB']['dbnamesub']} " \
            + f"password={config['DB']['password']} " \
            + f"sslmode={config['DB']['sslmode']}"


def get_users_to_bill():
    SQL =   """
            select distinct 
                subscription_id 
            from 
                queries 
            where
                subscription_id is not null
                and success = true 
                and billed = false 
                and completed >= now() - interval %s
            ;
            """

    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (config['BILLING']['billing_horizon'], ) )
        uuids = cur.fetchall()
        cur.close()
    
    return [uuid[0] for uuid in uuids]


def get_billing_qty(db_cursor, subscription_id):

    SQL1 =   """
            update queries
            set 
                billed = True, 
                date_billed = now() 
            where 
                subscription_id = %s 
                and success = true 
                and billed = false 
                and completed >= now() - interval %s
            returning 
                id ;
            """

    SQL2 =  """
            insert into bills
                (subscription_id, units)
            values
                (%s, %s)
            ;
            """

    db_cursor.execute( SQL1, (
        subscription_id, config['BILLING']['billing_horizon'] ) )
    query_ids = db_cursor.fetchall()
    
    qty = len(query_ids)
    assert qty > 0
    logging.debug(f'subscription_id: {subscription_id}, units: {qty}')
    
    db_cursor.execute( SQL2, (subscription_id, qty) )

    return qty


def process_single_bill(subscription_id):
    """Use two stage DB transaction to process bills"""
    try:
        conn = psycopg2.connect(CONN_STR)
        conn.autocommit = False
        cur = conn.cursor()
        
        post_bill_to_API(
            subscription_id, get_billing_qty(cur, subscription_id))

        conn.commit()
        logging.debug(f'Bill posted successfully: {subscription_id}')
    except:
        conn.rollback()
        raise RuntimeError(f'Error while processing bill: {subscription_id}')
    finally:
        if conn:
            cur.close()
            conn.close()


def process_bills():
    users_to_bill = get_users_to_bill() 
    num_bills, n_successful = len(users_to_bill), 0
    logging.info(f'Processing {num_bills} bills')
    
    for subscription_id in users_to_bill:
        try:
            process_single_bill(subscription_id)
            n_successful += 1
        except:
            logging.warning(f'Error while processing bill: {subscription_id}')

    logging.info(
        f'Processed {num_bills} bills, with {num_bills - n_successful} failures')


def post_bill_to_API(uuid, qty):
        r = requests.post(
                config['BILLING']['baseURL'],
                data=make_body(uuid, qty),
                params={'api-version': '2018-08-31'},
                headers=make_headers(uuid),
                timeout=config['BILLING'].getint('timeout_s'))
        logging.debug(f'Status code: {r.status_code} for UUID: {uuid}')
#        logging.debug(r.json())
        assert r.status_code == 200


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
    

def make_body(uuid, qty):
    now = datetime.datetime.utcnow()
    effectiveStartTime = now.strftime('%Y-%m-%dT%H:%M:%S')
    body = {'resourceId': uuid,
            'quantity': qty,
            'dimension': config['BILLING']['dimension'],
            'effectiveStartTime': effectiveStartTime,
            'planId': get_plan_id(uuid)[0]}
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
    
    




if __name__ == "__main__":
    logging.info('Starting billing service')

    if config['DEBUG']['enable_fast_query']:
        schedule.every(
            config['DEBUG'].getint('fast_query_interval_s')).seconds.do(job)
    else:
        schedule.every(
            config['BILLING'].getint('query_interval_hrs')).hours.do(job)

    job() # initial run
    while True:
        schedule.run_pending()
        time.sleep(1)



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

