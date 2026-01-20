import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

# CONFIG
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
BASE_ID = os.environ.get("BASE_ID")
REQUESTS_TABLE_ID = os.environ.get("REQUESTS_TABLE_ID")
CONSULTANTS_TABLE_ID = os.environ.get("CONSULTANTS_TABLE_ID")

REPORT_FILE = "weekly_report.csv"

# INIT
api = Api(AIRTABLE_API_KEY)
requests_table = api.table(BASE_ID, REQUESTS_TABLE_ID)
consultants_table = api.table(BASE_ID, CONSULTANTS_TABLE_ID)

