'''
Logic related to the handling of filings and documents
'''
from sec_xbrl.requests_wrapper import GetRequest
from sec_xbrl.document import Document
from sec_xbrl.sgml import Sgml
from sec_xbrl.dtd import DTD
from sec_xbrl.financials import get_financial_report
from datetime import datetime

from thefuzz import fuzz

FILING_SUMMARY_FILE = 'FilingSummary.xml'

import re

"""
1001003 - Statement - CONSOLIDATED BALANCE SHEETS
1002004 - Statement - CONSOLIDATED BALANCE SHEETS (Parenthetical)
1003005 - Statement - CONSOLIDATED INCOME STATEMENTS
1004006 - Statement - CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME
1005007 - Statement - CONSOLIDATED SHAREHOLDERS' EQUITY STATEMENTS
1006008 - Statement - CONSOLIDATED CASH FLOWS STATEMENTS
"""

class Statements:
    # used in parsing financial data; these are the statements we'll be parsing
    # To resolve "could not find anything for ShortName..." error, likely need
    # to add the appropriate ShortName from the FilingSummary.xml here.
    # TODO: perhaps add guessing/best match functionality to limit this list
    income_statements = ['income statement',
                    'statement income statement',
                    "statement consolidated income statement",
                    'consolidated statements of income',
                    'consolidated statements of operations',
                    'consolidated statement of earnings',
                    'condensed consolidated statements of income (unaudited)',
                    'condensed consolidated statements of income',
                    'condensed consolidated statements of operations (unaudited)',
                    'condensed consolidated statements of operations',
                    'condensed consolidated statement of earnings (unaudited)',
                    'condensed consolidated statement of earnings',
                    'condensed statements of income',
                    'condensed statements of operations',
                    'condensed statements of operations and comprehensive loss',
                    
                    ]
    balance_sheets = [
                    'balance sheet',
                    'balance sheets',
                    'statement balance sheet'
                    'statement balance sheets'
                    "statement consolidated balance sheet",
                    'consolidated balance sheets',
                    'consolidated statement of financial position',
                    'condensed consolidated statement of financial position (current period unaudited)',
                    'condensed consolidated statement of financial position (unaudited)',
                    'condensed consolidated statement of financial position',
                    'condensed consolidated balance sheets (current period unaudited)',
                    'condensed consolidated balance sheets (unaudited)',
                    'condensed consolidated balance sheets',
                    'condensed balance sheets',
                    ]
    cash_flows = [
                    "statement consolidated cash flows",
                    "statement consolidated cash flow statements",
                    "statement consolidated statement of cash flows",
                    'consolidated statements of cash flows',
                    'condensed consolidated statements of cash flows (unaudited)',
                    'condensed consolidated statements of cash flows',
                    'condensed statements of cash flows'
                    "cash flow statement",
                    "cash flows statement",
                    "cash flows",
                    "cash flow",
                    "cashflow",
                    'statement cash flow'
                    ]
    retained_earnings = ['consolidated retained earnings',
                    'consolidated statement of retained earnings',
                    'condensed consolidated statement of retained earnings',
                    'condensed statement of retained earnings'
                    'condensed consolidated statement of retained earnings (unaudited)',
                    "statement of changes in common shareholders' equity",
                    "consolidated statement of changes in common shareholders' equity",
                    "shareholders' equity statements",
                    "shareholders' equity statement",
                    "shareholders' equity",
                    "shareholders equity",
                    "shareholder equity",
                    "statement shareholders equity",
                    "retained earnings",
                    "retained earnings statement",
                    "retained earnings statements",
                    "statement retained earnings"
                    ]

    all_statements = income_statements + balance_sheets + cash_flows + retained_earnings


from datetime import datetime
from pathlib import Path
#import json
import os



