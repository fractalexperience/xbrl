import sys
sys.path.insert(0, r'../../../')
from xbrl.base import pool


# EIOPA Taxonomy version 2.5.0
url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
# Create the data pool and load taxonomy.
data_pool = pool.Pool()
data_pool.cache_package(url)
entry_point = 'http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2020-07-15/mod/qes.xsd'
tax = data_pool.add_taxonomy([entry_point])
tax.compile_dr_sets()

for key, drs in tax.dr_sets.items():
    print(key)
    print('Primary items')
    for pi in drs.primary_items.values():
        print(' '*10*pi.level, pi.concept.qname, pi.concept.get_label())
    print('Hypercubes\n------------------------')
    for hc_key, hc in drs.hypercubes.items():
        print(hc.concept.qname, hc.concept.get_label())
        print('     Dimensions\n------------------------')
        for dim_key, dim in hc.dimensions.items():
            print(' '*5, dim.concept.qname, dim.concept.get_label(), ' => ', 
                  'typed ... ' if not dim.concept.is_explicit_dimension
                  else ','.join([m.qname for m in dim.members.values()] if dim.members else ''))
