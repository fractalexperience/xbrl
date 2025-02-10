# ESEF.jl

Link: https://github.com/trr266/ESEF.jl

## **Summary**

ESEF.jl is a Julia package designed to extract, process, and analyze data from European Single Electronic Format (ESEF) filings. ESEF is the electronic reporting format mandated for financial statements of companies listed on EU-regulated markets.  The project aims to:

1.  **Extract data:** Download and parse XBRL filings from a public index.
2.  **Transform data:** Convert XBRL data into a structured tabular format suitable for analysis.
3.  **Enrich data:** Link and integrate the ESEF data with information from Wikidata (a collaboratively edited knowledge base) and the Global Legal Entity Identifier Foundation (GLEIF).
4.  **Analyze and visualize:**  Provide tools for exploring and visualizing ESEF data.
5.  **Load into SPARQL DB:** Create local graph database for querying the XBRL filings using SPARQL.
6.  **Load into Wikidata:** Create quickstatements to upload enriched LEI-ISIN company data to Wikidata.

## **Downloading ESEF filings**


### **Data Source for XBRL Filings**

The primary source for downloading and parsing XBRL filings is, as you mentioned, `filings.xbrl.org`. The code specifically uses the index file located at:

```
https://filings.xbrl.org/index.json
```

The `get_esef_xbrl_filings()` function in `src/xbrl/esef_filings_api.jl` fetches this index, parses it, and uses the information to construct URLs for downloading the XBRL data in JSON format.

### **German ESEF Filings**

The code extracts German ESEF filings as part of the complete ESEF XBRL Index from `filings.xbrl.org`. The `get_esef_xbrl_filings()` function retrieves all filings listed in the index.

The key parts for extracting the German filings are:

1.  **`get_esef_xbrl_filings()` Function:** This function iterates through the filings in the `index.json` file.
2.  **Country Code:** Within the loop, the code extracts the `country` from each filing (`filing_value["country"]`). This country code follows the ISO 3166-1 alpha-2 standard.
3.  **Joining the Wikidata country names.**
4.  **Filtering by Country:** There's a section in the `get_esef_xbrl_filings()` function that attempts to filter by country.

```jl
    df = @transform! df @subset(
        begin
            :country_alpha_2 == "CS"
        end
    ) begin
        :country_alpha_2 = "CZ"
    end
```

This section is intended to filter by the "CS" country code (which was mapped to Czechia/Czech Republic). If you wanted to process *only* German ESEF filings, you would modify this part to filter using the German country code, which is "DE":

```jl
    df = @transform! df @subset(
        begin
            :country_alpha_2 == "DE"
        end
    ) begin
        :country_alpha_2 = "DE"
    end
```

This code will:

*   Filter the DataFrame `df` to include only rows where `:country_alpha_2` is equal to `"DE"`.
*   Then, replace all `:country_alpha_2` values in those rows with `"DE"` (which effectively does nothing in this case, but is included due to the transform! macro.)

**Important Considerations:**

*   **Completeness of `filings.xbrl.org`:** The primary limitation is the completeness and accuracy of the `filings.xbrl.org` index. If German ESEF filings are not properly indexed on that site, they won't be accessible to ESEF.jl through this approach.
*   **Alternative Sources:** If you need a more comprehensive source of German ESEF filings, you might need to explore other options, such as:
    *   **The German Federal Gazette (Bundesanzeiger):** This is the official publication platform in Germany. However, accessing and processing data from the Bundesanzeiger might require scraping or using their API (if available) and adapting the ESEF.jl code to handle the specific data format and structure.
    *   **Commercial Data Providers:** Some commercial data providers specialize in collecting and distributing financial data, including ESEF filings.
*   **Schema Variations:** Be aware that there might be slight variations in the XBRL schemas used by different countries or even different companies within a country. The ESEF.jl code might need to be adapted to handle these variations gracefully.

In summary, ESEF.jl downloads data from the public index `filings.xbrl.org`, and you can extract German ESEF filings by filtering on the "DE" country code. If you need a more comprehensive or reliable source, you might need to explore alternative data sources.



##  **Core Components & Functionality**

Here's a breakdown of the key modules and their functions:

*   **`.devcontainer`:**  Configuration for a development environment using Docker.  This ensures a consistent and reproducible environment for development and testing.

*   **`.github/workflows`:**  GitHub Actions workflows for continuous integration (CI), automated formatting, and compatibility checks.  These automate quality control and release processes.

*   **`data`:**  Contains static data like `regulated_markets.yml`, a list of regulated markets in Europe.

