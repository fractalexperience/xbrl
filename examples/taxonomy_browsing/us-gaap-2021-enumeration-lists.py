import sys, os
sys.path.insert(0, r'../../../')
from xbrl.base import pool, const
from xbrl.engines import tax_reporter


# US-GAAP taxonomy - version 2021
data_pool = pool.Pool()
tax = data_pool.add_package('https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip')
# Create taxonomy reporter
rep = tax_reporter.TaxonomyReporter(tax)
# View specific domain-member base set, which contains enumeratino lists for extensible enumerations.
role = 'http://fasb.org/us-gaap/role/eedm/ExtensibleEnumerationLists'
rep.r_base_set('definitionArc', role, const.XDT_DOMAIN_MEMBER_ARCROLE)
output_file = os.path.join(data_pool.output_folder, 'us-gaap-2021-enumeration_lists.html')
rep.save_as(output_file)
print(f'Report created in {output_file}')