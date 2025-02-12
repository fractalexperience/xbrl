from ..taxonomy import concept, linkbase, roletype, arcroletype, simple_type, item_type, tuple_type
from ..base import fbase, const, element, util
import os

import logging

# Get a logger.  __name__ is a good default name.
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

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

class Schema(fbase.XmlFileBase):
    def __init__(self, location, container_pool, esef_filing_root=None):
        self.target_namespace = ''
        self.target_namespace_prefix = ''
        parsers = {
            f'{{{const.NS_XS}}}schema': self.l_schema,
            f'{{{const.NS_XS}}}annotation': self.l_annotation,
            f'{{{const.NS_XS}}}appinfo': self.l_appinfo,
            f'{{{const.NS_LINK}}}linkbase': self.l_linkbase,
            f'{{{const.NS_XS}}}import': self.l_import,
            f'{{{const.NS_LINK}}}linkbaseRef': self.l_linkbase_ref,
            f'{{{const.NS_LINK}}}roleType': self.l_roletype,
            f'{{{const.NS_LINK}}}arcroleType': self.l_arcroletype,
            f'{{{const.NS_XS}}}element': self.l_element,
            f'{{{const.NS_XS}}}complexType': self.l_complex_type,
            f'{{{const.NS_XS}}}simpleType': self.l_complex_type,
        }
        self.imports = {}
        self.linkbase_refs = {}
        """ Elements, which are concepts """
        self.concepts = {}
        """ Elements, which are not concepts """
        self.elements = {}
        self.elements_by_id = {}
        """ Role types in the schema """
        self.role_types = {}
        """ Arcrole types in the schema """
        self.arcrole_types = {}
        """ Simple types """
        self.simple_types = {}
        """ Complex types with simple content: Key is qname, value is the item type object """
        self.item_types = {}
        """ Complex types with simple content: Key is unique identifier, value is the item type object """
        self.item_types_by_id = {}
        """ Complex types with complex content: Key is qname, value is the tuple type object """
        self.tuple_types = {}
        """ Complex types with complex content: Key is unique identifier, value is the tuple type object """
        self.tuple_types_by_id = {}

        self.pool = container_pool
        resolved_location = util.reduce_url(location)
        if self.pool is not None:
            self.pool.discovered[location] = True

        #this_fb =  fbase.XmlFileBase(location=None, container_pool=None, parsers=None, root=None, esef_filing_root = None); self = this_fb
        super().__init__(location = resolved_location, 
                         container_pool = container_pool, 
                         parsers = parsers, 
                         esef_filing_root=esef_filing_root)
        
        if self.pool is not None:
            self.pool.schemas[resolved_location] = self

    def l_schema(self, e):
        self.target_namespace = e.get('targetNamespace')
        self.target_namespace_prefix = self.namespaces_reverse.get(self.target_namespace, None)
        # Load files referenced in schemaLocation attribute
        for uri, href in self.schema_location_parts.items():
            logger.debug(f'schema.l_schema() calling add_reference: href = {href}, base = {self.base}, esef_filing_root = {self.esef_filing_root}')
            self.pool.add_reference(href, self.base, self.esef_filing_root)
            logger.debug(f"Added reference: {href} to {self.base} with esef_filing_root: {self.esef_filing_root}")
        self.l_children(e)

    def l_element(self, e):
        sgr = e.attrib.get('substitutionGroup')
        if sgr is not None:
            concept.Concept(e, self)
        else:
            element.Element(e, self)

    def l_complex_type(self, e):
        name = e.attrib.get('name')
        if name in const.xbrl_types:
            return  # Basic types are predefined.
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_XS}}}simpleContent':
                item_type.ItemType(e, self)
            if e2.tag == f'{{{const.NS_XS}}}complexContent':
                tuple_type.TupleType(e, self)

    def l_simple_type(self, e):
       simple_type.SimpleType(e, self)

    def l_annotation(self, e):
        self.l_children(e)

    def l_appinfo(self, e):
        self.l_children(e)

    def l_linkbase(self, e):
        # Loading a linkbase, which is positioned internally inside annotation/appinfo element of the schema.
        lb = linkbase.Linkbase(self.location, self.pool, e, self.esef_filing_root)
        self.pool.linkbases[self.location] = lb
        self.pool.current_taxonomy.attach_linkbase(self.location, lb)

    def l_linkbase_ref(self, e):
        href = e.get(f'{{{const.NS_XLINK}}}href')
        if not href.startswith('http'):
            href = util.reduce_url(os.path.join(self.base, href).replace('\\', '/'))
        self.linkbase_refs[href] = e
        self.pool.add_reference(href, self.base, self.esef_filing_root)
        logger.debug(f"Added reference: {href} to {self.base} with esef_filing_root: {self.esef_filing_root}")
    def l_roletype(self, e):
        roletype.RoleType(e, self)

    def l_arcroletype(self, e):
        arcroletype.ArcroleType(e, self)

    def l_import(self, e):
        href = e.get('schemaLocation')
        self.imports[href] = e
        self.pool.add_reference(href, self.base, self.esef_filing_root)
        logger.debug(f"Added reference: {href} to {self.base} with esef_filing_root: {self.esef_filing_root}")
