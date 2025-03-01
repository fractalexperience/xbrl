# XBRL Filings API

[filings.xbrl.org](/) API documentation: [https://filings.xbrl.org/api](https://filings.xbrl.org/api)

This sub-repository ([https://github.com/reeyarn/openesef/tree/master/openesef/filings_xbrl_org](https://github.com/reeyarn/openesef/tree/master/openesef/filings_xbrl_org)) provides a Python implementation for interacting with the [filings.xbrl.org](/) public API. The code is designed to fetch, parse, and manipulate XBRL data, specifically tailored for ESEF (European Single Electronic Format) filings.  The [filings.xbrl.org](/) API follows the [JSON API](https://jsonapi.org/) standard.

## Overview

The main functionalities of the API include:

- **Fetching XBRL Data**: Retrieve XBRL data from a specified JSON endpoint and return it as a Pandas DataFrame.
- **Flattening Nested Dictionaries**: Convert nested dictionaries into a flat structure for easier data manipulation.
- **Entity Retrieval**: Fetch entity information by making API calls and caching results for efficiency.
- **Filings Index Retrieval**: Access the filings index from the API, handling pagination and saving results locally.
- **Error Handling**: Collect and manage error information associated with filings.
- **Country Rollup Calculation**: Generate a summary of report counts by country.
- **File Integrity Verification**: Verify the SHA-256 hash of downloaded files.
- **ZIP File Downloading**: Download ZIP files from specified URLs.

## Resources provided by the filings.xbrl.org API:

*   **filing** – [`https://filings.xbrl.org/api/filings`](https://filings.xbrl.org/api/filings)
*   **entity** – [`https://filings.xbrl.org/api/entities`](https://filings.xbrl.org/api/entities)
*   **validation\_message** – [`https://filings.xbrl.org/api/validation_messages`](https://filings.xbrl.org/api/validation_messages)



## Functions

### `pluck_xbrl_json(url)`

Fetches and parses XBRL data from a JSON endpoint.

- **Args**: 
  - `url` (str): The URL of the XBRL JSON endpoint.
- **Returns**: 
  - `pandas.DataFrame`: A DataFrame containing the extracted XBRL facts.

### `flatten_dict(data, parent_key='', sep='_')`

Flattens a nested dictionary into a single-level dictionary.

- **Args**: 
  - `data` (dict): The dictionary to flatten.
  - `parent_key` (str): The prefix for keys in the flattened dictionary.
  - `sep` (str): The separator to use between keys.
- **Returns**: 
  - `dict`: A flattened dictionary.

### `get_entity_by_api(href)`

Retrieves entity information from the API.

- **Args**: 
  - `href` (str): The API endpoint for the entity.
- **Returns**: 
  - `str`: The name of the entity.

### `get_filings_index_by_api()`

Fetches the filings index from the API, handling pagination.

- **Returns**: 
  - `pandas.DataFrame`: A DataFrame containing the filings index data.

### `get_esef_xbrl_filings()`

Fetches and parses the XBRL ESEF filings index.

- **Returns**: 
  - `tuple`: A tuple containing two DataFrames: 
    - `df`: DataFrame with parsed XBRL ESEF index data.
    - `df_error`: DataFrame with error information.

### `calculate_country_rollup(df)`

Calculates a country-wise rollup of report counts.

- **Args**: 
  - `df` (pandas.DataFrame): The input DataFrame containing country data.
- **Returns**: 
  - `pandas.DataFrame`: A DataFrame containing the country rollup information.

### `get_wikidata_country_iso2_lookup()`

Returns a lookup table for country ISO2 codes and their corresponding labels from Wikidata.

- **Returns**: 
  - `pandas.DataFrame`: DataFrame with columns 'country_alpha_2' and 'countryLabel'.


### `verify_sha256_hash(file_path, expected_hash)`

Verifies the SHA-256 hash of a file to ensure its integrity.

- **Args**: 
  - `file_path` (str): The path to the file to verify.
  - `expected_hash` (str): The expected SHA-256 hash value.
- **Returns**: 
  - `bool`: True if the hash matches, False otherwise.

### `download_zip_file(url, save_path)`

Downloads a ZIP file from a specified URL and saves it to the given path.

- **Args**: 
  - `url` (str): The URL of the ZIP file to download.
  - `save_path` (str): The local path where the ZIP file will be saved.
- **Returns**: 
  - `None`: Downloads the file and saves it locally.



## Requirements

- Python 3.10
- Pandas
- Requests
- tqdm

## Usage

To use the functions provided in this module, simply import the necessary functions and call them with the appropriate parameters. Ensure that you have the required libraries installed.

```python
from openesef.filings_xbrl_org.api import get_filings_index_by_api, get_entity_by_api

df_xbrl_org = get_filings_index_by_api()
#df_xbrl_org["entity_name"] = df_xbrl_org["relationships.entity.links.related"].progress_apply(get_entity_by_api)


for index, row in df_xbrl_org.iterrows():
    zip_url = row["attributes.package_url"] # Assuming the URL is stored in this field
    #file_name = f"../data/xbrl_org/{row['entity_name']}.zip" # Customize the file name as needed
    file_name = url.split("/")[-1]
    download_zip_file(zip_url, file_name)
    # Verify the downloaded file (assuming you have the expected hash)
    expected_hash = row["attributes"]["sha256_hash"] # Assuming the expected hash is stored in this field
    if verify_sha256_hash(file_name, expected_hash):
        print(f"{file_name} downloaded and verified successfully.")
    else:
        print(f"Hash verification failed for {file_name}.")
```
