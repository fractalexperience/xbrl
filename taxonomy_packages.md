# Taxonomy Packages - Examples



**Taxonomy Package** is a ZIP archive containing all files included in a XBRL taxonomy. In addition to this, there is a special folder called **META-INF**, which contains the description of the package and instructions about how to read the content.



## Example 1

Simplest case of opening a package from a Web location. 

```python
from xbrl.taxonomy import tpack


url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
# Download and open package in system default temporary folder
package = tpack.TaxonomyPackage(url)
# View package content in the console
print(package)
```



## Example 2

Open a taxonomy package from a Web location (in this case ) and create a HTML report for its content in the temporary folder.

```python
from xbrl.taxonomy import tpack
from xbrl.engines import tax_reporter


# ESMA Taxonomy version 2020
# https://www.esma.europa.eu/document/esma-esef-taxonomy-2020
url = 'https://www.esma.europa.eu/sites/default/files/library/esef_taxonomy_2020.zip'
# Download and open package in system default temporary folder
package = tpack.TaxonomyPackage(url)
# Render package content to HTML using the taxonomy reporter
rep = tax_reporter.TaxonomyReporter()
rep.r_package(package)
output_file = os.path.join(package.output_folder, 'esef_taxonomy_2020_package_content.html')
rep.save_as(output_file)
```



## Example 3

List files in a package together with their resolved locations.

```python
from xbrl.taxonomy import tpack


url = 'https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomies/IFRST_2021-03-24.zip'
# Download and open package in system default temporary folder
package = tpack.TaxonomyPackage(url)
# Create list of resolved locations
package.compile()
# View list of files
for url, fn in package.files.items():
    print(url, ' => ', fn)
    
# http://xbrl.ifrs.org/taxonomy/2021-03-24/basic_ifrs_entry_point_2021-03-24.xsd  =>  IFRST_2021-03-24/basic_ifrs_entry_point_2021-03-24.xsd
# http://xbrl.ifrs.org/taxonomy/2021-03-24/combined_entry_point_2021-03-24.xsd  =>  IFRST_2021-03-24/combined_entry_point_2021-03-24.xsd
# etc. 
```



