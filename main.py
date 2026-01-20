import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.environ.get("AIRTABLE_API_KEY"))
table = api.table(os.environ.get("BASE_ID"), 'tblqGPYW8tuusMMrl') # base_id, table_id

print(table.all())
