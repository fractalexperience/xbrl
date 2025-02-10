import sys
sys.path.insert(0,  '../..')
from openesef.base.pool import Pool
import requests
import os

from openesef.engines import tax_reporter

# Configure cache folder for external taxonomies (e.g., IFRS)
CACHE_DIR = os.path.expanduser("~/.xbrl_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize pool with cache
data_pool = Pool(cache_folder=CACHE_DIR)

# Apple's 10-K iXBRL and XBRL URLs
# https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/0000320193-20-000096-index.htm
location_ixbrl = 'https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019320000096/aapl-20200926.htm'
location_xbrl = 'https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_htm.xml'
location_taxonomy = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926.xsd"
location_linkbase_cal = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_cal.xml"
location_linkbase_def = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_def.xml"
location_linkbase_lab = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_lab.xml"
location_linkbase_pre = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_pre.xml"


# Process both inline XBRL and native XBRL formats
# Parse inline document (iXBRL)

files = []
for location in [location_ixbrl, location_xbrl, location_taxonomy, location_linkbase_cal, location_linkbase_def, location_linkbase_lab, location_linkbase_pre]:
    files.append(location.split('/')[-1])
    if not os.path.exists(location.split('/')[-1]):
        response = requests.get(location, headers={'User-Agent': 'Your Name <your.email@example.com>'})
        # Save the response content to a file
        with open(location.split('/')[-1], 'wb') as file:
            file.write(response.content)
    
taxonomy = data_pool.add_taxonomy(files, esef_filing_root=os.getcwd())


print("\nTaxonomy statistics:")
print(f"Schemas: {len(taxonomy.schemas)}")
print(f"Linkbases: {len(taxonomy.linkbases)}")
print(f"Concepts: {len(taxonomy.concepts)}")


xid_inline = data_pool.add_instance_location(
    esef_filing_root=os.getcwd(), 
    filename="aapl-20200926.htm",
    key="apple_10k_inline", 
    attach_taxonomy=True
)


# Parse native document (XBRL)
xid_native = data_pool.add_instance_location(
    esef_filing_root=os.getcwd(), 
    filename="aapl-20200926_htm.xml",
    key="apple_10k_native", 
    attach_taxonomy=True
)

reporter = tax_reporter.TaxonomyReporter(taxonomy)


# Print information about the loaded documents
print('\nData Pool Information')
print('-' * 30)
print(data_pool.info())

print('\nInline XBRL Instance Information')
print('-' * 30)
print(xid_inline)

print('\nNative XBRL Instance Information')
print('-' * 30)
print(xid_native)

# You can access the taxonomy information through the instances
if xid_native.taxonomy:
    print('\nTaxonomy Information')
    print('-' * 30)
    print(xid_native.taxonomy)