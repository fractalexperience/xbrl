import sys
sys.path.insert(0, r'../../../')
from xbrl.taxonomy import tpack


url = 'https://dev.eiopa.europa.eu/Taxonomy/Full/2.5.0/S2/EIOPA_SolvencyII_XBRL_Taxonomy_2.5.0_hotfix.zip'
# Download and open package in system default temporary folder
package = tpack.TaxonomyPackage(url)
# View package content in the console
print(package)


