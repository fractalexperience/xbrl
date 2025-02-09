import sys
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from lxml import etree as lxml
import os, datetime, zipfile

# Yesterday's archive from Companieshouse http://download.companieshouse.gov.uk/en_accountsdata.html
url = f'http://download.companieshouse.gov.uk/Accounts_Bulk_Data-{datetime.datetime.now()-datetime.timedelta(days=1):%Y-%m-%d}.zip'
data_pool = pool.Pool()
output_folder = os.path.join(data_pool.output_folder, 'ch')
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
archive_filename = data_pool.cache(url)
archive = zipfile.ZipFile(archive_filename)
zil = archive.infolist()
# Process first 100 documents from archive
for f in [f for f in zil][:100]:
    with archive.open(f) as zf:
        print('Parsing', f.filename)
        root = lxml.XML(zf.read())
        if str(root.tag).endswith('xbrl'):
            # File is native XBRL, so no strip needed
            archive.extract(f, output_folder)
            continue
        # Add instance document to data pool using archive location + file name as key
        xid = data_pool.add_instance_element(root, key=f'{url}|{f.filename}', attach_taxonomy=True)
        if not (xid.ixbrl or xid.ixbrl.output):
            continue
        # Write stripped content to output folder
        ofn = os.path.join(output_folder, f'{f.filename}.xbrl')
        with open(ofn, 'wt', encoding="utf-8") as output_file:
            output_file.write(''.join(xid.ixbrl.output))
print(data_pool)
