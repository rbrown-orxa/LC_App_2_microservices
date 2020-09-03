
MAX_CONTENT_LENGTH = 1024 * 1024 * 5 # limit file upload size to 5 MB
UPLOAD_EXTENSIONS = ['.csv', ]
UPLOAD_PATH = 'tmp'

PROFILES_BUILDING = './profiles/building_profiles.csv'
PROFILES_EV = './profiles/profiles_for_production_use.csv'

REQUIRE_ACCESS_TOKEN = False

APPLY_BILLING = False
BILLING_DB_CONN_STR = 'postgres://postgres:password@localhost:5432/postgres'
MAX_FREE_CALLS = 10
# Replace these with actual values sent from frontend. Used by billing module.
EMAIL = 'user@orxa.io'
SUBSCRIPTION_ID = '8307CBA6-CA74-450F-9528-386E0CF07F33' #None 

PICKLE_RESULTS = False
