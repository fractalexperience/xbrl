"""
https://devv.ai/search?threadId=echbdlppi9z4
"""

import sys

#sys.path = [p for p in sys.path if 'openesef' not in p] # Remove any existing openesef paths
#sys.path.insert(0, "./openesef")  # if you're in the same directory as parse_concepts.py


import datetime
#from openesef.util import util_mylogger
from openesef.util.util_mylogger import setup_logger #util_mylogger

import logging 
if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="../dir/log/")
else:
    logger = logging.getLogger("main.check_esef") 

#import openesef
from openesef.base import pool, const
from openesef.engines import tax_reporter
from openesef.edgar.edgar import EG_LOCAL
from openesef.edgar.filing import Filing

from openesef.base.pool import Pool

from openesef.taxonomy.taxonomy import Taxonomy
from openesef.instance.instance import Instance


from lxml import etree as lxml_etree
from io import StringIO, BytesIO



import fs
import os
import re
import gzip
import pathlib
import pandas as pd
import logging
#logging.basicConfig(level=logging.DEBUG)
from itertools import chain
##openesef.base.pool.logger.setLevel(logging.INFO)
#openesef.taxonomy.taxonomy.logger.setLevel(logging.INFO)
#openesef.engines.tax_reporter.logger.setLevel(logging.INFO)
import traceback
import io
#traceback.print_exc(limit=10)

# import logging

# # Get a logger.  __name__ is a good default name.
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

def ungzip_file(gzip_path, output_path):
    if not os.path.exists(output_path):
        with gzip.open(gzip_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())

def prepare_files(full_instance_zip_path, location_path):
    """Prepare files with ESEF structure awareness"""
    # Ungzip files if needed
    if os.path.exists(full_instance_zip_path):
        instance_file = full_instance_zip_path
        if full_instance_zip_path.endswith('.gzip'):
            ungzipped_file = full_instance_zip_path[:-5]
            ungzip_file(full_instance_zip_path, ungzipped_file)
            instance_file = ungzipped_file
        
        # Handle GZIP files in the ESEF structure
        for root, _, files in os.walk(location_path):
            for file in files:
                if file.endswith('.gzip'):
                    ungzipped_file = os.path.join(root, file[:-5])
                    ungzip_file(os.path.join(root, file), ungzipped_file)
        
        return instance_file



def get_network_concepts(reporter, network):
    """Get all concepts in a network using the reporter"""
    # Get the arc name, role, and arcrole from the network
    arc_name = network.arc_name
    role = network.role
    arcrole = network.arcrole
    
    # Use r_base_set to get the network details
    reporter.r_base_set(arc_name, role, arcrole)
    
    # Get all nodes in the network
    nodes = reporter.taxonomy.get_bs_members(arc_name, role, arcrole)
    
    # Create a hierarchy
    concepts_by_level = {}
    for node in nodes:
        level = node.Level
        if level not in concepts_by_level:
            concepts_by_level[level] = []
        
        concept_info = {
            'name': str(node.Concept.qname) if hasattr(node.Concept, 'qname') else str(node.Concept),
            'label': node.Concept.get_label() if hasattr(node.Concept, 'get_label') else 'N/A',
            'period_type': node.Concept.period_type if hasattr(node.Concept, 'period_type') else 'N/A',
            'balance': node.Concept.balance if hasattr(node.Concept, 'balance') else 'N/A',
            'level': level,
            'children': []
        }
        concepts_by_level[level].append(concept_info)
    
    # Build the hierarchy from bottom up
    max_level = max(concepts_by_level.keys()) if concepts_by_level else 0
    for level in range(max_level, 0, -1):
        current_level_concepts = concepts_by_level.get(level, [])
        parent_level_concepts = concepts_by_level.get(level - 1, [])
        
        # Add current level concepts as children to their parents
        for parent in parent_level_concepts:
            parent['children'].extend([c for c in current_level_concepts])
    
    # Return root level concepts (level 0)
    return concepts_by_level.get(0, [])

