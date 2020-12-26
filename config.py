MAX_CONTENT_LENGTH = 1024 * 1024 * 5 # limit file upload size to 5 MB
UPLOAD_EXTENSIONS = ['.csv', ]
UPLOAD_PATH = 'tmp'

PROFILES_BUILDING = './profiles/building_profiles.csv'
PROFILES_EV = './profiles/profiles_for_production_use.csv'
ANNUALS_BUILDING = './profiles/building_annual_kWh.csv'
COUNTRY_DETAILS = './profiles/country.csv'


DEBUG_MODE = False # Sets log level to debug if True

REQUIRE_AUTH = True

APPLY_BILLING = True # Affects AAD users
MAX_FREE_CALLS = 5 # Affects B2C users
APPLY_DEFAULT_VALUES = True

#Subscription quota limit
MAX_CALLS_BASIC_PLAN = 5
MAX_CALLS_SILVER_PLAN_MONTHLY = 20
MAX_CALLS_SILVER_PLAN_ANNUAL = 240
MAX_CALLS_GOLD_PLAN = 'unlimited'
 
#Use these for local testing:
#BILLING_DB_CONN_STR = "host=localhost "\
#                      + "user=postgres "\
#                      + "dbname=postgres "\
#                      + "password=password "\
#                      + "sslmode=allow"    

#SUBSCRIPTION_DB_CONN_STR = "host=localhost "\
#                       + "user=postgres "\
#                       + "dbname=postgres "\
#                       + "password=password "\
#                       + "sslmode=allow"         

#Use these  for production:
BILLING_DB_CONN_STR = "host=lcapppostgreserver.postgres.database.azure.com "\
                     + "user=lcapp@lcapppostgreserver "\
                     + "dbname=postgres "\
                     + "password=SANorxagrid12 "\
                     + "sslmode=require"

SUBSCRIPTION_DB_CONN_STR = "host=lcapppostgreserver.postgres.database.azure.com "\
                         + "user=lcapp@lcapppostgreserver "\
                         + "dbname=Azuresubscriptiondb "\
                         + "password=SANorxagrid12 "\
                         + "sslmode=require"         

SUBSCRIPTION_URL = 'https://marketplaceapi.microsoft.com/api/saas/subscriptions'


#Dummy uuid for b2c/free users
# DUMMY_UUID = "dd7a9e38-ff3f-11ea-adc1-0242ac120002"

PICKLE_RESULTS = False

# Provide the B2C Tenant name, specify the non-MFA B2C Policy name, and the API client id
TENANT_NAME = "derapp"
TENANT_ID = "6b0c9fa6-80f1-4706-87fe-39b5b846ab67"
B2C_POLICY = "B2C_1_sign_up_sign_in"
CLIENT_ID = "b249bf9e-9569-4c14-b12a-46b2563b2090"

# Azure Market Place AD authentication credentials to get authorization token
CLIENT_ID_AD = "c6c8b5c0-7a93-4743-8823-3b83431de29b"
CLIENT_SECRET = "utFQ4~yygj-Zz2nq~2-bLq-~~lz1rynZEh"
RESOURCE = "20e940b3-4c77-4b0b-9a53-9e16a1b010a7"
TENANT_ID_AD = "f0e8a3c1-f57f-446b-b105-37b6d1ee94cc"
END_POINT = "https://login.microsoftonline.com/f0e8a3c1-f57f-446b-b105-37b6d1ee94cc/oauth2/token"
FULLFILLMENT_URI = "https://marketplaceapi.microsoft.com/api/saas/subscriptions/"
SAAS_API_VERSION = '2018-08-31'

CLIENT_ID_AD_MULT = "454f560c-4e04-46dc-bb7d-a74f753f3952"

CO2_EMISSION_KWH = 0.0005 #Metric ton
