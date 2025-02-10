# examples_old/taxonomy_discovery Contents
## examples_old/taxonomy_discovery/us-gaap-2021-package-all.py
```py
import sys
sys.path.insert(0, r'../../../')
from xbrl.base import pool


# US-GAAP taxonomy - version 2021
url = 'https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip'
# Create the data pool.
data_pool = pool.Pool()
# The method does the following:
# - Download the ZIP archive of the taxonomy package URL provided and store it in cache
# - Query the package about available entry points and location remappings
# - Load all available entry points into a single taxonomy object.
tax = data_pool.add_package(url)
# Output taxonomy summary information
print(tax)
```

## examples_old/taxonomy_discovery/us-gaap-2021-package-std.py
```py
import sys
sys.path.insert(0, r'../../../')
from xbrl.base import pool


# US-GAAP taxonomy - version 2021
url = 'https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip'
# Create the data pool.
data_pool = pool.Pool()
# - Download the ZIP archive of the taxonomy package URL provided and store it in cache
data_pool.cache_package(url)
# Load a specific entry point
entry_point = 'https://xbrl.fasb.org/us-gaap/2021/entire/us-gaap-entryPoint-std-2021-01-31.xsd'
tax = data_pool.add_taxonomy([entry_point])
# Output taxonomy summary information
print(tax)
```

## examples_old/taxonomy_discovery/us-gaap-2021-web-std.py
```py
import sys
sys.path.insert(0, r'../../../')
from xbrl.base import pool


entry_point = 'https://xbrl.fasb.org/us-gaap/2021/entire/us-gaap-entryPoint-std-2021-01-31.xsd'
data_pool = pool.Pool()
# Load a specific entry point directly from Web
tax = data_pool.add_taxonomy([entry_point])
# Output taxonomy summary information
print(tax)
```
