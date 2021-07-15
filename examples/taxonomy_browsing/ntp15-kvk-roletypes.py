import os, sys
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tax_reporter


# NTP-KVK Taxonomy for 2020
url = 'https://www.nltaxonomie.nl/nt15/kvk/20201209/entrypoints/kvk-rpt-jaarverantwoording-2020-ifrs-full.xsd'
data_pool = pool.Pool()
# Load the entrypoint directly from Web.
tax = data_pool.add_taxonomy([url])
# Create taxonomy reporter
rep = tax_reporter.TaxonomyReporter(tax)
# Create HTML report for role types
rep.r_role_types()
output_file = os.path.join(data_pool.output_folder, 'ntp15-kvk-roletypes.html')
rep.save_as(output_file)
# Create HTML report for arcrole types
rep.r_arcrole_types()
output_file = os.path.join(data_pool.output_folder, 'ntp15-kvk-arcroletypes.html')
rep.save_as(output_file)


