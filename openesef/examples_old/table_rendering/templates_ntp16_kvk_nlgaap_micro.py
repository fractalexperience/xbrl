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