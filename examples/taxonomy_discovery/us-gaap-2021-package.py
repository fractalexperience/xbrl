import os, sys, datetime
sys.path.insert(0, r'../../../')
from xbrl.base import pool


# US-GAAP taxonomy - version 2021
url = 'https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip'
# Create the data pool.
data_pool = pool.Pool()
# This method does the following:
# - Download the ZIP archive of the taxonomy package URL provided and store it in cache
# - Query the package about available entry ponits and location remappings
# - Load all available entry points into a single taxonomy object.
tax = data_pool.add_package(url)
# Output taxonomy summary information
print(tax)
