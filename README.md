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
git clone https://github.com/fractalexperience/XBRL-Model.git
```



## Examples

Create a data pool and open an instance document

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



