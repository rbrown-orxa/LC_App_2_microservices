
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


