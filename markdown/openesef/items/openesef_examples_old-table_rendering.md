# examples_old/table_rendering Contents
## examples_old/table_rendering/templates_eba_310_resol_con.py
```py
import sys, datetime
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tlb_reporter
import json

t1 = datetime.datetime.now()
tax_url = 'D:\\sv\\work\\taxonomy_viewer\\source\\04-eba\\eba_3.1\\eba-3.1.zip'
entrypoint = 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/res/cir-2018-1624/2021-07-15/mod/resol_con.xsd'
ep_code = 'resol_con'
dp = pool.Pool()
package = dp.cache_package(tax_url)
dp.index_package(package)
tax = dp.add_taxonomy([entrypoint])
eng = tlb_reporter.TableReporter(tax, None)
ids = sorted(['eba_tT_20.01.a', 'eba_tT_20.01.w', 'eba_tT_03.01'])

for tid in ids:
    print(tid)
    eng.compile_table_id(tid)
    eng.do_layout(tid)
    dp.save_output(eng.render_templates_html(tid), f'{ep_code}_{tid}_template.html')
    dp.save_output(eng.render_templates_html(tid, True), f'{ep_code}_{tid}_template_w_constraints.html')
    #dp.save_output(eng.render_map_html(tid), f'{ep_code}_{tid}_map.html')
    #dpm_map = eng.get_dpm_map(tid)
    #dpp.save_output(json.dumps(dpm_map.Mappings), f'[{tid}]_map.json')

print(f'{len(ids)} tables processed.', 'Processing time: ', datetime.datetime.now() - t1)
```

## examples_old/table_rendering/templates_eiopa_250_qes.py
```py
import sys, datetime
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tlb_reporter
import json

t1 = datetime.datetime.now()
tax_url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
doc_url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Instance_documents_2.5.0_hotfix.zip'
dp = pool.Pool()
dp.cache_package(tax_url)
ep_code = 'tep'
xid_file = f'random/{ep_code}_250_instance.xbrl'
afn = dp.cache(doc_url)
xid = dp.add_instance_archive(afn, xid_file, None, True)
eng = tlb_reporter.TableReporter(xid.taxonomy, xid)
# for tid in xid.taxonomy.tables:
# ids = ['s2md_tS.22.06.01.04', 's2md_tS.19.01.01.01', 's2md_tS.02.02.01.02', 's2md_tS.08.01.01.01', 's2md_tS.04.01.01.01', 's2md_tS.02.02.01.02']
ids = sorted(xid.taxonomy.tables)
# ids = ['s2md_tS.02.01.01.01','s2md_tS.19.01.01.01']
for tid in ids:
    print(tid)
    eng.compile_table_id(tid)
    eng.do_layout(tid)
    dp.save_output(eng.render_templates_html(tid), f'{ep_code}_250_{tid}_template.html')
    dp.save_output(eng.render_templates_html(tid, True), f'{ep_code}_250_{tid}_template_w_constraints.html')
    dp.save_output(eng.render_map_html(tid), f'{ep_code}_250_{tid}_map.html')
    dpm_map = eng.get_dpm_map(tid)
    dp.save_output(json.dumps(dpm_map.Mappings), f'[{tid}]_map.json')

print(f'{len(ids)} tables processed.', 'Processing time: ', datetime.datetime.now() - t1)
```

## examples_old/table_rendering/templates_ntp16_kvk_nlgaap_micro.py
```py
import sys, datetime
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tlb_reporter
import json

t1 = datetime.datetime.now()
# tax_url = 'http://nltaxonomie.nl/nt16/kvk/20211208.a/entrypoints/kvk-rpt-jaarverantwoording-2021-nlgaap-micro-publicatiestukken.xsd'
tax_url = 'http://www.nltaxonomie.nl/nt16/kvk/20211208.a/entrypoints/kvk-rpt-jaarverantwoording-2021-nlgaap-klein-publicatiestukken.xsd'
# tax_url = 'D:\\sv\\work\\conformance-suites\\table-linkbase-conf-2015-08-12\\conf\\tests\\3200-dimension-relationship-node\\3240-dimension-relationship-node-formula-axis\\table-examples.xsd'
dp = pool.Pool()
tax = dp.add_taxonomy([tax_url])
print(tax)

eng = tlb_reporter.TableReporter(tax, None)
# ids = ['kvk-table_2PeriodesTypeJaarrekening2AbstractsDurationInstantParentFirst_BalanceSheetMicroEntitiesTable']
ids = tax.tables
for tid in ids:
    print(tid)
    eng.compile_table_id(tid)
    eng.do_layout(tid)
    dp.save_output(eng.render_templates_html(tid), f'{tid}_template.html')
    dp.save_output(eng.render_templates_html(tid, True), f'{tid}_template_w_constraints.html')
#     dp.save_output(eng.render_map_html(tid), f'{ep_code}_250_{tid}_map.html')
#     dpm_map = eng.get_dpm_map(tid)
#     dp.save_output(json.dumps(dpm_map.Mappings), f'[{tid}]_map.json')
#
print(f'{len(ids)} tables processed.', 'Processing time: ', datetime.datetime.now() - t1)
```