class Filing:
    STATEMENTS = Statements()
    CACHE_DIR = Path('sec_reports')
    CACHE_VALIDITY_DAYS = 30  # Cache files for 30 days by default
    sgml = None

    def __init__(self, url, company=None):
        self.url = url
        self.company = company
        
        # Create base cache directory if it doesn't exist
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Load from cache or fetch and cache
        self._load_or_fetch_filing()

    def _get_cache_path(self):
        """
        Generate cache path maintaining EDGAR's folder structure
        Example URL: https://www.sec.gov/Archives/edgar/data/100885/0001437749-22-002494.txt
        Returns: sec_reports/100885/0001437749-22-002494.txt
        """
        # Extract CIK and filename using regex
        pattern = r'/data/(\d+)/(\d+-\d+-\d+\.txt)$'
        match = re.search(pattern, self.url)
        
        if not match:
            raise ValueError(f"Unable to parse CIK and filename from URL: {self.url}")
            
        cik, filename = match.groups()
        
        # Create CIK subdirectory
        cik_dir = self.CACHE_DIR / cik
        cik_dir.mkdir(exist_ok=True)
        
        return cik_dir / filename

    def _is_cache_valid(self, cache_path):
        """Check if cache file exists and is not too old"""
        if not cache_path.exists():
            return False
        
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - file_time
        return age.days < self.CACHE_VALIDITY_DAYS

    def _save_to_cache(self, text):
        """Save raw text to cache"""
        cache_path = self._get_cache_path()
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'Saved filing to cache: {cache_path}')

    def _load_from_cache(self, cache_path):
        """Load filing text from cache and process it"""
        with open(cache_path, 'r', encoding='utf-8') as f:
            self.text = f.read()
        
        #print(f'Loaded filing from cache: {cache_path}')
        
        # Process the text
        #print('Processing SGML from cache: ' + self.url)
        dtd = DTD()
        self.sgml = Sgml(self.text, dtd)
        
        # Process documents
        self.documents = {}
        for document_raw in self.sgml.map[dtd.sec_document.tag][dtd.document.tag]:
            document = Document(document_raw)
            self.documents[document.filename] = document

        # Process filing date
        acceptance_datetime_element = self.sgml.map[dtd.sec_document.tag][dtd.sec_header.tag][dtd.acceptance_datetime.tag]
        acceptance_datetime_text = acceptance_datetime_element[:8]
        self.date_filed = datetime.strptime(acceptance_datetime_text, '%Y%m%d')

    def _fetch_and_process_filing(self):
        """Fetch filing from URL and process it"""
        print(f'Fetching filing from {self.url}')
        response = GetRequest(self.url).response
        self.text = response.text
        
        # Save raw text to cache before processing
        self._save_to_cache(self.text)

        print('Processing SGML at ' + self.url)
        dtd = DTD()
        self.sgml = Sgml(self.text, dtd)

        # Process documents
        self.documents = {}
        for document_raw in self.sgml.map[dtd.sec_document.tag][dtd.document.tag]:
            document = Document(document_raw)
            self.documents[document.filename] = document

        # Process filing date
        acceptance_datetime_element = self.sgml.map[dtd.sec_document.tag][dtd.sec_header.tag][dtd.acceptance_datetime.tag]
        acceptance_datetime_text = acceptance_datetime_element[:8]
        self.date_filed = datetime.strptime(acceptance_datetime_text, '%Y%m%d')

    def _load_or_fetch_filing(self):
        """Load filing from cache if available, otherwise fetch and cache it"""
        try:
            cache_path = self._get_cache_path()
        except ValueError as e:
            print(f"Warning: {e}")
            # If we can't parse the URL, fetch without caching
            self._fetch_and_process_filing()
            return
            
        if self._is_cache_valid(cache_path):
            try:
                self._load_from_cache(cache_path)
                return
            except Exception as e:
                print(f'Error loading from cache: {e}. Fetching fresh data...')
        
        self._fetch_and_process_filing()

    def get_statements(self):
        """Get financial statements from the filing"""
        return self.STATEMENTS.process(self)



    def get_financial_data(self):
        '''
        This is mostly just for easy QA to return all financial statements
        in a given file, but the intended workflow is for he user to pick
        the specific statement they want (income, balance, cash flows)
        '''
        return self._get_financial_data(self.STATEMENTS.all_statements, True)



    def _get_financial_data(self, statement_short_names, get_all):
        '''
        Returns financial data used for processing 10-Q and 10-K documents
        '''
        financial_data = []

        for names in self._get_statement(statement_short_names):
            #names = self._get_statement(statement_short_names)[0]
            short_name = names[0]
            filename = names[1]
            #print('Getting financial data for {0} (filename: {1})'.format(short_name, filename))
            financial_html_text = self.documents[filename].doc_text.data

            financial_report = get_financial_report(company = self.company, date_filed = self.date_filed, financial_html_text = financial_html_text)

            if get_all:
                financial_data.append(financial_report)
            else:
                return financial_report

        return financial_data



    def _get_statement(self, statement_short_names):
        '''
        Return a list of tuples of (short_names, filenames) for
        statement_short_names in filing_summary_xml
        '''
        statement_names = []
        str_statements = ""; 
        str_documents = ""; 
        num_statements = 0
        if FILING_SUMMARY_FILE in self.documents:
            filing_summary_doc = self.documents[FILING_SUMMARY_FILE]
            filing_summary_xml = filing_summary_doc.doc_text.xml
            xml_string = str(filing_summary_xml)
            res_longnames = re.findall(r'<longname>(.*?)</longname>', xml_string)
            if len(res_longnames) == 0:
                raise ValueError(f'No financial documents in this filing: {self.url}')
            else:
                str_documents = "\n".join(res_longnames)
                for longname in res_longnames:
                    if re.search(r'statement', longname, re.IGNORECASE):
                        num_statements += 1
                        str_statements += f"{longname}\n"
                #print(f'Number of statements in this filing: {num_statements}')
                if num_statements == 0:
                    str_statements = '\n   '.join(res_longnames)
                    print(f"Documents in this filing: \n{str_statements}")
                    raise ValueError(f'No financial documents in this filing: {self.url}')


            for short_name in statement_short_names:
                filename = self.get_html_file_name(filing_summary_xml, short_name)
                if filename is not None:
                    statement_names += [(short_name, filename)]
        else:
            raise ValueError(f'No financial documents in this filing: {self.url}')            
        # else:
        #     print('No financial documents in this filing')

        if len(statement_names) == 0:
            print(f"Documents in this filing (for debugging): \n{str_documents}")
            raise ValueError('No financial documents could be found. Likely need to update constants in edgar.filing.Statements. See above printout for the list of documents in this filing.')
            
        return statement_names
    
    def print_statement_names_raw(self):
        if FILING_SUMMARY_FILE in self.documents:
            filing_summary_doc = self.documents[FILING_SUMMARY_FILE]
            filing_summary_xml = filing_summary_doc.doc_text.xml
            # Solution 3: Use explicit parser
            xml_string = str(filing_summary_xml)
            res_longnames = re.findall(r'<longname>(.*?)</longname>', xml_string)
            if len(res_longnames) == 0:
                raise ValueError(f'No financial documents in this filing: {self.url}')
            else:
                num_statements = 0
                for longname in res_longnames:
                    if re.search(r'statement', longname):
                        num_statements += 1
                #print(f'Number of statements in this filing: {num_statements}')
                if num_statements == 0:
                    raise ValueError(f'No financial documents in this filing: {self.url}')
            with open("/tmp/filing_summary.xml", "w") as f:
                f.write(xml_string)
            xml_bytes = xml_string.encode('utf-8')
            #parser = lxml_etree.XMLParser(encoding='utf-8')
            xml = lxml_etree.fromstring(xml_bytes)
            for child in xml.getchildren():
                print(child.tag)



    @staticmethod
    def get_html_file_name(filing_summary_xml, report_short_name):
        '''
        Return the HtmlFileName (FILENAME) of the Report in FilingSummary.xml
        (filing_summary_xml) with ShortName in lowercase matching report_short_name
        e.g.
             report_short_name of consolidated statements of income matches
             CONSOLIDATED STATEMENTS OF INCOME
        #report_short_name = balance_sheets[1]
        '''
        reports = filing_summary_xml.find_all('report')
        best_match = {
            'ratio': 75,
            'filename': None
        }        
        for report in reports:
            short_name = report.find('shortname')
            #print(short_name)
            if short_name is None:
                #print('The following report has no ShortName element')
                #print(report)
                continue
            # otherwise, get the text and keep procesing
            short_name = short_name.get_text().lower()
            short_name = re.sub(r'[^a-zA-Z\s]', ' ', short_name)

            # we want to make sure it matches, up until the end of the text
            this_ratio = fuzz.ratio(short_name, report_short_name.lower())
            if this_ratio > best_match['ratio']:
                best_match['ratio'] = this_ratio
                best_match['filename'] = report.find('htmlfilename').get_text()

        if best_match['ratio'] > 80: # this condition need to fuzzy 
            filename = best_match['filename']
            return filename
        else:
            #print(f'could not find anything for ShortName {report_short_name.lower()}')
            return None



    def get_income_statements(self):
        return self._get_financial_data(statement_short_names = self.STATEMENTS.income_statements, get_all = False)

    def get_balance_sheets(self):
        return self._get_financial_data(statement_short_names = self.STATEMENTS.balance_sheets, get_all = False)

    def get_cash_flows(self):
        return self._get_financial_data(statement_short_names = self.STATEMENTS.cash_flows, get_all = False)

    def get_retained_earnings(self):
        return self._get_financial_data(statement_short_names = self.STATEMENTS.retained_earnings, get_all = False)
