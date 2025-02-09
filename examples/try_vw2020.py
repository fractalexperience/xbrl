"""
https://devv.ai/search?threadId=echbdlppi9z4
"""

import sys
sys.path.insert(0, "../")
import openesef
print(openesef.__path__)
print(openesef.__file__)

from openesef.base import pool, const
from openesef.engines import tax_reporter
import os
import gzip
import pathlib

def ungzip_file(gzip_path, output_path):
    with gzip.open(gzip_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())

def prepare_files(instance_file, location_path):
    """Prepare files with ESEF structure awareness"""
    # Ungzip files if needed
    if instance_file.endswith('.gzip'):
        ungzipped_file = instance_file[:-5]
        ungzip_file(instance_file, ungzipped_file)
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

def load_and_parse_xbrl(instance_file, taxonomy_folder):
    data_pool = pool.Pool()
    
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

    print(f"\nLoading files:")
    print(f"Entry point: {entry_point}")
    print(f"Presentation: {presentation_file}")

    # Load taxonomy
    taxonomy = data_pool.add_taxonomy([entry_point, presentation_file], esef_filing_root=taxonomy_folder)
    
    # Create taxonomy reporter
    reporter = tax_reporter.TaxonomyReporter(taxonomy)
    
    print("\nTaxonomy statistics:")
    print(f"Schemas: {len(taxonomy.schemas)}")
    print(f"Linkbases: {len(taxonomy.linkbases)}")
    print(f"Concepts: {len(taxonomy.concepts)}")
    
    # Get presentation networks
    networks = get_presentation_networks(taxonomy)
    print(f"\nFound {len(networks)} presentation networks")
    
    # Store concepts by statement
    concepts_by_statement = {}
    
    for network in networks:
        network_id = getattr(network, 'role', None)
        if network_id is None:
            network_id = str(network)
        statement_name = network_id.split('/')[-1]
        
        # Get all concepts in the network
        concepts = get_network_concepts(reporter, network)
        concepts_by_statement[statement_name] = concepts
    
    get_child_concepts(reporter, network, concept, taxonomy, visited=None)

    return concepts_by_statement

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

def print_concepts_by_statement(concepts_by_statement):
    if not concepts_by_statement:
        print("\nNo concepts found in the presentation linkbase")
        return

    for statement, concepts in concepts_by_statement.items():
        print(f"\n=== {statement} ===")
        print("=" * 80)
        for concept in concepts:
            print_concept_tree(concept)



# def get_presentation_networks(taxonomy):
#     """Get presentation networks from taxonomy"""
#     print("\nAccessing presentation networks...")
#     if 'base_sets' in taxonomy.__dict__:
#         print(f"Number of base sets: {len(taxonomy.base_sets)}")
#         presentation_networks = []
#         for key, base_set in taxonomy.base_sets.items():
#             if 'presentation' in str(key).lower():
#                 presentation_networks.append(base_set)
#         return presentation_networks
#     else:
#         print("No base_sets found in taxonomy")
#         return []

# def print_concept_tree(concept, level=0):
#     """Print concept hierarchy with indentation"""
#     indent = "  " * level
#     print(f"{indent}Concept: {concept['name']}")
#     print(f"{indent}Label: {concept['label']}")
#     print(f"{indent}Period Type: {concept['period_type']}")
#     print(f"{indent}Balance: {concept['balance']}")
#     print(f"{indent}Level: {concept.get('level', 'N/A')}")
#     print(f"{indent}" + "-" * 40)
    
#     # Print children recursively
#     for child in concept.get('children', []):
#         print_concept_tree(child, level + 1)

# def get_network_concepts(reporter, network):
#     """Get all concepts in a network using the reporter"""
#     # Get the arc name, role, and arcrole from the network
#     arc_name = network.arc_name
#     role = network.role
#     arcrole = network.arcrole
    
#     # Use r_base_set to get the network details
#     reporter.r_base_set(arc_name, role, arcrole)
    
#     # Get all nodes in the network
#     nodes = reporter.taxonomy.get_bs_members(arc_name, role, arcrole)
    
#     # Create a hierarchy
#     concepts_by_level = {}
#     for node in nodes:
#         level = node.Level
#         if level not in concepts_by_level:
#             concepts_by_level[level] = []
        
