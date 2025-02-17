"""

"""

from openesef.base.pool import Pool

import importlib
from openesef.edgar.edgar import EG_LOCAL
from openesef.edgar.stock import Stock
import re

import tempfile
from io import StringIO

#import openesef.edgar.edgar; importlib.reload(openesef.edgar.edgar); from openesef.edgar.edgar import *
#import openesef.edgar.stock; importlib.reload(openesef.edgar.stock); from openesef.edgar.stock import *; from openesef.edgar.stock import Stock
#import openesef.edgar.filing; importlib.reload(openesef.edgar.filing); from openesef.edgar.filing import *; from openesef.edgar.filing import Filing
egl = EG_LOCAL('/text/edgar')
egl.symbols_data_path


stock = Stock('AAPL', egl = egl); #self = stock
filing = stock.get_filing(period='annual', year=2023)

len(filing.documents)

for key, doc in filing.documents.items():
    if re.search(r'xml|xhtml', doc.filename, flags=re.IGNORECASE):    
        print()
        print(doc.sequence, key, doc.type, doc.filename, len(doc.doc_text.data))
        print(doc.description)

