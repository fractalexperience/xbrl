from openesef.edgar.loader import load_xbrl_filing
from openesef.util.util_mylogger import setup_logger 
import logging 

if __name__=="__main__":
    logger = setup_logger("main", logging.DEBUG, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.edgar") 


xid, tax = load_xbrl_filing(ticker="AAPL", year=2020)

print(xid)
print(tax)

for i, (key, value) in enumerate(xid.dei.items()):
    print(f"{i}: {key}: {value}")
