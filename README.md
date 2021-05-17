# XBRL-Model
A Lightweight XBRL Taxonomy and Instance Document Model



## Overview

XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage. XBRL is the open international standard for digital business reporting, managed by a global not for profit consortium, [XBRL International](https://www.xbrl.org/).  

XBRL-Model is a Python based framework, which includes parsers and data objects to represent XBRL instance documents and taxonomies according various XBRL specifications. The following specifications are supported: 

XBRL v.2.1 - https://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html

XBRL Dimensions 1.0 - https://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18+corrected-errata-2012-01-25-clean.html

Extensible Enumerations 2.0 - https://www.xbrl.org/Specification/extensible-enumerations-2.0/REC-2020-02-12/extensible-enumerations-2.0-REC-2020-02-12.html

Taxonomy Packages 1.0 - https://www.xbrl.org/Specification/taxonomy-package/PR-2015-12-09/taxonomy-package-PR-2015-12-09.html



## Getting Started

Download package

``` 
git clone https://github.com/fractalexperience/xbrl.git
```



## Examples

**Example1**: Create a data pool and open two instance documents containing the same information. The first one is designed as [Inline XBRL](https://www.xbrl.org/specification/inlinexbrl-part1/rec-2013-11-18/inlinexbrl-part1-rec-2013-11-18.html) and contains additional HTML tags. The second one is a native XBRL instance according [XBRL version 2.1](https://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html).

``` python

from xbrl.base import pool

# Create the data pool. Note that its cache folder must be accessible with full access righs
# in the local file system.
data_pool = pool.Pool('..\\cache')
# A random iXBRL instance from SEC/EDGAR system
location_ixbrl = 'https://www.sec.gov/Archives/edgar/data/1000177/000114036121014948/brhc10022989_20f.htm'
# Same instance, but in native XBRL format.
location_xbrl = 'https://www.sec.gov/Archives/edgar/data/1000177/000114036121014948/brhc10022989_20f_htm.xml'
# Parse inline document
xid_inline = data_pool.add_instance_location(location=location_ixbrl, key=location_ixbrl, attach_taxonomy=True)
# PArse native document
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

**Example2**: Query a taxonomy package to extract contained taxonomy entry points

``` python
from xbrl import tpack

location = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
cache_folder = '../cache'  # The cache folder is needed to store the taxonomy package for further use
package = tpack.TaxonomyPackage(location, cache_folder)
for ep in package.entrypoints:  # Each entrypoint is described with a prefix, URL and description
    prefix = ep[0]
    url = ep[1]
    description = ep[2]
    print(prefix, url, description)
```

**Ex3**: Create a data pool and add a taxonomy

```python
data_pool = pool.Pool('..\\cache')
data_pool.index_packages()  # Locate available taxonomy packages
entrypoint = 'http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2020-07-15/mod/qrs.xsd'
taxonomy = data_pool.add_taxonomy([entrypoint])  # Parse taxonomy object
print(taxonomy.info())
```



