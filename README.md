# Open-ESEF
Open-ESEF is a project to create a free and open-source XBRL tool for the ESEF filings following the standards set by the European Securities and Markets Authority (ESMA).

In this forked repo, I was trying to modify the code from `xbrl` package to make it work for ESEF. 

The issue was that, unlike xbrl @ US-SEC-EDGAR, ESEF files have a folder structure, and the schema references are relative to the instance file, not the taxonomy folder. Example:
```
% ls -R examples/sap-2022-12-31-DE

META-INF	reports		www.sap.com

sap-2022-12-31-DE/META-INF:
catalog.xml		taxonomyPackage.xml

sap-2022-12-31-DE/reports:
sap-2022-12-31-DE.xhtml

sap-2022-12-31-DE/www.sap.com:
sap-2022-12-31.xsd		sap-2022-12-31_cal.xml		sap-2022-12-31_def.xml		sap-2022-12-31_lab-de.xml	sap-2022-12-31_lab-en.xml	sap-2022-12-31_pre.xml
```

I have tried to modify the code to handle ESEF by adding the `esef_filing_root` parameter and passing it around.
I added the `esef_filing_root` parameter to the following files:
taxonomy/taxonomy.py
base/pool.py
base/fbase.py
taxonomy/tpack.py
taxonomy/linkbase.py
taxonomy/schema.py
taxonomy/taxonomy.py
..

## Forked from XBRL-Model
https://github.com/fractalexperience/xbrl/ 
A Lightweight XBRL Taxonomy and Instance Document Model

## Overview

XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage. XBRL is the open international standard for digital business reporting, managed by a global not for profit consortium, [XBRL International](https://www.xbrl.org/).  

The XBRL Model is able to parse XBRL instance documents and companion taxonomies and extract information such as reporting facts and their descriptors, reporting artifacts, such as taxonomy concepts, labels, references, hierarchies, enumerations, dimensions etc. It is equipped with a cache manager to allow efficiently maintain Web resources, as well as a package manager, which allows to load taxonomies  from taxonomy packages, where all files are distributed in a form of a ZIP archive.

Special attention is paid to efficient in-memory storage of various resources. There is a data pool, which allows objects, which are reused across different taxonomies to be stored in memory only once. This way it is possible to maintain multiple entry points and multiple taxonomy versions at the time, without a risk of memory overflow. 

For more information see project's [Web page](https://fractalexperience.github.io/xbrl/).

