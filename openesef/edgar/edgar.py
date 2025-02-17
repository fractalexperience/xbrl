'''
This file will be used to traverse the EDGAR filing system and determine
the location of filings

https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm

The EDGAR indexes list the following information for each filing: Company Name,
Form Type, CIK (Central Index Key), Date Filed, and File Name (including folder
path).

Four types of indexes are available. The company, form, and master indexes
contain the same information sorted differently.

company — sorted by company name
form — sorted by form type
master — sorted by CIK number
XBRL — list of submissions containing XBRL financial files, sorted by CIK
    number; these include Voluntary Filer Program submissions

Forms that we'll be concerned with (all forms are listed at
https://www.sec.gov/forms):
    10-Q: quarterly report and financial statements
    10-K: annual report and financial statements
    8-K: important events (commonly filed)
    4: insider trading (gets us the stock symbol (issuerTradingSymbol))
These can all have ammendments made, e.g. 10-Q/A
'''
from requests_wrapper import GetRequest
import json
import re
from datetime import datetime
import os


#SYMBOLS_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'symbols.csv')


FINANCIAL_FORM_MAP = {
    'annual': ['10-K','10-K/A', "20-K", "20-K/A", "40-F"],
    'quarterly': ['10-Q','10-Q/A', ],
    'agm': ["DEF14A", 'DEFA14A'],
    'other': ['3', '4', '5']
}
SUPPORTED_FORMS = FINANCIAL_FORM_MAP['annual'] + FINANCIAL_FORM_MAP['quarterly'] + FINANCIAL_FORM_MAP['agm'] + FINANCIAL_FORM_MAP['other']

EDGAR_MIN_YEAR = 1993

ARCHIVES_URL = 'https://www.sec.gov/Archives/'
FULL_INDEX_URL = ARCHIVES_URL+'edgar/full-index/'
INDEX_JSON = 'index.json'
# company.idx gives us a list of all companies that filed in the period
COMPANY_IDX = 'company.idx' # sorted by company name
FORM_IDX = 'form.idx' # sorted by form type
MASTER_IDX = 'master.idx' # sorted by cik
#CRAWLER_IDX = 'crawler.idx'
#XBRL_IDX = 'xbrl.idx'


# don't need the following structures, commenting them just in case
# class Directory():
# 	'''
# 	Directory and Item classes will be used to help model and serve as a reference
# 	'''
# 	def __init__(self, item, name, parent_dir):
# 		self.item = item # array of items in the directory
# 		self.name = name # name of the directory
# 		self.parent_dir = parent_dir # location of parent directory

# class Item():
# 	def __init__(self, last_modified, name, type, href, size):
# 		self.last_modified = last_modified # MM/dd/YYYY hh:mm:ss AM/PM
# 		self.name = self.name
# 		self.type = self.type # dir or file
# 		self.href = self.href # relative to directory
# 		self.size = self.size



class FilingInfo:
    '''
    FilingInfo class will model crawler.idx filing information
    '''
    def __init__(self, company, form, cik, date_filed, file):
        self.company = company
        self.form = form
        self.cik = cik
        self.date_filed = date_filed
        self.url = ARCHIVES_URL+file

    def __repr__(self):
        return '[{0}, {1}, {2}, {3}, {4}]'.format(
            self.company, self.form, self.cik, self.date_filed, self.url)
        


def get_index_json(year='', quarter=''):
    '''
    Returns json of index.json
        year and quarter are defaulted to '', but can be replaced with an item.href
        from index.json
    '''
    url = FULL_INDEX_URL+year+quarter+INDEX_JSON
    # print('getting data at '+url)

    response = GetRequest(url).response
    text = response.text

    json_text = json.loads(text)
    #print(text)
    #print(json['directory']['item'][0]['href'])
    return json_text



def get_latest_quarter_dir(year):
    '''
    Given a year (e.g. 2018), traverse the items in index.json to find
    the latest quarter, returning the number (e.g. 1, 2, 3, 4) and the
    reference in the system (e.g. 'QTR4/')
    '''
    year_str = str(year)+'/'
    index_json = get_index_json(year=year_str)
    items = index_json['directory']['item']

    # item list is in order, with the latest at the end
    for i in reversed(range(len(items))):
        item = items[i]

        if item['type'] == 'dir':
            # return the 
            #str_qtr = item['name'].replace('QTR',''); 
            str_qtr = re.sub(r'\D', '', item['name'])
            int_qtr = int(str_qtr); 
            if int_qtr in [1,2,3,4]:
                return int_qtr, item['href']
            else:
                print(f"Invalid quarter: {int_qtr}")


