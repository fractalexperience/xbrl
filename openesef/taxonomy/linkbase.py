from ..base import fbase, const, util
from ..taxonomy import xlink


from ..util.util_mylogger import setup_logger #util_mylogger
import logging 
if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.linkbase") 


# import logging

# # Get a logger.  __name__ is a good default name.
# logger = logging.getLogger(__name__)
# #logger.setLevel(logging.DEBUG)

# # Check if handlers already exist and clear them to avoid duplicates.
# if logger.hasHandlers():
#     logger.handlers.clear()

# # Create a handler for console output.
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)

# # Create a formatter.
# log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# formatter = logging.Formatter(log_format)

# # Set the formatter on the handler.
# handler.setFormatter(formatter)

# # Add the handler to the logger.
# logger.addHandler(handler)

class Linkbase(fbase.XmlFileBase):
    def __init__(self, location, container_pool, root=None, esef_filing_root=None):
        parsers = {
            f'{{{const.NS_LINK}}}linkbase': self.l_linkbase,
            f'{{{const.NS_LINK}}}calculationLink': self.l_link,
            f'{{{const.NS_LINK}}}presentationLink': self.l_link,
            f'{{{const.NS_LINK}}}definitionLink': self.l_link,
            f'{{{const.NS_LINK}}}labelLink': self.l_link,
            f'{{{const.NS_LINK}}}referenceLink': self.l_link,
            f'{{{const.NS_GEN}}}link': self.l_link,  # Generic link
            f'{{{const.NS_LINK}}}roleRef': self.l_role_ref,
            f'{{{const.NS_LINK}}}arcroleRef': self.l_arcrole_ref
        }
        self.role_refs = {}
        self.arcrole_refs = {}
        self.refs = set({})
        self.pool = container_pool
        self.links = []
        resolved_location = util.reduce_url(location)
        if self.pool is not None:
            self.pool.discovered[location] = True
        #from openesef.base import ebase, fbase
        #this_fbase = fbase.XmlFileBase(None, container_pool, parsers, root, esef_filing_root); #self = this_fbase
        #this_ebase = ebase.XmlElementBase(None, container_pool, parsers, root, esef_filing_root); #self = this_ebase
        
        
        
        
        super().__init__(resolved_location, container_pool, parsers, root, esef_filing_root)
        if self.pool is not None:
            self.pool.linkbases[resolved_location] = self

    def l_linkbase(self, e):
        # Load files referenced in schemaLocation attribute
        for uri, href in self.schema_location_parts.items():
            logger.debug(f'linkbase.l_linkbase() calling add_reference: href = {href}, base = {self.base}, esef_filing_root = {self.esef_filing_root}')
            self.pool.add_reference(href, self.base, self.esef_filing_root)
            logger.debug(f"Added reference: {href} to {self.base} with esef_filing_root: {self.esef_filing_root}")
        self.l_children(e)

    def l_link(self, e):
        xl = xlink.XLink(e, self, esef_filing_root=self.esef_filing_root)
        self.links.append(xl)

    ''' Effectively reading roleRef and arcroleRef is the same thing here, 
        because it only discovers the corresponding schema '''
    def l_arcrole_ref(self, e):
        self.l_ref(e)

    def l_role_ref(self, e):
        self.l_ref(e)

    def l_ref(self, e):
        if self.pool is None:
            return
        xpointer = e.attrib.get(f'{{{const.NS_XLINK}}}href')
        if xpointer.startswith('#'):
            href = self.location
        else:
            href = xpointer[:xpointer.find('#')]
        fragment_identifier = xpointer[xpointer.find('#')+1:]
        self.refs.add(href)
        self.pool.add_reference(href, self.base, self.esef_filing_root)
        logger.debug(f"Added reference: {href} to {self.base} with esef_filing_root: {self.esef_filing_root}")