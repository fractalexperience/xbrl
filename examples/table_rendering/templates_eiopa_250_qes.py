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