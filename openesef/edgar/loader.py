
# openesef/edgar/loader.py
from openesef.base.pool import Pool
from openesef.taxonomy.taxonomy import Taxonomy
from openesef.edgar.edgar import EG_LOCAL
from openesef.edgar.stock import Stock
from openesef.edgar.filing import Filing
from openesef.instance.instance import Instance
import fs
from lxml import etree as lxml_etree
from io import BytesIO
import logging

#logger = logging.getLogger(__name__) # Get logger for this module

from openesef.util.util_mylogger import setup_logger 

if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.edgar") 


def load_xbrl_filing(ticker=None, year=None, filing_url=None, edgar_local_path='/text/edgar'):
    """
    Loads an XBRL filing either by ticker and year or by URL.

    Args:
        ticker (str, optional): Stock ticker symbol. Defaults to None.
        year (int, optional): Filing year. Defaults to None.
        filing_url (str, optional): URL of the filing. Defaults to None.
        edgar_local_path (str, optional): Path to local Edgar repository. Defaults to '/text/edgar'.

    Returns:
        tuple: A tuple containing the Instance object (xid) and the Taxonomy object (this_tax), or (None, None) on failure.
    """
    memfs = fs.open_fs('mem://') # Create in-memory filesystem
    egl = EG_LOCAL(edgar_local_path)

    if ticker and year:
        stock = Stock(ticker, egl=egl)
        filing = stock.get_filing(period='annual', year=year)
    elif filing_url:
        filing = Filing(url=filing_url, egl=egl)
    else:
        logger.error("Either ticker and year or filing_url must be provided.")
        return None, None

    if not filing:
        logger.error("Filing not found.")
        return None, None

    entry_points = []
    for key, filename in filing.xbrl_files.items():
        logger.debug(f"Caching XBRL file: {key}, {filename}")
        content = filing.documents[filename].doc_text.data
        content = list(content.values())[0] if isinstance(content, dict) else content
        with memfs.open(filename, 'w') as f:
            f.write(content)
        logger.debug(f"Cached {filename} to memory, length={len(content)}")
        if "xml" in filename:
            entry_points.append(f"mem://{filename}")

    data_pool = Pool(max_error=32, esef_filing_root="mem://", memfs=memfs)
    this_tax = Taxonomy(
        entry_points=entry_points,
        container_pool=data_pool,
        esef_filing_root="mem://",
        memfs=memfs
    )
    data_pool.current_taxonomy = this_tax

    xid = None
    if filing.xbrl_files.get("xml"):
        xml_filename = filing.xbrl_files.get("xml")
        instance_str = filing.documents[xml_filename].doc_text.data
        instance_str = list(instance_str.values())[0] if isinstance(instance_str, dict) else instance_str
        instance_byte = instance_str.encode('utf-8')
        instance_io = BytesIO(instance_byte)
        instance_tree = lxml_etree.parse(instance_io)
        root = instance_tree.getroot()
        data_pool.cache_from_string(location=xml_filename, content=instance_str, memfs=memfs)
        xid = Instance(container_pool=data_pool, root=root, memfs=memfs)
    else:
        logger.warning("No XML instance document found in filing.")

    return xid, this_tax