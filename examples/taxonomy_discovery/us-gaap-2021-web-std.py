import sys
sys.path.insert(0, r'../../../')
from xbrl.base import pool


entry_point = 'https://xbrl.fasb.org/us-gaap/2021/entire/us-gaap-entryPoint-std-2021-01-31.xsd'
data_pool = pool.Pool()
# Load a specific entry point directly from Web
tax = data_pool.add_taxonomy([entry_point])
# Output taxonomy summary information
print(tax)
