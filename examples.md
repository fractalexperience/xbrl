# XBRL Model - Examples

Below there are a few usage examples for XBRL Model package. Of course there can be much more use cases. If you have ideas and suggestions, please email at xbrl@fractalexperience.com

Note that some of the examples may download significant amount of information from Web locations, so you have to provide a cache folder with full rights on local file system.



## Example 1

Create a data pool and open two instance documents containing the same information. The first one is designed as [Inline XBRL](https://www.xbrl.org/specification/inlinexbrl-part1/rec-2013-11-18/inlinexbrl-part1-rec-2013-11-18.html) and contains additional HTML tags. The second one is a native XBRL instance according [XBRL version 2.1](https://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html).

```python
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



## Example 2

Query a taxonomy package (EIOPA 2.5.0) to extract contained taxonomy entry points and supporting package information. 

```python
from xbrl.taxonomy import tpack


location = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
# The cache folder must be available and accessible
# with full rights in local file system
package = tpack.TaxonomyPackage(location, r'..\cache')
# Taxonomy package information includes:
#   Basic properties: Name, Version, Publisher etc.
#   Entrypoints: Each entry point has a name, url and description.
#   Redirects: This information instructs the processor how to replace Web URLs to files in the package
#   Superseded packages: List of superseded packages if any.
print(package)


```



## Example 3

Create a data pool and add a taxonomy - in this case US-GAAP 2021

```python
from xbrl.base import pool

# US-GAAP taxonomy - version 2021
location = 'https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip'
# Create the data pool. The cache folder must be accessible with full rights 
# in the local file system.
data_pool = pool.Pool(r'..\cache')
# This method does the following: 
# - Download the ZIP archive of the taxonomy package URL provided and store it in cache
# - Query the package about available entry ponits and location remappings
# - Load all available entry points into a single taxonomy object.
tax = data_pool.add_package(location)
# Output taxonomy summary information
print(tax)

# Schemas: 169
# Linkbases: 281
# Concepts: 20409
# Labels: 34786
# References: 40310
# Hierarchies: 2131
# Dimensional Relationship Sets: 2131
# Dimensions: 291
# Hypercubes: 363
# Enumerations: 0
# Enumerations Sets: 285
```