#         concept_info = {
#             'name': str(node.Concept.qname) if hasattr(node.Concept, 'qname') else str(node.Concept),
#             'label': node.Concept.get_label() if hasattr(node.Concept, 'get_label') else 'N/A',
#             'period_type': node.Concept.period_type if hasattr(node.Concept, 'period_type') else 'N/A',
#             'balance': node.Concept.balance if hasattr(node.Concept, 'balance') else 'N/A',
#             'level': level,
#             'children': []
#         }
#         concepts_by_level[level].append(concept_info)
    
#     # Build the hierarchy from bottom up
#     max_level = max(concepts_by_level.keys()) if concepts_by_level else 0
#     for level in range(max_level, 0, -1):
#         current_level_concepts = concepts_by_level.get(level, [])
#         parent_level_concepts = concepts_by_level.get(level - 1, [])
        
#         # Add current level concepts as children to their parents
#         for parent in parent_level_concepts:
#             parent['children'].extend([c for c in current_level_concepts])
    
#     # Return root level concepts (level 0)
#     return concepts_by_level.get(0, [])

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

# def get_presentation_networks(taxonomy):
#     print("\nAccessing presentation networks...")
    
#     if 'base_sets' in taxonomy.__dict__:
#         print(f"Number of base sets: {len(taxonomy.base_sets)}")
        
#         presentation_networks = []
#         for key, base_set in taxonomy.base_sets.items():
#             if 'presentation' in str(key).lower():
#                 print(f"\nFound presentation base set: {key}")
#                 presentation_networks.append(base_set)
        
#         return presentation_networks
#     else:
#         print("No base_sets found in taxonomy")
#         return []    
    

# def load_and_parse_xbrl(instance_file, location_path):
#     """
#     Load and parse XBRL with ESEF support
#     Args:
#         instance_file: Name of the instance file within the ESEF structure
#         location_path: Root path of the ESEF folder structure
#     """
#     # Create the data pool
#     data_pool = pool.Pool(cache_folder="../data/xbrl_cache")
    
#     # Find the entry points within ESEF structure
#     entry_point = None
#     presentation_file = None
    
#     # Search for files in the ESEF structure
#     for root, _, files in os.walk(location_path):
#         for file in files:
#             if file.endswith('.xsd'):
#                 entry_point = os.path.join(root, file)
#             elif file.endswith('_pre.xml'):
#                 presentation_file = os.path.join(root, file)
#             if entry_point and presentation_file:
#                 break
#         if entry_point and presentation_file:
#             break
    
#     if not entry_point:
#         raise Exception("No taxonomy entry point (.xsd file) found in ESEF structure")
    
#     # Convert paths to URIs for consistency
#     entry_point_uri = pathlib.Path(entry_point).as_uri()
#     presentation_file_uri = pathlib.Path(presentation_file).as_uri() if presentation_file else None
    
#     # Load the taxonomy using the pool with location_path
#     entry_points = [entry_point_uri]
#     if presentation_file_uri:
#         entry_points.append(presentation_file_uri)
    
#     taxonomy = data_pool.add_taxonomy(entry_points, esef_filing_root=location_path)
    
#     print("\nTaxonomy statistics:")
#     print(f"Schemas: {len(taxonomy.schemas)}")
#     print(f"Linkbases: {len(taxonomy.linkbases)}")
#     print(f"Concepts: {len(taxonomy.concepts)}")
    
#     networks = get_presentation_networks(taxonomy)
#     print(f"\nFound {len(networks)} presentation networks")
    
#     reporter = tax_reporter.TaxonomyReporter(taxonomy)
#     print(reporter)
    
#     # Store concepts by statement
#     concepts_by_statement = {}
#     for network in networks:
#         #network = networks[0]; network
#         network_id = getattr(network, 'role', None)
#         if network_id is None:
#             network_id = str(network)
#         statement_name = network_id.split('/')[-1]
        
#         # Get root concepts
#         if hasattr(network, 'roots'):
#             root_concepts = network.roots
#         else:
#             all_concepts = set(rel.from_ for rel in network.relationships)
#             all_concepts.update(rel.to for rel in network.relationships)
#             child_concepts = set(rel.to for rel in network.relationships)
#             root_concepts = all_concepts - child_concepts
        
#         concepts_by_statement[statement_name] = []
#         for root in root_concepts:
#             concept_tree = {
#                 'name': str(root.qname) if hasattr(root, 'qname') else str(root),
#                 'label': taxonomy.get_concept_label(root) if hasattr(taxonomy, 'get_concept_label') else 'N/A',
#                 'period_type': root.period_type if hasattr(root, 'period_type') else 'N/A',
#                 'balance': root.balance if hasattr(root, 'balance') else 'N/A',
#                 'children': get_child_concepts(reporter, network, root, taxonomy)
#             }
#             concepts_by_statement[statement_name].append(concept_tree)
    
