"""

"""

from openesef.base.pool import Pool, const
from openesef.taxonomy.taxonomy import Taxonomy
#from openesef.base.fbase import XmlFileBase
from openesef.edgar.edgar import EG_LOCAL
from openesef.edgar.stock import Stock
from openesef.edgar.filing import Filing
#from openesef.taxonomy.linkbase import Linkbase
from openesef.instance.instance import Instance
import re
from lxml import etree as lxml_etree
from io import StringIO, BytesIO
import traceback
import fs

from openesef.util.util_mylogger import setup_logger #util_mylogger
import logging 

if __name__=="__main__":
    logger = setup_logger("main", logging.DEBUG, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.try") 



import importlib
#import openesef.base.fbase; importlib.reload(openesef.base.fbase); from openesef.base.fbase import *
#import openesef.edgar.edgar; importlib.reload(openesef.edgar.edgar); from openesef.edgar.edgar import *
#import openesef.edgar.stock; importlib.reload(openesef.edgar.stock); from openesef.edgar.stock import *; from openesef.edgar.stock import Stock
#import openesef.edgar.filing; importlib.reload(openesef.edgar.filing); from openesef.edgar.filing import *; from openesef.edgar.filing import Filing
#import openesef.base.pool; importlib.reload(openesef.base.pool); from openesef.base.pool import *
egl = EG_LOCAL('/text/edgar')



# Create an in-memory filesystem
memfs = fs.open_fs('mem://')

memfs.listdir(".")


stock = Stock('TSLA', egl = egl); #self = stock
filing = stock.get_filing(period='annual', year=2020) #self = filing
#alternatively:
#filing = Filing(url="Archives/edgar/data/1318605/0001564590-20-004475.txt", egl = egl)


def clean_doc(text):
    if type(text) == dict:
        text =  list(text.values())[0]
    text = re.sub(r'^<XBRL>', '', text)
    text = re.sub(r'</XBRL>$', '', text)
    text = re.sub(r"\n", '', text)
    return text

entry_points = []

# len(filing.documents)
# # print the xbrl files
for key, filename in filing.xbrl_files.items():
    logger.info(f"{key}, {filing.documents[filename].type}, {filename}")
    content = filing.documents[filename].doc_text.data
    content = clean_doc(content)
    with  memfs.open(filename, 'w') as f:
        f.write(content)
    logger.info(f"Successfully cached {filename} to memory, length={len(content)}")
    entry_points.append(f"mem://{filename}")

memfs.listdir("/")

entry_points

data_pool = Pool(max_error=2, esef_filing_root="mem://", memfs=memfs); #self = data_pool


this_tax = Taxonomy(entry_points=entry_points,
                           container_pool = data_pool, 
                           esef_filing_root="mem://",
                           #in_memory_content=in_memory_content,
                           memfs=memfs)  #

data_pool.current_taxonomy = this_tax

if filing.xbrl_files.get("xml"):
    xml_filename = filing.xbrl_files.get("xml")
    instance_str = filing.documents[xml_filename].doc_text.data
    instance_str = clean_doc(instance_str)
    instance_byte = instance_str.encode('utf-8')
    instance_io = BytesIO(instance_byte)
    instance_tree = lxml_etree.parse(instance_io)
    root = instance_tree.getroot()
    data_pool.cache_from_string(location=xml_filename, content=instance_str, memfs=memfs)
    xid = Instance(container_pool=data_pool, root=root, memfs=memfs)
#     data_pool.add_instance(xid, key=f"mem://{xml_filename}", attach_taxonomy=False, memfs=memfs)
#     # try:
#     #     this_tax = Taxonomy(entry_points=[f"mem://{xml_filename}"],
#     #                        container_pool = data_pool, 
#     #                        esef_filing_root="mem://",
#     #                        memfs=memfs)  #
#     #     data_pool.current_taxonomy = this_tax
#     # except Exception as e:
#     #     logger.error(f"Error creating Taxonomy: {e}")
#     #     traceback.print_exc(limit=10)
#     # #exit()
    

# #fbase = XmlFileBase(location=None, container_pool=data_pool, memfs=memfs, esef_filing_root="mem://"); self = fbase
# #fbase = XmlFileBase(location="aapl-20180929_pre.xml", container_pool=data_pool, memfs=memfs, esef_filing_root="mem://"); self = fbase

# #in_memory_content = {}

# if filing.xbrl_files.get("sch"):
#     schema_filename = filing.xbrl_files.get("sch")
#     this_href = "mem://" + schema_filename
#     entry_points.append(this_href)
#     schema_str = filing.documents[schema_filename].doc_text.data
#     schema_str = clean_doc(schema_str)
#     data_pool.cache_from_string(location=this_href, content=schema_str, memfs=memfs)
#     data_pool.add_reference(href=this_href, base="mem://", esef_filing_root="mem://", memfs=memfs)



# for linkbase_type in ["pre", "cal", "def", "lab" ]:
#     #linkbase_type = "pre"; linkbase_filename = filing.xbrl_files.get(linkbase_type)
#     linkbase_filename = filing.xbrl_files.get(linkbase_type)
#     if linkbase_filename:
#         linkbase_str = filing.documents[linkbase_filename].doc_text.data
#         linkbase_str = clean_doc(linkbase_str)
#         #linkbase_io = StringIO(linkbase_str)
#         this_href = "mem://" + linkbase_filename
#         entry_points.append(this_href)
#         #in_memory_content[this_href] = linkbase_str
#         data_pool.add_reference(href=this_href, base=".", esef_filing_root="mem://", memfs=memfs)
#         #exit()
#         # data_pool.cache_from_string(location=this_href, content=linkbase_str, memfs=memfs)
#         # this_lb = Linkbase(location=None, container_pool=data_pool, esef_filing_root="mem://", memfs=memfs)        
#         # parsers = {
#         #     f'{{{const.NS_LINK}}}linkbase': this_lb.l_linkbase,
#         #     f'{{{const.NS_LINK}}}calculationLink': this_lb.l_link,
#         #     f'{{{const.NS_LINK}}}presentationLink': this_lb.l_link,
#         #     f'{{{const.NS_LINK}}}definitionLink': this_lb.l_link,
#         #     f'{{{const.NS_LINK}}}labelLink': this_lb.l_link,
#         #     f'{{{const.NS_LINK}}}referenceLink': this_lb.l_link,
#         #     f'{{{const.NS_GEN}}}link': this_lb.l_link,  # Generic link
#         #     f'{{{const.NS_LINK}}}roleRef': this_lb.l_role_ref,
#         #     f'{{{const.NS_LINK}}}arcroleRef': this_lb.l_arcrole_ref
#         # }
#         #fbase = XmlFileBase(location=this_href, container_pool=data_pool, parsers=None, root=None, esef_filing_root = "mem://", memfs=memfs)
#         #fbase = XmlFileBase(location=this_href, container_pool=data_pool, parsers=parsers, root=None, esef_filing_root = "mem://", memfs=memfs)


data_pool.current_taxonomy

# this_tax = data_pool.current_taxonomy
# data_pool.current_taxonomy.linkbases
# data_pool.current_taxonomy.schemas
# data_pool.current_taxonomy.concepts

memfs.listdir("/")

# this_tax = Taxonomy(entry_points=list(set(entry_points)),
#                            container_pool = data_pool, 
#                            esef_filing_root="mem://",
#                            #in_memory_content=in_memory_content,
#                            memfs=memfs)  #

print("\nTaxonomy statistics:")
print(f"Schemas: {len(this_tax.schemas)}") #
print(f"Linkbases: {len(this_tax.linkbases)}")
print(f"Concepts: {len(this_tax.concepts)}")


print(this_tax)

# Print facts with their corresponding concepts
for key, fact in xid.xbrl.facts.items():
    # Get the concept associated with this fact
    concept = this_tax.concepts_by_qname.get(fact.qname)
    
    if concept:
        if re.search(r"PropertyPlantAndEquipment", concept.name):
            print("Fact Details:")
            print(f"Concept Name: {concept.name}")
            if not "text" in concept.name.lower():
                print(f"Value: {fact.value}")
            else:
                print(f"Value: {fact.value[:100]}")
            
            print(f"Unit Ref: {fact.unit_ref}")
            print(f"Decimals: {fact.decimals}")
            print(f"Precision: {fact.precision}")
            #print(f"Context Ref: {fact.context_ref}")
            ref_context = xid.xbrl.contexts.get(fact.context_ref)
            if ref_context:
                # Print period information
                print(ref_context.get_period_string())
                # Print entity information            
                print(f"Entity: {ref_context.entity_scheme}: {ref_context.entity_identifier}")                    
                # # Print segment information if exists
                # if ref_context.entity and ref_context.entity.segment:
                #     print("\nSegment Information:")
                #     for member in ref_context.entity.segment:
                #         print(f"Dimension: {member.dimension}")
                #         print(f"Member: {member.member}")
                
                # # Print scenario information if exists
                # if ref_context.scenario:
                #         print("\nScenario Information:")
                #         for item in ref_context.scenario:
                #             print(f"Scenario Item: {item}")
            print("-" * 50)

# for key, concept in this_tax.concepts.items():
#     print(f"Concept: {key}")
#     print(f"Name: {concept.name}")
#     #print(f"Description: {concept.description}")
#     print(f"Domain: {concept.domain}")
#     #print(f"Unit: {concept.unit}")
#     print("---")

# for key, fact in xid.xbrl.facts.items():
#     #print(f"Concept: {fact.concept.name}")
#     #print(f"Fact: {key}")
#     print(f"Value: {fact.value}")
#     print(f"Context: {fact.context_ref}")
#     print("---")