
import requests

AAD_tenantId = 'f0e8a3c1-f57f-446b-b105-37b6d1ee94cc'
AAD_client_id = 'c6c8b5c0-7a93-4743-8823-3b83431de29b'
AAD_client_secret = 'utFQ4~yygj-Zz2nq~2-bLq-~~lz1rynZEh'
AAD_resource = '20e940b3-4c77-4b0b-9a53-9e16a1b010a7'
AAD_grant_type = 'client_credentials'

SaaS_api_version = '2018-08-31'


def get_AAD_token():
    #https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-AAD-registration#http-method
    url = f'https://login.microsoftonline.com/{AAD_tenantId}/oauth2/token'

    r = requests.post(url, data={
            'resource': AAD_resource, 
            'client_id': AAD_client_id,
            'client_secret': AAD_client_secret,
            'grant_type': AAD_grant_type
            })

    return r.json()['access_token']


def check_SaaS_subscription(subscription_id, token):
    #https://docs.microsoft.com/en-us/azure/marketplace/partner-center-portal/pc-saas-fulfillment-api-v2#get-subscription
    url =   f'https://marketplaceapi.microsoft.com/api/saas/subscriptions/' + \
            f'{subscription_id}'

    r = requests.get(url, params = {'api-version': SaaS_api_version},
                    headers = {'content-type': 'application/json',
                               'authorization': f'Bearer {token}' })

    status = r.json()['saasSubscriptionStatus']
    assert status == 'Subscribed', '401 User not subscribed'


if __name__ == '__main__':
    subscribed_subscription_id = '6b71cfa4-fa75-3540-fc41-b72fd8ef2555'
    unsubscribed_subscription_id = 'e51bc4ed-f54e-36a7-8974-1fb9b52da316'
    
    token = get_AAD_token()

    status = check_SaaS_subscription(subscribed_subscription_id, token)
#    status = check_SaaS_subscription(unsubscribed_subscription_id, token)


