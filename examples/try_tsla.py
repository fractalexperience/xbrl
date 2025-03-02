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
    logger = setup_logger("main", logging.DEBUG, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.try") 


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


this_tax = data_pool.current_taxonomy

periods_dict={}


# periods = set()
# for context in xid.xbrl.contexts.values():
#     periods.add(context.get_period_string())
#print(periods[0])


main_contexts = [context for context in xid.xbrl.contexts.values() if not context.descriptors ]

periods_dict = {}
doc_period_end_date = None 

for key, fact in xid.xbrl.facts.items():
    if re.search(r"DocumentPeriodEndDate", str(fact.qname)):
        doc_period_end_date = fact.value 
        doc_period_end_date_dt = pd.to_datetime(doc_period_end_date)
        break

#xid.xbrl.contexts[fact.context_ref]
# 1. Current Instance Date Context
for context in main_contexts:
    if context.period_instant is not None and pd.to_datetime(context.period_instant) == doc_period_end_date_dt:
        periods_dict["CurrentInstanceDateContext"] = {
            "context_id": context.id,
            "period_string": context.get_period_string(),
            "instant": context.period_instant
        }

# 2. Current Period Context (Annual)
periods_dict["CurrentPeriodContext"] = None
if doc_period_end_date:
    for context_id, context in xid.xbrl.contexts.items():
        if context.period_start is not None and context.period_end is not None and  not context.descriptors:
            period_start_dt = pd.to_datetime(context.period_start)
            period_end_dt = pd.to_datetime(context.period_end)
            # Check if the period is annual (approximately 365 days) and the end date matches
            if (period_end_dt - period_start_dt).days >= 360 and str(period_end_dt.date()) == str(doc_period_end_date_dt.date()):
                periods_dict["CurrentPeriodContext"] = {
                    "context_id": context_id,
                    "period_string": context.get_period_string(),
                    "start_date": context.period_start,
                    "end_date": context.period_end
                }
                break

# 3. Prior Instance Date Context
periods_dict["PriorInstanceDateContext"] = None
closest_prior_instant = None
closest_prior_context_id = None

if doc_period_end_date:
    for context_id, context in xid.xbrl.contexts.items():
        if context.period_instant is not None and not context.descriptors:
            try:
                context_instant_dt = pd.to_datetime(context.period_instant)
                if context_instant_dt < doc_period_end_date_dt:
                    # Check if this is the closest prior date we've found so far
                    if closest_prior_instant is None or (doc_period_end_date_dt - context_instant_dt) < (doc_period_end_date_dt - closest_prior_instant):
                        closest_prior_instant = context_instant_dt
                        closest_prior_context_id = context_id
            except ValueError:
                print(f"Could not compare dates: {context.period_instant} and {doc_period_end_date}")

    # If we found a prior instant date, store it
    if closest_prior_context_id:
        periods_dict["PriorInstanceDateContext"] = {
            "context_id": closest_prior_context_id,
            "period_string": xid.xbrl.contexts[closest_prior_context_id].get_period_string(),
            "instant": xid.xbrl.contexts[closest_prior_context_id].period_instant
        }

# 4. Prior Period Context (Annual)
periods_dict["PriorPeriodContext"] = None
if doc_period_end_date:
    for context_id, context in xid.xbrl.contexts.items():
        if context.period_start is not None and context.period_end is not None and not context.descriptors:
            period_start_dt = pd.to_datetime(context.period_start)
            period_end_dt = pd.to_datetime(context.period_end)
            # Check if the period is annual (approximately 365 days)
            if (period_end_dt - period_start_dt).days >= 360:
                try:
                    if period_end_dt < doc_period_end_date_dt:
                        periods_dict["PriorPeriodContext"] = {
                            "context_id": context_id,
                            "period_string": context.get_period_string(),
                            "start_date": context.period_start,
                            "end_date": context.period_end
                        }
                        break
                except ValueError:
                    print(f"Could not compare dates: {context.period_end} and {doc_period_end_date}")

df = pd.DataFrame.from_dict(periods_dict, orient="index")


# Print the results
for period_type, period_data in periods_dict.items():
    print(f"\n{period_type}:")
    if period_data:
        print(f"  Context ID: {period_data['context_id']}")
        print(f"  Period String: {period_data['period_string']}")
        if "instant" in period_data:
            print(f"  Instant Date: {period_data['instant']}")
        if "start_date" in period_data:
            print(f"  Start Date: {period_data['start_date']}")
        if "end_date" in period_data:
            print(f"  End Date: {period_data['end_date']}")
    else:
        print("  Not Found")

# Example of accessing DocumentPeriodEndDate
for key, fact in xid.xbrl.facts.items():
    if re.search(r"DocumentPeriodEndDate", str(fact.qname)):
        print(f"{key}: {fact.value}")
        print(f"{fact.context_ref}")
        print(f"{xid.xbrl.contexts[fact.context_ref].get_period_string()}")
        print("---")
        break

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