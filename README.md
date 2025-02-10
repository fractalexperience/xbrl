# Open-ESEF
Open-ESEF is a Python-based open-source project dedicated to developing a complimentary and freely available XBRL toolkit for processing XBRL filings in accordance with the standards established by the European Securities and Markets Authority (ESMA). The project is designed to handle XBRL taxonomy and instance documents compatible with the European Single Electronic Format (ESEF). 

In this forked repository, I modify the code from the `xbrl` package to facilitate its compatibility with ESEF. The issue in the original repository was that, unlike  US-SEC-EDGAR, ESEF files adhere to a folder structure. Consequently, the schema references in ESEF files are relative to the instance file rather than the taxonomy folder, and `xbrl` package does not handle this out of the box.  Using SAP SE 2022 ESEF filing as an example, the ESEF filing root folder contains the following folders and files:
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

## Forked from XBRL-Model (`fractalexperience/xbrl/`): 

### A Lightweight XBRL Taxonomy and Instance Document Model

https://github.com/fractalexperience/xbrl/

**Overview** The XBRL Model is able to parse XBRL instance documents and companion taxonomies and extract information such as reporting facts and their descriptors, reporting artifacts, such as taxonomy concepts, labels, references, hierarchies, enumerations, dimensions etc. It is equipped with a cache manager to allow efficiently maintain Web resources, as well as a package manager, which allows to load taxonomies  from taxonomy packages, where all files are distributed in a form of a ZIP archive.

Special attention is paid to efficient in-memory storage of various resources. There is a data pool, which allows objects, which are reused across different taxonomies to be stored in memory only once. This way it is possible to maintain multiple entry points and multiple taxonomy versions at the time, without a risk of memory overflow. 




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

---

### Example Workflow
```python
# Simplified flow from search results
cube = Cube(folder="/data/xbrl_cache")
cube.add_fact(fact, xid_instance)  # Fact from XBRL instance
cube.save()  # Serializes to ZIP archives
```
This stores facts with associated dimensions (e.g., `metric:ifrs-full:Revenue`, `entity:sap`, `period:2022`) for later analysis.

--- 

### Supported Standards
- **XBRL 2.1**: Core specification for facts and contexts.
- **XBRL Dimensions**: Explicit/typed dimensions via `xbrldi` namespace.
- **ESEF Rules**: Compliance with EU ESMA requirements for inline XBRL.

The project serves as a foundation for building ESEF validation tools, financial analytics platforms, or regulatory reporting systems.

Citations:
 https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/12467256/680f2e9a-70e1-4df5-be15-c4d1509e8f3e/openesef_all.md


