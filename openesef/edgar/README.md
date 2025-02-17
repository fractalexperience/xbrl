# How to locate XBRL files in EDGAR filings: EX-101

Okay, I've analyzed the provided documentation to understand the terms EX-100 and EX-101 within the context of EDGAR filings.

https://www.sec.gov/info/edgar/edgarfm-vol2-v14.pdf

https://www.sec.gov/files/edgar/filer-information/specifications/xbrl-guide.pdf

**Core Concept:**

*   EX-100 and EX-101 are *document type codes* used in EDGAR filings specifically for attaching files related to **interactive data**, often involving XBRL (Extensible Business Reporting Language). These documents are specifically linked to interactive data.

**Key Takeaways from the Document:**

1.  **XBRL Attachments:** The main purpose of EX-100 and EX-101 is for attaching XBRL instance documents, schema documents, and linkbase documents to an EDGAR submission.

2.  **Interactive Data/XBRL Validations:**

    *   The document mentions, "The EDGAR Interactive Data/XBRL validations will be extended to all EX-101 attachments regardless of the taxonomy used." This highlights that these codes trigger specific validation rules for interactive data submissions.

    *  Validations:  The documentation also includes syntax and semantics rules for creating an interactive submission, as well as, validation requirements for EX-101 documents.

3.  **Use of EDGARLink Templates:** The document states that EDGARLink Submission Templates 1, 2, and 3 are used to attach XBRL Document Types. This tells you *how* you'd actually use these codes during filing.

4.  **EX-100 vs EX-101:** While the document consistently references both EX-100 and EX-101 attachments, I've found that:

    * A single submission must not contain both EX-100 and EX-101 attachments.
    * An XBRL instance submitted in the Voluntary Filing Program must be an EX-100.INS
    * An Interactive Data instance in XBRL format must be an EX-101.INS

5.  **Document Naming:** XBRL document names must follow a specific convention. The XBRL document names must match {base}-{date}[_{suffix}].{extension}.
    >6 .3.3  XBRL document names must match {base}-{date}[_{suffix}].{extension}

| XBRL Document | Document Name Format |
|----------------|-------------------|
| Instance | {base}-{date}.xml |
| Schema | {base}-{date}.xsd |
| Calculation Linkbase | {base}-{date}_cal.xml |
| Definition Linkbase | {base}-{date}_def.xml |
| Label Linkbase | {base}-{date}_lab.xml |
| Presentation Linkbase | {base}-{date}_pre.xml |
| Reference Linkbase | {base}-{date}_ref.xml |

 - The `{base}` should begin with the registrant’s ticker symbol or other mnemonic abbreviation.

 - The `{date}` must denote the ending date of the period.  If the instance document is a prospectus or other report whose period is indefinite, `{date}` should match the filing date.


    Example:
    *   abccorp-20041130\_cal.xml
    *   abccorp-20041201\_ref.xml
    *   abccorp-20041012.xsd

**In summary:**

*   **EX-100 & EX-101:** Designate that attached files contain interactive data, often in XBRL format. They trigger specific validations within the EDGAR system.
*   **EX-100:** Indicates XBRL used in a Voluntary Filing Program submission
*   **EX-101:** Indicates interactive Data submission.






```python
from openesef.base.pool import Pool
from openesef.edgar.edgar import EG_LOCAL
from openesef.edgar.stock import Stock

#where you store the files downloaded from SEC's EDGAR
egl = EG_LOCAL('/text/edgar')


stock = Stock('AAPL', egl = egl); #self = stock
filing = stock.get_filing(period='annual', year=2023)

for key, doc in filing.documents.items():
    if re.search(r'xml|xhtml', doc.filename, flags=re.IGNORECASE) or re.search(r'101|100', doc.type, flags=re.IGNORECASE):    
        print()
        print(doc.sequence, key, doc.type, doc.filename, len(doc.doc_text.data))
        print(doc.description)
```

Output: 

```
8 aapl-20230930.xsd EX-101.SCH aapl-20230930.xsd 59744
XBRL TAXONOMY EXTENSION SCHEMA DOCUMENT

9 aapl-20230930_cal.xml EX-101.CAL aapl-20230930_cal.xml 155407
XBRL TAXONOMY EXTENSION CALCULATION LINKBASE DOCUMENT

10 aapl-20230930_def.xml EX-101.DEF aapl-20230930_def.xml 233485
XBRL TAXONOMY EXTENSION DEFINITION LINKBASE DOCUMENT

11 aapl-20230930_lab.xml EX-101.LAB aapl-20230930_lab.xml 854285
XBRL TAXONOMY EXTENSION LABEL LINKBASE DOCUMENT

12 aapl-20230930_pre.xml EX-101.PRE aapl-20230930_pre.xml 516240
XBRL TAXONOMY EXTENSION PRESENTATION LINKBASE DOCUMENT

90 aapl-20230930_htm.xml XML aapl-20230930_htm.xml 1
IDEA: XBRL DOCUMENT

94 FilingSummary.xml XML FilingSummary.xml 1
IDEA: XBRL DOCUMENT
```

## xlink:href


6.3.6  The URI content of the xlink:href attribute, the xsi:schemaLocation attribute and the schemaLocation attribute must be relative and contain no forward slashes, or a
recognized external location of a standard taxonomy schema file, or a “#” followed by a shorthand xpointer.

The xlink:href attribute must appear on the link:loc element; the schemaLocation attribute must appear on the xsd:import element, and the xsi:schemaLocation attribute must appear on the link:linkbase element and may appear on the xbrli:xbrl element.

Valid entries for the xlink:href attribute, the xsi:schemaLocation attribute and the schemaLocation attribute are document locations.  If they are relative URIs, they are subject to EDGARLink attachment naming conventions. Therefore, all documents attached to the submission will be at the same level of folder hierarchy. By restricting the content of these attributes, all documents in the DTS of an instance will be either a standard taxonomy or present in the submission.

Examples:

*  xlink:href="abccorp-20100123.xsd"

*  <xsd:import schemaLocation="http://xbrl.org/2006/xbrldi-2006.xsd" namespace=
…/>

Counterexamples:

*  xlink:href="http://www.example.com/2007/example.xsd”

*  xlink:href="#element(1/4)" (Comment: this is a scheme-based xpointer, not shorthand)

The XHTML namespace is intentionally omitted, since an XHTML declaration could not be a valid target for any XBRL element’s xlink:href or schemaLocation attribute, and its presence in the xsi:schemaLocation attribute would not impact XBRL validation.

There are dozens of other XBRL US GAAP Taxonomies documents to be used as templates to copy from during the preparation process, but their inclusion in an EDGAR filing tends to load unused linkbases and therefore introduces unwarranted complications such as unused extended links and a need for many prohibiting arcs. Reducing the amount of content in the DTS of the instance to its essentials frees users to more easily link the submitted documents to the linkbases of their particular interest for analysis.
