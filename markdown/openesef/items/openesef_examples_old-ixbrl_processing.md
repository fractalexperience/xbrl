# examples_old/ixbrl_processing Contents
## examples_old/ixbrl_processing/companieshouse.py
```py
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
```

## examples_old/ixbrl_processing/sec_cik_1000177_20-f.py
```py
from xbrl.base import pool

# Create the data pool. Note that its cache folder must be accessible with full access righs
# in the local file system.
data_pool = pool.Pool()
# A random iXBRL instance from SEC/EDGAR system
location_ixbrl = 'https://www.sec.gov/Archives/edgar/data/1000177/000114036121014948/brhc10022989_20f.htm'
# Same instance, but in native XBRL format.
location_xbrl = 'https://www.sec.gov/Archives/edgar/data/1000177/000114036121014948/brhc10022989_20f_htm.xml'
# Parse inline document
xid_inline = data_pool.add_instance_location(location=location_ixbrl, key=location_ixbrl, attach_taxonomy=True)
# Parse native document
xid_native = data_pool.add_instance_location(location=location_xbrl, key=location_xbrl, attach_taxonomy=True)
print('\nData pool info')
print('----------------------')
print(data_pool.info())
print('\nInline XBRL Instance info')
print('-------------------------')
print(xid_inline)
print('\nNative XBRL Instance info')
print('-------------------------')
print(xid_native)
```
