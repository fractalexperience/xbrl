from xbrl.base import pool
from xbrl.engines import tlb_engine
import datetime

archive_url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Instance_documents_2.5.0_hotfix.zip'
xid_file = 'random/qes_250_instance.xbrl'
data_pool = pool.Pool('..\\..\\..\\cache')

t1 = datetime.datetime.now()
print('Start parsing', xid_file, 'from', archive_url, 'at', t1)

afn = data_pool.resolver.cache(archive_url)
xid = data_pool.add_instance_archive(afn, xid_file, None, True)
print('Finished parsing at', datetime.datetime.now(), '. Time elapsed:', datetime.datetime.now() - t1)
t2 = datetime.datetime.now()
# print('Start compiling DR Sets at', t2)
# xid.taxonomy.compile_dr_sets()
print('Finished at', datetime.datetime.now(), '. Elapsed:', datetime.datetime.now() - t2, 'Total: ', datetime.datetime.now() - t1)

print('\nTables\n------------------')
eng = tlb_engine.TableEngine(xid.taxonomy, xid)
eng.compile_all()
for id, stru in eng.structures.items():
    print('Table: ', id)
    for axis, s_list in stru.items():
        print('Axis: ', axis)



# print('\nDocument\n------------------')
# print(xid)
# print('\nTaxonomy\n------------------')
# print(xid.taxonomy)