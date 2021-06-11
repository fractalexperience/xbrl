import os, sys, datetime
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tlb_reporter

t1 = datetime.datetime.now()
tax_url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
doc_url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Instance_documents_2.5.0_hotfix.zip'
data_pool = pool.Pool()
data_pool.cache_package(tax_url)
ep_code = 'tep'
xid_file = f'random/{ep_code}_250_instance.xbrl'
afn = data_pool.cache(doc_url)
xid = data_pool.add_instance_archive(afn, xid_file, None, True)
# xid.taxonomy.compile_dr_sets()
eng = tlb_reporter.TableReporter(xid.taxonomy, xid)
eng.compile_all()
output_file = os.path.join(data_pool.output_folder, f'{ep_code}_250_templates.html')
with open(output_file, 'wt', encoding="utf-8") as f:
    f.write(eng.render_html())
print(f'Render saved to {output_file}.', f'{len(eng.structures)} tables processed.', 'Processing time: ', datetime.datetime.now() - t1)