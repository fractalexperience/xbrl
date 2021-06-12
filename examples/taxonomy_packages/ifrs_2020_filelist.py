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
