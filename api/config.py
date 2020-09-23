
MAX_CONTENT_LENGTH = 1024 * 1024 * 5 # limit file upload size to 5 MB
UPLOAD_EXTENSIONS = ['.csv', ]
UPLOAD_PATH = 'tmp'

PROFILES_BUILDING = './profiles/building_profiles.csv'
PROFILES_EV = './profiles/profiles_for_production_use.csv'

REQUIRE_ACCESS_TOKEN = False

APPLY_BILLING = False # Queries will not be registered in billing database
# BILLING_DB_CONN_STR = 'postgres://postgres:password@localhost:5432/postgres'
BILLING_DB_CONN_STR = "host=lcapppostgreserver.postgres.database.azure.com "\
					+ "user=lcapp@lcapppostgreserver "\
					+ "dbname=postgres "\
					+ "password=SANorxagrid12 "\
					+ "sslmode=require"

MAX_FREE_CALLS = 5
# Replace these with actual values sent from frontend. Used by billing module.
EMAIL = 'user2@orxa.io'
SUBSCRIPTION_ID = '8307CBA6-CA74-450F-9528-386E0CF07F34'
SUBSCRIPTION_VALID = True

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