*   **`queries`:**  SPARQL queries used to extract data from both local Oxigraph SPARQL database and the Wikidata SPARQL endpoint.

    *   **`local`:** Contains queries to extract data from the local SPARQL database built from the ESEF XBRL filings.  Examples include:
        *   `concept_count.sparql`: Counts the occurrences of different concepts in the ESEF dataset.
        *   `equity_data.sparql`, `profit_data.sparql`, `total_assets_data.sparql`: Extracts specific financial data (equity, profit, total assets) from the ESEF dataset.
    *   **`wikidata`:** Contains queries to extract data from Wikidata.  Examples include:
        *   `company_search.sparql`: Searches for companies on Wikidata based on their name.
        *   `country_iso_2.sparql`: Retrieves ISO 2-letter country codes from Wikidata.
        *   `non_lei_isin_firms.sparql`: Finds companies with ISINs but without LEIs on Wikidata.

*   **`src`:**  The core source code of the project.

    *   **`src/dataset`:**  Deals with collecting and managing datasets relevant to ESEF.
        *   `esma_regulated_markets.jl`: Functions to retrieve and process data about regulated markets from the European Securities and Markets Authority (ESMA).  `get_regulated_markets_esma()` fetches the data, and `get_esma_regulated_countries()` extracts a list of countries.
    *   **`src/exploration`:** `visualizations.jl`: Functions to create visualizations of ESEF data, including maps and charts.
        *   `generate_esef_report_map()`: Generates a map showing ESEF report availability by country.
        *   `generate_esef_mandate_map()`: Generates a map showing ESEF mandate by country.
        *   `generate_esef_error_hist()`: Generates a histogram of ESEF filings by error count.
        *   `generate_esef_country_availability_bar()`: Generates a bar chart of ESEF report availability by country.
        *   `generate_esef_error_type_freq_bar()`: Generates a bar chart of ESEF error frequency.
        *   `generate_esef_error_country_heatmap()`: Generates a heatmap of error frequency by country.
        *   `generate_esef_publication_date_composite()`: Generates a composite visualization of report publication dates.

    *   **`src/helpers`:** Helper functions used throughout the project.
        *   `flatten_dict.jl`: `rec_flatten_dict()` function to flatten nested dictionaries, which is useful for parsing JSON data.
        *   `http_patient_post.jl`: `patient_post()` function for making HTTP POST requests with retries.
        *   `query_sparql.jl`: `query_sparql()` function to execute SPARQL queries against a SPARQL endpoint.
        *   `wikidata.jl`: Helper functions for working with Wikidata data.
        *   `truncate_text.jl`: `truncate_text()` function to truncate text strings.
        *   `unpack_value_cols.jl`: `unpack_value_cols()` function to extract values from columns containing dictionaries.

    *   **`src/lei`:**  Functions for retrieving and processing Legal Entity Identifier (LEI) data.
        *   `gleif_api.jl`: Functions for interacting with the GLEIF API to retrieve LEI data.  `get_lei_data()` retrieves LEI data, `get_lei_names()` extracts names from LEI data, and `get_isin_data()` retrieves ISINs associated with an LEI.
        *   `gleif_to_wikidata_quickstatements.jl`:  Functions for creating Wikidata QuickStatements from GLEIF LEI data. `generate_quick_statement_from_lei_obj()` generates a QuickStatement string from a GLEIF LEI object, `build_wikidata_record()` builds a Wikidata record for a given LEI, and `import_missing_leis_to_wikidata()` imports missing LEIs to Wikidata.
    *   **`src/local_sparql_db`:**  Handles the local SPARQL database.
        *   `oxigraph_server.jl`: Functions for managing an Oxigraph SPARQL server. `serve_oxigraph()` starts and stops the Oxigraph server.
        *   `sparql_api.jl`: Function `query_local_db_sparql` for querying the local Oxigraph SPARQL endpoint.
        *   `load_esef_db.jl`: Functions to build and load the ESEF data into the local SPARQL database.  `build_xbrl_dataframe()` and `build_wikidata_dataframe()` create DataFrames containing RDF triples from ESEF and Wikidata data, respectively. `serve_esef_data()` starts the Oxigraph server and loads the ESEF data into it. `export_concept_count_table()` exports the concept count table from the SPARQL database.  `export_profit_table`, `export_equity_table`, and `export_total_assets_table` export financial data tables.

    *   **`src/wikidata`:**  Functions for interacting with Wikidata.
        *   `company_data.jl`: Functions for retrieving and processing company data from Wikidata. `get_companies_with_isin_without_lei_wikidata()` retrieves companies with ISINs but without LEIs. `search_company_by_name()` searches for companies on Wikidata by name.  `get_full_wikidata_leis()` and `get_full_wikidata_isins()` retrieves all Wikidata items with LEI or ISIN properties.
        *   `iso_country_table.jl`: Function to create and memoize an ISO country code lookup table from Wikidata. `get_wikidata_country_iso2_lookup()` retrieves ISO 2-letter country codes from Wikidata.
        *   `quick_statements.jl`: Functions for building Wikidata QuickStatements.  `build_quick_statement()` constructs a QuickStatement string. `compose_merge_statement()` creates a merge statement.
        *  `sparql_api.jl`: Function `query_wikidata_sparql` for querying the Wikidata SPARQL endpoint.
        *  `currency_lookup.jl`: Function `get_iso4217_currencies` for currency lookups on Wikidata.

    *   **`src/xbrl`:**  Functions for retrieving and processing XBRL data.
        *   `esef_filings_api.jl`: Functions for interacting with the ESEF filings API. `get_esef_xbrl_filings()` retrieves metadata about ESEF filings from the filings.xbrl.org index. `pluck_xbrl_json()` retrieves and parses XBRL data from a JSON file. `calculate_country_rollup` calculates the count of reports by country.

