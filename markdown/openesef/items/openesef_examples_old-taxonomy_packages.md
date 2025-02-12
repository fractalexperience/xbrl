# examples_old/taxonomy_packages Contents
## examples_old/taxonomy_packages/eiopa_250_content.py
```py
import sys
sys.path.insert(0, r'../../../')
from xbrl.taxonomy import tpack


url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
# Download and open package in system default temporary folder
package = tpack.TaxonomyPackage(url)
# View package content in the console
print(package)
```

## examples_old/taxonomy_packages/eiopa_250_html.py
```py
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
```

## examples_old/taxonomy_packages/esma_2020_html.py
```py
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
```

## examples_old/taxonomy_packages/ifrs_2020_filelist.py
```py
import sys
sys.path.insert(0, r'../../../')
from xbrl.taxonomy import tpack


url = 'https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomies/IFRST_2021-03-24.zip'
# Download and open package in system default temporary folder
package = tpack.TaxonomyPackage(url)
# Create list of resolved locations
package.compile()
# View list of files
for url, fn in package.files.items():
    print(url, ' => ', fn)
```
