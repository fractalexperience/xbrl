I was trying to modify the code from `xbrl` package to make it work for ESEF. 
Please show me the modified code in `pool.py` and `taxonomy.py` to resolve the endless loop.

The issue is that, unlike xbrl @ US-SEC-EDGAR, ESEF files have a folder structure, and the schema references are relative to the instance file, not the taxonomy folder. Example:
```
pwd                    
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls
(base) mbp16@Reeyarns-MBP sap_Jahres-_2023-04-05_esef_xmls % ls -R sap-2022-12-31-DE
META-INF	reports		www.sap.com

sap-2022-12-31-DE/META-INF:
catalog.xml		taxonomyPackage.xml

sap-2022-12-31-DE/reports:
sap-2022-12-31-DE.xhtml

sap-2022-12-31-DE/www.sap.com:
sap-2022-12-31.xsd		sap-2022-12-31_cal.xml		sap-2022-12-31_def.xml		sap-2022-12-31_lab-de.xml	sap-2022-12-31_lab-en.xml	sap-2022-12-31_pre.xml
```
I have tried to modify the code to handle ESEF by adding the `esef_filing_root` parameter and passing it around.
I added the `esef_filing_root` parameter to the following files:
taxonomy/taxonomy.py
base/pool.py
base/fbase.py
taxonomy/tpack.py
taxonomy/linkbase.py
taxonomy/schema.py
taxonomy/taxonomy.py
..


Question: Does the current code not handling the `base` and `esef_filing_root` parameters correctly? 

