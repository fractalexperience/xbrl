"""

"""

from openesef.base.pool import Pool

import importlib
from openesef.edgar.edgar import EG_LOCAL
from openesef.edgar.stock import Stock
import re
from lxml import etree as lxml_etree
import tempfile
from io import StringIO, BytesIO

#import openesef.edgar.edgar; importlib.reload(openesef.edgar.edgar); from openesef.edgar.edgar import *
#import openesef.edgar.stock; importlib.reload(openesef.edgar.stock); from openesef.edgar.stock import *; from openesef.edgar.stock import Stock
#import openesef.edgar.filing; importlib.reload(openesef.edgar.filing); from openesef.edgar.filing import *; from openesef.edgar.filing import Filing
egl = EG_LOCAL('/text/edgar')
egl.symbols_data_path


stock = Stock('AAPL', egl = egl); #self = stock
filing = stock.get_filing(period='annual', year=2018) #self = filing

# len(filing.documents)
# # print the xbrl files
for key, filename in filing.xbrl_files.items():
    print(f"{key}, {filing.documents[filename].type}, {filename}")


data_pool = Pool(); #self = data_pool

if filing.xbrl_files.get("xml"):
    instance_str = filing.documents[filing.xbrl_files.get("xml")].doc_text.data
    instance_str = re.sub(r'^<XBRL>', '', instance_str)
    instance_str = re.sub(r'</XBRL>$', '', instance_str)
    instance_str = re.sub(r"\n", '', instance_str)
    instance_byte = instance_str.encode('utf-8')
    #instance_tree = lxml_etree.fromstring(instance_byte)
    #root = instance_tree.getroot()
    instance_io = BytesIO(instance_byte)
    instance_tree = lxml_etree.parse(instance_io)
    root = instance_tree.getroot()
    xid = data_pool.add_instance_element(root, key="memory_instance", attach_taxonomy=False)
    for linkbase_type in ["sch", "cal", "def", "lab", "pre"]:
        #linkbase_type = "pre"
        if filing.xbrl_files.get(linkbase_type):
            linkbase_str = filing.documents[filing.xbrl_files.get(linkbase_type)].doc_text.data
            linkbase_str = re.sub(r'^<LINKBASE>', '', linkbase_str)
            linkbase_str = re.sub(r'</LINKBASE>$', '', linkbase_str)
            linkbase_str = re.sub(r"\n", '', linkbase_str)
            linkbase_byte = linkbase_str.encode('utf-8')
            linkbase_io = BytesIO(linkbase_byte)
