import sys, os
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tax_reporter


# EIOPA Taxonomy version 2.5.0
url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
# Create the data pool and load taxonomy.
data_pool = pool.Pool()
data_pool.cache_package(url)
entry_point = 'http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2020-07-15/mod/qes.xsd'
tax = data_pool.add_taxonomy([entry_point])
# Create taxonomy reporter
rep = tax_reporter.TaxonomyReporter(tax)
# Render enumeration sets as HTML
rep.r_enumerations()
output_file = os.path.join(data_pool.output_folder, 'eiopa-250-enumerations.html')
rep.save_as(output_file)
print(f'Report created in {output_file}')
