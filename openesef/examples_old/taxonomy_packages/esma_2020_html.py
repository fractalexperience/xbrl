import sys, os
sys.path.insert(0, r'../../../')
from xbrl.taxonomy import tpack
from xbrl.engines import tax_reporter


# ESMA Taxonomy version 2020 - https://www.esma.europa.eu/document/esma-esef-taxonomy-2020
url = 'https://www.esma.europa.eu/sites/default/files/library/esef_taxonomy_2020.zip'
# Download and open package in system default temporary folder
package = tpack.TaxonomyPackage(url)
# Render package content to HTML using the taxonomy reporter
rep = tax_reporter.TaxonomyReporter()
rep.r_package(package)
output_file = os.path.join(package.output_folder, 'esef_taxonomy_2020_package_content.html')
rep.save_as(output_file)

