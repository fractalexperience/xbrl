```python

from openesef.base.pool import Pool

import importlib
from openesef.edgar.edgar import EG_LOCAL
from openesef.edgar.stock import Stock


#import openesef.edgar.edgar; importlib.reload(openesef.edgar.edgar); from openesef.edgar.edgar import *
#import openesef.edgar.stock; importlib.reload(openesef.edgar.stock); from openesef.edgar.stock import *; from openesef.edgar.stock import Stock
#import openesef.edgar.filing; importlib.reload(openesef.edgar.filing); from openesef.edgar.filing import *; from openesef.edgar.filing import Filing
egl = EG_LOCAL('/text/edgar')
egl.symbols_data_path


stock = Stock('AAPL', egl = egl); #self = stock
filing = stock.get_filing(period='annual', year=2023)

len(filing.documents)

for key, doc in filing.documents.items():
    print()
    print(key, type(doc), doc.sequence, doc.type, doc.filename, len(doc.doc_text.data))
```

Output: 

```
aapl-20230930.htm <class 'openesef.edgar.document.Document'> 1 10-K aapl-20230930.htm 1558938
a10-kexhibit4109302023.htm <class 'openesef.edgar.document.Document'> 2 EX-4.1 a10-kexhibit4109302023.htm 121845
a10-kexhibit21109302023.htm <class 'openesef.edgar.document.Document'> 3 EX-21.1 a10-kexhibit21109302023.htm 11105
a10-kexhibit23109302023.htm <class 'openesef.edgar.document.Document'> 4 EX-23.1 a10-kexhibit23109302023.htm 5327
a10-kexhibit31109302023.htm <class 'openesef.edgar.document.Document'> 5 EX-31.1 a10-kexhibit31109302023.htm 10383
a10-kexhibit31209302023.htm <class 'openesef.edgar.document.Document'> 6 EX-31.2 a10-kexhibit31209302023.htm 10419
a10-kexhibit32109302023.htm <class 'openesef.edgar.document.Document'> 7 EX-32.1 a10-kexhibit32109302023.htm 8232
aapl-20230930.xsd <class 'openesef.edgar.document.Document'> 8 EX-101.SCH aapl-20230930.xsd 59744
aapl-20230930_cal.xml <class 'openesef.edgar.document.Document'> 9 EX-101.CAL aapl-20230930_cal.xml 155407
aapl-20230930_def.xml <class 'openesef.edgar.document.Document'> 10 EX-101.DEF aapl-20230930_def.xml 233485
aapl-20230930_lab.xml <class 'openesef.edgar.document.Document'> 11 EX-101.LAB aapl-20230930_lab.xml 854285
aapl-20230930_pre.xml <class 'openesef.edgar.document.Document'> 12 EX-101.PRE aapl-20230930_pre.xml 516240
aapl-20230930_g1.jpg <class 'openesef.edgar.document.Document'> 13 GRAPHIC aapl-20230930_g1.jpg 15067
aapl-20230930_g2.jpg <class 'openesef.edgar.document.Document'> 14 GRAPHIC aapl-20230930_g2.jpg 201856
R1.htm <class 'openesef.edgar.document.Document'> 15 XML R1.htm 93178
R2.htm <class 'openesef.edgar.document.Document'> 16 XML R2.htm 7694
R3.htm <class 'openesef.edgar.document.Document'> 17 XML R3.htm 74846
R4.htm <class 'openesef.edgar.document.Document'> 18 XML R4.htm 43545
R5.htm <class 'openesef.edgar.document.Document'> 19 XML R5.htm 119109
R6.htm <class 'openesef.edgar.document.Document'> 20 XML R6.htm 12018
R7.htm <class 'openesef.edgar.document.Document'> 21 XML R7.htm 49964
R8.htm <class 'openesef.edgar.document.Document'> 22 XML R8.htm 88288
R9.htm <class 'openesef.edgar.document.Document'> 23 XML R9.htm 10295
R10.htm <class 'openesef.edgar.document.Document'> 24 XML R10.htm 28488
R11.htm <class 'openesef.edgar.document.Document'> 25 XML R11.htm 19735
R12.htm <class 'openesef.edgar.document.Document'> 26 XML R12.htm 151504
R13.htm <class 'openesef.edgar.document.Document'> 27 XML R13.htm 14327
R14.htm <class 'openesef.edgar.document.Document'> 28 XML R14.htm 30400
R15.htm <class 'openesef.edgar.document.Document'> 29 XML R15.htm 84856
R16.htm <class 'openesef.edgar.document.Document'> 30 XML R16.htm 81083
R17.htm <class 'openesef.edgar.document.Document'> 31 XML R17.htm 49826
R18.htm <class 'openesef.edgar.document.Document'> 32 XML R18.htm 17914
R19.htm <class 'openesef.edgar.document.Document'> 33 XML R19.htm 36207
R20.htm <class 'openesef.edgar.document.Document'> 34 XML R20.htm 13955
R21.htm <class 'openesef.edgar.document.Document'> 35 XML R21.htm 64339
R22.htm <class 'openesef.edgar.document.Document'> 36 XML R22.htm 15092
R23.htm <class 'openesef.edgar.document.Document'> 37 XML R23.htm 22940
R24.htm <class 'openesef.edgar.document.Document'> 38 XML R24.htm 50648
R25.htm <class 'openesef.edgar.document.Document'> 39 XML R25.htm 18208
R26.htm <class 'openesef.edgar.document.Document'> 40 XML R26.htm 18965
R27.htm <class 'openesef.edgar.document.Document'> 41 XML R27.htm 151413
R28.htm <class 'openesef.edgar.document.Document'> 42 XML R28.htm 13342
R29.htm <class 'openesef.edgar.document.Document'> 43 XML R29.htm 34859
R30.htm <class 'openesef.edgar.document.Document'> 44 XML R30.htm 83925
R31.htm <class 'openesef.edgar.document.Document'> 45 XML R31.htm 59030
R32.htm <class 'openesef.edgar.document.Document'> 46 XML R32.htm 49705
R33.htm <class 'openesef.edgar.document.Document'> 47 XML R33.htm 11806
R34.htm <class 'openesef.edgar.document.Document'> 48 XML R34.htm 33325
R35.htm <class 'openesef.edgar.document.Document'> 49 XML R35.htm 9341
R36.htm <class 'openesef.edgar.document.Document'> 50 XML R36.htm 64554
R37.htm <class 'openesef.edgar.document.Document'> 51 XML R37.htm 8966
R38.htm <class 'openesef.edgar.document.Document'> 52 XML R38.htm 20274
R39.htm <class 'openesef.edgar.document.Document'> 53 XML R39.htm 15851
R40.htm <class 'openesef.edgar.document.Document'> 54 XML R40.htm 37173
R41.htm <class 'openesef.edgar.document.Document'> 55 XML R41.htm 6613
R42.htm <class 'openesef.edgar.document.Document'> 56 XML R42.htm 93697
R43.htm <class 'openesef.edgar.document.Document'> 57 XML R43.htm 11996
R44.htm <class 'openesef.edgar.document.Document'> 58 XML R44.htm 36138
R45.htm <class 'openesef.edgar.document.Document'> 59 XML R45.htm 11205
R46.htm <class 'openesef.edgar.document.Document'> 60 XML R46.htm 24705
R47.htm <class 'openesef.edgar.document.Document'> 61 XML R47.htm 10886
R48.htm <class 'openesef.edgar.document.Document'> 62 XML R48.htm 17160
R49.htm <class 'openesef.edgar.document.Document'> 63 XML R49.htm 4783
R50.htm <class 'openesef.edgar.document.Document'> 64 XML R50.htm 8213
R51.htm <class 'openesef.edgar.document.Document'> 65 XML R51.htm 8855
R52.htm <class 'openesef.edgar.document.Document'> 66 XML R52.htm 8748
R53.htm <class 'openesef.edgar.document.Document'> 67 XML R53.htm 12409
R54.htm <class 'openesef.edgar.document.Document'> 68 XML R54.htm 32214
R55.htm <class 'openesef.edgar.document.Document'> 69 XML R55.htm 30338
R56.htm <class 'openesef.edgar.document.Document'> 70 XML R56.htm 23892
R57.htm <class 'openesef.edgar.document.Document'> 71 XML R57.htm 39272
R58.htm <class 'openesef.edgar.document.Document'> 72 XML R58.htm 16021
R59.htm <class 'openesef.edgar.document.Document'> 73 XML R59.htm 24454
R60.htm <class 'openesef.edgar.document.Document'> 74 XML R60.htm 29653
R61.htm <class 'openesef.edgar.document.Document'> 75 XML R61.htm 57467
R62.htm <class 'openesef.edgar.document.Document'> 76 XML R62.htm 23686
R63.htm <class 'openesef.edgar.document.Document'> 77 XML R63.htm 15651
R64.htm <class 'openesef.edgar.document.Document'> 78 XML R64.htm 45088
R65.htm <class 'openesef.edgar.document.Document'> 79 XML R65.htm 21424
R66.htm <class 'openesef.edgar.document.Document'> 80 XML R66.htm 7983
R67.htm <class 'openesef.edgar.document.Document'> 81 XML R67.htm 14392
R68.htm <class 'openesef.edgar.document.Document'> 82 XML R68.htm 33975
R69.htm <class 'openesef.edgar.document.Document'> 83 XML R69.htm 29520
R70.htm <class 'openesef.edgar.document.Document'> 84 XML R70.htm 6992
R71.htm <class 'openesef.edgar.document.Document'> 85 XML R71.htm 17170
R72.htm <class 'openesef.edgar.document.Document'> 86 XML R72.htm 23168
R73.htm <class 'openesef.edgar.document.Document'> 87 XML R73.htm 17798
R74.htm <class 'openesef.edgar.document.Document'> 88 XML R74.htm 14230
R75.htm <class 'openesef.edgar.document.Document'> 89 XML R75.htm 10562
aapl-20230930_htm.xml <class 'openesef.edgar.document.Document'> 90 XML aapl-20230930_htm.xml 1
Financial_Report.xlsx <class 'openesef.edgar.document.Document'> 91 EXCEL Financial_Report.xlsx 151245
Show.js <class 'openesef.edgar.document.Document'> 92 XML Show.js 972
report.css <class 'openesef.edgar.document.Document'> 93 XML report.css 2685
FilingSummary.xml <class 'openesef.edgar.document.Document'> 94 XML FilingSummary.xml 1
MetaLinks.json <class 'openesef.edgar.document.Document'> 97 JSON MetaLinks.json 1003982
0000320193-23-000106-xbrl.zip <class 'openesef.edgar.document.Document'> 98 ZIP 0000320193-23-000106-xbrl.zip 556106