#     return concepts_by_statement

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
            print(f"Warning: No members found for network {network.role}")
            return []
        
        # Print network details for debugging
        print(f"\nNetwork Role: {network.role}")
        print(f"Network Arc Name: {network.arc_name}")
        print(f"Network Arcrole: {network.arcrole}")
        print(f"Number of members: {len(members)}")
        
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
        print(f"Error processing network {network.role}: {str(e)}")
        return []

if __name__ == "__main__":
    #from try_vw2020 import *
    # Specify your ESEF files and folders
    location_path = os.path.expanduser("~/Dropbox/data/proj/bmcg/bundesanzeiger/public/100737/2020/volkswagen_Konzernabschluss_2021-06-08_esef_xmls")
    instance_file = "reports/volkswagenag.xhtml.html"  # Relative to location_path
    
    # Full path to instance file
    full_instance_path = os.path.join(location_path, instance_file)
    
    # Prepare files
    instance_file = prepare_files(full_instance_path, location_path)
    
    # Parse the XBRL and group concepts
    instance_file = full_instance_path
    taxonomy_folder = location_path
    #load_and_parse_xbrl(instance_file, taxonomy_folder)
    #concepts = load_and_parse_xbrl(instance_file, location_path)

    data_pool = pool.Pool()
    
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

    print(f"\nLoading files:")
    print(f"Entry point: {entry_point}")
    print(f"Presentation: {presentation_file}")

    # Load taxonomy
    taxonomy = data_pool.add_taxonomy([entry_point, presentation_file], esef_filing_root=taxonomy_folder)
    
    # Create taxonomy reporter
    reporter = tax_reporter.TaxonomyReporter(taxonomy)
    
    print("\nTaxonomy statistics:")
    print(f"Schemas: {len(taxonomy.schemas)}")
    print(f"Linkbases: {len(taxonomy.linkbases)}")
    print(f"Concepts: {len(taxonomy.concepts)}")
    
    # Get presentation networks
    networks = get_presentation_networks(taxonomy)
    print(f"\nFound {len(networks)} presentation networks")

    # Get presentation networks directly from taxonomy
    networks = []
    for key, base_set in taxonomy.base_sets.items():
        if 'presentation' in str(key).lower():
            networks.append(base_set)
    
    print(f"\nFound {len(networks)} presentation networks")
    
    # Store concepts by statement
    concepts_by_statement = {}
    
    for network in networks:
        statement_name = network.role.split('/')[-1]
        concepts = get_network_details(reporter, network)
        if concepts:  # Only add if we found concepts
            concepts_by_statement[statement_name] = concepts
            
    # for network in networks:
    #     network_id = getattr(network, 'role', None)
    #     if network_id is None:
    #         network_id = str(network)
    #     statement_name = network_id.split('/')[-1]
        
    #     # Get all concepts in the network
    #     concepts = get_network_concepts(reporter, network)
    #     concepts_by_statement[statement_name] = concepts
    
    # for network in networks:
    #     network_id = getattr(network, 'role', None)
    #     if network_id is None:
    #         network_id = str(network)
    #     statement_name = network_id.split('/')[-1]
        
    #     # Get root concepts
    #     root_concepts = network.roots
        
    #     # Process each root concept
    #     concepts_by_statement[statement_name] = []
    #     for root in root_concepts:
    #         concept_tree = {
    #             'name': str(root.qname) if hasattr(root, 'qname') else str(root),
    #             'label': root.get_label() if hasattr(root, 'get_label') else 'N/A',
    #             'period_type': root.period_type if hasattr(root, 'period_type') else 'N/A',
    #             'balance': root.balance if hasattr(root, 'balance') else 'N/A',
    #             'level': 0,  # Root level
    #             'children': get_child_concepts(reporter, network, root, taxonomy)
    #         }
    #         concepts_by_statement[statement_name].append(concept_tree)    

    # Print the results
    print_concepts_by_statement(concepts_by_statement)

    for statement, concepts in concepts_by_statement.items():
        print(f"\n=== {statement} ===")
        print("-" * 80)
        for concept in concepts:
            print_concept_tree(concept, level=1)
            get_child_concepts(reporter, network, concept, taxonomy, visited=None)

    