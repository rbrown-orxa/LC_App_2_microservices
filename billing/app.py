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
                and completed >= now() - interval '24 hours';
            """

    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute( SQL )
        uuids = cur.fetchall()
        cur.close()
    
    return [uuid[0] for uuid in uuids]


def get_units_to_bill(subscription_id):
    # Todo: make this a 2-stage transaction

    SQL = """
    update queries
    set 
        billed = True, 
        date_billed = now() 
    where 
        subscription_id = %s 
        and success = true 
        and billed = false 
        and completed >= now() - interval '24 hours'
    returning 
        id;
    """
    
    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (subscription_id, ) )
        query_ids = cur.fetchall()
        cur.close()
    
    return len(query_ids)


def process_bills():
    users_to_bill = get_users_to_bill() 
    num_bills = len(users_to_bill)
    n_successful = 0
    logging.info(f'Processing {num_bills} bills')
    for subscription_id in users_to_bill:
        qty = get_units_to_bill(subscription_id) 
        # Todo: make this a 2-stage transaction
        # Todo: handle case where qty is zero
        logging.debug(f'subscription_id: {subscription_id}, units: {qty}')
        try:
            post_bill(subscription_id, qty)
        except:
            # logging.exception(f'Error while processing bill: {uuid}')
            logging.warning(f'Error while processing bill: {subscription_id}')
            # Todo: rollback db transaction started in get_users_to_bill()
        else:
            # Todo: commit db transaction started in get_users_to_bill()
            n_successful += 1
            logging.info('Bill posted successfully: {subscription_id}')
    failed = num_bills - n_successful
    logging.info(f'Processed {num_bills} bills, with {failed} failures')


def post_bill(uuid, qty):
        r = requests.post(
                config['BILLING']['baseURL'],
                data=make_body(uuid, qty),
                params={'ApiVersion': '2018-08-31'},
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

def make_body(uuid, qty):
    now = datetime.datetime.utcnow()
    effectiveStartTime = now.strftime('%Y-%m-%dT%H:%M:%S')
    body = {'resourceId': uuid,
            'quantity': qty,
            'dimension': config['BILLING']['dimension'],
            'effectiveStartTime': effectiveStartTime,
            'planId': config['BILLING']['planId']}
    return json.dumps(body)


def make_headers(uuid):
    headers = {'Content-type': 'application/json',
                'x-ms-requestid': uuid,
                'x-ms-correlationid': 'orxagrid_lcapp2',
                'authorization': f"Bearer {config['BILLING']['access_token']}"}
    return headers




if __name__ == "__main__":
    logging.info('Starting billing service')

    if config['DEBUG']['enable']:
        schedule.every(
            config['DEBUG'].getint('query_interval_s')).seconds.do(job)
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




