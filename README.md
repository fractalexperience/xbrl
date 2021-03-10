# XBRL-Model
A Lightweight XBRL Taxonomy and Instance Document Model



## Overview

XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage. XBRL is the open international standard for digital business reporting, managed by a global not for profit consortium, [XBRL International](https://www.xbrl.org/).  

XBRL-Model is a Python based framework, which includes parsers and data objects to represent XBRL instance documents and taxonomies according various XBRL specifications. The following specifications are supported: 

XBRL v.2.1 - https://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html

XBRL Dimensions - https://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18+corrected-errata-2012-01-25-clean.html

Extensible Enumerations - https://www.xbrl.org/Specification/extensible-enumerations-2.0/REC-2020-02-12/extensible-enumerations-2.0-REC-2020-02-12.html



## Getting Started

Install package

``` 
git clone https://github.com/fractalexperience/xbrl.git
```



## Examples

**Ex1**: Create a data pool and open an instance document

``` python

location = 'https://www.sec.gov/Archives/edgar/data/1341439/000156459020056896/orcl-10q_20201130_htm.xml'
# Set cache folder
cache_filder = os.path.join(dirname, '..\\cache')
# Create data pool
data_pool = pool.Pool(cache_filder)
# Open instance document
data_pool.add_instance(location=location, key=location, attach_taxonomy=True)
print('Data pool info')
print('----------------------')
print(data_pool.info())

```

**Ex2**: Query a taxonomy package to extract contained taxonomy entry points

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



