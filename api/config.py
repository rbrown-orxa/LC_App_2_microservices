
MAX_CONTENT_LENGTH = 1024 * 1024 * 5 # limit file upload size to 5 MB
UPLOAD_EXTENSIONS = ['.csv', ]
UPLOAD_PATH = 'tmp'
PROFILES_BUILDING = './profiles/building_profiles.csv'
PROFILES_EV = './profiles/profiles_for_production_use.csv'
PICKLE_RESULTS = False
REQUIRE_ACCESS_TOKEN = False
BILLING_DB_CONN_STR = 'localhost:5432'
MAX_FREE_CALLS = 10