def find_latest_filing_info_going_back_from(period, cik, year, quarter):
    '''
    Returns the latest filing info list in the given year, going backwards from
    the given year and quarter
    '''
    filing_info_list = []
    while quarter > 0 and len(filing_info_list) == 0:
        filing_info_list = get_financial_filing_info(period=period, cik=cik, year=year, quarter=quarter)
        quarter -= 1

    return filing_info_list


def get_filing_info(cik='', forms=[], year=0, quarter=0):
    '''
    Public wrapper to get FilingInfo for a given company, type of form, and 
    period
    '''
    current_year = datetime.now().year

    if year!=0 and ((len(str(year)) != 4) or year < EDGAR_MIN_YEAR or year > current_year):
        raise InvalidInputException('{} is not a supported year'.format(year))
    if quarter not in [0, 1, 2, 3, 4]:
        raise InvalidInputException('Quarter must be 1, 2, 3, or 4. 0 indicates default (latest)')

    year_str = '' if year==0 else str(year)+'/'
    quarter_str = '' if quarter==0 else 'QTR{}/'.format(quarter)

    if quarter == 0 and year != 0:
        # we just want the latest available
        quarter_str = get_latest_quarter_dir(year)[1]

    return _get_filing_info(cik=cik, forms=forms, year=year_str, quarter=quarter_str)

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def _get_cache_path(year, quarter):
    """Create cache directory if it doesn't exist and return cache file path"""
    cache_dir = Path('edgar_cache')
    cache_dir.mkdir(exist_ok=True)
    filename = f'master_idx_{year}_{quarter}.txt'
    filename = filename.replace('/', '_')
    return os.path.join(cache_dir, filename)

def _is_cache_valid(cache_path, max_age_days=1):
    """Check if cache file exists and is not too old"""
    if not os.path.exists(cache_path):
        return False
    
    file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
    age = datetime.now() - file_time
    return age.days < max_age_days

def _get_filing_info(cik='', forms=[], year='', quarter=''):
    """
    Return a List of FilingInfo
    If forms are specified, only filings with the given value will be returned
    e.g. 10-K, 10-Q, 3, 4, 5
    """
    def _get_raw_data(row):
        return row.split('|')

    def _add_filing_info(filing_infos, data, forms):
        if len(data) == 5 and (forms == [] or data[2] in forms):
            filing_infos.append(FilingInfo(
                data[1],  # Company Name
                data[2],  # Form Type
                data[0],  # CIK
                data[3],  # Date Filed
                data[4].strip()  # File Name
            ))

    for form in forms:
        if form not in SUPPORTED_FORMS:
            raise InvalidInputException(f'{form} is not a supported form')

    # Check cache first
    cache_path = _get_cache_path(year, quarter)
    
    if _is_cache_valid(cache_path):
        #print(f'Using cached data from {cache_path}')
        with open(cache_path, 'r') as f:
            text = f.read()
    else:
        # If cache doesn't exist or is too old, fetch from URL
        url = f'{FULL_INDEX_URL}{year}{quarter}{MASTER_IDX}'
        print(f'Fetching filing info from {url}')
        
        response = GetRequest(url).response
        text = response.text
        
        # Save to cache
        with open(cache_path, 'w') as f:
            f.write(text)
        print(f'Saved response to cache: {cache_path}')

    rows = text.split('\n')
    data_rows = rows[11:]
    filing_infos = []

    if cik != '':
        # Binary search to get company's filing info
        start = 0
        end = len(data_rows)

        while start < end:
            mid = (start + end) // 2
            data = _get_raw_data(data_rows[mid])

            if data[0] == cik:
                # matched cik
                _add_filing_info(filing_infos, data, forms)

                # Get all before and after (there can be multiple)
                # Go backwards to get those before
                index = mid - 1
                data = _get_raw_data(data_rows[index])
                while data[0] == cik and index >= 0:
                    _add_filing_info(filing_infos, data, forms)
                    index -= 1
                    data = _get_raw_data(data_rows[index])

                # After
                index = mid + 1
                data = _get_raw_data(data_rows[index])
                while data[0] == cik and index < len(data_rows):
                    _add_filing_info(filing_infos, data, forms)
                    index += 1
                    data = _get_raw_data(data_rows[index])

                break

            elif data[0] < cik:
                start = mid + 1
            else:
                end = mid - 1
    else:
        # Go through all
        for row in data_rows:
            data = _get_raw_data(row)
            _add_filing_info(filing_infos, data, forms)

    return filing_infos


def get_financial_filing_info(period, cik, year='', quarter=''):
    if period not in FINANCIAL_FORM_MAP:
        raise KeyError('period must be either "annual" or "quarterly"')

    forms = FINANCIAL_FORM_MAP[period]
    return get_filing_info(cik=cik, forms=forms, year=year, quarter=quarter)



########## Exceptions ##########
class InvalidInputException(Exception):
    pass