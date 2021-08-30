import sys, datetime
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tlb_reporter
import json

t1 = datetime.datetime.now()
tax_url = 'http://nltaxonomie.nl/nt16/kvk/20211208.a/entrypoints/kvk-rpt-jaarverantwoording-2021-nlgaap-micro-publicatiestukken.xsd'
dp = pool.Pool()
tax = dp.add_taxonomy([tax_url])
print(tax)

eng = tlb_reporter.TableReporter(tax, None)
eng.compile_all()
# ids = ['s2md_tS.19.01.01.01']
ids = tax.tables
for tid in ids:
    print(tid)
#     eng.do_layout(tid)
#     dp.save_output(eng.render_templates_html(tid), f'{ep_code}_250_{tid}_template.html')
#     dp.save_output(eng.render_templates_html(tid, True), f'{ep_code}_250_{tid}_template_w_constraints.html')
#     dp.save_output(eng.render_map_html(tid), f'{ep_code}_250_{tid}_map.html')
#     dpm_map = eng.get_dpm_map(tid)
#     dp.save_output(json.dumps(dpm_map.Mappings), f'[{tid}]_map.json')
#
# print(f'{len(ids)} tables processed.', 'Processing time: ', datetime.datetime.now() - t1)