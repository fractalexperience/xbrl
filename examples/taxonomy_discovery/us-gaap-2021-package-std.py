import sys
sys.path.insert(0, r'../../../')
from xbrl.base import pool


# US-GAAP taxonomy - version 2021
url = 'https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip'
# Create the data pool.
data_pool = pool.Pool()
# - Download the ZIP archive of the taxonomy package URL provided and store it in cache
data_pool.cache_package(url)
# Load a specific entry point
entry_point = 'https://xbrl.fasb.org/us-gaap/2021/entire/us-gaap-entryPoint-std-2021-01-31.xsd'
tax = data_pool.add_taxonomy([entry_point])
# Output taxonomy summary information
print(tax)
