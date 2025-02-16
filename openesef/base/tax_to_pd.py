import openesef.base.pool as pool
import os 
import pandas as pd
from collections import defaultdict


def export_taxonomy_to_dataframe(tax):
    # Create lists to store concept information
    data = []
    
    # Iterate through all concepts in the tax
    for concept_id, concept in tax.concepts.items():
        #concept_id, concept = list(tax.concepts.items())[4492]
        # Get basic concept information
        concept_info = {
            'concept_name': concept.name,
            'concept_qname': concept.qname,
            'namespace': concept.namespace,
            'data_type': concept.data_type,
            'period_type': concept.period_type,
            'balance': concept.balance,
            'abstract': concept.abstract,
            'nillable': concept.nillable
        }
        
        # Get labels in different languages and roles
        labels = defaultdict(dict)
        if hasattr(concept, 'resources') and 'label' in concept.resources:
            for lang, role_labels in concept.resources['label'].items():
                for label in role_labels:
                    labels[lang][label.xlink.role] = label.text
        concept_info['labels'] = labels
        
        # Get references
        references = []
        if hasattr(concept, 'references') and concept.references:
            for ref_list in concept.references.values():
                for ref in ref_list:
                    references.append(str(ref))
        concept_info['references'] = references
        
        # Get presentation relationships
        presentation_parents = []
        presentation_children = []
        if hasattr(concept, 'chain_up'):
            presentation_parents = [p for p in concept.chain_up.values()]
        if hasattr(concept, 'chain_dn'):
            presentation_children = [c for c in concept.chain_dn.values()]
        
        try:
            concept_info['presentation_parents'] = [p.Concept for parents in presentation_parents for p in parents]
        except Exception as e:
            concept_info['presentation_parents'] = []  # Default to empty list on error
            # Optionally log the error: print(f"Error processing presentation_parents: {e}")
        try:
            concept_info['presentation_children'] = [c.Concept for children in presentation_children for c in children]
        except Exception as e:
            concept_info['presentation_children'] = []  # Default to empty list on error
            # Optionally log the error: print(f"Error processing presentation_children: {e}")
        
        # Add to data list
        data.append(concept_info)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    
    # Normalize the labels column (optional)
    labels_df = pd.json_normalize(df['labels'].apply(lambda x: {f"{lang.split('/')[-1]}": text 
                                                            for lang, roles in x.items() 
                                                            for role, text in roles.items()}))
    # Update column names to remove redundant parts
    #labels_df.columns = [col.split('|')[0] + '_' + col.split('/')[-1] for col in labels_df.columns]
        
    # Drop the original labels column and concatenate with normalized labels
    df = df.drop('labels', axis=1)
    df = pd.concat([df, labels_df], axis=1)
    #df.loc[df.concept_name.str.contains("Revenue")].to_dict()
    #df.loc[df.concept_name=="UnrecognizedTaxBenefits"].to_dict()
    #df.loc[df.concept_name.str.contains("TaxBenefit")].to_dict()
    return df

if __name__ == "__main__":
    CACHE_DIR = os.path.expanduser("~/.xbrl_cache")
    #data_pool = Pool(cache_folder=CACHE_DIR, max_error=10)
    data_pool = pool.Pool(cache_folder=CACHE_DIR, max_error=10); #self = data_pool
    location = "https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-all-2024.xsd"
    tax = data_pool.add_taxonomy([location], esef_filing_root=os.getcwd())

    df = export_taxonomy_to_dataframe(tax)
    df.iloc[4492]
    df.to_excel("us-gaap-all-2024.xlsx", index=False)
