# XBRL Model

XBRL Model is a Python package for dealing with XBRL data. XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage. XBRL is the open international standard for digital business reporting, managed by a global not for profit consortium, [XBRL International](https://www.xbrl.org/). 

The XBRL Model package includes parsers and data objects to represent both instance documents (containing real data) and XBRL taxonomies (containing metadata). It supports various [XBRL specifications](https://specifications.xbrl.org/specifications.html) - in particular: 

* XBRL v.2.1 - https://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html
* XBRL Dimensions 1.0 - https://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18+corrected-errata-2012-01-25-clean.html
* Extensible Enumerations 2.0 - https://www.xbrl.org/Specification/extensible-enumerations-2.0/REC-2020-02-12/extensible-enumerations-2.0-REC-2020-02-12.html
* Taxonomy Packages 1.0 - https://www.xbrl.org/Specification/taxonomy-package/PR-2015-12-09/taxonomy-package-PR-2015-12-09.html
* Inline XBRL 1.1 - https://www.xbrl.org/specification/inlinexbrl-part1/rec-2013-11-18/inlinexbrl-part1-rec-2013-11-18.html

## Use Cases

XBRL Model can be used to process large amounts of XBRL filings from open data providers such as [SEC/EDGAR](https://www.sec.gov/), [GOV.UK](https://www.gov.uk/) and many others. It is able to automatically download and unpack Web based data sources and contains a caching mechanism to improve speed when processing Web based taxonomies. It contains an in-memory mechanism to maintain multiple taxonomies, and taxonomy versions in the same time and thus can become a fundament for various Web based applications for XBRL reporting and data analysis.

## XBRL Explained

- [Terminology](terminology.html)

- [Objects](objects.html)

- 

  





