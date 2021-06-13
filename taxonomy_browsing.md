# Taxonomy Browsing - Examples



**XBRL Taxonomies** include a large amount of different objects such as **Reporting Concept** definitions (Metrics), **Dimensions** and their **Members**, **Enumerations**, Lexical information in form of **Labels** and **References** to normative documents, semantic information in form of inter-concept relationships, layout information in form of **Tables**, analytic information in form of **Formulas** etc. {XM} can be used to effectively browse these objects and display them in form of **HTML reports**.



## Example 1 - Report concepts

Download an load US-GAAP 2021 Financial Reporting Taxonomy and create a report of concepts in "srt" namespace. Click [here](us-gaap-2021-concepts-srt.html) to see the result.

````python
import sys, os
sys.path.insert(0, r'../../../')
from xbrl.base import pool
from xbrl.engines import tax_reporter


# US-GAAP taxonomy - version 2021
url = 'https://xbrl.fasb.org/us-gaap/2021/us-gaap-2021-01-31.zip'
# Create the data pool and load taxonomy.
data_pool = pool.Pool()
tax = data_pool.add_package(url)
# Create taxonomy reporter
rep = tax_reporter.TaxonomyReporter(tax)
# List concepts with 'srt' prefix
rep.r_concepts([c for c in tax.concepts.values() if c.prefix == 'srt'])
output_file = os.path.join(data_pool.output_folder, 'us-gaap-2021-concepts-srt.html')
rep.save_as(output_file)

````



