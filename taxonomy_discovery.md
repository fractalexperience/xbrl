# Taxonomy Discovery Examples



**Taxonomy discovery** is the process of loading XML Schema files and XBRL Linkbase files included in a specific taxonomy. The process starts with a list of XML Schema (*.xsd) files called **Entry Point**. Then it **recursively** follows all references inside XML Schemas and XBRL Linkbases, until all the content is loaded in memory. 



## Example 1 - Load all

Download US-GAAP 2021 taxonomy package and index it in taxonomy cache. Then load **all** entry points described in the package in a single taxonomy object.

```python
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

# Schemas: 169
# Linkbases: 281
# Role Types: 612
# Arcrole Types: 17
# Concepts: 20409
# Labels: 34786
# References: 40310
# Hierarchies: 2131
# Dimensional Relationship Sets: 2131
# Dimensions: 291
# Hypercubes: 363
# Enumerations: 0
# Enumerations Sets: 285
# Table Groups: 0
# Tables: 0

```



## Example 2 - Load specific entry point

Download US-GAAP 2021 taxonomy package and index it in taxonomy cache. Then load entry point with https://xbrl.fasb.org/us-gaap/2021/entire/us-gaap-entryPoint-std-2021-01-31.xsd into ataxonomy object.

```python
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

# Schemas: 132
# Linkbases: 273
# Role Types: 594
# Arcrole Types: 11
# Concepts: 18266
# Labels: 19609
# References: 0
# Hierarchies: 2129
# Dimensional Relationship Sets: 2129
# Dimensions: 291
# Hypercubes: 363
# Enumerations: 0
# Enumerations Sets: 285
# Table Groups: 0
# Tables: 0
```



## Example 3 - Load directly from Web location

Load the same entry point as example 2 directly from Web location without using the taxonomy package. 

*Note: The process takes much longer time, because its needed to download and cache every single file from taxonomy. However, once files are cached, the process is a bit faster then using the package.* 

*Note2: Not every taxonomy is available for direct download. Some taxonomies are only available in form of a package.* 

```python
from xbrl.base import pool


entry_point = 'https://xbrl.fasb.org/us-gaap/2021/entire/us-gaap-entryPoint-std-2021-01-31.xsd'
data_pool = pool.Pool()
# Load a specific entry point directly from Web
tax = data_pool.add_taxonomy([entry_point])
# Output taxonomy summary information
print(tax)

# Schemas: 132
# Linkbases: 273
# Role Types: 594
# Arcrole Types: 11
# Concepts: 18266
# Labels: 19609
# References: 0
# Hierarchies: 2129
# Dimensional Relationship Sets: 2129
# Dimensions: 291
# Hypercubes: 363
# Enumerations: 0
# Enumerations Sets: 285
# Table Groups: 0
# Tables: 0

```

