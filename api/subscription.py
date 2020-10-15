import requests
import psycopg2
import logging
import uuid

import config as cfg


CONN_STR = cfg.SUBSCRIPTION_DB_CONN_STR


def check_user_subscribed(object_id):
    logging.info(f'Checking subscriptions for {object_id}')
    assert object_id, '401 User object id required'
    for sub_id, plan_id in get_subscription_ids(object_id):
        logging.info(sub_id)
        if subscription_is_valid( sub_id, get_AAD_token() ):
            logging.info('Found a valid subscription for user, ending check')
            return sub_id, plan_id # str, str
        logging.info('Individual subscription ID check failed')
    logging.info('Failed to find any valid subscriptions')
    assert False, '402 User not subscribed'


def get_subscription_ids(object_id):
    SQL =   """
            SELECT subscriptionid, planid from subscriptiondetails
            where objectid = %s
            order by id desc ;
            """

    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (object_id, ) )
        rv = cur.fetchall()
        cur.close()
        
    return rv
    
#    return [elem[0] for elem in subscription_ids]


def get_AAD_token():
    #Todo: add a cache, and a check to reuse token if still valid
    #https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-AAD-registration#http-method
    url = f'https://login.microsoftonline.com/{cfg.TENANT_ID_AD}/oauth2/token'

    try:

        r = requests.post(url, timeout=5, data={
                'resource': cfg.RESOURCE, 
                'client_id': cfg.CLIENT_ID_AD,
                'client_secret': cfg.CLIENT_SECRET,
                'grant_type': 'client_credentials'
                })

        return r.json()['access_token']
    except:
        assert False, '503 failed to reach auth server'


def subscription_is_valid(subscription_id, token):
    #Todo: add a cache, with expire time per entry for invalidation
    #https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-saas-fulfillment-api-v2#get-subscription
    url =   f'{cfg.SUBSCRIPTION_URL}/{subscription_id}'

    try:

        r = requests.get(url, timeout=5,
                        params = {'api-version': cfg.SAAS_API_VERSION},
                        headers = {'content-type': 'application/json',
                                   'authorization': f'Bearer {token}' })
    except:
        assert False, '503 failed to reach subscription server'

    try:
        status = r.json()['saasSubscriptionStatus']
    except KeyError:
        return False

    if status == 'Subscribed':
        return True


def create_test_table():

    SQL =   """
            CREATE TABLE if not exists 
                subscriptiondetails
                (
                    id serial primary key,
                    objectid uuid not null,
                    subscriptionid uuid not null,
                    -- subscriptionname text not null,
                    -- offerid text not null,
                    planid text not null,
                    -- purchasertenantid uuid not null,
                    -- subscriptionstatus text not null,
                    created timestamptz not null default NOW(),
                    unique(subscriptionid)
                );
            """

    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute(SQL)
        cur.close()


def insert_dummy_data(object_id, subscription_id, plan_id):

    SQL =   """
            insert into subscriptiondetails
            (objectid, subscriptionid, planid)
            values (%s, %s, %s)
            on conflict do nothing;
            """
    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute(SQL, (object_id, subscription_id, plan_id))
        cur.close()


if __name__ == '__main__':
    """
    Inline test to check a valid and an invalid subscription_id.
    Creates dummy test data, so do NOT run against production DB"""
    
    logging.basicConfig(level=logging.INFO)

    CONN_STR = "host=localhost "\
                        + "user=postgres "\
                        + "dbname=postgres "\
                        + "password=password "\
                        + "sslmode=allow"

    create_test_table()

    # should pass
    print('\nTest 1 - this should pass')
    oid = '5995EBF0-D3D8-4C3F-8921-DC59DB7E5280'
    sid_1 = '6b71cfa4-fa75-3540-fc41-b72fd8ef2555' #valid
    sid_2 = 'ea3c3199-253d-14c3-be36-7e5118102b75' #valid
    planid = 'm1'
    insert_dummy_data(oid, sid_1, planid)
    insert_dummy_data(oid, sid_2, planid)
    check_user_subscribed(oid)

    # should pass
    print('\nTest 2 - this test should pass')
    oid = '9320C4D7-5B8A-45E6-98F8-4E36B47C0618'
    sid_1 = 'd673ba79-5854-a957-96b5-9c5eafc4079d' #valid
    sid_2_bad = '009E9534-4961-456D-AF46-0CB03FEB23D7' # invalid
    planid = 'm1'    
    insert_dummy_data(oid, sid_1, planid)
    insert_dummy_data(oid, sid_2_bad, planid)
    check_user_subscribed(oid)

    # should fail
    print('\nTest 3 - this should raise an assertion error with code 402')
    oid = '975040DE-D354-4D1D-9802-B20D2AE54572'
    sid_1_bad = '1031BCA9-DB8C-4805-A751-FC99D90B0F51' # invalid
    planid = 'm1'    
    insert_dummy_data(oid, sid_1_bad, planid)
    check_user_subscribed(oid)