def get_presentation_networks(taxonomy):
    print("\nAccessing presentation networks...")
    
    if 'base_sets' in taxonomy.__dict__:
        print(f"Number of base sets: {len(taxonomy.base_sets)}")
        
        presentation_networks = []
        for key, base_set in taxonomy.base_sets.items():
            if 'presentation' in str(key).lower():
                print(f"\nFound presentation base set: {key}")
                presentation_networks.append(base_set)
        
        return presentation_networks
    else:
        print("No base_sets found in taxonomy")
        return []


def print_concept_tree(concept, level=0):
    """Print concept hierarchy with indentation"""
    indent = "  " * level
    print(f"{indent}Concept: {concept['name']}")
    print(f"{indent}Label: {concept['label']}")
    print(f"{indent}Period Type: {concept['period_type']}")
    print(f"{indent}Balance: {concept['balance']}")
    print(f"{indent}Level: {concept.get('level', 'N/A')}")
    print(f"{indent}" + "-" * 40)
    
    # Print children recursively
    for child in concept.get('children', []):
        print_concept_tree(child, level + 1)

def yield_concept_tree(concept, level=0):
    """Yield concept hierarchy with indentation"""
    this_concept_dict = {
        'concept_name': concept['name'],
        'concept_label': concept['label'],
        'concept_period_type': concept['period_type'],
        'concept_balance': concept['balance'],
        'concept_level': concept.get('level', 'N/A')
    }
    yield this_concept_dict
    for child in concept.get('children', []):
        yield from yield_concept_tree(child, level + 1)


def print_concepts_by_statement(concepts_by_statement):
    if not concepts_by_statement:
        print("\nNo concepts found in the presentation linkbase")
        return

    for statement, concepts in concepts_by_statement.items():
        print(f"\n=== {statement} ===")
        print("=" * 80)
        for concept in concepts:
            print_concept_tree(concept)

def get_df_from_concepts_by_statement(concepts_by_statement):
    concept_tree_list = []
    if not concepts_by_statement:
        print("\nNo concepts found in the presentation linkbase")
        return

    for statement, concepts in concepts_by_statement.items():
        for concept in concepts:
            concept_tree_list.append(yield_concept_tree(concept))

    df = pd.DataFrame(concept_tree_list)
    return df


def get_child_concepts(reporter, network, concept, taxonomy, visited=None):
    """Recursively get all child concepts of a given concept"""
    if visited is None:
        visited = set()

    # Get concept identifier (name or qname)
    concept_id = str(concept.qname) if hasattr(concept, 'qname') else str(concept)

    # Avoid circular references
    if concept_id in visited:
        return []
    
    visited.add(concept_id)
    children = []

    # Get all members from the network
    members = network.get_members(start_concept=concept, include_head=False)
    
    # Process each member
    for member in members:
        member_id = str(member.Concept.qname) if hasattr(member.Concept, 'qname') else str(member.Concept)
        if member_id not in visited:
            child_info = {
                'name': member_id,
                'label': member.Concept.get_label() if hasattr(member.Concept, 'get_label') else 'N/A',
                'period_type': member.Concept.period_type if hasattr(member.Concept, 'period_type') else 'N/A',
                'balance': member.Concept.balance if hasattr(member.Concept, 'balance') else 'N/A',
                'level': member.Level if hasattr(member, 'Level') else 'N/A',
                'children': get_child_concepts(reporter, network, member.Concept, taxonomy, visited)
            }
            children.append(child_info)
    
    return children

    # Compile the network using the reporter
    reporter.compile_network(network)
    
    # Get the network layout
    layout = reporter.get_network_layout(network)
    if layout:
        # Find children in the layout
        for item in layout:
            if item.Parent == concept and item.Concept not in visited:
                child_info = {
                    'name': str(item.Concept.qname) if hasattr(item.Concept, 'qname') else str(item.Concept),
                    'label': reporter.get_concept_label(item.Concept),
                    'period_type': item.Concept.period_type if hasattr(item.Concept, 'period_type') else 'N/A',
                    'balance': item.Concept.balance if hasattr(item.Concept, 'balance') else 'N/A',
                    'level': item.Level,
                    'children': get_child_concepts(reporter, network, item.Concept, taxonomy, visited)
                }
                children.append(child_info)
    
    return children


