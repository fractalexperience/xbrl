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