"""
based on ESEF.jl/src/xbrl/esef_filings_api.jl


"""
import requests
import pandas as pd
import json
from functools import lru_cache
import os
from tqdm import tqdm
import gzip

def pluck_xbrl_json(url):
    """
    Fetches and parses XBRL data from a JSON endpoint, returning a DataFrame.

    Args:
        url (str): The URL of the XBRL JSON endpoint.

    Returns:
        pandas.DataFrame: A DataFrame containing the extracted XBRL facts.
    """
    r = requests.get(url)

    # Check 200 HTTP status code
    assert r.status_code == 200, f"HTTP request failed with status code: {r.status_code}"

    raw_data = json.loads(r.content.decode('utf-8'))

    finished_facts = []

    for k, fact in raw_data.get("facts", {}).items():
        flat_fact = flatten_dict(fact)

        if "dimensions.entity" in flat_fact:
            flat_fact["dimensions.entity"] = flat_fact["dimensions.entity"].replace("scheme:", "")

        for k_subfact, v_subfact in flat_fact.items():
            finished_facts.append({
                "subject": k,
                "predicate": k_subfact,
                "object": str(v_subfact)
            })

    return pd.DataFrame(finished_facts)

def flatten_dict(data, parent_key='', sep='_'):
    """
    Flattens a nested dictionary into a single-level dictionary.

    Args:
        data (dict): The dictionary to flatten.
        parent_key (str): The prefix for keys in the flattened dictionary.
        sep (str): The separator to use between keys.

    Returns:
        dict: A flattened dictionary.
    """
    items = []
    for k, v in data.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_entity_by_api(href):
    # href ="api/entities/549300CSLHPO6Y1AZN37"
    lei = href.split("/")[-1]
    url = f"https://filings.xbrl.org{href}"
    local_filename = f"../data/xbrl_org/entities/{lei}.json.gz"
    if os.path.exists(local_filename):
        with gzip.open(local_filename, "rb") as jfr:
            json_string = jfr.read().decode('utf-8')
    else:
        r = requests.get(url)
        assert r.status_code == 200, f"HTTP request failed with status code: {r.status_code}"
        json_string = r.content.decode('utf-8')
        with gzip.open(local_filename , "wb") as jfw:  # Use gzip to write the file
            jfw.write(json_string.encode('utf-8'))  # Encode the string to bytes

    raw_data = json.loads(json_string)
    entity_name = raw_data.get("data", {}).get("attributes", {}).get("name", "")
    return entity_name


def get_filings_index_by_api():
    all_data = []
    for page_number in tqdm(range(1, 563)):
        #page_number = 1
        local_filename = f"../data/xbrl_org/pages/filing_xbrl_org_index_20250228_page_{page_number}.json.gz"
        if os.path.exists(local_filename):
            with gzip.open(local_filename, "rb") as jfr:
                json_string = jfr.read().decode('utf-8')
        else:
            url = f"https://filings.xbrl.org/api/filings?include=entity&page%5Bnumber%5D={page_number}"
            r = requests.get(url)
            assert r.status_code == 200, f"HTTP request failed with status code: {r.status_code}"
            json_string = r.content.decode('utf-8')
            #with open(local_filename, "w") as jfw:
            #    jfw.write(json_string)
            with gzip.open(local_filename, "wb") as jfw:  # Use gzip to write the file
                jfw.write(json_string.encode('utf-8'))  # Encode the string to bytes
        
        raw_data = json.loads(json_string)
        this_data_raw = raw_data.get("data", [])
        this_data =  [flatten_dict(d) for d in this_data_raw]
        
        all_data.extend(this_data)
    
    df =  pd.DataFrame(all_data)
    df.to_excel("../data/filing_xbrl_org_index_20250228.xlsx") #save in data folder, not the subfolder.
    df.to_pickle("../data/xbrl_org/filing_xbrl_org_index_20250228.p.gz", compression="gzip")
    return df

