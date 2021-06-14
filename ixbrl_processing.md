# Inline XBRL Processing - Examples



[Inline XBRL](https://specifications.xbrl.org/spec-group-index-inline-xbrl.html) filings are well formed XHTML files, which include embedded XBRL facts. In many cases it is needed to extract the native XBRL content from such a filing for further processing. {XM} includes a module to directly load iXBRL files in memory and serialize them back as native XBRL. 



## Example 1 - Parse iXBRL vs native XBRL

20-F form from [NORDIC AMERICAN TANKERS Ltd](https://www.sec.gov/Archives/edgar/data/1000177/000114036121014948/0001140361-21-014948-index.html). Create a data pool and open two instance documents containing the same information. The first one is designed as [Inline XBRL](https://www.xbrl.org/specification/inlinexbrl-part1/rec-2013-11-18/inlinexbrl-part1-rec-2013-11-18.html) and contains additional HTML tags. The second one is a native XBRL instance according [XBRL version 2.1](https://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html), which contains the same information.

```python
from xbrl.base import pool

# Create the data pool. Note that it creates a cache folder in system temporary storage.
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



## Example 2 - Batch process a document archive

Batch process daily archive from [companieshouse.gov.uk](http://download.companieshouse.gov.uk/en_accountsdata.html) (around 10000 documents) - strip Inline XBRL content and produce native XBRL instance documents.

```python
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



