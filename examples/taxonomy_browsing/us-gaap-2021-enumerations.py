import sys, os
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tax_reporter


# US-GAAP taxonomy - version 2021
url = 'https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip'
# Create the data pool and load taxonomy.
data_pool = pool.Pool()
tax = data_pool.add_package(url)
# Create taxonomy reporter
rep = tax_reporter.TaxonomyReporter(tax)
# Render enumeration sets as HTML
rep.r_enumeration_sets()
output_file = os.path.join(data_pool.output_folder, 'us-gaap-enumeration_sets.html')
rep.save_as(output_file)