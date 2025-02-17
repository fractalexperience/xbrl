'''
This module ties it all together; it will be the main module that's used 
'''
import pandas as pd
from sec_xbrl.edgar import get_financial_filing_info, get_latest_quarter_dir, find_latest_filing_info_going_back_from, SYMBOLS_DATA_PATH
from sec_xbrl.filing import Filing
from datetime import datetime

import os
import requests
from datetime import datetime, timedelta

def update_symbols_data():
    """
    Downloads fresh company tickers data from SEC and saves it to SYMBOLS_DATA_PATH
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    try:
        response = requests.get(url, headers={"User-Agent": "yourname@yourcompany.com"})
        response.raise_for_status()
        
        # Convert JSON data to DataFrame
        data = response.json()
        df = pd.DataFrame.from_dict(data, orient='index')
        
        # Ensure CIK is padded with leading zeros to 10 digits
        df['cik_str'] = df['cik_str'].astype(str).str.zfill(10)
        
        # Save to CSV
        df.to_csv(SYMBOLS_DATA_PATH, index=False)
        print(f"Successfully updated {SYMBOLS_DATA_PATH}")
    except Exception as e:
        print(f"Error updating symbols data: {str(e)}")
        raise

def should_update_symbols_file(days=28):
    """
    Checks if the symbols file needs to be updated (older than 28 days or 4 weeks)
    """
    if not os.path.exists(SYMBOLS_DATA_PATH):
        return True
    
    file_time = datetime.fromtimestamp(os.path.getmtime(SYMBOLS_DATA_PATH))
    current_time = datetime.now()
    return (current_time - file_time) > timedelta(days=days)


# stock
class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        # Check and update symbols file if needed
        if should_update_symbols_file():
            update_symbols_data()
        self.cik = self._find_cik()


    def _find_cik(self):
        df = pd.read_csv(SYMBOLS_DATA_PATH, converters={'cik_str' : str})
        try:
            #cik = df.loc[df['symbol'] == self.symbol]['cik'].iloc[0]
            cik = df.loc[df['ticker'] == self.symbol]['cik_str'].iloc[0]
            print('cik for {} is {}'.format(self.symbol, cik))
            return cik
        except IndexError as e:
            raise IndexError('could not find cik, must add to symbols.csv') from None


    def get_filing(self, period='annual', year=0, quarter=0):
        '''
        Returns the Filing closest to the given period, year, and quarter.
        Raises NoFilingInfoException if nothing is found for the params.

        :param period: either "annual" (default) or "quarterly"
        :param year: year to search, if 0, will default latest
        :param quarter: 1, 2, 3, 4, or default value of 0 to get the latest
        '''
        filing_info_list = get_financial_filing_info(period=period, cik=self.cik, year=year, quarter=quarter)

        if len(filing_info_list) == 0:
            # get the latest
            current_year = datetime.now().year if year == 0 else year
            current_quarter = quarter if quarter > 0 else get_latest_quarter_dir(current_year)[0]
            #print('No {} filing info found for year={} quarter={}. Finding latest.'.format(period, current_year, current_quarter))

            # go back through the quarters to find the latest
            filing_info_list = find_latest_filing_info_going_back_from(period, self.cik, current_year, current_quarter)

            if len(filing_info_list) == 0:
                # we still have nothing, one last try with the previous year
                # this is useful when you're checking for data early on in a
                # calendar year, since it takes time for the filings to come in
                print('Will do a final attempt to find filing info from last year')
                filing_info_list = find_latest_filing_info_going_back_from(period, self.cik, current_year - 1, 4)

            if len(filing_info_list) == 0:
                # still not successful, throw hands up and quit
                raise NoFilingInfoException('No filing info found. Try a different period (annual/quarterly), year, and/or quarter.')

        filing_info = filing_info_list[0]

        url = filing_info.url
        filing = Filing(company=self.symbol, url=url)

        return filing



class NoFilingInfoException(Exception):
    pass


if __name__ == "__main__":
    #from sec_xbrl.stock import *
    stock = Stock("TSLA")
    filing = stock.get_filing(period='annual', year=2022)
    print(filing)
