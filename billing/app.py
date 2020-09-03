import schedule
import time
import logging
import configparser
import psycopg2
import datetime
import json
import requests


config = configparser.ConfigParser()
config.read('config.ini')
loglevel = getattr(logging, config['DEBUG']['loglevel'].upper())
logging.basicConfig(level=loglevel)

CONN_STR = f"host={config['DB']['host']} " \
        + f"user={config['DB']['user']} " \
        + f"dbname={config['DB']['dbname']} " \
        + f"password={config['DB']['password']} " \
        + f"sslmode={config['DB']['sslmode']}"
logging.debug(f'Connection string: {CONN_STR}')


def job():
    try:
        bills = get_billing_quantities()
        logging.debug(f'Bills:\n {bills}')
        process_bills(bills)
    except:
        logging.exception('Error while running batch billing job')


def process_bills(bills):
    num_bills = len(bills)
    n_successful = 0
    logging.info(f'Processing {num_bills} bills')
    for uuid, qty in bills.items():
        logging.debug(f'UUID: {uuid}, units: {qty}')
        try:
            # Todo: make this a 2-stage transaction
            register_billed_quantity(uuid, qty)
            post_bill(uuid, qty)
            n_successful += 1
        except:
            # logging.exception(f'Error while processing bill: {uuid}')
            logging.warning(f'Error while processing bill: {uuid}')
            register_failed_bill(uuid, qty)
    failed = num_bills - n_successful
    logging.info(f'Processed {num_bills} bills, with {failed} failures')


def post_bill(uuid, qty):
        r = requests.post(
                config['BILLING']['baseURL'],
                data=make_body(uuid, qty),
                params={'ApiVersion': '2018-08-31'},
                headers=make_headers(uuid),
                timeout=1)
        logging.info(f'Status code: {r.status_code} for UUID: {uuid}')
        logging.debug(r.json())
        assert r.status_code == 200


def register_failed_bill(uuid, qty):

    SQL =   """
            UPDATE billing
            SET 
            billing_failed_queries = billing_failed_queries + %s
            WHERE subscription_id = %s
            """

    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (qty, uuid) )
        # conn.commit()
        cur.close()


def register_billed_quantity(uuid, qty):

    SQL =   """
            UPDATE billing
            SET 
            total_billed_queries = total_billed_queries + %s,
            last_bill_date = NOW(),
            last_bill_qty = %s
            WHERE subscription_id = %s
            """

    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (qty, qty, uuid) )
        # conn.commit()
        cur.close()


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


def get_billing_quantities():
    SQL =   """
            SELECT
            subscription_id,
            ( total_successful_queries 
                - total_billed_queries 
                - billing_failed_queries
            )
                AS queries_to_bill
            FROM billing
            WHERE
            ( total_successful_queries 
                - total_billed_queries 
                - billing_failed_queries
            ) 
                > 0
            GROUP BY subscription_id ;
            """

    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute( SQL )
        rv = cur.fetchall()
        cur.close()
    
    return dict(rv)



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