def print_concepts_by_statement(concepts_by_statement):
    if not concepts_by_statement:
        print("\nNo concepts found in the presentation linkbase")
        return
    
    for statement, concepts in concepts_by_statement.items():
        print(f"\n=== {statement} ===")
        print("-" * 80)
        for concept in concepts:
            print(f"Concept: {concept['name']}")
            print(f"Label: {concept['label']}")
            print(f"Period Type: {concept['period_type']}")
            print(f"Balance: {concept['balance']}")
            print("-" * 40)



def get_network_details(reporter, network):
    """Get all concepts in a network using the reporter"""
    try:
        # Get all members from the network
        members = network.get_members()
        if not members:
            logger.warning(f"Warning: No members found for network {network.role}")
            return []
        
        # Print network details for debugging
        logger.info(f"\nNetwork Role: {network.role}")
        logger.info(f"Network Arc Name: {network.arc_name}")
        logger.info(f"Network Arcrole: {network.arcrole}")
        logger.info(f"Number of members: {len(members)}")
        
        # Create hierarchy using member levels
        concepts_by_level = {}
        for member in members:
            level = member.Level
            if level not in concepts_by_level:
                concepts_by_level[level] = []
            
            concept_info = {
                'name': str(member.Concept.qname) if hasattr(member.Concept, 'qname') else str(member.Concept),
                'label': member.Concept.get_label() if hasattr(member.Concept, 'get_label') else 'N/A',
                'period_type': member.Concept.period_type if hasattr(member.Concept, 'period_type') else 'N/A',
                'balance': member.Concept.balance if hasattr(member.Concept, 'balance') else 'N/A',
                'level': level,
                'children': []
            }
            concepts_by_level[level].append(concept_info)
        
        # Build hierarchy from bottom up
        max_level = max(concepts_by_level.keys()) if concepts_by_level else 0
        for level in range(max_level, 0, -1):
            current_level = concepts_by_level.get(level, [])
            parent_level = concepts_by_level.get(level - 1, [])
            
            # Add current level concepts as children to their parents
            for parent in parent_level:
                parent['children'].extend(current_level)
        
        # Return root level concepts (level 0)
        return concepts_by_level.get(0, [])
        
    except Exception as e:
        logger.error(f"Error processing network {network.role}: {str(e)}")
        return []

#load_and_parse_xbrl_to_concept_df

