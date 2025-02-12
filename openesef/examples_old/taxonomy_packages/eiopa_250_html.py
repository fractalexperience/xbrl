import sys, os
sys.path.insert(0, r'../../../')
from xbrl.taxonomy import tpack
from xbrl.engines import tax_reporter

# EIOPA Taxonomy version 2.5.0: https://www.eiopa.europa.eu/tools-and-data/supervisory-reporting-dpm-and-xbrl
url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
# Download and open package in system default temporary folder
package = tpack.TaxonomyPackage(url)
# Render package content to HTML using the taxonomy reporter
rep = tax_reporter.TaxonomyReporter()
rep.r_package(package)
output_file = os.path.join(package.output_folder, 'eiopa_taxonomy_2.5.0_package_content.html')
rep.save_as(output_file)
