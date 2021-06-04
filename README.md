# XBRL-Model
A Lightweight XBRL Taxonomy and Instance Document Model

## Overview

XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage. XBRL is the open international standard for digital business reporting, managed by a global not for profit consortium, [XBRL International](https://www.xbrl.org/).  

The XBRL Model is able to parse XBRL instance documents and companion taxonomies and extract information such as reporting facts and their descriptors, reporting artifacts, such as taxonomy concepts, labels, references, hierarchies, enumerations, dimensions etc. It is equipped with a cache manager to allow efficiently maintain Web resources, as well as a package manager, which allows to load taxonomies  from taxonomy packages, where all files are distributed in a form of a ZIP archive.

Special attention is paid to efficient in-memory storage of various resources. There is a data pool, which allows objects, which are reused across different taxonomies to be stored in memory only once. This way it is possible to maintain multiple entry points and multiple taxonomy versions at the time, without a risk of memory overflow. 

For more information see project's [Web page](https://fractalexperience.github.io/xbrl/).

## Getting Started

Download package

``` 
git clone https://github.com/fractalexperience/xbrl.git
```

## Examples

See the examples page at: [https://fractalexperience.github.io/xbrl/examples.html](https://fractalexperience.github.io/xbrl/examples.html) for more instructions about package usage.

## XBRL Explained 

Please check the Terminology ([https://fractalexperience.github.io/xbrl/terminology.html](https://fractalexperience.github.io/xbrl/terminology.html)) and XBRL objects page ([https://fractalexperience.github.io/xbrl/objects.html](https://fractalexperience.github.io/xbrl/objects.html)) for brief explanation about data objects and structures inside taxonomies and instance documents. See also the specifications page ([https://fractalexperience.github.io/xbrl/specs.html](https://fractalexperience.github.io/xbrl/specs.html)) about supported XBRL specifications. 

