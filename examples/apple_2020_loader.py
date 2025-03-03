from openesef.util.util_mylogger import setup_logger 
import logging 

from openesef.util.parse_concepts import get_presentation_networks

if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.edgar") 

from openesef.edgar.loader import load_xbrl_filing

xid, tax = load_xbrl_filing(ticker="AAPL", year=2020)

print(xid)
print(tax)

for i, (key, value) in enumerate(xid.dei.items()):
    print(f"{i}: {key}: {value}")


get_presentation_networks(tax)