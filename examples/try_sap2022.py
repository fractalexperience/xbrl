"""

to search for keyword in whole code base

find ./openesef/ -name "*.py" -type f -exec grep -il reporter {} \;
"""


#from xbrl.instance import XbrlInstance
from openesef.base import pool, const
from openesef.engines import tax_reporter
#from openesef.instance import XbrlInstance
import os
import gzip

import logging


if __name__ == "__main__":
    #from openesef.base import pool
    esef_filing_root="/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/"
    filename="reports/sap-2022-12-31-DE.xhtml"
    data_pool = pool.Pool(cache_folder="../data/xbrl_cache")
    data_pool.add_instance_location(esef_filing_root=esef_filing_root, filename=filename, attach_taxonomy=True)