Log showing the base and esef_filing_root being mishandled:  
```
(base) mbp16@Reeyarns-MBP code_fse % python3 try_sap2022.py
2025-02-09 14:37:25,571 - xbrl.base.pool - INFO - 

Initializing Pool with cache_folder=../data/xbrl_cache, output_folder=None
INFO:xbrl.base.pool:

Initializing Pool with cache_folder=../data/xbrl_cache, output_folder=None
2025-02-09 14:37:25,593 - xbrl.base.pool - WARNING - Schema file not found: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/file:/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
WARNING:xbrl.base.pool:Schema file not found: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/file:/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:25,593 - xbrl.base.pool - WARNING - Could not resolve schema reference: file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
WARNING:xbrl.base.pool:Could not resolve schema reference: file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,104 - xbrl.base.pool - DEBUG - Resolving schema reference: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolving schema reference: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,104 - xbrl.base.pool - INFO - 
\Calling add_taxonomy(...):
INFO:xbrl.base.pool:
\Calling add_taxonomy(...):
2025-02-09 14:37:26,104 - xbrl.base.pool - INFO - Processing 1 entry points
INFO:xbrl.base.pool:Processing 1 entry points
2025-02-09 14:37:26,104 - xbrl.base.pool - DEBUG - Added packaged entry points for file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Added packaged entry points for file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,104 - xbrl.base.pool - DEBUG - Generated taxonomy key: file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Generated taxonomy key: file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,104 - xbrl.base.pool - DEBUG - Loading new taxonomy
DEBUG:xbrl.base.pool:Loading new taxonomy
2025-02-09 14:37:26,104 - xbrl.taxonomy.taxonomy - DEBUG - Taxonomy.load(): Loading file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd with self.esef_filing_root=/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.taxonomy:Taxonomy.load(): Loading file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd with self.esef_filing_root=/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,104 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd 
from base: 

 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd 
from base: 

 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,104 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,105 - xbrl.base.pool - DEBUG - Resolved URL: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,105 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,105 - xbrl.base.pool - DEBUG - Resolved URL: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,105 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,105 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,105 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml
2025-02-09 14:37:26,105 - xbrl.base.pool - DEBUG - Loading linkbase: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml
DEBUG:xbrl.base.pool:Loading linkbase: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml
2025-02-09 14:37:26,106 - xbrl.taxonomy.linkbase - DEBUG - Added reference: http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,106 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,106 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,106 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,106 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: http://www.xbrl.org/lrr/role/negated-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: http://www.xbrl.org/lrr/role/net-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: http://www.xbrl.org/lrr/role/net-2009-12-16.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,107 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,107 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,108 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,108 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,108 - xbrl.base.pool - DEBUG - Checking count of exceptions: 1
DEBUG:xbrl.base.pool:Checking count of exceptions: 1
2025-02-09 14:37:26,108 - xbrl.base.pool - ERROR - Failed to load resource 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml 
XmlElementBase.__init__() got an unexpected keyword argument 'esef_filing_root'
ERROR:xbrl.base.pool:Failed to load resource 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml 
XmlElementBase.__init__() got an unexpected keyword argument 'esef_filing_root'
Traceback (most recent call last):
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/pool.py", line 605, in add_reference
    lb = self.linkbases.get(resolved_href, linkbase.Linkbase(resolved_href, self, esef_filing_root=esef_filing_root)) # Use resolved_href
                                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/taxonomy/linkbase.py", line 44, in __init__
    super().__init__(resolved_location, container_pool, parsers, root, esef_filing_root)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/fbase.py", line 47, in __init__
    super().__init__(root, parsers)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/ebase.py", line 15, in __init__
    self.load(e)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/ebase.py", line 24, in load
    method(e)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/taxonomy/linkbase.py", line 53, in l_linkbase
    self.l_children(e)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/ebase.py", line 28, in l_children
    self.load(e2)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/ebase.py", line 24, in load
    method(e)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/taxonomy/linkbase.py", line 56, in l_link
    xl = xlink.XLink(e, self, esef_filing_root=self.esef_filing_root)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/taxonomy/xlink.py", line 87, in __init__
    super(XLink, self).__init__(e, parsers, esef_filing_root = esef_filing_root)
TypeError: XmlElementBase.__init__() got an unexpected keyword argument 'esef_filing_root'
2025-02-09 14:37:26,108 - xbrl.taxonomy.schema - DEBUG - Added reference: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.schema:Added reference: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_pre.xml to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,108 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - Loading linkbase: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml
DEBUG:xbrl.base.pool:Loading linkbase: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml
2025-02-09 14:37:26,109 - xbrl.taxonomy.linkbase - DEBUG - Added reference: http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,109 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,109 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - 

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:

Calling add_reference(...): 
sap-2022-12-31.xsd 
from base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
 and esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - ==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.base.pool:==
  Calling _resolve_url(...): 
href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com, 
esef_filing_root: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
DEBUG:xbrl.base.pool:Resolved URL (esef_filing_root): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd
2025-02-09 14:37:26,110 - xbrl.taxonomy.linkbase - DEBUG - Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.linkbase:Added reference: sap-2022-12-31.xsd to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,110 - xbrl.base.pool - DEBUG - Checking count of exceptions: 2
DEBUG:xbrl.base.pool:Checking count of exceptions: 2
2025-02-09 14:37:26,110 - xbrl.base.pool - ERROR - Failed to load resource 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml 
XmlElementBase.__init__() got an unexpected keyword argument 'esef_filing_root'
ERROR:xbrl.base.pool:Failed to load resource 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml 
XmlElementBase.__init__() got an unexpected keyword argument 'esef_filing_root'
Traceback (most recent call last):
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/pool.py", line 605, in add_reference
    lb = self.linkbases.get(resolved_href, linkbase.Linkbase(resolved_href, self, esef_filing_root=esef_filing_root)) # Use resolved_href
                                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/taxonomy/linkbase.py", line 44, in __init__
    super().__init__(resolved_location, container_pool, parsers, root, esef_filing_root)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/fbase.py", line 47, in __init__
    super().__init__(root, parsers)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/ebase.py", line 15, in __init__
    self.load(e)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/ebase.py", line 24, in load
    method(e)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/taxonomy/linkbase.py", line 53, in l_linkbase
    self.l_children(e)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/ebase.py", line 28, in l_children
    self.load(e2)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/base/ebase.py", line 24, in load
    method(e)
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/taxonomy/linkbase.py", line 56, in l_link
    xl = xlink.XLink(e, self, esef_filing_root=self.esef_filing_root)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mbp16/Dropbox/sciebo/WebScraping+ESEF_Paper/Research/code_fse/xbrl/taxonomy/xlink.py", line 87, in __init__
    super(XLink, self).__init__(e, parsers, esef_filing_root = esef_filing_root)
TypeError: XmlElementBase.__init__() got an unexpected keyword argument 'esef_filing_root'
2025-02-09 14:37:26,111 - xbrl.taxonomy.schema - DEBUG - Added reference: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
DEBUG:xbrl.taxonomy.schema:Added reference: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31_cal.xml to /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com with esef_filing_root: /Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/
2025-02-09 14:37:26,111 - xbrl.base.pool - DEBUG - 


```

