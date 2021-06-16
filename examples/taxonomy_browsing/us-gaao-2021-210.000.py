import sys, os
sys.path.insert(0, r'../../../')
from xbrl.base import pool, const
from xbrl.engines import tax_reporter


# US-GAAP taxonomy - version 2021
url = 'https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip'
# Create the data pool and load taxonomy.
data_pool = pool.Pool()
tax = data_pool.add_package(url)
# package = data_pool.cache_package(url)
# entry_point = 'https://xbrl.fasb.org/us-gaap/2021/entire/us-gaap-entryPoint-all-2021-01-31.xsd'
# tax = data_pool.add_taxonomy([entry_point])
# Create taxonomy reporter
rep = tax_reporter.TaxonomyReporter(tax)
role = 'http://fasb.org/us-gaap/role/disclosure/BalanceSheetOffsetting'
# List presentation hierarchies in a HTML table
rep.r_base_set('presentationArc', role, const.PARENT_CHILD_ARCROLE)
output_file = os.path.join(data_pool.output_folder, 'us-gaap-2021-210.000.html')
rep.save_as(output_file)