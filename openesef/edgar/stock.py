'''
This module ties it all together; it will be the main module that's used 

- 2025-02-14: Updated `stock.py` to update the symbols data file using the SEC Disclosure Data API. 
  - https://www.sec.gov/files/company_tickers.json
  - This file is used to update the `symbols.csv` file, which contains the list of companies and their associated financial filings.
  - The `symbols.csv` file is used to fetch the filing information based on the company symbol.

'''
import pandas as pd
from .edgar import get_financial_filing_info, get_latest_quarter_dir, find_latest_filing_info_going_back_from, EG_LOCAL #,SYMBOLS_DATA_PATH
from .filing import Filing
from datetime import datetime
#import pandas as pd 
import os
import requests
from datetime import datetime, timedelta


from openesef.util.util_mylogger import setup_logger #util_mylogger
import logging 
if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.edgar") 

def update_symbols_data(egl = EG_LOCAL('edgar')):
    """
    Downloads fresh company tickers data from SEC and saves it to egl.symbols_data_path (updated from edgar.SYMBOLS_DATA_PATH)
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    try:
        response = requests.get(url, headers={"User-Agent": "yourname@yourcompany.com"})
        response.raise_for_status()
        
        # Convert JSON data to DataFrame
        data = response.json()
        df = pd.DataFrame.from_dict(data, orient='index')
        
        # Ensure CIK is padded with leading zeros to 10 digits
        df['cik_str'] = df['cik_str'].astype(str) #.str.zfill(10)
        
        # Save to CSV
        df.to_csv(egl.symbols_data_path, index=False)
        logger.debug(f"Successfully updated {egl.symbols_data_path}")
    except Exception as e:
        logger.error(f"Error updating symbols data: {str(e)}")
        raise

def should_update_symbols_file(days=28, egl = EG_LOCAL('edgar')):
    """
    Checks if the symbols file needs to be updated (older than 28 days or 4 weeks)
    """
    if not os.path.exists(egl.symbols_data_path):
        return True
    
    file_time = datetime.fromtimestamp(os.path.getmtime(egl.symbols_data_path))
    current_time = datetime.now()
    return (current_time - file_time) > timedelta(days=days)


# stock
class Stock:
    def __init__(self, symbol, egl = EG_LOCAL('edgar')):
        self.symbol = symbol
        # Check and update symbols file if needed
        self.egl = egl
        if should_update_symbols_file(egl = egl):
            update_symbols_data(egl = egl)
        self.cik = self._find_cik()
    def __str__(self):
        return f"Stock(symbol={self.symbol}, cik={self.cik})"
    def __repr__(self):
        return self.__str__()

    def _find_cik(self):
        df = pd.read_csv(self.egl.symbols_data_path, converters={'cik_str' : str})
        try:
            #cik = df.loc[df['symbol'] == self.symbol]['cik'].iloc[0]
            cik = df.loc[df['ticker'] == self.symbol]['cik_str'].iloc[0]
            logger.debug(f'cik for {self.symbol} is {cik}')
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
        filing_info_list = get_financial_filing_info(period=period, cik=self.cik, year=year, quarter=quarter, egl=self.egl)

        if len(filing_info_list) == 0:
            # get the latest
            current_year = datetime.now().year if year == 0 else year
            current_quarter = quarter if quarter > 0 else get_latest_quarter_dir(current_year)[0]
            logger.debug(f'No {period} filing info found for year={current_year} quarter={current_quarter}. Finding latest.')

            # go back through the quarters to find the latest
            filing_info_list = find_latest_filing_info_going_back_from(period, self.cik, current_year, current_quarter, egl = self.egl)

            if len(filing_info_list) == 0:
                # we still have nothing, one last try with the previous year
                # this is useful when you're checking for data early on in a
                # calendar year, since it takes time for the filings to come in
                logger.debug('Will do a final attempt to find filing info from last year')
                filing_info_list = find_latest_filing_info_going_back_from(period, self.cik, current_year - 1, 4, egl = self.egl)

            if len(filing_info_list) == 0:
                # still not successful, throw hands up and quit
                raise NoFilingInfoException('No filing info found. Try a different period (annual/quarterly), year, and/or quarter.')

        filing_info = filing_info_list[0]

        url = filing_info.url
        filing = Filing(company=self.symbol, url=url, egl = self.egl)

        return filing



class NoFilingInfoException(Exception):
    pass


if __name__ == "__main__":
    #from sec_xbrl.stock import *
    stock = Stock("TSLA")
    filing = stock.get_filing(period='annual', year=2022)
    print(filing)
