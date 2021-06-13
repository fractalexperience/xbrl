# XBRL Model

XBRL Model is a Python package for dealing with XBRL data. XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage. XBRL is the open international standard for digital business reporting, managed by a global not for profit consortium, [XBRL International](https://www.xbrl.org/). 

## Supported XBRL Specifications

The XBRL Model package includes parsers and data objects to represent both instance documents (containing real data) and XBRL taxonomies (containing metadata). It supports various [XBRL specifications](https://specifications.xbrl.org/specifications.html) - in particular: 

* [XBRL version 2.1](https://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html) - Basic XBRL Specification
* [XBRL Dimensions 1.0](https://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18+corrected-errata-2012-01-25-clean.html) - The XBRL Dimensions specification enables the reporting of multi-dimensional facts against dimensions defined in an XBRL taxonomy. This specification is sometimes referred to by the historical abbreviation of "XDT" (XBRL Dimensional Taxonomies).
* [Table Linkbase 1.0](https://www.xbrl.org/Specification/table-linkbase/REC-2014-03-18+errata-2018-07-17/table-linkbase-REC-2014-03-18+corrected-errata-2018-07-17.html) - The Table Linkbase provides a mechanism for taxonomy authors to define a tabular layout of facts. The resulting tables can be used for both presentation and data entry.
* [Extensible Enumerations 2.0](https://www.xbrl.org/Specification/extensible-enumerations-2.0/REC-2020-02-12/extensible-enumerations-2.0-REC-2020-02-12.html) - This specification allows domain member networks, to constrain the allowed values for primary reporting concepts, enabling taxonomy authors to define extensible enumerations with multi-language labels.
* [Taxonomy Packages 1.0](https://www.xbrl.org/Specification/taxonomy-package/PR-2015-12-09/taxonomy-package-PR-2015-12-09.html) - Taxonomy Packages provide a standardised mechanism for providing documentation about the content of a taxonomy. This can include information about the name, version and publisher of the taxonomy, as well as a list of the "entry points" available within the taxonomy. Taxonomy Packages can also provide URL remappings, enabling XBRL tools to be automatically configured for off-line use.
*  [Inline XBRL 1.1](https://www.xbrl.org/specification/inlinexbrl-part1/rec-2013-11-18/inlinexbrl-part1-rec-2013-11-18.html) - [Inline XBRL](https://www.xbrl.org/ixbrl), or [iXBRL](https://www.xbrl.org/ixbrl), provides a mechanism for embedding XBRL tags in HTML documents. This allows the XBRL benefits of tagged data to be combined with a human-readable presentation of a report, which is under the control of the preparer.

## Use Cases

XBRL Model can be used to process large amounts of XBRL filings from open data providers such as [SEC/EDGAR](https://www.sec.gov/), [GOV.UK](https://www.gov.uk/) and many others. It is able to automatically download and unpack Web based data sources and contains a caching mechanism to improve speed when processing Web based taxonomies. It contains an in-memory mechanism to maintain multiple taxonomies, and taxonomy versions in the same time and thus can become a fundament for various Web based applications for XBRL reporting and data analysis.

## Examples

The package includes a number of examples to illustrate various use cases. Click on links below to see the list of examples.

[Taxonomy Packages](taxonomy_packages.html) - Most of the taxonomies are nowadays distributed in form of taxonomy packages. 

[Taxonomy Discovery](taxonomy_discovery.html) - Loading of a XBRL taxonomy can be a challenging operations, because some taxonomies contain 10,000+ files. {XM} supports various scenarios to load taxonomies as well as an optimized model for in-memory taxonomy storage.

[Taxonomy Browsing](taxonomy_browsing) - XBRL Taxonomies contain large amounts of different objects. {XM} can be used to effectively display information about them as well as the relationships amongst each other.

[Table Rendering](table_rendering.html) - {XM} can calculate table layout and render document templates as HTML files. 

[Instance Document Analysis](xid_analysis.html) - {XM} includes basic tools for processing of XBRL filings.

[iXBRL Processing](ixbrl_processing) - {XM} is able to extract native XBRL from Inline XBRL filings. To do so, it supports related transformation registries and structures. 



## XBRL Explained

Check links below for very brief explanation about what XBRL is and how data is structured.

- [Terminology](terminology.html)

- [Objects](objects.html)

- [XBRL Specifications](specs.html)

- [Validation](validation.html)

  





