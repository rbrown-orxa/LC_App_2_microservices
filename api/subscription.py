import requests
import psycopg2
import logging
import uuid



AAD_tenantId = 'f0e8a3c1-f57f-446b-b105-37b6d1ee94cc'
AAD_client_id = 'c6c8b5c0-7a93-4743-8823-3b83431de29b'
AAD_client_secret = 'utFQ4~yygj-Zz2nq~2-bLq-~~lz1rynZEh'
AAD_resource = '20e940b3-4c77-4b0b-9a53-9e16a1b010a7'
AAD_grant_type = 'client_credentials'

SaaS_api_version = '2018-08-31'

#Todo: change this to subscription db credentials
CONN_STR = f"host=localhost " \
        + f"user=postgres " \
        + f"dbname=postgres " \
        + f"password=password " \
        + f"sslmode=allow"

PRODUCTION_DBNAME = 'Azuresubscriptiondb'



def check_user_subscribed(object_id):
    logging.info(f'Checking subscriptions for {object_id}')
    if not current_app.config['APPLY_BILLING']:
        return # Check has passed

    for sid in get_subscription_ids(object_id):
        logging.info(sid)
        if subscription_is_valid( sid, get_AAD_token() ):
            logging.info('Found a valid subscription for user, ending check')
            return sid # str
        logging.info('Individual subscription ID check failed')
    logging.info('Failed to find any valid subscriptions')
    assert False, '402 User not subscribed'


def get_subscription_ids(object_id):
    SQL =   """
            SELECT subscriptionid from subscriptiondetails
            where objectid = %s
            order by id desc ;
            """

    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (object_id, ) )
        subscription_ids = cur.fetchall()
        cur.close()
    
    return [elem[0] for elem in subscription_ids]


def get_AAD_token():
    #Todo: add a cache, and a check to reuse token if still valid
    #https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-AAD-registration#http-method
    url = f'https://login.microsoftonline.com/{AAD_tenantId}/oauth2/token'

    try:
        r = requests.post(url, timeout=2, data={
                'resource': AAD_resource, 
                'client_id': AAD_client_id,
                'client_secret': AAD_client_secret,
                'grant_type': AAD_grant_type
                })

        return r.json()['access_token']
    except:
        assert False, '503 failed to reach auth server'


def subscription_is_valid(subscription_id, token):
    #https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-saas-fulfillment-api-v2#get-subscription
    url =   f'https://marketplaceapi.microsoft.com/api/saas/subscriptions/' + \
            f'{subscription_id}'

    try:
        r = requests.get(url, timeout=2,
                        params = {'api-version': SaaS_api_version},
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
                    -- planid text not null,
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


def insert_dummy_data(object_id, subscription_id):

    SQL =   """
            insert into subscriptiondetails
            (objectid, subscriptionid)
            values (%s, %s)
            on conflict do nothing;
            """
    with psycopg2.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute(SQL, (object_id, subscription_id))
        cur.close()


if __name__ == '__main__':
    """
    Inline test to check a valid and an invalid subscription_id.
    Creates dummy test data, so do NOT run against production DB"""
    
    logging.basicConfig(level=logging.INFO)
    input('WARNING - This test creates dummy data in DB. '
    'DO NOT run against production DB. '
    'Press enter to continue, or CTRL-C to quit')

    create_test_table()

    # should pass
    print('\nTest 1 - this should pass')
    oid = '5995EBF0-D3D8-4C3F-8921-DC59DB7E5280'
    sid_1 = '6b71cfa4-fa75-3540-fc41-b72fd8ef2555' #valid
    sid_2 = 'ea3c3199-253d-14c3-be36-7e5118102b75' #valid
    insert_dummy_data(oid, sid_1)
    insert_dummy_data(oid, sid_2)
    check_user_subscribed(oid)

    # should pass
    print('\nTest 2 - this test should pass')
    oid = '9320C4D7-5B8A-45E6-98F8-4E36B47C0618'
    sid_1 = 'd673ba79-5854-a957-96b5-9c5eafc4079d' #valid
    sid_2_bad = '009E9534-4961-456D-AF46-0CB03FEB23D7' # invalid
    insert_dummy_data(oid, sid_1)
    insert_dummy_data(oid, sid_2_bad)
    check_user_subscribed(oid)

    # should fail
    print('\nTest 3 - this should raise an assertion error with code 402')
    oid = '975040DE-D354-4D1D-9802-B20D2AE54572'
    sid_1_bad = '1031BCA9-DB8C-4805-A751-FC99D90B0F51' # invalid
    insert_dummy_data(oid, sid_1_bad)
    check_user_subscribed(oid)




    """
    Microsoft Documentation

    Metering service APIs - Microsoft commercial marketplace | Microsoft Docs
    https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/marketplace-metering-service-apis

    Register a SaaS application - Azure Marketplace | Microsoft Docs
    https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-saas-registration#get-the-token-with-an-http-post

    Microsoft identity platform ID tokens - Microsoft identity platform | Microsoft Docs
    https://docs.microsoft.com/en-us/azure/active-directory/develop/id-tokens#using-claims-to-reliably-identify-a-user-subject-and-object-id

    Microsoft identity platform access tokens - Microsoft identity platform | Microsoft Docs
    https://docs.microsoft.com/en-us/azure/active-directory/develop/access-tokens

    SaaS fulfillment APIs v2 in Microsoft commercial marketplace | Microsoft Docs
    https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-saas-fulfillment-api-v2#get-subscription
    """






