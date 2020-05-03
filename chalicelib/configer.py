from os import environ


# APPLICATION VARIABLES
APP_NAME = 'covid-19-bot'
BASE_TG_URL = "https://api.telegram.org/"
TEST_TOKEN = "1111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

# ENVIRONMENT VARIABLES
TG_TOKEN = TEST_TOKEN if not environ.get('TG_TOKEN') else environ['TG_TOKEN']
DEBUG = True if not environ.get('DEBUG') else bool(environ['DEBUG'])

# AWS VARIABLES
SNS_TOPIC_FOR_COVID_CASES = "CovidCasesNotifications"
DDB_CONFIG_TABLE_NAME = 'config'
DDB_CASES_TABLE_NAME = 'cases'
DDB_TOTAL_TABLE_NAME = 'total'

# SOURCES
REGIONS = ['russia']
MAX_DEEP_DAY = 15

# RUSSIA SOURCE
RUSSIA_OFFICIAL_URL = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/information/'