def concept_to_df(instance_file, taxonomy_folder, concept_df_output_file = None, meta = {}, force_recreate = False):
    """
    instance_file: str
    taxonomy_folder: str
    concept_df_output_file: str
    meta: dict, a dictionary of metadata for the instance file, such as ISIN company name, filing date, etc

    instance_file = "/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/352123/2023/marley_spoon_2024-05-10_esef_xmls/222100A4X237BRODWF67-2023-12-31-en/marleyspoongroup/reports/222100A4X237BRODWF67-2023-12-31-en.xhtml"
    taxonomy_folder = "/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/352123/2023/marley_spoon_2024-05-10_esef_xmls/222100A4X237BRODWF67-2023-12-31-en/marleyspoongroup/"    
    concept_df_output_file = "/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/352123/2023/marley_spoon_2024-05-10_esef_xmls/"
  
    """
    meta_str = ""
    if meta:
        meta_str = "; ".join([f"{k}={v}" for k,v in meta.items()])
        logger.info(f"Starting to parse for observation: {meta_str}")
    if concept_df_output_file:
        #if os.path.exists(concept_df_output_file) or os.path.exists(concept_df_output_file.replace(".csv", ".p.gz")):
        if os.path.exists(concept_df_output_file.replace(".csv", ".p.gz")):
            logger.info(f"Concepts already parsed, skipping {concept_df_output_file}")
            if not force_recreate:
                return True
        
    
    # Find required files
    entry_point = None
    presentation_file = None
    for root, dirs, files in os.walk(taxonomy_folder):
        for file in files:
            if file.endswith('.xsd'):
                entry_point = os.path.join(root, file)
            elif file.endswith('_pre.xml'):
                presentation_file = os.path.join(root, file)    

    # for file in os.listdir(taxonomy_folder):
    #     if file.endswith('.xsd'):
    #         entry_point = os.path.join(taxonomy_folder, file)
    #     elif file.endswith('_pre.xml'):
    #         presentation_file = os.path.join(taxonomy_folder, file)
    
    if not entry_point or not presentation_file:
        #raise Exception("Required files not found")
        return None
    logger.info(f"\nLoading files:")
    logger.info(f"Entry point: {entry_point}")
    logger.info(f"Presentation: {presentation_file}")

    data_pool = pool.Pool(cache_folder="../data/xbrl_cache", max_error=1024); #self = data_pool

    # Load taxonomy
    try:
        tax = data_pool.add_taxonomy(entry_points = [entry_point, presentation_file], esef_filing_root=taxonomy_folder)
    except Exception as e:
        #logger.error(f"Error loading taxonomy: {e}", exc_info=True)
        tb_output = io.StringIO()
        traceback.print_exc(limit=10, file=tb_output)
        logger.error(f"Error loading taxonomy: {e}\n{tb_output.getvalue()}\n{meta_str}")
        tb_output.close()

        return None
    
    # Create taxonomy reporter
    try:    
        reporter = tax_reporter.TaxonomyReporter(tax)
    except Exception as e:
        tb_lines = traceback.format_exc(limit=10)
        logger.error(f"Error loading taxonomy: {e}\n{tb_lines}")                
        return None
    
    logger.info("\nTaxonomy statistics:")
    logger.info(f"Schemas: {len(tax.schemas)}")
    logger.info(f"Linkbases: {len(tax.linkbases)}")
    logger.info(f"Concepts: {len(tax.concepts)}")
    
    # Get presentation networks
    try:    
        networks = get_presentation_networks(tax)
        logger.info(f"\nFound {len(networks)} presentation networks")
    except Exception as e:
        tb_lines = traceback.format_exc(limit=10)
        logger.error(f"Error loading taxonomy: {e}\n{tb_lines}\n{meta_str}")        
        return None
    
    # Store concepts by statement
    

    try:
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
        if not df.empty:
            df["concept_is_extended"] = df["concept_name"].apply(lambda x: not "ifrs-full" in x)

        if concept_df_output_file:
            df.to_csv(concept_df_output_file, index=False, sep="|")  
            df.to_pickle(concept_df_output_file.replace(".csv", ".p.gz"), compression="gzip")

        return True
    except Exception as e:
        tb_lines = traceback.format_exc(limit=10)
        logger.error(f"Error loading taxonomy: {e}\n{tb_lines}\n{meta_str}")                
        return None

    # for network in networks:
    #     network_id = getattr(network, 'role', None)
    #     if network_id is None:
    #         network_id = str(network)
    #     statement_name = network_id.split('/')[-1]
        
    #     # Get all concepts in the network
    #     concepts = get_network_concepts(reporter, network)
    #     concepts_by_statement[statement_name] = concepts
    
    # get_child_concepts(reporter, network, concept, taxonomy, visited=None)

    return concepts_by_statement

