"""

"""

from openesef.base.pool import Pool, const
from openesef.engines import tax_reporter
from openesef.taxonomy.taxonomy import Taxonomy
#from openesef.base.fbase import XmlFileBase
from openesef.edgar.edgar import EG_LOCAL
from openesef.edgar.stock import Stock
from openesef.edgar.filing import Filing
from openesef.util.parse_concepts import *
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
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.try") 




egl = EG_LOCAL('/text/edgar')
# Create an in-memory filesystem
memfs = fs.open_fs('mem://')



stock = Stock('AAPL', egl = egl); #self = stock
filing = stock.get_filing(period='annual', year=2020) #self = filing
#filing = Filing(url="Archives/edgar/data/1318605/0001564590-20-004475.txt", egl = egl)



entry_points = []
for key, filename in filing.xbrl_files.items():
    logger.info(f"{key}, {filing.documents[filename].type}, {filename}")
    content = filing.documents[filename].doc_text.data #.get("<XML>", "")
    content = list(content.values())[0] if type(content) == dict else content
    print(content[:100])
    with  memfs.open(filename, 'w') as f:
        f.write(content)
    logger.info(f"Successfully cached {filename} to memory, length={len(content)}")
    if "xml" in filename:
        entry_points.append(f"mem://{filename}")

memfs.listdir("/")


data_pool = Pool(max_error=2, esef_filing_root="mem://", memfs=memfs); #self = data_pool

#self = Taxonomy(entry_points=None, container_pool = data_pool, esef_filing_root="mem://", memfs=memfs)

this_tax = Taxonomy(entry_points=entry_points,
                           container_pool = data_pool, 
                           esef_filing_root="mem://",
                           memfs=memfs)  #

data_pool.current_taxonomy = this_tax

if filing.xbrl_files.get("xml"):
    xml_filename = filing.xbrl_files.get("xml")
    instance_str = filing.documents[xml_filename].doc_text.data #.get("<XML>", "")
    instance_str = list(instance_str.values())[0] if type(instance_str) == dict else instance_str
    #instance_str = clean_doc(instance_str)
    instance_byte = instance_str.encode('utf-8')
    instance_io = BytesIO(instance_byte)
    instance_tree = lxml_etree.parse(instance_io)
    root = instance_tree.getroot()
    data_pool.cache_from_string(location=xml_filename, content=instance_str, memfs=memfs)
    xid = Instance(container_pool=data_pool, root=root, memfs=memfs)

print(xid)

for i, (key, value) in enumerate(xid.dei.items()):
    print(f"{i}: {key}: {value}")

reporting_contexts = xid.identify_reporting_contexts()
df_contexts = pd.DataFrame.from_dict(reporting_contexts, orient="index")
print(df_contexts)

this_tax = data_pool.current_taxonomy

print(this_tax)

# this_tax = data_pool.current_taxonomy
# data_pool.current_taxonomy.linkbases
# data_pool.current_taxonomy.schemas
# data_pool.current_taxonomy.concepts

memfs.listdir("/")

print("\nTaxonomy statistics:")
print(f"Schemas: {len(this_tax.schemas)}") #
print(f"Linkbases: {len(this_tax.linkbases)}")
print(f"Concepts: {len(this_tax.concepts)}")


print(this_tax)

#xid is of type <class 'openesef.instance.instance.Instance'>

# Print facts with their corresponding concepts
for key, fact in xid.xbrl.facts.items():
    # Get the concept associated with this fact
    concept = this_tax.concepts_by_qname.get(fact.qname)
    if concept:
        if True or re.search(r"PropertyPlantAndEquipment", concept.name):
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
                # Print segment information if exists
                if ref_context.segment:
                    print("\nSegment Information:")
                    # The segment is stored directly in the Context object
                    for dimension, member in ref_context.segment.items():
                        print(f"Dimension: {dimension}")
                        print(f"Member: {member.text if hasattr(member, 'text') else member}")
                
                # Print scenario information if exists
                if ref_context.scenario:
                    print("\nScenario Information:")
                    # The scenario is stored directly in the Context object
                    for dimension, member in ref_context.scenario.items():
                        print(f"Dimension: {dimension}")
                        print(f"Member: {member.text if hasattr(member, 'text') else member}")
            print("-" * 50)

reporter = tax_reporter.TaxonomyReporter(this_tax)

networks = get_presentation_networks(this_tax)

concepts_by_statement = {}

for network in networks:
    statement_name = network.role.split('/')[-1]
    concepts = get_network_details(reporter, network)
    if concepts:  # Only add if we found concepts
        concepts_by_statement[statement_name] = concepts


concept_tree_list = []
for statement, concepts in concepts_by_statement.items():
    statement_concept = concepts[0]
    this_statement_list = []
    for concept in concepts:
        this_concept_generator = yield_concept_tree(concept) 
        # Collect all levels of concepts
        for this_concept_dict in this_concept_generator:
            this_concept_dict['statement_label'] = statement_concept["label"]
            this_concept_dict['statement_name'] = statement_concept["name"]
            this_statement_list.append(this_concept_dict)
    #this_statement_list = list(set(this_statement_list))         
    concept_tree_list.append(this_statement_list)
concept_tree_list = list(chain.from_iterable(concept_tree_list))
df = pd.DataFrame.from_records(concept_tree_list)
df = df.drop_duplicates(subset=["concept_name"]).reset_index(drop=True)
df["concept_ns"] = df["concept_name"].apply(lambda x: x.split(":")[0])
if not df.empty:
    df["concept_is_extended"] = df["concept_name"].apply(lambda x: not re.search(r"ifrs-full|us-gaap|dei|srt|country|stpr", x))

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