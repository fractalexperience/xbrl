# Open-ESEF
- Open-ESEF is a Python-based open-source project for handling XBRL filings that follow ESEF, the European Single Electronic Format. 

- ESEF is a standard for electronic financial reporting developed by the European Securities and Markets Authority (ESMA). 

- This project is based on open-source code from these repos: 
  - [XBRL-Model](https://github.com/fractalexperience/xbrl/) project.
  - [SEC EDGAR Financial Reports](https://github.com/farhadab/sec-edgar-financials) project.
  - [pyXBRL](https://github.com/ifanchu/pyXBRL)

- See also:
  - https://github.com/trr266/ESEF.jl (Julia)
  - https://github.com/JeffFerguson/gepsio (.Net)
  - https://github.com/emilycoco/parse-xbrl (JavaScript)
  - https://github.com/altova/sec-xbrl/tree/master (Python, Altova)
  - https://github.com/secdatabase/SEC-XBRL-Financial-Statement-Dataset (https://www.secdatabase.com/)
  - https://github.com/altova/sec-xbrl/ (Python)
  - https://github.com/DataQualityCommittee/dqc_us_rules/ (xbrl.us/dqc aka XBRL-US Data Quality Committee Rules)
  - https://github.com/steffen-zou/Extract-financial-data-from-XBRL/

- Project is under development.
  - Development completeness: 66%.
    - On Feb 28, 2025, added filings.xbrl.org api interaction functions to download ESEF filings from filings.xbrl.org.

## How to use the Open-ESEF

### Installation

The **openesef** project can be installed directly from its GitHub repository using standard Python development workflows. Here's how to set it up:

1. **Clone the Repository**  
   Use `git clone` to download the source code:
   ```
   git clone https://github.com/reeyarn/openesef/
   ```

2. **Install in Editable Mode**  
   Navigate to the project directory and install using pip with the `-e` flag for development:
   ```bash
   cd openesef
   pip install -r requirements.txt
   pip install -e .
   ```

   This links the package to your Python environment while preserving the ability to modify code.

3. Verify installation by importing modules in Python:
  ```
  from openesef import base, taxonomy, instance  # Core components
  ```

### How to Use

#### Example 1: SEC Filings with iXBRL following US -GAAP

- Loading using ticker and year:
```python
from openesef.instance.loader import load_xbrl_filing
xid, tax = load_xbrl_filing(ticker="AAPL", year=2020)
```

- Or, loading using filing URL:
```python
from openesef.instance.loader import load_xbrl_filing
xid, tax = load_xbrl_filing(filing_url="/Archives/edgar/data/320193/0000320193-20-000096.txt")
```

- Now print the info:
```python
# Print the XBRL instance info:
print(xid)

# Print the taxonomy info:
print(tax)

# Print the DEI info:
for i, (key, value) in enumerate(xid.dei.items()):
    print(f"{i}: {key}: {value}")

# Print the presentation networks:
from openesef.util.parse_concepts import get_presentation_networks
get_presentation_networks(tax)    
```


See more: [https://github.com/reeyarn/openesef/blob/master/examples/apple_2020.ipynb](https://github.com/reeyarn/openesef/blob/master/examples/apple_2020.ipynb)

#### Example 2: Volkswagen 2020 ESEF Filing following IFRS


```python
# Simplified flow from search results
cube = Cube(folder="/data/xbrl_cache")
cube.add_fact(fact, xid_instance)  # Fact from XBRL instance
cube.save()  # Serializes to ZIP archives
```
This stores facts with associated dimensions (e.g., `metric:ifrs-full:Revenue`, `entity:sap`, `period:2022`) for later analysis.

https://github.com/reeyarn/openesef/blob/master/examples/try_vw2020.py

## Forked from XBRL-Model (`fractalexperience/xbrl/`): 

In this forked repository, I modify the code from the `fractalexperience/xbrl/` package to facilitate its compatibility with ESEF. 

The issue in the original repository was that, unlike  US-SEC-EDGAR, ESEF files adhere to a folder structure. Consequently, the schema references in ESEF files are relative to the instance file rather than the taxonomy folder, and `fractalexperience/xbrl/` package did not handle this out of the box.  Using SAP SE 2022 ESEF filing as an example, the ESEF filing root folder contains the following folders and files:
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



### Original XBRL-Model

https://github.com/fractalexperience/xbrl/

**Overview** The XBRL Model is able to parse XBRL instance documents and companion taxonomies and extract information such as reporting facts and their descriptors, reporting artifacts, such as taxonomy concepts, labels, references, hierarchies, enumerations, dimensions etc. It is equipped with a cache manager to allow efficiently maintain Web resources, as well as a package manager, which allows to load taxonomies  from taxonomy packages, where all files are distributed in a form of a ZIP archive.

Special attention is paid to efficient in-memory storage of various resources. There is a data pool, which allows objects, which are reused across different taxonomies to be stored in memory only once. This way it is possible to maintain multiple entry points and multiple taxonomy versions at the time, without a risk of memory overflow. 

## SEC EDGAR Financial Reports (Under Construction and Review)


The following modules have been added to the `edgar` folder to enhance the functionality of the Open-ESEF project for handling filings from SEC EDGAR. 

These files are **under review**; I will remove redundant modules and the non-XBRL parts of code. Only filing retrieval and parsing related code will be kept.

- The `edgar` folder contains modules that are used to handle filings from SEC EDGAR.
- The `edgar` folder is a fork of the [SEC EDGAR Financial Reports](https://github.com/farhadab/sec-edgar-financials) project.

  1. **stock.py**  
     This module handles the retrieval and management of stock symbols and their associated financial filings from the SEC. It includes functionality to update the symbols data and fetch filing information based on company symbols.

  2. **dtd.py**  
     This module defines the Document Type Definition (DTD) used for EDGAR documents. It provides a structured representation of the elements within the EDGAR filings, facilitating the parsing and validation of these documents.

  3. **sgml.py**  
     This module is responsible for parsing SGML documents from SEC filings. It utilizes the DTD to convert SGML data into a more manageable dictionary format, allowing for easier data extraction and manipulation.

  4. **requests_wrapper.py**  
     This module wraps the requests library to handle HTTP requests to the SEC's EDGAR system. It includes custom error handling to manage request exceptions effectively.

  5. **financials.py**  
     This module handles the logic related to financial reports extracted from EDGAR filings. It provides functionality to parse financial data and model financial elements for further analysis.

  6. **filing.py**  
     This module contains logic related to the handling of filings and documents from the SEC. It manages the retrieval, caching, and processing of filing data, ensuring that the necessary information is available for analysis.

  7. **edgar.py**  
     This module is used to traverse the EDGAR filing system and determine the location of filings. It provides functions to access various indexes and retrieve filing information based on specified criteria.

- These modules collectively enhance the Open-ESEF project by providing robust tools for interacting with SEC filings and extracting relevant financial data.

## Open-ESEF Architecture


Below is a structured breakdown of its functionality and architecture:


### Overview

XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage. XBRL is the open international standard for digital business reporting, managed by a global not for profit consortium, [XBRL International](https://www.xbrl.org/).  


The project provides tools for parsing, validating, and analyzing XBRL data, particularly for financial reporting under the ESEF mandate. It models taxonomies, handles dimensional data, and processes instance documents while maintaining lightweight storage structures.

---

### Key Components

#### 1. **Taxonomy Management**
- **Concept Handling**: Resolves XBRL concepts, labels, and relationships using `Taxonomy` classes.
- **Linkbase Processing**: Manages XBRL linkbases (presentation, definition, calculation) and resolves references to external taxonomies like IFRS 2021.
- **Entry Points**: Defines `EntryPoint` objects to organize taxonomy resources (e.g., URLs, descriptions).

#### 2. **Instance Document Processing**
- **Fact Extraction**: Parses XBRL facts with contextual metadata (entity, period, units, decimals).
- **Dimensional Analysis**: Handles explicit and typed dimensions in contexts, including scenario/segment containers.
- **Unit/Period Resolution**: Captures metric units (e.g., monetary units) and temporal contexts.

#### 3. **Data Modeling (Cube Class)**
- **Semantic Indexing**: Uses a `Cube` class to map facts to a multidimensional space:
  - **Dimensions**: Includes `metric`, `entity`, `period`, `unit`, and custom taxonomy-defined dimensions.
  - **Members**: Represents values tied to dimensions (e.g., `usd` for `unit`, `2022-12-31` for `period`).
- **Storage Optimization**: Serializes data into JSON files within ZIP archives, using SHA-1 hashing for content addressing.

---

### ESEF-Specific Features
- **ESEF Filing Root Handling**: Resolves local file paths and URLs relative to ESEF report directories (e.g., `/sap-2022-12-31-DE/`).
- **IFRS Taxonomy Integration**: References IFRS 2021 taxonomy packages (`full_ifrs-cor_2021-03-24.xsd`) for validation and concept resolution.
- **Inline XBRL (iXBRL) Support**: Processes embedded XHTML/XBRL hybrid documents and extracts facts.

---

### Data Flow
1. **Input**: ESEF instance documents (e.g., `sap-2022-12-31-DE.xhtml`) and associated taxonomies.
2. **Resolution**:
   - Resolves schema imports (e.g., `xbrl-instance-2003-12-31.xsd`).
   - Maps concepts to their taxonomy-defined types (monetary, shares, dates).
3. **Fact Extraction**:
   - Captures numeric facts, contexts, and units.
   - Generates signatures for facts using dimensional constraints (e.g., `entity:sap:metric:revenue`).
4. **Storage**: Archives processed data into structured ZIP files with partitioned JSON datasets.

---

### Technical Highlights
- **SHA-1 Hashing**: Used for content addressing and deduplication in archives.
- **LXML Integration**: Parses XML/HTML documents and resolves XLink references.
- **Logging**: Detailed debug logs for taxonomy resolution and instance processing.
- **Modular Design**: Separates core components (`base`), taxonomy logic (`taxonomy`), and reporting engines (`engines`).


### Supported Standards
- **XBRL 2.1**: Core specification for facts and contexts.
- **XBRL Dimensions**: Explicit/typed dimensions via `xbrldi` namespace.
- **ESEF Rules**: Compliance with EU ESMA requirements for inline XBRL.

The project serves as a foundation for building ESEF validation tools, financial analytics platforms, or regulatory reporting systems.

### To-Do's: 
   - Check the `engines` folder; what do they do? `HtmlHelper`, `tax_reporter`, `tlb_reporter` (this one does not have document yet)
   - Check the examples of the original repo:
     - Taxonomy Packages - Most of the taxonomies are nowadays distributed in form of taxonomy packages. [Link](https://fractalexperience.github.io/xbrl/taxonomy_packages.html)
     - Taxonomy Discovery - Loading of a XBRL taxonomy can be a challenging operations, because some taxonomies contain 10,000+ files. {XM} supports various scenarios to load taxonomies as well as an optimized model for in-memory taxonomy storage. [Link](https://fractalexperience.github.io/xbrl/taxonomy_discovery.html)
     - Taxonomy Browsing - XBRL Taxonomies contain large amounts of different objects. {XM} can be used to effectively display information about them as well as the relationships amongst each other. [Link1](https://github.com/reeyarn/openesef/blob/master/markdown/tax_browsing.md) [Link2](https://fractalexperience.github.io/xbrl/taxonomy_browsing)
        - Report Concepts
        - Presentation Hierarchies
        - View specific presentation hierarchies
        - View extensible enumerations lists
        - Extensible Enumeration Sets
        - Extensible Enumerations
        - Role Types and Arcrole Types
        - Dimensional Relationship Sets 
  
     - Table Rendering - {XM} can calculate table layout and render document templates as HTML files. Where is it?
     - Instance Document Analysis - {XM} includes basic tools for processing of XBRL filings. Where is it?
     - iXBRL Processing - {XM} is able to extract native XBRL from Inline XBRL filings. To do so, it supports related transformation registries and structures. [Link](https://fractalexperience.github.io/xbrl/ixbrl_processing)
     
