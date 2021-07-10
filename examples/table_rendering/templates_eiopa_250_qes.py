import os, sys, datetime
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tlb_reporter
import json


def write_file(content, filename):
    with open(os.path.join(data_pool.output_folder, filename), 'wt', encoding="utf-8") as f:
        f.write(content)

t1 = datetime.datetime.now()
tax_url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
doc_url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Instance_documents_2.5.0_hotfix.zip'
data_pool = pool.Pool()
data_pool.cache_package(tax_url)
ep_code = 'tep'
xid_file = f'random/{ep_code}_250_instance.xbrl'
afn = data_pool.cache(doc_url)
xid = data_pool.add_instance_archive(afn, xid_file, None, True)
eng = tlb_reporter.TableReporter(xid.taxonomy, xid)
eng.compile_all()
# for tid in xid.taxonomy.tables:
# ids = ['s2md_tS.22.06.01.04', 's2md_tS.19.01.01.01', 's2md_tS.02.02.01.02', 's2md_tS.08.01.01.01', 's2md_tS.04.01.01.01', 's2md_tS.02.02.01.02']
# ids = sorted(xid.taxonomy.tables)
ids = ['s2md_tS.19.01.01.01']
for tid in ids:
    print(tid)
    eng.do_layout(tid)
    write_file(eng.render_templates_html(tid), f'{ep_code}_250_{tid}_template.html')
    write_file(eng.render_templates_html(tid, True), f'{ep_code}_250_{tid}_template_w_constraints.html')
    write_file(eng.render_map_html(tid), f'{ep_code}_250_{tid}_map.html')
    dpm_map = eng.get_dpm_map(tid)
    write_file(json.dumps(dpm_map.Mappings), f'[{tid}]_map.json')

print(f'{len(ids)} tables processed.', 'Processing time: ', datetime.datetime.now() - t1)