@lru_cache(maxsize=None)
def get_esef_xbrl_filings():
    """
    Fetches and parses the XBRL ESEF filings index, returning two DataFrames.

    Returns:
        tuple: A tuple containing two pandas.DataFrames:
            - df: DataFrame containing the parsed XBRL ESEF index data.
            - df_error: DataFrame containing error information.

    API Docs: https://filings.xbrl.org/docs/api
    Example: https://filings.xbrl.org/api/filings?include=entity&page%5Bnumber%5D=562
    """
    existing_json_filename = "../data/filing_xbrl_org_index_20250228.json"
    
    if not os.path.exists(existing_json_filename):
        xbrl_esef_index_endpoint = "https://filings.xbrl.org/index.json"
        r = requests.get(xbrl_esef_index_endpoint)

        # Check 200 HTTP status code
        assert r.status_code == 200, f"HTTP request failed with status code: {r.status_code}"
        json_string = r.content.decode('utf-8')
    else:
        with open(existing_json_filename, "r") as jfr:
            json_string = jfr.read()

    raw_data = json.loads(json_string)

    df_data = []
    df_error_data = []

    # Parse XBRL ESEF Index Object
    for d_key, d_value in raw_data.items():
        entity_name = d_value["entity"]["name"]
        
        for filing_key, filing_value in d_value["filings"].items():
            error_payload = filing_value["errors"]
            error_count = len(error_payload)
            error_codes = [d["code"] for d in error_payload]
            
            country = filing_value["country"]
            date = filing_value["date"]
            
            xbrl_json_path = filing_value.get("xbrl-json")
            xbrl_json_path = None if xbrl_json_path == "" else xbrl_json_path
            
            df_data.append({
                "key": d_key,
                "entity_name": entity_name,
                "country_alpha_2": country,
                "date": date,
                "filing_key": filing_key,
                "error_count": error_count,
                "error_codes": error_codes,
                "xbrl_json_path": xbrl_json_path
            })
            
            for error_code in error_codes:
                df_error_data.append({
                    "key": d_key,
                    "error_code": error_code
                })
    
    df = pd.DataFrame(df_data)
    df_error = pd.DataFrame(df_error_data)

    #  country code transformation
    df.loc[df['country_alpha_2'] == 'CS', 'country_alpha_2'] = 'CZ'

    # Add in country names
    country_lookup = get_wikidata_country_iso2_lookup()

    # Merge DataFrames
    df = pd.merge(df, country_lookup, on='country_alpha_2', how='left')

    return df, df_error

def calculate_country_rollup(df):
    """
    Calculates a country-wise rollup of report counts.

    Args:
        df (pandas.DataFrame): The input DataFrame containing country data.

    Returns:
        pandas.DataFrame: A DataFrame containing the country rollup information.
    """
    # Remove rows with missing countryLabel
    country_rollup = df.dropna(subset=['countryLabel']).copy()

    # Group by countryLabel and count reports
    country_rollup = country_rollup.groupby('countryLabel').size().reset_index(name='report_count')

    # Sort by report_count in descending order
    country_rollup = country_rollup.sort_values(by='report_count', ascending=False)

    return country_rollup

def flatten_dict(data, sep='.', prefix=''):
    """
    Flattens a nested dictionary into a single-level dictionary.

    Args:
        data (dict): The dictionary to flatten.
        sep (str): Separator for the flattened keys.
        prefix (str): Prefix for the flattened keys.

    Returns:
        dict: A flattened dictionary.
    """
    items = []
    for k, v in data.items():
        new_key = prefix + sep + k if prefix else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, sep=sep, prefix=new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

@lru_cache(maxsize=1)
def get_wikidata_country_iso2_lookup():
    """
    Returns a lookup table for country ISO2 codes and their corresponding labels from Wikidata.

    Returns:
        pandas.DataFrame: DataFrame with columns 'country_alpha_2' and 'countryLabel'.
    """
    # This is a placeholder.  You'll need to implement this function to
    # fetch the data from Wikidata and return a DataFrame.
    # Example:
    data = {'country_alpha_2': ['CZ', 'DE', 'FR'], 'countryLabel': ['Czechia', 'Germany', 'France']}
    return pd.DataFrame(data)