def instance_to_df(xid, this_tax):
    # Initialize a list to store dictionaries of fact details
    facts_data = []
    # Get the concept associated with this fact
    for key, fact in xid.xbrl.facts.items():
        # Get the concept associated with this fact
        concept = this_tax.concepts_by_qname.get(fact.qname)
        
        if concept:
            fact_dict = {
                'concept_name': concept.qname,
                'value': fact.value[:100] if "text" in concept.name.lower() else fact.value,
                'unit_ref': fact.unit_ref,
                'decimals': fact.decimals,
                'precision': fact.precision
            }
            
            ref_context = xid.xbrl.contexts.get(fact.context_ref)
            if ref_context:
                # Add period information
                fact_dict['period'] = ref_context.get_period_string()                
                #fact_dict['period_instant'] = ref_context.period_instant
                fact_dict['period_start'] = ref_context.period_start
                #fact_dict['period_end'] = ref_context.period_end
                # # Add entity information
                # fact_dict['entity_scheme'] = ref_context.entity_scheme
                # fact_dict['entity_identifier'] = ref_context.entity_identifier
                # Add segment information
                if ref_context.segment:
                    segment_info = {}
                    for dimension, member in ref_context.segment.items():
                        segment_info[dimension] = member.text if hasattr(member, 'text') else str(member)
                    fact_dict['segment'] = segment_info
                else:
                    fact_dict['segment'] = None
                    
                # Add scenario information
                if ref_context.scenario:
                    scenario_info = {}
                    for dimension, member in ref_context.scenario.items():
                        scenario_info[dimension] = member.text if hasattr(member, 'text') else str(member)
                    fact_dict['scenario'] = scenario_info
                else:
                    fact_dict['scenario'] = None
            
            facts_data.append(fact_dict)
    # Create DataFrame from the collected data
    df_facts = pd.DataFrame(facts_data)
    # Optional: Clean up the DataFrame
    # Remove rows where all values are None or NaN
    #df_facts = df_facts.dropna(how='all')
    return df_facts


def clean_doc(text):
    if type(text) == dict:
        text =  list(text.values())[0]
    text = re.sub(r'^<XBRL>', '', text)
    text = re.sub(r'</XBRL>$', '', text)
    text = re.sub(r"\n", '', text)
    return text

def filing_to_xbrl(url, egl = EG_LOCAL('/text/edgar')):
    """
    url: str
    """
    filing = Filing(url, egl = egl)
    memfs = fs.open_fs('mem://')
    entry_points = []
    
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