*   **`test`:** Contains `runtests.jl`, which defines unit tests to verify the correctness of the code.

*   **`Project.toml`:**  Defines the project's dependencies.

## **ESEF Processing Workflow**

1.  **Data Acquisition:**
    *   `get_esef_xbrl_filings()` retrieves a list of ESEF filings from `filings.xbrl.org`.
    *   `pluck_xbrl_json()` fetches and parses the XBRL data in JSON format from the URLs specified in the index.

2.  **Data Transformation:**
    *   `rec_flatten_dict()` is used to flatten the nested JSON structure of the XBRL data into a tabular format.
    *   The code then transforms this flattened data into a DataFrame.
    *   `unpack_value_cols` extracts values from dictionary columns.

3.  **Data Enrichment:**
    *   `get_lei_data()` fetches LEI data from GLEIF API.
    *   `get_companies_with_isin_without_lei_wikidata()`  queries Wikidata to identify companies with ISINs but no LEIs.
    *   `get_wikidata_country_iso2_lookup()` retrieves ISO country codes.

4.  **Data Storage (SPARQL):**

    *   `build_xbrl_dataframe` builds a Dataframe of rdf triples, which are written to an `.nt` file
    *   `serve_esef_data()` loads the .nt file into an `oxigraph` server.
    *  The server is then queried to extract the XBRL facts in a structured table.

5.  **Data Loading into Wikidata**

    *   `generate_quick_statement_from_lei_obj()` converts LEI data retrieved from the GLEIF API, along with linked ISINs, into Wikidata QuickStatements format.
    *   QuickStatements are used to create new items or add data to existing items on Wikidata.

## **Uploading to Wikidata**

The `lei/gleif_to_wikidata_quickstatements.jl` module provides the core functionality for uploading data to Wikidata:

1.  **`generate_quick_statement_from_lei_obj()`:** Takes a dictionary containing information about a legal entity (obtained from GLEIF) and generates a QuickStatement string.  The QuickStatement includes the entity's legal name, LEI, country, and ISINs.
2.  **`import_missing_leis_to_wikidata()`:** Takes a list of LEIs, retrieves the corresponding data from the GLEIF API, and generates QuickStatements to create new Wikidata items for these LEIs.  It then writes these QuickStatements to a text file.

To upload the data to Wikidata:

1.  **Run `import_missing_leis_to_wikidata()`:** Call the function with a list of LEIs that you want to add to Wikidata.  This will generate a text file containing the QuickStatements.
2.  **Use the QuickStatements tool:** Go to the QuickStatements tool on Wikidata (<https://quickstatements.toolforge.org/>).
3.  **Upload the QuickStatements file:** Upload the text file generated by `import_missing_leis_to_wikidata()` to the QuickStatements tool.
4.  **Review and execute the statements:** Review the QuickStatements in the tool and execute them to add the data to Wikidata.

**Important Notes:**

*   **Rate Limiting:** The GLEIF API is rate-limited to 1 request per second. The code includes `sleep(1)` calls to respect this limit. The Wikidata SPARQL endpoint also has rate limits.
*   **Wikidata Editing:** Be mindful of Wikidata's policies when adding or modifying data.  Ensure that the data is accurate and verifiable.
*   **Error Handling:** The code includes basic error handling (e.g., checking HTTP status codes), but more robust error handling may be needed for production use.
*   **Dependencies:** The `Project.toml` file lists all the dependencies of the project.  Make sure to install these dependencies before running the code.
*   **Configuration:** The project uses configuration files (e.g., `regulated_markets.yml`) and environment variables to manage settings.
*   **SPARQL queries:** Note that some SPARQL queries can take a long time to execute and are limited in the number of rows returned (e.g. 1000000).

In summary, ESEF.jl is a comprehensive tool for working with ESEF data, from extraction and transformation to enrichment and analysis. It leverages external APIs (GLEIF, Wikidata) and local SPARQL database to provide a rich set of functionalities for exploring and understanding ESEF filings.