Existing code: ```"""
XBRL Pool Module Documentation

The Pool class serves as a central repository for managing XBRL taxonomies, instances, and related resources.
It inherits from Resolver class and provides functionality for loading, caching, and managing XBRL documents.

Key Features:
1. Taxonomy Management
   - Loading and caching taxonomies
   - Managing taxonomy packages
   - Handling multiple entry points

2. Instance Document Management
   - Loading instance documents from files, archives, or XML elements
   - Managing relationships between instances and taxonomies

3. Resource Management
   - Caching and resolving schemas and linkbases
   - Managing taxonomy packages
   - Handling alternative locations for resources

Class Attributes:
    taxonomies (dict): Stores loaded taxonomies
    current_taxonomy (Taxonomy): Reference to the currently active taxonomy
    current_taxonomy_hash (str): Hash identifier for the current taxonomy
    discovered (dict): Tracks discovered resources to prevent circular references
    schemas (dict): Stores loaded schema documents
    linkbases (dict): Stores loaded linkbase documents
    instances (dict): Stores loaded instance documents
    alt_locations (dict): Maps URLs to alternative locations
    packaged_entrypoints (dict): Maps entry points to package locations
    packaged_locations (dict): Maps locations to package contents
    active_packages (dict): Currently opened taxonomy packages
    active_file_archive (ZipFile): Currently opened archive file
"""

import os, zipfile, functools
from lxml import etree as lxml
from xbrl.base import resolver, util
from xbrl.taxonomy import taxonomy, schema, tpack, linkbase
from xbrl.instance import instance
import gzip
from xbrl.base import const, util
import os

import zipfile
import functools

import time
from typing import Optional, Dict, List, Union, Tuple
import traceback
import pathlib

import re 
import urllib.parse
from xbrl.base import util

import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a handler (e.g., StreamHandler for console output)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Create a formatter
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

# Set the formatter on the handler (not the logger)
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)



class Pool(resolver.Resolver):
    def __init__(self, cache_folder=None, output_folder=None, alt_locations=None, esef_filing_root=None):
        """
        Initializes a new Pool instance
        Args:
            cache_folder (str): Path to cache directory
            output_folder (str): Path to output directory
            alt_locations (dict): Alternative URL mappings        
            esef_filing_root (str): Path to location of the ESEF structure
        """
        logger.info(f"\n\nInitializing Pool with cache_folder={cache_folder}, output_folder={output_folder}")

        super().__init__(cache_folder, output_folder)
        self.taxonomies = {}
        self.current_taxonomy = None
        self.current_taxonomy_hash = None
        self.discovered = {}
        self.schemas = {}
        self.linkbases = {}
        self.instances = {}
        self.count_exceptions = 0
        # Alternative locations. If set, this is used to resolve Qeb references to alternative (existing) URLs. 
        self.alt_locations = alt_locations
        # Index of all packages in the cache/taxonomy_packages folder by entrypoint 
        self.packaged_entrypoints = {}
        self.packaged_locations = None
        # Currently opened taxonomy packages 
        self.active_packages = {}
        # Currently opened archive, where files can be read from - optional.
        self.active_file_archive = None
        self.esef_filing_root = esef_filing_root

    def __str__(self):
        return self.info()

    def check_count_exceptions(self):
        logger.debug(f"Checking count of exceptions: {self.count_exceptions}")
        if self.count_exceptions > 8:
            logger.warning(f"Number of exceptions: {self.count_exceptions}")
            raise Exception(f"Number of exceptions: {self.count_exceptions}")

    def __repr__(self):
        return self.info()

    def info(self):
        return '\n'.join([
            f'Taxonomies: {len(self.taxonomies)}',
            f'Instance documents: {len(self.instances)}',
            f'Taxonomy schemas: {len(self.schemas)}',
            f'Taxonomy linkbases: {len(self.linkbases)}'])

    def index_packages(self):
        """ Index the content of taxonomy packages found in cache/taxonomies/ """
        package_files = [os.path.join(r, file) for r, d, f in
                         os.walk(self.taxonomies_folder) for file in f if file.endswith('.zip')]
        for pf in package_files:
            self.index_package(tpack.TaxonomyPackage(pf))

    def index_package(self, package):
        """ Index the content of a taxonomy package """
        for ep in package.entrypoints:
            eps = ep.Urls
            for path in eps:
                self.packaged_entrypoints[path] = package.location

    def add_instance_location(self, esef_filing_root, filename, key=None, attach_taxonomy=True):
        """Loads an instance document from a file location within an ESEF structure."""

        instance_location = os.path.join(esef_filing_root, filename)
        instance_location = os.path.abspath(instance_location)

        if key is None:
            key = instance_location

        try:
            parser = lxml.XMLParser(huge_tree=True)
            doc = lxml.parse(instance_location, parser=parser)
            root = doc.getroot()

            # Resolve schemaRefs relative to the *esef_filing_root*, not the instance file
            self.resolve_and_update_schema_refs(root, esef_filing_root)

            # Write back the modified XML
            doc.write(instance_location)

            xid = instance.Instance(location=instance_location, container_pool=self)
            #self.add_instance(xid, key, attach_taxonomy)
            self.add_instance(xid, key, attach_taxonomy, esef_filing_root) # Pass esef_filing_root

            return xid

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            self.count_exceptions += 1
            self.check_count_exceptions()
            return None

    def resolve_and_update_schema_refs(self, root, esef_filing_root):
        """Resolves and updates schemaRef elements within an ESEF context."""
        nsmap = {'link': const.NS_LINK}
        schema_refs = root.findall(".//link:schemaRef", namespaces=nsmap)

        resolved_schemas = set()  # Keep track of resolved schemas

        for schema_ref in schema_refs:
            href = schema_ref.get(f'{{{const.NS_XLINK}}}href')
            if href:
                resolved_href = self.resolve_esef_schema_ref(href, esef_filing_root)
                if resolved_href and resolved_href not in resolved_schemas:
                    schema_ref.set(f'{{{const.NS_XLINK}}}href', resolved_href)
                    resolved_schemas.add(resolved_href)  # Add to the set of resolved schemas
                elif resolved_href in resolved_schemas:
                    logger.debug(f"Skipping already resolved schema: {resolved_href}") # Skip if already resolved
                else:
                    logger.warning(f"Could not resolve schema reference: {href}")

    def resolve_esef_schema_ref(self, href, esef_filing_root):
        """Resolves schema references within an ESEF structure."""

        resolved_path = os.path.abspath(os.path.join(esef_filing_root, href))
        if os.path.isfile(resolved_path):
            return pathlib.Path(resolved_path).as_uri()
        else:
            logger.warning(f"Schema file not found: {resolved_path}")
            return None

    def add_instance_location_depreciated (self, esef_filing_root, filename, key=None, attach_taxonomy=True):
        """Loads an instance document from a file location.

        Args:
            esef_filing_root (str): Directory path to the instance file.
            filename (str): The name of the instance file.
            key (str, optional): Optional identifier. Defaults to None.
            attach_taxonomy (bool, optional): Whether to load associated taxonomy. Defaults to True.

        Returns:
            Instance: The loaded instance document, or None if an error occurs.
        """

        location = os.path.join(esef_filing_root, filename)  # Combine path and filename
        location = os.path.abspath(location)
        logger.info(f"\n\nAdding instance from location: {location}")

        if key is None:
            key = location  # Or another suitable default

        try:
            parser = lxml.XMLParser(huge_tree=True)
            doc = lxml.parse(location, parser=parser)
            root = doc.getroot()

            nsmap = {'link': const.NS_LINK}
            schema_refs = root.findall(".//link:schemaRef", namespaces=nsmap)
            logger.info(f"Found {len(schema_refs)} schema references")

            for schema_ref in schema_refs:
                href = schema_ref.get(f'{{{const.NS_XLINK}}}href')
                if href:
                    resolved_href = self.resolve_schema_ref(href, location)
                    if resolved_href:
                        if not resolved_href.startswith(('http://', 'https://', 'file://')):
                            resolved_href = os.path.abspath(resolved_href)
                        if not resolved_href.startswith(('http://', 'https://')):
                            resolved_href_removeprefix = resolved_href.replace('file://', '')
                            resolved_href = pathlib.Path(resolved_href_removeprefix).as_uri()
                        schema_ref.set(f'{{{const.NS_XLINK}}}href', resolved_href)
                        logger.debug(f"Resolved schema reference: \n{resolved_href}")
                    else:
                        logger.warning(f"Could not resolve schema reference: {href}")

            # Write back the modified XML if any schema references were updated
            if schema_refs:  # Only write if changes were made
                doc.write(location)
                logger.debug("Successfully wrote back modified XML")

            xid = instance.Instance(location=location, container_pool=self)
            self.add_instance(xid, key, attach_taxonomy)
            logger.info(f"Successfully added instance from {location}")
            return xid

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            traceback.print_exc(limit=10)
            self.count_exceptions += 1
            self.check_count_exceptions()
            return None

    def add_instance_archive(self, archive_location, filename, key=None, attach_taxonomy=False):
        """
        Adds an XBRL instance from an archive file (supports both .zip and .gzip formats)
        
        Args:
            archive_location (str): Path to the archive file (.zip or .gzip)
            filename (str): Name of the file within the archive (for zip) or the original filename (for gzip)
            key (str, optional): Key to identify the instance. Defaults to None.
            attach_taxonomy (bool, optional): Whether to attach taxonomy. Defaults to False.
        
        Returns:
            Instance: The loaded XBRL instance or None if loading fails
        
        Raises:
            FileNotFoundError: If archive_location doesn't exist
            ValueError: If archive format is not supported
        """
        if not os.path.exists(archive_location):
            raise FileNotFoundError(f"Archive not found: {archive_location}")

        # Handle GZIP files
        if archive_location.endswith('.gzip'):
            try:
                with gzip.open(archive_location, 'rb') as gf:
                    content = gf.read()
                    root = lxml.XML(content)
                    return self.add_instance_element(
                        root,
                        filename if key is None else key,
                        attach_taxonomy
                    )
            except Exception as e:
                self.count_exceptions += 1
                self.check_count_exceptions()

                raise ValueError(f"Error processing gzip file: {str(e)}")

        # Handle ZIP files
        elif archive_location.endswith('.zip'):
            try:
                archive = zipfile.ZipFile(archive_location)
                zil = archive.infolist()
                xid_file = [f for f in zil if f.filename.endswith(filename)]
                
                if not xid_file:
                    raise ValueError(f"File {filename} not found in archive")
                    
                xid_file = xid_file[0]
                
                with archive.open(xid_file) as xf:
                    root = lxml.XML(xf.read())
                    return self.add_instance_element(
                        root,
                        xid_file if key is None else key,
                        attach_taxonomy
                    )
            except Exception as e:
                self.count_exceptions += 1
                self.check_count_exceptions()

                raise ValueError(f"Error processing zip file: {str(e)}")

        else:
            self.count_exceptions += 1
            self.check_count_exceptions()

            raise ValueError("Unsupported archive format. Use .zip or .gzip")
    
    def add_instance_element(self, e, key=None, attach_taxonomy=False):
        """
        Adds an instance document from an XML element
        Args:
            e (Element): XML element
            key (str): Optional identifier
            attach_taxonomy (bool): Whether to load associated taxonomy
        """
        xid = instance.Instance(container_pool=self, root=e)
        if key is None:
            key = e.tag
        self.add_instance(xid, key, attach_taxonomy)
        return xid

    #def add_instance(self, xid, key=None, attach_taxonomy=False):
    def add_instance(self, xid, key=None, attach_taxonomy=False, esef_filing_root=None): # Add esef_filing_root    
        """
        Adds an instance document to the pool
        Args:
            xid (Instance): The instance document to add
            key (str): Optional identifier
            attach_taxonomy (bool): Whether to load associated taxonomy
        """
        if key is None:
            key = xid.location_ixbrl
        self.instances[key] = xid

        if attach_taxonomy and xid.xbrl is not None:
            # entry_points = [ref if ref.startswith('http') else self.resolve_schema_ref(ref, xid.location) # Use xid.location
            #                 for ref in xid.xbrl.schema_refs]

            # entry_points = [pathlib.Path(ep).as_uri() if os.path.isfile(ep) else ep  # Check if it's a file
            #                 for ep in entry_points]
            entry_points = [ref if ref.startswith('http') else self.resolve_schema_ref(ref, xid.location)
                            for ref in xid.xbrl.schema_refs]
            entry_points = [pathlib.Path(ep).as_uri() if os.path.isfile(ep) else ep for ep in entry_points]

            tax = self.add_taxonomy(entry_points, esef_filing_root) # Pass esef_filing_root
            xid.taxonomy = tax

    def add_taxonomy(self, entry_points, esef_filing_root=None): # Add esef_filing_root
        """
        Adds a taxonomy from a list of entry points
        Args:
            entry_points (list): List of entry points
        Returns:
            Taxonomy: The loaded taxonomy object
        """
        logger.info("\n\Calling add_taxonomy(...):")
        ep_list = entry_points if isinstance(entry_points, list) else [entry_points]
        logger.info(f"Processing {len(ep_list)} entry points")

        # self.packaged_locations = {}
        for ep in ep_list:
            # if self.active_file_archive and ep in self.active_file_archive.namelist():
            #     self.packaged_locations[ep] = (self.active_file_archive, ep)
            # else:
            # For ESEF, try to resolve relative to esef_filing_root first
            if not ep.startswith(('http://', 'https://', 'file://')):
                potential_path = os.path.join(esef_filing_root, ep)
                if os.path.exists(potential_path):
                    ep = pathlib.Path(potential_path).as_uri()            
            
            self.add_packaged_entrypoints(ep) 
            logger.debug(f"Added packaged entry points for {ep}")

        key = ','.join(entry_points)
        logger.debug(f"Generated taxonomy key: {key}")
        if key in self.taxonomies:
            logger.debug(f"Taxonomy already loaded: {key}")
            return self.taxonomies[key]  # Previously loaded
        
        logger.debug(f"Loading new taxonomy")
        taxonomy.Taxonomy(ep_list, self, esef_filing_root=esef_filing_root)  # Sets the new taxonomy as current
        self.taxonomies[key] = self.current_taxonomy
        self.packaged_locations = None
        return self.current_taxonomy

    def add_packaged_entrypoints(self, ep): 
        """
        Adds packaged entry points
        Args:
            ep (str): Entry point
        Returns: None
        """
        pf = self.packaged_entrypoints.get(ep)
        if not pf:
            return  # Not found
        pck = self.active_packages.get(pf, None)
        if pck is None:
            pck = tpack.TaxonomyPackage(pf)
            pck.compile()
        self.index_package_files(pck)

    def index_package_files(self, pck):
        """
        Indexes files in a taxonomy package
        Args:
            pck (TaxonomyPackage): The taxonomy package object
        Returns: None
        """
        if self.packaged_locations is None:
            self.packaged_locations = {}
        for pf in pck.files.items():
            self.packaged_locations[pf[0]] = (pck, pf[1])  # A tuple

    def cache_package(self, location, esef_filing_root=None):
        """ 
        Stores a taxonomy package from a Web location to local taxonomy package repository 
        Args:
            location (str): Location of taxonomy package
        Returns:
            TaxonomyPackage: The loaded taxonomy package object
        """
        package = tpack.TaxonomyPackage(location, self.taxonomies_folder, esef_filing_root=esef_filing_root)
        self.index_packages()
        return package

    def _is_esef_package(self, package):
        """
        Checks if the given package is an ESEF taxonomy package
        Args:
            package: The taxonomy package to check
        Returns:
            bool: True if it's an ESEF package, False otherwise
        """
        # Check for typical ESEF package indicators
        if hasattr(package, 'meta_inf') and package.meta_inf:
            # Check for ESEF-specific metadata in taxonomyPackage.xml
            if hasattr(package.meta_inf, 'taxonomy_package'):
                meta = package.meta_inf.taxonomy_package
                # Check for ESEF identifiers in the metadata
                if any('esef' in str(identifier).lower() for identifier in meta.get('identifier', [])):
                    return True
        
        # Check for typical ESEF folder structure
        if hasattr(package, 'files'):
            file_paths = package.files.keys()
            has_reports = any('reports' in path.lower() for path in file_paths)
            has_taxonomy = any('taxonomy' in path.lower() for path in file_paths)
            if has_reports and has_taxonomy:
                return True
        
        return False    
    
    def add_package(self, location, esef_filing_root = None):
        """
        Adds a taxonomy package provided in the location parameter, creates a taxonomy 
        using all entrypoints in the package and returns the taxonomy object.
        Args:
            location (str): Location of taxonomy package
        Returns:
            Taxonomy: The loaded taxonomy object
        """
        package = self.cache_package(location, esef_filing_root)
        self.active_packages[location] = package
        entry_points = [f for ep in package.entrypoints for f in ep.Urls]
        # If we have a esef_filing_root and this is an ESEF package, resolve entry points
        if esef_filing_root and self._is_esef_package(package):
            resolved_entry_points = []
            for ep in entry_points:
                if not ep.startswith(('http://', 'https://', 'file://')):
                    # Try to find the entry point in the ESEF structure
                    for root, _, files in os.walk(esef_filing_root):
                        if os.path.basename(ep) in files:
                            resolved_path = os.path.join(root, os.path.basename(ep))
                            resolved_ep = pathlib.Path(resolved_path).as_uri()
                            resolved_entry_points.append(resolved_ep)
                            break
                    else:
                        # If not found, keep original
                        resolved_entry_points.append(ep)
                else:
                    resolved_entry_points.append(ep)
            entry_points = resolved_entry_points

        tax = self.add_taxonomy(entry_points, esef_filing_root=esef_filing_root)
        return tax

    def add_reference(self, href, base, esef_filing_root=None): # Add esef_filing_root
        """

        Loads referenced schema or linkbase
        Args:
            href (str): Reference URL
            base (str): Base URL for relative references
        Returns: None

        Loads schema or linkbase depending on file type. TO IMPROVE!!! -- original comment
        """
        
        if href is None:
            return

        # Skip basic schema objects
        if any(domain in href for domain in ['http://xbrl.org', 'http://www.xbrl.org']):
            return
        
        if not esef_filing_root:
            logger.debug("No esef_filing_root provided, using self.esef_filing_root")
            esef_filing_root = self.esef_filing_root

        logger.debug(f"\n\nCalling add_reference(...): \n{href} \nfrom base: \n{base}\n and esef_filing_root: {esef_filing_root}")    

        if esef_filing_root:
            # Dynamically determine subfolders within the esef_filing_root
            subfolders = [d for d in os.listdir(esef_filing_root) if os.path.isdir(os.path.join(esef_filing_root, d))]

            for subfolder in subfolders:
                potential_base = os.path.join(esef_filing_root, subfolder)
                resolved_href = self._resolve_url(href, potential_base, esef_filing_root)

                if os.path.exists(resolved_href.replace("file://", "")): # Check if resolved path exists
                    base = potential_base # Use this base path
                    break # Stop searching after finding a valid base

        # Validate file extension
        allowed_extensions = ('xsd', 'xml', 'json')
        file_ext = href.split('.')[-1]
        if file_ext not in allowed_extensions:
            logger.warning(f"Skipping reference: Invalid file extension {file_ext}")
            return        


        # Handle alternative locations
        # Artificially replace the reference - only done for very specific purposes.
        if self.alt_locations and href in self.alt_locations:
            original_href = href
            href = self.alt_locations[href]
            logger.debug(f"Replaced href \n{original_href} \nwith alternative location \n{href}")            
            
        # Resolve URL # Generate unique key that includes the base path to prevent loops
        resolved_href = href
        if not href.startswith('http'):
            if esef_filing_root:
                # Try to resolve relative to esef_filing_root first
                potential_path = os.path.join(esef_filing_root, href)
                if os.path.exists(potential_path):
                    resolved_href = pathlib.Path(potential_path).as_uri()
                else:
                    # Fall back to base path resolution
                    resolved_href = self._resolve_url(href, base, esef_filing_root)

            # Create a unique key that includes both href and base to prevent loops
            key = f'{self.current_taxonomy_hash}_{resolved_href}_{base}'
            
            if key in self.discovered:
                return
                
            self.discovered[key] = False

        try:
            if resolved_href.endswith(".xsd"):
                #logger.debug(f"Loading schema: \n{resolved_href}")

                if resolved_href.startswith("file://"):
                    schema_path = re.sub("file://", "", resolved_href) # Remove file:// for schema.Schema
                else:
                    schema_path = resolved_href # Use the URL directly

                #logger.debug(f"schema_path: \n{schema_path}")

                sh = self.schemas.get(schema_path, schema.Schema(schema_path, self, esef_filing_root=esef_filing_root))
                self.current_taxonomy.attach_schema(schema_path, sh)
            else:
                logger.debug(f"Loading linkbase: \n{resolved_href}")
                # Remove file:// prefix if present
                if resolved_href.startswith("file://"):
                    resolved_href = re.sub("file://", "", resolved_href)

                lb = self.linkbases.get(resolved_href, linkbase.Linkbase(resolved_href, self, esef_filing_root=esef_filing_root)) # Use resolved_href
                self.current_taxonomy.attach_linkbase(resolved_href, lb) # Use resolved_href

        except OSError as e:
            self.count_exceptions += 1
            self.check_count_exceptions()

            logger.error(f"OSError Failed to load resource \n{href} \n{str(e)}")
            # Log the error but don't raise it to allow continued processing
            traceback.print_exc(limit=10)

        except Exception as e:
            self.count_exceptions += 1
            self.check_count_exceptions()

            logger.error(f"Failed to load resource \n{href} \n{str(e)}")
            traceback.print_exc(limit=10)

    @staticmethod
    def check_create_path(existing_path, part):
        new_path = os.path.join(existing_path, part)
        if not os.path.exists(new_path):
            os.mkdir(new_path)
        return new_path

    def save_output(self, content, filename):
        """
        Saves content to output directory
        Args:
            content (str): Content to save
            filename (str): Target filename
        Returns: None        
        """
        if os.path.sep in filename:
            functools.reduce(self.check_create_path, filename.split(os.path.sep)[:-1], self.output_folder)
        location = os.path.join(self.output_folder, filename)
        with open(location, 'wt', encoding="utf-8") as f:
            f.write(content)


    def _resolve_url(self, href: str, base: Optional[str], esef_filing_root: Optional[str] = None) -> str:
        """
        Resolves URLs, correctly handling relative paths and file URLs.
        Returns a file URL for local files and an absolute URL for remote resources.
        """
        logger.debug(f"==\n  Calling _resolve_url(...): \nhref: \n{href}, \nbase: \n{base}, \nesef_filing_root: \n{esef_filing_root}")

        if href.startswith(('http://', 'https://')):
            logger.debug(f"Resolved URL: \n{href}")
            return href
        elif href.startswith('file://'):
            logger.debug(f"Resolved URL: \n{href}")
            return href

        # Try to find the file in ESEF structure first
        if esef_filing_root :
            # First, try to find in www.company.com subdirectory
            esef_filing_root_parent = os.path.dirname(esef_filing_root)
            for root, _, files in os.walk(esef_filing_root_parent):
                if os.path.basename(href) in files:
                    resolved_path = os.path.join(root, os.path.basename(href))
                    
                    resolved = pathlib.Path(resolved_path).as_uri()
                    logger.debug(f"Resolved URL (esef_filing_root): \n{resolved}")
                    return resolved
                    
            # If not found in www subdirectory, try base directory
            if base:
                resolved_path = os.path.abspath(os.path.join(os.path.dirname(base), href))
                if os.path.isfile(resolved_path):
                    resolved = pathlib.Path(resolved_path).as_uri()
                    logger.debug(f"Resolved URL (ESEF base): \n{resolved}")
                    return resolved

        if base is None or not base.strip():
            if os.path.isfile(href):
                resolve_result = pathlib.Path(os.path.abspath(href)).as_uri()
                logger.debug(f"Resolved URL: \n{href} to \n{resolve_result}")
                return resolve_result # Ensure absolute path
            else:  
                logger.debug(f"Resolved URL: \n{href}")
                ##return f"https://{href}" # Assume it's a remote URL and prepend https://
                return href # Don't assume https, could be a relative local path
        if base.startswith(('http://', 'https://')):
            resolved = urllib.parse.urljoin(base, href)
        elif base.startswith('file://') or base.startswith("/"):
            try:  # Use try-except to handle potential parsing errors
                base_path = urllib.parse.urlparse(base).path
                resolved_path = os.path.abspath(os.path.join(os.path.dirname(base_path), href))
                resolved = pathlib.Path(resolved_path).as_uri()
            except ValueError: # Log the error and return the original href
                self.count_exceptions += 1
                self.check_count_exceptions()
                logger.error(f"Invalid base URL: {base}")
                return href # Or handle the error differently, e.g., raise an exception
        else:  # base is a local path
            resolved_path = os.path.abspath(os.path.join(os.path.dirname(base), href))
            resolved = pathlib.Path(resolved_path).as_uri()

        logger.debug(f"Resolved URL: \n{resolved}")
        return resolved

    def resolve_schema_ref(self, href, instance_path):
        """
        Resolves schema reference URL.  Returns a local file path or an absolute URL.
        """
        logger.debug(f"Resolving schema reference: \n{href}")

        if href.startswith(('http://', 'https://', 'file://')):
            return href  # Already an absolute URL

        # Resolve relative to the instance_path
        #resolved_path= os.path.abspath(os.path.join(os.path.dirname(instance_path), href))
        resolved_path = os.path.abspath(os.path.join(os.path.dirname(instance_path), href)) # Ensure absolute path
        logger.debug(f"Resolved path: \n{resolved_path}")

        return resolved_path # Return the absolute path; don't prepend https://


    
# to test     
if __name__ == "__main__":
    esef_filing_root="/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/"
    filename="reports/sap-2022-12-31-DE.xhtml"
    data_pool = Pool(cache_folder="../data/xbrl_cache", esef_filing_root=esef_filing_root)
    #data_pool.add_instance_location(location=os.path.join(esef_filing_root, filename), attach_taxonomy=True)     
    data_pool.add_instance_location(esef_filing_root=esef_filing_root, filename=filename, attach_taxonomy=True)
```