if __name__ == "__main__" and False:
    #from parse_concepts import *
    # Specify your ESEF files and folders
    location_path = os.path.expanduser("~/Dropbox/data/proj/bmcg/bundesanzeiger/public/100737/2020/volkswagen_Konzernabschluss_2021-06-08_esef_xmls")
    instance_file = "reports/volkswagenag.xhtml.html.gzip"  # Relative to location_path
    instance_gzip_file = "volkswagenag.xhtml.html.gzip"
    
    # Full path to instance file
    full_instance_path = os.path.join(location_path, instance_file)
    
    # Prepare files
    full_instance_zip_path = os.path.join(location_path, instance_gzip_file)
    instance_file = prepare_files(full_instance_zip_path, location_path)
    
    # Parse the XBRL and group concepts
    instance_file = full_instance_path
    taxonomy_folder = location_path
    #load_and_parse_xbrl(instance_file, taxonomy_folder)
    #concepts = load_and_parse_xbrl(instance_file, location_path)

    data_pool = pool.Pool(cache_folder="../data/xbrl_cache")
    
    # Find required files
    entry_point = None
    presentation_file = None
    
    for file in os.listdir(taxonomy_folder):
        if file.endswith('.xsd'):
            entry_point = os.path.join(taxonomy_folder, file)
        elif file.endswith('_pre.xml'):
            presentation_file = os.path.join(taxonomy_folder, file)
    
    if not entry_point or not presentation_file:
        raise Exception("Required files not found")

    logger.info(f"\nLoading files:")
    logger.info(f"Entry point: {entry_point}")
    logger.info(f"Presentation: {presentation_file}")

    # Load taxonomy
    taxonomy = data_pool.add_taxonomy([entry_point, presentation_file], esef_filing_root=taxonomy_folder)
    
    # Create taxonomy reporter
    reporter = tax_reporter.TaxonomyReporter(taxonomy)
    
    logger.info("\nTaxonomy statistics:")
    logger.info(f"Schemas: {len(taxonomy.schemas)}")
    logger.info(f"Linkbases: {len(taxonomy.linkbases)}")
    logger.info(f"Concepts: {len(taxonomy.concepts)}")
    
    # Get presentation networks
    networks = get_presentation_networks(taxonomy)
    logger.info(f"\nFound {len(networks)} presentation networks")

    # Get presentation networks directly from taxonomy
    networks = []
    for key, base_set in taxonomy.base_sets.items():
        if 'presentation' in str(key).lower():
            networks.append(base_set)
    
    logger.info(f"\nFound {len(networks)} presentation networks")
    
    # Store concepts by statement
    concepts_by_statement = {}
    
    for network in networks:
        statement_name = network.role.split('/')[-1]
        concepts = get_network_details(reporter, network)
        if concepts:  # Only add if we found concepts
            concepts_by_statement[statement_name] = concepts
            


    # Print the results
    #print_concepts_by_statement(concepts_by_statement)

    # print("\n\nget_child_concepts")
    # for statement, concepts in concepts_by_statement.items():
    #     print(f"\n=== {statement} ===")
    #     print("-" * 80)
    #     for concept in concepts:
    #         get_child_concepts(reporter, network, concept, taxonomy, visited=None)

    logger.info("\n\nprint_concept_tree") 
    for statement, concepts in concepts_by_statement.items():
        logger.info(f"\n=== {statement} ===")
        logger.info(concepts)
        logger.info("-" * 80)
        for concept in concepts:
            print_concept_tree(concept, level=0)

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
        concept_tree_list.append(this_statement_list)

    concept_tree_list = list(chain.from_iterable(concept_tree_list))
    df = pd.DataFrame.from_records(concept_tree_list)
    df["concept_is_extended"] = df["concept_name"].apply(lambda x: not "ifrs-full" in x)
    df.head(30)
    df.to_csv("df.csv", index=False)

    # df1 = get_df_from_concepts_by_statement(concepts_by_statement)
    # df1.head(30)
    # df1.to_csv("concept_tree_df.csv", index=False)

if __name__ == "__main__" :
    #from parse_concepts import *
    location_path = os.path.expanduser("~/Dropbox/data/proj/bmcg/bundesanzeiger/public/213034/2021/grammer_Jahres-_2022-05-02_esef_xmls/")
    instance_file = "KALABE.xhtml.html"  # Relative to location_path

    # Full path to instance file
    full_instance_path = os.path.join(location_path, instance_file)
    taxonomy_folder = location_path
    #load_and_parse_xbrl(instance_file, taxonomy_folder)
    #concepts = load_and_parse_xbrl(instance_file, location_path)

    data_pool = pool.Pool(cache_folder="../data/xbrl_cache")
    
    # Find required files
    entry_point = None
    presentation_file = None
    
    for file in os.listdir(taxonomy_folder):
        if file.endswith('.xsd'):
            entry_point = os.path.join(taxonomy_folder, file)
        elif file.endswith('_pre.xml'):
            presentation_file = os.path.join(taxonomy_folder, file)
    
    if not entry_point or not presentation_file:
        raise Exception("Required files not found")

    logger.info(f"\nLoading files:")
    logger.info(f"Entry point: {entry_point}")
    logger.info(f"Presentation: {presentation_file}")

    # Load taxonomy
    taxonomy = data_pool.add_taxonomy([entry_point, presentation_file], esef_filing_root=taxonomy_folder)
    
    
    logger.info("\nTaxonomy statistics:")
    logger.info(f"Schemas: {len(taxonomy.schemas)}")
    logger.info(f"Linkbases: {len(taxonomy.linkbases)}")
    logger.info(f"Concepts: {len(taxonomy.concepts)}")
        