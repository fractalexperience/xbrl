#  Project Contents
## __init__.py
```py
from . import tuple_type
from . import xlink
from . import tpack
from . import resource
from . import locator
from . import base_set
from . import item_type
from . import roletype
from . import taxonomy
from . import concept
from . import simple_type
from . import arcroletype
from . import arc
from . import linkbase
from . import schema

# Import subpackages
from . import table
from . import formula
from . import xdt
```

## arc.py
```py
from ..base import ebase, const, util


class Arc(ebase.XmlElementBase):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        self.xl_from = e.attrib.get(f'{{{const.NS_XLINK}}}from')
        self.xl_to = e.attrib.get(f'{{{const.NS_XLINK}}}to')
        self.arcrole = e.attrib.get(f'{{{const.NS_XLINK}}}arcrole')
        self.order = e.attrib.get('order')
        self.priority = e.attrib.get('priority')
        self.use = e.attrib.get('use')
        self.weight = e.attrib.get('weight')
        self.preferredLabel = e.attrib.get('preferredLabel')
        u = e.attrib.get(f'{{{const.NS_XBRLDT}}}usable')
        self.usable = False if u is not None and u in ['false', '0'] else True
        self.target_role = e.attrib.get(f'{{{const.NS_XBRLDT}}}targetRole')
        self.axis = e.attrib.get('axis')  # for tableBreakdownArc
        if self.xlink is not None:
            self.xlink.arcs_from.setdefault(f'{self.arcrole}|{self.xl_from}', []).append(self)
            self.xlink.arcs_to.setdefault(f'{self.arcrole}|{self.xl_to}', []).append(self)
```

## arcroletype.py
```py
from ..base import ebase, const, util


class ArcroleType(ebase.XmlElementBase):
    def __init__(self, e, container_schema=None):
        self.schema = container_schema
        self.definition = None
        self.arcrole_uri = e.attrib.get('arcroleURI')
        self.cycles_allowed = e.attrib.get('cyclesAllowed')
        self.used_on = []
        self.labels = {}
        parsers = {
            f'{{{const.NS_LINK}}}arcroleType': self.l_children,
            f'{{{const.NS_LINK}}}definition': self.l_definition,
            f'{{{const.NS_LINK}}}usedOn': self.l_used_on
        }
        super().__init__(e, parsers)
        if self.id is not None:
            self.schema.arcrole_types[self.arcrole_uri] = self

    def l_definition(self, e):
        self.definition = e.text

    def l_used_on(self, e):
        self.used_on.append(e.text)

    def get_label(self):
        lbl = util.get_label(self.labels)
        return self.definition if lbl is None or lbl == '' else lbl
```

## base_set.py
```py
from ..base import data_wrappers, const


class BaseSet:
    def __init__(self, arc_name, arcrole, role):
        self.arc_name = arc_name
        self.arcrole = arcrole
        self.role = role
        self.roots = []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def get_key(self):
        return f'{self.arc_name}|{self.arcrole}|{self.role}'

    """
    start_concept - Concept to be considered root of the branch. If None, then processing starts from hierarchy root.
    include_head - Flag whether to include root of the branch into the result set.
    s_groups - List of substitution groups to be included in processing. If it is None, then all are processed.
    """

    def get_members(self, start_concept=None, include_head=True, s_groups=None):
        members = []
        for r in self.roots:
            r_label = r.get_label()
            self.get_branch_members(r, r_label, members, start_concept, include_head, False, 0, None, [r], s_groups)
        return members

    def get_branch_members(
            self, concept, label_pref, members, start_concept, inc_head,
            flag_include, level, related_arc, stack, s_groups=None):
        if concept is None:
            return
        trigger_include = (not start_concept and level == 0) or (start_concept and start_concept == concept.qname)
        new_flag_include = flag_include or trigger_include

        cbs_dn = concept.chain_dn.get(self.get_key(), None)
        is_leaf = True if cbs_dn is None else False
        if (trigger_include and inc_head) or flag_include:
            members.append(data_wrappers.BaseSetNode(concept, level, related_arc, is_leaf, label_pref))

        if cbs_dn is None:
            return
        # Recursion
        lst = sorted([n for n in cbs_dn if n.Concept not in stack],
                     key=lambda t: 0 if t.Arc.order is None else float(t.Arc.order))
        used = set()
        balance = None
        for node in lst:
            if node.Concept.qname in used or (s_groups is not None and node.Concept.substitution_group not in s_groups):
                continue
            if balance is None:
                balance = node.Concept.balance  # Set only first time
            used.add(node.Concept.qname)
            stack.append(node.Concept)
            # Find preferred label
            node_lbl = node.Concept.get_label()
            node_lbl_pref = node_lbl
            if node.Arc.preferredLabel:
                node_lbl_pref = node.Concept.get_label(role=node.Arc.preferredLabel)
            if not node_lbl_pref:
                node_lbl_pref = node_lbl

            self.get_branch_members(
                node.Concept, node_lbl_pref, members, start_concept, inc_head,
                new_flag_include, level + 1, node.Arc, stack, s_groups)
            stack.remove(node.Concept)

    def get_langs(self):
        langs = set()
        lbls = [n.Concept.resources.get('label', {}) for n in self.get_members()]
        for dct in lbls:
            for v in dct.values():
                for lbl in v:
                    langs.add(lbl.lang)
        return langs

    def info(self):
        rts = ','.join([r.qname for r in self.roots])
        return '\n'.join([
            f'Arc name: {self.arc_name}',
            f'Arc role: {self.arcrole}',
            f'Role: {self.role}',
            f'Roots: {rts}'])
```

## concept.py
```py
from ..base import const, element, util


class Concept(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        # Basic properties
        self.period_type = e.attrib.get(f'{{{const.NS_XBRLI}}}periodType')
        self.balance = e.attrib.get(f'{{{const.NS_XBRLI}}}balance')
        self.data_type = e.attrib.get('type')
        # Extensible enumerations properties
        domain = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}domain')
        domain2 = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS_2}}}domain')
        self.domain = domain if domain is not None else domain2
        linkrole = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}linkrole')
        linkrole2 = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS_2}}}linkrole')
        self.linkrole = linkrole if linkrole is not None else linkrole2
        hu = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}headUsable')
        hu2 = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS_2}}}headUsable')
        self.head_usable = hu is not None and (hu.lower() == 'true' or hu == '1') or \
            hu2 is not None and (hu2.lower() == 'true' or hu == '1')
        # XDT specific properties
        self.typed_domain_ref = e.attrib.get(f'{{{const.NS_XBRLDT}}}typedDomainRef')
        self.is_dimension = self.substitution_group.endswith('dimensionItem')
        self.is_hypercube = self.substitution_group.endswith('hypercubeItem')
        self.is_explicit_dimension = True if self.is_dimension and self.typed_domain_ref is None else False
        self.is_typed_dimension = True if self.is_dimension and self.typed_domain_ref is not None else False
        self.is_enumeration = True if self.data_type and self.data_type.endswith('enumerationItemType') else False
        self.is_enumeration_set = True if self.data_type and self.data_type.endswith('enumerationSetItemType') else False

        if self.schema is not None:
            self.namespace = self.schema.target_namespace
        # Collections
        self.resources = {}  # Related labels - first by lang and then by role
        self.references = {}  # Related reference resources
        self.chain_up = {}  # Related parent concepts. Key is the base set key, value is the list of parent concepts
        self.chain_dn = {}  # Related child concepts. Key is the base set key, value is the list of child concepts

        unique_id = f'{self.namespace}:{self.name}'
        self.schema.concepts[unique_id] = self

    def __str__(self):
        return self.qname

    def __repr__(self):
        return self.qname

    def get_label(self, lang='en', role='/label'):
        return util.get_label(self.resources, lang, role)

    def get_label_or_qname(self, lang='en', role='/label'):
        lbl = util.get_label(self.resources, lang, role)
        return lbl if lbl else self.qname

    def get_label_or_name(self, lang='en', role='/label'):
        lbl = util.get_label(self.resources, lang, role)
        return self.name if lbl is None else lbl

    def get_lang(self):
        return util.get_lang(self.resources)

    def get_enum_label(self, role):
        labels = self.resources.get('label', None)
        if labels is None:
            return None
        candidates = [l for lbls in labels.values() for l in lbls if l.xlink.role == role]
        if not candidates:
            return util.get_label(self.resources)
        return candidates[0].text

    def get_reference(self, lang='en', role='/label'):
        return util.get_reference(self.resources, lang, role)

    def info(self):
        return '\n'.join([
            f'QName: {self.qname}',
            f'Data type: {self.data_type}',
            f'Abstract: {self.abstract}',
            f'Nillable: {self.nillable}',
            f'Period Type: {self.period_type}',
            f'Balance: {self.balance}'])
```

## formula/__init__.py
```py
from . import existence_assertion
from . import assertion
from . import consistency_assertion
from . import filter
from . import assertion_set
from . import parameter
from . import value_assertion
```

## formula/assertion.py
```py
from ...taxonomy import resource


class Assertion(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.severity = 'ERROR'
        super().__init__(e, container_xlink)
        self.implicit_filtering = e.attrib.get('implicitFiltering')
        self.aspect_model = e.attrib.get('aspectModel')
```

## formula/assertion_set.py
```py
from ...taxonomy import resource


class AssertionSet(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.assertions = {}
        self.tables = {}
        super().__init__(e, container_xlink)
        container_xlink.linkbase.pool.current_taxonomy.assertion_sets[container_xlink.linkbase.location] = self
```

## formula/consistency_assertion.py
```py
from ...taxonomy.formula import assertion


class ConsistencyAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        self.strict = e.attrib.get('strict')
        self.abs_radius = e.attrib.get('absoluteAcceptanceRadius')
        self.prop_radius = e.attrib.get('proportionalAcceptanceRadius')
        container_xlink.linkbase.pool.current_taxonomy.consistency_assertions[self.xlabel] = self
```

## formula/existence_assertion.py
```py
from ...taxonomy.formula import assertion


class ExistenceAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        self.test = e.attrib.get('test')
        container_xlink.linkbase.pool.current_taxonomy.existence_assertions[self.xlabel] = self
```

## formula/filter.py
```py
from ...taxonomy import resource


class Filter(resource.Resource):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
```

## formula/parameter.py
```py
from ...taxonomy import resource


class Parameter(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        self.name = e.attrib.get('name')
        self.select = e.attrib.get('select')
        self.data_type = e.attrib.get('as')
        container_xlink.linkbase.pool.current_taxonomy.parameters[self.xlabel] = self
```

## formula/value_assertion.py
```py
from ...taxonomy.formula import assertion


class ValueAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        self.test = e.attrib.get('test')
        container_xlink.linkbase.pool.current_taxonomy.value_assertions[self.xlabel] = self
```

## item_type.py
```py
from ..base import const, element, util, data_wrappers
from lxml import etree as lxml


class ItemType(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        self.restrictions = []
        self.base = None
        if container_schema is not None:
            self.namespace = container_schema.target_namespace
            self.qname = f'{container_schema.target_namespace_prefix}:{self.name}'
        unique_id = f'{self.namespace}:{self.name}'
        self.schema.item_types[self.qname] = self
        self.schema.item_types_by_id[unique_id] = self
        self.l_restrictions(e)

    def l_restrictions(self, e):
        for e2 in e.iterchildren():
            if isinstance(e2, lxml._Comment):
                continue
            if e2.tag != f'{{{const.NS_XS}}}simpleContent':
                continue
            for e3 in e2.iterchildren():
                if isinstance(e3, lxml._Comment):
                    continue
                if e3.tag != f'{{{const.NS_XS}}}restriction':
                    print('Unknown simpleContent element: ', e3.tag)
                    continue
                self.base = e3.attrib.get('base')
                for e4 in e3.iterchildren():
                    if isinstance(e4, lxml._Comment):
                        continue
                    self.restrictions.append(data_wrappers.XsdRestriction(
                            util.get_local_name(e4.tag), e4.attrib.get('value')))
```

## linkbase.py
```py
from openesef.base import fbase, const, util
from openesef.taxonomy import xlink
#from openesef.base import ebase

from openesef.util.util_mylogger import setup_logger #util_mylogger
import logging 
if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.taxonomy.linkbase") 


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
    def __init__(self, location, container_pool, root=None, esef_filing_root=None, memfs=None):
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
        self.location = location
        self.role_refs = {}
        self.arcrole_refs = {}
        self.refs = set({})
        self.pool = container_pool
        self.memfs = memfs
        self.links = []
        resolved_location = util.reduce_url(location)
        if self.pool is not None:
            self.pool.discovered[location] = True
        #from openesef.base import ebase, fbase
        #this_fbase = fbase.XmlFileBase(None, container_pool, parsers, root, esef_filing_root); #self = this_fbase
        #this_ebase = ebase.XmlElementBase(None, container_pool, parsers, root, esef_filing_root); #self = this_ebase
        
        
        
        #fbase.XmlFileBase(location=resolved_location, container_pool=container_pool, parsers=parsers, root=None, esef_filing_root = esef_filing_root, memfs=memfs)
        try:
            super().__init__(location=resolved_location, container_pool=container_pool, 
                         parsers=parsers, root=root, esef_filing_root=esef_filing_root, memfs=memfs)
        except Exception as e:
            logger.error(f"Failed to load linkbase: location={resolved_location}, esef_filing_root={esef_filing_root} \n{str(e)}")
            #traceback.print_exc(limit=10)
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
```

## locator.py
```py
from ..base import ebase, const, util
import os


class Locator(ebase.XmlElementBase):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        href = e.attrib.get(f'{{{const.NS_XLINK}}}href')
        if href.startswith('#'):
            href = f'{self.xlink.linkbase.location}{href}' if self.xlink else href
        elif href.startswith('..'):
            href = os.path.join(self.xlink.linkbase.base, href)
            href = href.replace('\\', '/')
        elif not href.startswith('http') and self.xlink is not None:
            href = os.path.join(self.xlink.linkbase.base, href)
            href = href.replace('\\', '/')
        self.href = util.reduce_url(href)
        self.label = e.attrib.get(f'{{{const.NS_XLINK}}}label')
        self.url = None if self.href is None else self.href[:self.href.find('#')]
        self.fragment_identifier = None if self.href is None else self.href[self.href.find('#')+1:]
        if self.xlink is not None:
            self.xlink.locators[self.label] = self
            self.xlink.locators_by_href[self.href] = self
```

## resource.py
```py
from ..base import ebase, const, util


class Resource(ebase.XmlElementBase):
    def __init__(self, e, container_xlink=None, assign_origin=False):
        self.xlink = container_xlink
        self.nested = {}
        super().__init__(e, assign_origin=assign_origin)
        self.xlabel = e.attrib.get(f'{{{const.NS_XLINK}}}label')
        self.role = e.attrib.get(f'{{{const.NS_XLINK}}}role')
        self.text = e.text
        self.parent = None  # Parent resource if any - e.g. a table
        self.order = 0  # Order in the structure taken from arc
        if self.xlink is not None:
            self.xlink.resources.setdefault(self.xlabel, []).append(self)

    def get_label(self, lang='en', role='/label'):
        return util.get_label(self.nested, lang, role)

    def get_rc_label(self):
        return util.get_rc_label(self.nested)

    def get_db_label(self):
        return util.get_db_label(self.nested)

    def get_languages(self):
        return set([lbl.lang
                    for kind, res_dict in self.nested.items()
                    for key_label, list_labels in res_dict.items()
                    for lbl in list_labels if kind == 'label'])
```

## roletype.py
```py
from ..base import ebase, const, util


class RoleType(ebase.XmlElementBase):
    def __init__(self, e, container_schema=None):
        self.schema = container_schema
        self.definition = None
        self.role_uri = e.attrib.get('roleURI')
        self.used_on = []
        self.labels = {}
        parsers = {
            f'{{{const.NS_LINK}}}roleType': self.l_children,
            f'{{{const.NS_LINK}}}definition': self.l_definition,
            f'{{{const.NS_LINK}}}usedOn': self.l_used_on
        }
        super().__init__(e, parsers)
        if self.id is not None:
            self.schema.role_types[self.role_uri] = self

    def l_definition(self, e):
        self.definition = e.text

    def l_used_on(self, e):
        self.used_on.append(e.text)

    def get_label(self):
        lbl = util.get_label(self.labels)
        return (self.definition if self.definition else '') if lbl is None or lbl == '' else lbl
```

## schema.py
```py
from openesef.taxonomy import concept, linkbase, roletype, arcroletype, simple_type, item_type, tuple_type
from openesef.base import fbase, const, element, util
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
    def __init__(self, location, container_pool, esef_filing_root=None, virtual_location=None, memfs=None):
        self.target_namespace = ''
        self.target_namespace_prefix = ''
        self.location = location
        self.virtual_location = virtual_location or location  # Use virtual location for references
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
        #this_fb =  fbase.XmlFileBase(location=resolved_location, container_pool=data_pool, parsers=None, root=None, esef_filing_root = esef_filing_root); self = this_fb
        super().__init__(location = resolved_location, 
                         container_pool = container_pool, 
                         parsers = parsers, 
                         esef_filing_root=esef_filing_root, 
                         memfs=memfs)
        
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
    def get_reference_location(self):
        """
        Get the location to use for references
        Returns:
            str: The virtual location if available, otherwise the physical location
        """
        return self.virtual_location or self.location
```

## simple_type.py
```py
from ..base import const, element, util


class SimpleType(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        unique_id = f'{self.namespace}:{self.name}'
        self.schema.simple_types[unique_id] = self
```

## table/__init__.py
```py
from . import def_node
from . import breakdown
from . import dr_node
from . import rule_node
from . import cell
from . import layout
from . import cr_node
from . import str_node
from . import tlb_resource
from . import aspect_node
from . import table
```

## table/aspect_node.py
```py
from ...taxonomy.table import def_node, str_node
from ...base import const


class AspectNode(def_node.DefinitionNode):
    """ Implements an aspect node """
    def __init__(self, e, container_xlink=None):
        self.aspect = None
        self.filters = {}
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_TABLE}}}dimensionAspect':
                self.aspect = e2.text
                continue
            self.aspect = e2.tag.split('}')[1]

    def get_constraints(self, tag='default'):
        return {self.aspect: None}
```

## table/breakdown.py
```py
from ...taxonomy.table import tlb_resource


class Breakdown(tlb_resource.TableResource):
    """ Implements a XBRL table breakdown"""

    def __init__(self, e, container_xlink=None):
        self.parent_child_order = e.attrib.get('parentChildOrder')
        self.axis = None
        self.is_open = False
        self.is_closed = False
        super().__init__(e, container_xlink)
```

## table/cell.py
```py
from ...taxonomy.table import str_node
from ...base import data_wrappers


class Cell:
    def __init__(self, constraints=None, label=None, colspan=1, rowspan=1, indent=0,
                 is_header=False, is_fact=False, is_fake=False, is_grayed=False,
                 html_class=None, r_code=None, c_code=None, origin=None):
        self.label = label
        self.is_header = is_header
        self.is_fact = is_fact
        self.is_fake = is_fake
        self.is_grayed = is_grayed
        self.colspan = colspan
        self.rowspan = rowspan
        self.indent = indent
        self.c_code = c_code
        self.r_code = r_code
        self.html_classes = None if html_class is None else set(html_class.split(' '))
        # Final version of constraints
        self.constraints = {} if constraints is None else constraints
        if origin and isinstance(origin, str_node.StructureNode):
            origin.cells.append(self)

    def add_constraints(self, constraints, axis):
        for asp, mem in constraints.items():
            self.add_constraint(asp, mem, axis)

    def add_constraint(self, asp, mem, axis):
        if self.constraints is None:
            self.constraints = {}
        self.constraints[asp] = data_wrappers.Constraint(asp, mem, axis)

    def add_class(self, cls):
        if self.html_classes is None:
            self.html_classes = set({})
        self.html_classes.add(cls)

    def get_address(self, open_x=False, open_y=False, open_z=False):
        if open_y:
            return self.c_code  # If the table is open-Y, then we only take the column code as address
        return f'{self.r_code}.{self.c_code}'

    def get_class(self):
        if self.html_classes is None:
            return ''
        return f' class="{" ".join(self.html_classes)}"'

    def get_label(self):
        return '' if self.label is None else self.label

    def get_indent(self):
        if self.indent == 0:
            return ''
        return f' style="text-indent: {self.indent}px;"'

    def get_colspan(self):
        if self.colspan == 1:
            return ''
        return f' colspan="{self.colspan}"'

    def get_rowspan(self):
        if self.rowspan == 1:
            return ''
        return f' rowspan="{self.rowspan}"'
```

## table/cr_node.py
```py
from ...taxonomy.table import def_node
from ...base import const


class ConceptRelationshipNode(def_node.DefinitionNode):
    """ Implements a concept relationship node """
    def __init__(self, e, container_xlink=None):
        self.relationship_sources = []
        self.role = None
        self.arcrole = None
        self.formula_axis = 'descendant-or-self'
        self.generations = None
        self.link_name = None
        self.arc_name = const.ARC_PRESENTATION
        super().__init__(e, container_xlink)
        self.detail_parsers = {
            f'{{{const.NS_TABLE}}}relationshipSource': self.l_rel_src,
            f'{{{const.NS_TABLE}}}relationshipSourceExpression': self.l_rel_src,
            f'{{{const.NS_TABLE}}}linkrole': self.l_linkrole,
            f'{{{const.NS_TABLE}}}linkroleExpression': self.l_linkrole,
            f'{{{const.NS_TABLE}}}arcrole': self.l_arcrole,
            f'{{{const.NS_TABLE}}}arcroleExpression': self.l_arcrole,
            f'{{{const.NS_TABLE}}}formulaAxis': self.l_axis,
            f'{{{const.NS_TABLE}}}formulaAxisExpression': self.l_axis,
            f'{{{const.NS_TABLE}}}generations': self.l_generations,
            f'{{{const.NS_TABLE}}}generationsExpression': self.l_generations,
            f'{{{const.NS_TABLE}}}linkname': self.l_linkname,
            f'{{{const.NS_TABLE}}}linknameExpression': self.l_linkname,
            f'{{{const.NS_TABLE}}}arcname': self.l_arcname,
            f'{{{const.NS_TABLE}}}arcnameExpression': self.l_arcname
        }
        self.dependencies = {
            const.PARENT_CHILD_ARCROLE: const.ARC_PRESENTATION,
            const.SUMMATION_ITEM_ARCROLE: const.ARC_CALCULATION,
            const.GENERAL_SPECIAL_ARCROLE: const.ARC_DEFINITION,
            const.ESSENCE_ALIAS_ARCROLE: const.ARC_DEFINITION,
            const.SIMILAR_TUPLE_ARCROLE: const.ARC_DEFINITION,
            const.REQUIRES_ELEMENT_ARCROLE: const.ARC_DEFINITION,
            const.XDT_DOMAIN_MEMBER_ARCROLE: const.ARC_DEFINITION
        }
        self.load_details(e)

    def l_arcname(self, e):
        self.arc_name = e.text

    def l_linkname(self, e):
        self.link_name = e.text

    def l_generations(self, e):
        self.generations = e.text

    def l_axis(self, e):
        self.formula_axis = e.text

    def l_arcrole(self, e):
        self.arcrole = e.text
        self.arc_name = self.dependencies.get(self.arcrole, const.ARC_PRESENTATION)

    def l_linkrole(self, e):
        self.role = e.text

    def l_rel_src(self, e):
        self.relationship_sources.append(e.text)
```

## table/def_node.py
```py
from ...taxonomy.table import tlb_resource


class DefinitionNode(tlb_resource.TableResource):
    """ Implements a definition node """
    def __init__(self, e, container_xlink=None):
        self.detail_parsers = None
        super().__init__(e, container_xlink)

    def load_details(self, e):
        for e2 in e.iterchildren():
            method = self.detail_parsers.get(e2.tag, None)
            if method is None:
                print(f'Unknown CR element: {e2.tag}')
                return
            method(e2)
```

## table/dr_node.py
```py
from ...taxonomy.table import def_node
from ...base import const


class DimensionalRelationshipNode(def_node.DefinitionNode):
    """ Implements a dimensional relationship node """
    def __init__(self, e, container_xlink=None):
        self.relationship_sources = []
        self.role = None
        self.formula_axis = 'descendant-or-self'
        self.generations = None
        self.dimension = None
        super().__init__(e, container_xlink)
        self.detail_parsers = {
            f'{{{const.NS_TABLE}}}relationshipSource': self.l_rel_src,
            f'{{{const.NS_TABLE}}}relationshipSourceExpression': self.l_rel_src,
            f'{{{const.NS_TABLE}}}dimension': self.l_dimension,
            f'{{{const.NS_TABLE}}}linkrole': self.l_linkrole,
            f'{{{const.NS_TABLE}}}linkroleExpression': self.l_linkrole,
            f'{{{const.NS_TABLE}}}formulaAxis': self.l_axis,
            f'{{{const.NS_TABLE}}}formulaAxisExpression': self.l_axis,
            f'{{{const.NS_TABLE}}}generations': self.l_generations,
            f'{{{const.NS_TABLE}}}generationsExpression': self.l_generations
        }
        self.load_details(e)

    def l_axis(self, e):
        self.formula_axis = e.text

    def l_generations(self, e):
        self.generations = e.text

    def l_linkrole(self, e):
        self.role = e.text

    def l_dimension(self, e):
        self.dimension = e.text

    def l_rel_src(self, e):
        self.relationship_sources.append(e.text)
```

## table/layout.py
```py
class Layout:
    def __init__(self, lbl, rc):
        self.label = lbl
        self.rc_code = rc
        # Each cell here corresponds to a table
        self.cells = []
        # Open dimensions per axis
        self.open_dimensions = {}

    def is_open_x(self):
        return any([ax for ax in self.open_dimensions.values() if ax == 'x'])

    def is_open_y(self):
        return any([ax for ax in self.open_dimensions.values() if ax == 'y'])

    def is_open_z(self):
        return any([ax for ax in self.open_dimensions.values() if ax == 'z'])
```

## table/rule_node.py
```py
from ...taxonomy.table import def_node, str_node
from ...base import const
import lxml.etree


class RuleNode(def_node.DefinitionNode):
    """ Implements a rule node """
    def __init__(self, e, container_xlink=None):
        abst = e.attrib.get('abstract')
        self.is_abstract = abst is not None and abst.lower() in ['true', '1']
        merg = e.attrib.get('merge')
        self.is_merged = merg is not None and merg.lower() in ['true', '1']
        self.tag_selector = e.attrib.get('tagSelector')
        self.rule_sets = {'default': {}}
        self.rule_parsers = {
            f'{{{const.NS_FORMULA}}}concept': self.l_formula_concept,
            f'{{{const.NS_FORMULA}}}period': self.l_formula_period,
            f'{{{const.NS_FORMULA}}}unit': self.l_formula_unit,
            f'{{{const.NS_FORMULA}}}explicitDimension': self.l_explicit_dimension
        }
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            if e2 is lxml.etree._Comment:
                continue
            if e2.tag == f'{{{const.NS_TABLE}}}ruleSet':
                name = e2.attrib.get('tag')
                for e3 in e2.iterchildren():
                    self.l_rule_set(e3, name)
            else:
                self.l_rule_set(e2, 'default')

    def l_rule_set(self, e, rule_set_name):
        restrictions = self.rule_sets.setdefault(rule_set_name, {})
        method = self.rule_parsers.get(e.tag, None)
        if method is None:
            print(f'Unknown rule: {e.tag}')
            return
        method(e, restrictions)

    def l_formula_concept(self, e, restrictions):
        for e2 in e.iterchildren():
            if e2.tag != f'{{{const.NS_FORMULA}}}qname':
                print(f'Unknown element in formula:concept rule {e2.tag}')
                continue
            restrictions['concept'] = e2.text.strip()

    def l_formula_unit(self, e, restrictions):
        numerator = []
        denominator = []
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_FORMULA}}}multiplyBy':
                numerator.append(self.get_measure(e2))
            elif e2.tag == f'{{{const.NS_FORMULA}}}divideBy':
                denominator.append(self.get_measure(e2))
            else:
                print(f'Unknown element {e2.tag} under formula:unit')
        numerator_str = '*'.join(numerator) if numerator else '1'
        denominator_str = '*'.join(denominator) if denominator else ''
        separator = '/' if denominator else ''
        restrictions['measure'] = f'{numerator_str}{separator}{denominator_str}'

    def get_measure(self, e):
        msr = e.attrib.get('measure')
        # Specific case for QName representation of a measure. TODO: Replace with XPath function
        if msr.startswith('QName'):
            msr = msr.split('(')[1].split(')')[0].split(',')[1].replace("'", "").replace('"', '')
        return msr

    def l_formula_period(self, e, restrictions):
        for e2 in e.iterchildren():
            p = ''
            if e2.tag == f'{{{const.NS_FORMULA}}}instant':
                p = e2.attrib.get('value')
            elif e2.tag == f'{{{const.NS_FORMULA}}}duration':
                start = e2.attrib.get('start')
                end = e2.attrib.get('end')
                p = f'{start}/{end}'
            restrictions['period'] = p

    def l_explicit_dimension(self, e, restrictions):
        dimension_qname = e.attrib.get('dimension')
        if dimension_qname is None:
            print('Missing dimension in formula:explicitDimension rule')
        for e2 in e.iterchildren():
            if e2.tag != f'{{{const.NS_FORMULA}}}member':
                print(f'Unknown element in formula:explicitDimension rule {e2.tag}')
                continue
            for e3 in e2.iterchildren():
                if e3.tag == f'{{{const.NS_FORMULA}}}qname':
                    restrictions[dimension_qname] = e3.text.strip()
                elif e3.tag == f'{{{const.NS_FORMULA}}}qnameExpression':
                    restrictions[dimension_qname] = e3.text.strip()  # TODO: Evaluate parameters
                else:
                    print(f'Unknown element in formula:member element {e3.tag}')

    def get_constraints(self, tag='default'):
        constraints = {}
        c_set = self.rule_sets.get(tag, None)
        if c_set is not None:
            for asp, mem in c_set.items():
                constraints[asp] = mem
        return constraints
```

## table/str_node.py
```py
from ...taxonomy.table import aspect_node
from ...taxonomy.table import dr_node
from ...taxonomy.table import cr_node
from ...base import const


class StructureNode:
    def __init__(self, parent, origin, grayed=False, lvl=0, fake=False, abst=False, concept=None):
        """ Parent structure node in the hierarchy """
        self.parent = parent
        """ Resource, which is the origin of this structure node """
        self.origin = origin
        self.span = 0
        self.level = lvl
        self.is_grayed = grayed
        self.is_fake = fake
        self.is_abstract = abst
        self.nested = None
        self.concept = concept

        self.r_code = None
        self.c_code = None
        self.cells = []

        """ Contains the untagged (tag='default') and tagged constraint sets for the node. """
        self.constraint_set = {}
        if self.parent is not None:
            if parent.nested is None:
                parent.nested = []
            self.parent.nested.append(self)

    def increment_span(self):
        self.span += 1
        if self.parent is None:
            return
        self.parent.increment_span()

    def add_constraint(self, aspect, value, tag='default'):
        self.constraint_set.setdefault(tag, {})[aspect] = value

    def get_caption(self, use_id=True, lang='en'):
        if not self.origin:
            return ''
        display_label = self.origin.get_label(lang=lang)
        if not display_label:
            display_label = self.origin.xlabel if use_id else ''
        if self.concept:
            display_label = self.concept.get_label(lang=lang)
        if isinstance(self.origin, dr_node.DimensionalRelationshipNode):
            display_label_tot = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_TOTAL)
            if display_label_tot:
                display_label = display_label_tot
        elif isinstance(self.origin, cr_node.ConceptRelationshipNode):
            if any([s for s in self.origin.relationship_sources if 'PeriodStart' in s]):
                display_label_start = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_PERIOD_START)
                if display_label_start:
                    display_label = display_label_start
            if any([s for s in self.origin.relationship_sources if 'PeriodEnd' in s]):
                description_end = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_PERIOD_END)
                if description_end:
                    display_label = description_end
        return display_label


    def get_aspect_caption(self):
        return self.origin.aspect if isinstance(self.origin, aspect_node.AspectNode) else self.origin.xlabel

    def get_rc_caption(self):
        if self.origin is not None:
            cap = self.origin.get_rc_label()
            return cap if cap else self.get_aspect_caption()
        return ''

    def get_db_caption(self):
        if self.origin is not None:
            cap = self.origin.get_db_label()
            return cap if cap else self.get_aspect_caption()
        return ''

    def get_fake_copy(self):
        cloned = StructureNode(parent=self, origin=self.origin, grayed=True, lvl=self.level, fake=True,
                               abst=self.is_abstract, concept=self.concept)
        for tag, dct in self.constraint_set.items():
            cloned.constraint_set.setdefault(tag, {}).update(dct)
        return cloned
```

## table/table.py
```py
from ...taxonomy.table import tlb_resource, str_node


class Table(tlb_resource.TableResource):
    """ Implements a XBRL table """
    def __init__(self, e, container_xlink=None):
        self.has_rc_labels = False
        self.has_db_labels = False
        self.open_axes = set({})
        self.open_dimensions = {}
        self.parent_child_order = e.attrib.get('parentChildOrder')
        super().__init__(e, container_xlink)
        container_xlink.linkbase.pool.current_taxonomy.tables[self.xlabel] = self

    def get_label(self, lang='en', role='/label'):
        lbl = super().get_label(lang, role)
        return self.xlabel if lbl is None else lbl

    def get_rc_label(self):
        rc = super().get_rc_label()
        return '' if rc is None else rc

    def get_rc_or_id(self):
        rc = super().get_rc_label()
        return rc if rc else self.xlabel

    def get_db_label(self):
        db = super().get_db_label()
        return '' if db is None else db
```

## table/tlb_resource.py
```py
from ...taxonomy import resource


class TableResource(resource.Resource):
    """ Implements a Table Linkbase resource """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)

    def get_constraints(self, tag='default'):
        return None
```

## taxonomy.py
```py
from openesef.base import const, data_wrappers, util
from openesef.taxonomy.xdt import dr_set
#from io import StringIO, BytesIO

from openesef.util.util_mylogger import setup_logger #util_mylogger
import logging 
if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.taxonomy") 

import traceback


class Taxonomy:
    """ entry_points is a list of entry point locations
        cache_folder is the place where to store cached Web resources """
    def __init__(self, entry_points, container_pool, esef_filing_root = None, in_memory_content = {}, memfs=None):
        self.entry_points = entry_points
        self.pool = container_pool
        self.pool.current_taxonomy = self
        self.pool.current_taxonomy_hash = util.get_hash(','.join(entry_points))
        self.esef_filing_root = esef_filing_root  # Add ESEF location path
        self.in_memory_content = in_memory_content or {} # Dictionary to store in-memory content
        self.memfs = memfs
        # All schemas indexed by resolved location 
        self.schemas = {}
        # All linkbases indexed by resolved location 
        self.linkbases = {}
        self.processing_schemas = set()  # Track schemas being processed to prevent loops
        # All concepts  indexed by full id - target namespace + id 
        self.concepts = {}
        # All concepts indexed by QName
        self.concepts_by_qname = {}
        # General elements, which are not concepts 
        self.elements = {}
        self.elements_by_id = {}
        # All base set objects indexed by base set key 
        self.base_sets = {}
        # Dimension defaults - Key is dimension QName, value is default member concept 
        self.defaults = {}
        # Default Members - Key is the default member QName, value is the corresponding dimension concept. 
        self.default_members = {}
        # Dimensional Relationship Sets 
        self.dr_sets = {}
        # Excluding Dimensional Relationship Sets 
        self.dr_sets_excluding = {}
        # Key is primary item QName, value is the list of dimensional relationship sets, where it participates. 
        self.idx_pi_drs = {}
        # Key is the Qname of the dimensions. Value is the set of DR keys, where this dimension participates 
        self.idx_dim_drs = {}
        # Key is the QName of the hypercube. Value is the set of DR Keys, where this hypercube participates. 
        self.idx_hc_drs = {}
        # Key is the QName of the member. Value is the set of DR keys, where this member participates. 
        self.idx_mem_drs = {}
        # All table resources in taxonom 
        self.tables = {}
        # All role types in all schemas 
        self.role_types = {}
        self.role_types_by_href = {}
        # All arcrole types in all schemas 
        self.arcrole_types = {}
        self.arcrole_types_by_href = {}
        # Global resources - these, which have an id attribute 
        self.resources = {}
        # All locators 
        self.locators = {}
        # All parameters 
        self.parameters = {}
        # All assertions by type 
        self.value_assertions = {}
        self.existence_assertions = {}
        self.consistency_assertions = {}
        # Assertion Sets 
        self.assertion_sets = {}
        # Simple types 
        self.simple_types = {}
        # Complex types with simple content. Key is the QName, value is the item type object. 
        self.item_types = {}
        # Complex types with simple content. Key is the unique identifier, value is the item type object. 
        self.item_types_by_id = {}
        # Complex types with complex content: Key is qname, value is the tuple type object 
        self.tuple_types = {}
        # Complex types with complex content: Key is unique identifier, value is the tuple type object 
        self.tuple_types_by_id = {}
        self.load()
        self.compile()

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        return '\n'.join([
            f'Schemas: {len(self.schemas)}',
            f'Linkbases: {len(self.linkbases)}',
            f'Role Types: {len(self.role_types)}',
            f'Arcrole Types: {len(self.arcrole_types)}',
            f'Concepts: {len(self.concepts)}',
            f'Item Types: {len(self.item_types)}',
            f'Tuple Types: {len(self.tuple_types)}',
            f'Simple Types: {len(self.simple_types)}',
            f'Labels: {sum([0 if not "label" in c.resources else len(c.resources["label"]) for c in self.concepts.values()])}',
            f'References: {sum([0 if not "reference" in c.resources else len(c.resources["reference"]) for c in self.concepts.values()])}',
            f'Hierarchies: {len(self.base_sets)}',
            f'Dimensional Relationship Sets: {len(self.base_sets)}',
            f'Dimensions: {len([c for c in self.concepts.values() if c.is_dimension])}',
            f'Hypercubes: {len([c for c in self.concepts.values() if c.is_hypercube])}',
            f'Enumerations: {len([c for c in self.concepts.values() if c.is_enumeration])}',
            f'Enumerations Sets: {len([c for c in self.concepts.values() if c.is_enumeration_set])}',
            f'Table Groups: {len([c for c in self.concepts.values() if "table" in c.resources])}',
            f'Tables: {len(self.tables)}',
            f'Parameters: {len(self.parameters)}',
            f'Assertion Sets: {len(self.assertion_sets)}',
            f'Value Assertions: {len(self.value_assertions)}',
            f'Existence Assertions: {len(self.existence_assertions)}',
            f'Consistency Assertions: {len(self.consistency_assertions)}'
        ])

    def _process_entry_point(self, entry_point):
        """Process a single entry point, tracking schema loading status"""
        if entry_point in self.processing_schemas:
            return  # Skip if already processing this schema
            
        self.processing_schemas.add(entry_point)
        try:
            # Load the schema
            #schema_obj = self.container_pool.add_schema(entry_point, self.esef_filing_root)
            schema_obj = self.pool.add_schema(location=entry_point, 
                                              esef_filing_root=self.esef_filing_root, 
                                              memfs=self.memfs)
            if schema_obj:
                self.schemas[entry_point] = schema_obj
        except Exception as e:
            logger.error(f'Taxonomy._process_entry_point(): Error processing {entry_point}: {e}')
            traceback.print_exc(limit=10)
        finally:
            self.processing_schemas.remove(entry_point)

    def load(self):
        for ep in self.entry_points:
            logger.debug(f'Taxonomy.load(): Loading {ep} with self.esef_filing_root={self.esef_filing_root}')
            logger.debug(f'Calling self.pool.add_reference(...) with href = {ep}, base = "", esef_filing_root = {self.esef_filing_root}')
            # Check if we have in-memory content
            if self.in_memory_content and ep in self.in_memory_content:
                logger.debug(f'Loading {ep} from memory')
                content = self.in_memory_content[ep]
                self.pool.add_reference_from_string(content, ep, '')
            else:
                logger.debug(f'Loading {ep} from file/URL')
                #self.pool.add_reference(href=ep, base='', esef_filing_root=self.esef_filing_root)

                self.pool.add_reference(href = ep, 
                                    base = '', 
                                    esef_filing_root = self.esef_filing_root,
                                    memfs = self.memfs)
            self._process_entry_point(ep)

    def add_in_memory_content(self, location, content):
        """Add content to be loaded from memory for a specific location"""
        self.in_memory_content[location] = content


    def resolve_prefix(self, pref):
        for sh in self.schemas.values():
            ns = sh.namespaces.get(pref, None)
            if ns is not None:
                return ns
        return None

    def resolve_qname(self, qname):
        pref = qname.split(':')[0] if ':' in qname else ''
        ns = self.resolve_prefix(pref)
        nm = qname.split(':')[1] if ':' in qname else qname
        return f'{ns}:{nm}'

    def attach_schema(self, href, sh):
        if href in self.schemas:
            return
        self.schemas[href] = sh
        for key, imp in sh.imports.items():
            logger.debug(f'Taxonomy.attach_schema(): Adding import {key} from {sh.base} with self.esef_filing_root={self.esef_filing_root}')
            logger.debug(f'Calling self.pool.add_reference(...) with href = {key}, base = {sh.base}, esef_filing_root = {self.esef_filing_root}')
            self.pool.add_reference(href = key, 
                                    base = sh.base, 
                                    esef_filing_root = self.esef_filing_root)
        for key, ref in sh.linkbase_refs.items():
            logger.debug(f'Taxonomy.attach_schema(): Adding linkbase {key} from {sh.base} with self.esef_filing_root={self.esef_filing_root}') 
            logger.debug(f'Calling self.pool.add_reference(...) with href = {key}, base = {sh.base}, esef_filing_root = {self.esef_filing_root}')
            self.pool.add_reference(href = key, 
                                    base = sh.base, 
                                    esef_filing_root = self.esef_filing_root)

    def attach_linkbase(self, href, lb):
        if href in self.linkbases:
            return
        self.linkbases[href] = lb
        for href in lb.refs:
            logger.debug(f'Taxonomy.attach_linkbase(): Adding reference {href} from {lb.base} with self.esef_filing_root={self.esef_filing_root}')
            logger.debug(f'Calling self.pool.add_reference(...) with href = {href}, base = {lb.base}, esef_filing_root = {self.esef_filing_root}')
            self.pool.add_reference(href = href, 
                                    base = lb.base, 
                                    esef_filing_root = self.esef_filing_root)

    def get_bs_roots(self, arc_name, role, arcrole):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}')
        if not bs:
            return None
        return bs.roots

    def get_bs_members(self, arc_name, role, arcrole, start_concept=None, include_head=True):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}', None)
        if not bs:
            return None
        return bs.get_members(start_concept, include_head)

    def get_enumerations(self):
        enumerations = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enumerations.get(key)
            if not e:
                members = self.get_bs_members('definitionArc', c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE, c.domain, c.head_usable)
                e = data_wrappers.Enumeration(key, [], [] if members is None else [m.Concept for m in members])
                enumerations[key] = e
            e.Concepts.append(c)
        return enumerations

    def get_enumeration_sets(self):
        enum_sets = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationSetItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enum_sets.get(key)
            if not e:
                members = self.get_bs_members('definitionArc', c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE, c.domain, c.head_usable)
                if members is None:
                    continue
                e = data_wrappers.Enumeration(key, [], [m.Concept for m in members])
                enum_sets[key] = e
            e.Concepts.append(c)
        return enum_sets

    def compile(self):
        self.compile_schemas()
        self.compile_linkbases()
        self.compile_defaults()
        self.compile_dr_sets()

    def compile_schemas(self):
        for sh in self.schemas.values():
            for c in sh.concepts.values():
                self.concepts_by_qname[c.qname] = c
                if c.id is not None:
                    key = f'{sh.location}#{c.id}'  # Key to search from locator href
                    self.concepts[key] = c
            for key, e in sh.elements.items():
                self.elements[key] = e
            for key, e in sh.elements_by_id.items():
                self.elements_by_id[key] = e
            for key, art in sh.arcrole_types.items():
                self.arcrole_types[key] = art
                self.arcrole_types_by_href[f'{sh.location}#{art.id}'] = art
            for key, rt in sh.role_types.items():
                self.role_types[key] = rt
                self.role_types_by_href[f'{sh.location}#{rt.id}'] = rt

            for key, it in sh.item_types.items():
                self.item_types[key] = it
            for key, it in sh.item_types_by_id.items():
                self.item_types_by_id[key] = it
            for key, tt in sh.tuple_types.items():
                self.tuple_types[key] = tt
            for key, tt in sh.tuple_types_by_id.items():
                self.tuple_types_by_id[key] = tt

            for key, st in sh.simple_types.items():
                self.simple_types[key] = st

    def compile_linkbases(self):
        # Pass 1 - Index global objects
        for lb in self.linkbases.values():
            for xl in lb.links:
                for key, loc in xl.locators_by_href.items():
                    self.locators[key] = loc
                for key, l_res in xl.resources.items():
                    for res in l_res:
                        if res.id:
                            href = f'{xl.linkbase.location}#{res.id}'
                            self.resources[href] = res
        # Pass 2 - Connect resources to each other
        for lb in self.linkbases.values():
            for xl in lb.links:
                xl.compile()

    def compile_defaults(self):
        # key = f'definitionArc|{const.XDT_DIMENSION_DEFAULT_ARCROLE}|{const.ROLE_LINK}'
        frag = f'definitionArc|{const.XDT_DIMENSION_DEFAULT_ARCROLE}'
        for key, bs in self.base_sets.items():
            if frag not in key:
                continue
            bs = self.base_sets.get(key, None)
        # if bs is None:
        #     return
            for dim in bs.roots:
                chain_dn = dim.chain_dn.get(key, None)
                if chain_dn is None:
                    continue
                for def_node in chain_dn:
                    self.defaults[dim.qname] = def_node.Concept.qname
                    self.default_members[def_node.Concept.qname] = dim.qname

    def compile_dr_sets(self):
        for bs in [bs for bs in self.base_sets.values() if bs.arc_name == 'definitionArc']:
            if bs.arcrole == const.XDT_DIMENSION_DEFAULT_ARCROLE:
                self.add_default_member(bs)
                continue
            if bs.arcrole == const.XDT_ALL_ARCROLE:
                self.add_drs(bs, self.dr_sets)
                continue
            if bs.arcrole == const.XDT_NOTALL_ARCROLE:
                self.add_drs(bs, self.dr_sets_excluding)
                continue

    def add_drs(self, bs, drs_collection):
        drs = dr_set.DrSet(bs, self)
        drs.compile()
        drs_collection[bs.get_key()] = drs

    def add_default_member(self, bs):
        for d in bs.roots:
            members = bs.get_members(start_concept=d, include_head=False)
            if not members:
                continue
            for m in members:
                self.defaults[d.qname] = m
                self.default_members[m.qname] = d

    def get_prefixes(self):
        return set(c.prefix for c in self.concepts.values())

    def get_languages(self):
        return set([r.lang for k, r in self.resources.items() if r.name == 'label'])
```

## tpack.py
```py
import os
import zipfile
from lxml import etree as lxml
from ..base import const, resolver, util, data_wrappers


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


class TaxonomyPackage(resolver.Resolver):
    """ Implements taxonomy package functionality """
    def __init__(self, location=None, cache_folder=None, output_folder=None, archive=None, esef_filing_root=None):
        super().__init__(cache_folder, output_folder)
        self.archive = archive
        self.location = location
        self.esef_filing_root = esef_filing_root
        if self.location and self.location.startswith('http'):
            # Download the taxonomy package and save in the cache folder
            self.location = self.cache(location)
        """ Entry points is a list of tuples with following structure: (prefix, location, description) """
        self.entrypoints = []
        """ Key is element name, value is element text. """
        self.properties = {}
        """ List of superseded packages, each represented by ts URL. """
        self.superseded_packages = []
        """ List of XBRL reports included in the package """
        self.reports = []
        self.files = None
        self.redirects = {}
        self.redirects_reduced = None
        self.catalog_location = None
        if self.location and os.path.exists(self.location):
            self.archive = zipfile.ZipFile(self.location)
            self.init()

    def __del__(self):
        if self.archive:
            self.archive.close()

    def init(self):
        zil = self.archive.infolist()
        package_files = [f for f in zil if f.filename.endswith('META-INF/taxonomyPackage.xml')]
        if len(package_files) == 0:
            return
        package_file = package_files[0]
        with self.archive.open(package_file) as zf:
            package = lxml.XML(zf.read())
            for e in package.iterchildren():
                if str(e.tag).endswith('entryPoints'):
                    self.l_entrypoints(e)
                elif str(e.tag).endswith('supersededTaxonomyPackages'):
                    self.l_superseded(e)
                elif not len(e):  # second level
                    name = util.get_local_name(str(e.tag))
                    self.properties[name] = e.text
        zi_catalog = [f for f in zil if f.filename.endswith('META-INF/catalog.xml')][0]
        self.catalog_location = os.path.dirname(zi_catalog.filename)
        with self.archive.open(zi_catalog) as cf:
            catalog = lxml.XML(cf.read())
            self.l_redirects(catalog)
        self.reports = [f for f in zil if '/reports/' in f.filename]

    def get_url(self, url):
        """ Reads the binary content of a file addressed by a URL. """
        if not self.files:
            self.compile()
        logger.debug(f"Trying to get URL: {url}")    
        file_path = self.files.get(url)
        if not file_path:
            return None
        if self.archive is not None:
            try:
                with self.archive.open(file_path) as f:
                    return f.read()
            except KeyError:
                # Handle cases where the file is not directly in the archive
                # but within a subdirectory specified by 
                logger.debug(f"File not found in archive: {url}")
                if self.esef_filing_root:
                    resolved_path = os.path.join(self.esef_filing_root, url)
                    if os.path.exists(resolved_path):
                        with open(resolved_path, 'rb') as f:
                            return f.read()
                return None  # Or raise an exception if appropriate
        return bytes(file_path, encoding='utf-8')

    def get_hash(self):
        return util.get_hash(self.location)

    def compile(self):
        self.files = {}
        if not self.archive:
            return        
        zip_infos = self.archive.infolist()
        if not zip_infos:
            return
        # Index files by calculating effective URL based on catalog
        root = zip_infos[0].filename.split('/')[0]  # Root of the archive file
        # Add files from esef_filing_root if provided
        if self.esef_filing_root:
            for root, _, files in os.walk(self.esef_filing_root):
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), self.esef_filing_root)
                    self.files[file_path] = file_path

        for fn in [zi.filename for zi in zip_infos if not zi.is_dir()]:
            matched_redirects = [(u, r) for u, r in self.redirects_reduced.items() if fn.startswith(r)]

            self.files[fn] = fn
            if not matched_redirects:
                # self.files[fn] = fn
                continue


            file_root = matched_redirects[0][1]
            rewrite_prefix = matched_redirects[0][0]
            url = fn.replace(file_root, rewrite_prefix)
            self.files[url] = fn

    def l_redirects(self, ce):
        for e in ce.iterchildren():
            if e.tag != f'{{{const.NS_OASIS_CATALOG}}}rewriteURI':
                continue
            url = e.attrib.get('uriStartString')
            rewrite_prefix = e.attrib.get('rewritePrefix')
            self.redirects[url] = rewrite_prefix
        # Reduce redirects according to position of catalog.xml
        self.redirects_reduced = dict([(u, util.reduce_url(os.path.join(self.catalog_location, r)))
                                       for u, r in self.redirects.items()])

    def l_entrypoints(self, ep):
        for e in ep.iterchildren():
            if str(e.tag).endswith('entryPoint'):
                prefix = None
                ep = []
                desc = None
                for e2 in e.iterchildren():
                    if str(e2.tag).endswith('entryPointDocument'):
                        href = e2.attrib.get('href')
                        ep.append(href)
                    elif str(e2.tag).endswith('name'):
                        prefix = e2.text
                    elif str(e2.tag).endswith('description'):
                        desc = e2.text
                self.entrypoints.append(data_wrappers.EntryPoint(prefix, ep, desc, util.get_hash(''.join(ep))))

    def l_superseded(self, ep):
        for e in ep.iterchildren():
            if str(e.tag).endswith('taxonomyPackageRef'):
                self.superseded_packages.append(e.text)

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        o = ['Properties', '----------']
        for prop, value in self.properties.items():
            o.append(f'{prop}: {value}')
        o.append('\nEntry points')
        o.append('------------')
        for ep in self.entrypoints:
            o.append(f'{ep.Name}, {",".join(ep.Urls)}, {ep.Description}')
        o.append('\nRedirects\n---------')
        for start_string, rewrite_prefix in self.redirects.items():
            o.append(f'{start_string} => {rewrite_prefix}')
        if self.superseded_packages:
            o.append('\nSuperseded Packages\n-------------------')
            o.append('\n'.join(self.superseded_packages))
        return '\n'.join(o)
```

## tuple_type.py
```py
from ..base import const, element, util


class TupleType(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        if container_schema is not None:
            self.namespace = container_schema.target_namespace
            self.qname = f'{container_schema.target_namespace_prefix}:{self.name}'
        unique_id = f'{self.namespace}:{self.name}'
        self.schema.tuple_types[self.qname] = self
        self.schema.tuple_types_by_id[unique_id] = self
```

## xdt/__init__.py
```py
from . import dr_set
from . import primary_item
from . import dimension
from . import hypercube
```

## xdt/dimension.py
```py
class Dimension:
    def __init__(self, concept, container_dr_set, arc=None):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.target_role = arc.target_role if arc else None
        self.members = {} if self.concept.is_explicit_dimension else None
```

## xdt/dr_set.py
```py
from . import hypercube
from . import primary_item
from . import dimension
from ...base import const


class DrSet:
    """ Dimensional Relationship Set """

    def __init__(self, start_base_set, container_taxonomy):
        self.bs_start = start_base_set
        self.drs_type = 'including' if self.bs_start.arcrole == const.XDT_ALL_ARCROLE else 'excluding'
        self.taxonomy = container_taxonomy
        self.root_primary_items = {}
        self.primary_items = {}
        self.hypercubes = {}

    def __str_(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def compile(self):
        # print('start compiling DRS', self.bs_start.role)
        self.root_primary_items.update({pi.qname: primary_item.PrimaryItem(pi, self) for pi in self.bs_start.roots})
        if not self.root_primary_items:
            return
        for pi in self.root_primary_items.values():
            self.taxonomy.idx_pi_drs.setdefault(pi.concept.qname, set({})).add(self)
        pi = next(iter(self.root_primary_items.values()))
        self.populate_hypercubes(pi)
        # Add root primary items to the set. This is needed in case no domain-member set is available
        self.primary_items.update(self.root_primary_items)
        self.populate_nested_pi()

    def populate_nested_pi(self):
        pis = self.taxonomy.get_bs_members(self.bs_start.arc_name, self.bs_start.role, const.XDT_DOMAIN_MEMBER_ARCROLE)
        if not pis:
            return
        self.primary_items.update({
            pi.Concept.qname: primary_item.PrimaryItem(pi.Concept, self, pi.Arc, pi.Level)
            for pi in pis if pi.Concept.qname not in self.taxonomy.idx_mem_drs})
        for pi in pis:
            self.taxonomy.idx_pi_drs.setdefault(pi.Concept.qname, set()).add(self)

    def populate_hypercubes(self, pi):
        if pi.target_role:
            bs_hc = self.taxonomy.base_sets.get(
                f'{self.bs_start.arc_name}|{pi.target_role}|{{{const.XDT_ALL_ARCROLE}}}')
            if bs_hc is None:
                bs_hc = self.taxonomy.base_sets.get(
                    f'{self.bs_start.arc_name}|{pi.target_role}|{{{const.XDT_NOTALL_ARCROLE}}}')
        else:
            bs_hc = self.bs_start
        hypercubes = bs_hc.get_members(include_head=False)
        for hc in [hypercube.Hypercube(t.Concept, self, t.Arc) for t in hypercubes]:
            self.hypercubes[hc.concept.qname] = hc
            self.taxonomy.idx_hc_drs.setdefault(hc.concept.qname, set({})).add(self)
            role = hc.target_role if hc.target_role else bs_hc.role
            key = f'{bs_hc.arc_name}|{const.XDT_HYPERCUBE_DIMENSION_ARCROLE}|{role}'
            self.populate_dimensions(hc, key)

    def populate_dimensions(self, hc, key):
        bs_dim = self.taxonomy.base_sets.get(key)
        if bs_dim is None:
            return
        dimensions = bs_dim.get_members(include_head=False)
        for dim in [dimension.Dimension(t.Concept, self, t.Arc) for t in dimensions]:
            hc.dimensions[dim.concept.qname] = dim
            self.taxonomy.idx_dim_drs.setdefault(dim.concept.qname, set({})).add(self)
            role = dim.target_role if dim.target_role else bs_dim.role
            key = f'{bs_dim.arc_name}|{const.XDT_DIMENSION_DOMAIN_ARCROLE}|{role}'
            if dim.concept.is_explicit_dimension:
                self.populate_members(dim, key)

    def populate_members(self, dim, key):
        bs_mem = self.taxonomy.base_sets.get(key)
        if bs_mem is None:
            return
        members = bs_mem.get_members(start_concept=dim.concept.qname,
                                     include_head=False)  # the head is the dimension itself
        if not members:
            return
        for member in members:
            self.taxonomy.idx_mem_drs.setdefault(member.Concept.qname, set({})).add(self)
            if member.Arc is None or member.Arc.usable is True:
                dim.members[member.Concept.qname] = member
            """ Add additional members from domain-member set. """
            additional_members = self.taxonomy.get_bs_members(
                arc_name=bs_mem.arc_name, role=member.Arc.target_role if member.Arc.target_role else bs_mem.role,
                arcrole=const.XDT_DOMAIN_MEMBER_ARCROLE, start_concept=member.Concept.qname, include_head=False)
            if not additional_members:
                continue
            for additional_member in additional_members:
                if not additional_member or not additional_member.Concept:
                    continue
                self.taxonomy.idx_mem_drs.setdefault(additional_member.Concept.qname, set({})).add(self)
                if additional_member.Arc is None or additional_member.Arc.usable is True:
                    dim.members[additional_member.Concept.qname] = additional_member

    def get_dimensions(self):
        dims = set()
        for hc in self.hypercubes.values():
            dims.update(d for d in hc.dimensions)
        return dims

    def get_dimension_members(self, dim_qname):
        mems = []
        for hc in self.hypercubes.values():
            for dim in hc.dimensions.values():
                if dim.concept.qname != dim_qname:
                    continue
                for mem in [m for m in dim.members.values()]:
                                  # key=lambda m: float(m.Arc.order) if m.Arc and m.Arc.order else 0):
                    mems.append(mem)
        return mems

    def info(self):
        return self.bs_start.get_key()
```

## xdt/hypercube.py
```py
class Hypercube:
    def __init__(self, concept, container_dr_set, arc=None):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.primary_item = None
        self.target_role = arc.target_role
        self.dimensions = {}

    def has_signature(self, signature):
        """ Check if the hypercube includes a specific signature """
        parts = signature.split('|')
        for part in parts:
            dim_qname = part.split('#')[0]
            mem_qname = part.split('#')[1]
            dim = self.dimensions.get(dim_qname)
            if dim is None or dim.members is None:
                return False  # No matching dimension
            mem = dim.members.get(mem_qname)
            if mem is None:
                return False  # No matching member
        return True

    def num_signatures(self):
        """ Calculates the number of signatures for the hypercube """
        if self.dimensions is None:
            return 0
        return sum([0 if d is None or d.members is None else len(d.members) for d in self.dimensions.values()])
```

## xdt/primary_item.py
```py
class PrimaryItem:
    def __init__(self, concept, container_dr_set, arc=None, lvl=0):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.target_role = arc.target_role if arc else None
        self.level = lvl
        """ All hypercube definitions related to that primary item - all and notAll """
        self.hypercubes = {}
```

## xlink.py
```py
from ..taxonomy import arc, base_set, locator, resource, concept, roletype, arcroletype
from ..taxonomy.formula import parameter, value_assertion, existence_assertion, consistency_assertion, assertion, \
    filter, assertion_set
from ..base import ebase, const, util, data_wrappers
from ..taxonomy.table import table, breakdown, rule_node, cr_node, dr_node, aspect_node
import urllib.parse

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
class XLink(ebase.XmlElementBase):
    """ Represents an extended link """
    def __init__(self, e, container_linkbase, esef_filing_root=None):
        self.linkbase = container_linkbase
        parsers = {
            'default': self.l_xlink,
            f'{{{const.NS_GEN}}}arc': self.l_arc,
            f'{{{const.NS_LINK}}}labelArc': self.l_arc,
            f'{{{const.NS_LINK}}}referenceArc': self.l_arc,
            f'{{{const.NS_LINK}}}definitionArc': self.l_arc,
            f'{{{const.NS_LINK}}}presentationArc': self.l_arc,
            f'{{{const.NS_LINK}}}calculationArc': self.l_arc,
            f'{{{const.NS_TABLE}}}tableBreakdownArc': self.l_arc,
            f'{{{const.NS_TABLE}}}breakdownTreeArc': self.l_arc,
            f'{{{const.NS_TABLE}}}aspectNodeFilterArc': self.l_arc,
            f'{{{const.NS_TABLE}}}tableFilterArc': self.l_arc,
            f'{{{const.NS_TABLE}}}tableParameterArc': self.l_arc,
            f'{{{const.NS_TABLE}}}definitionNodeSubtreeArc': self.l_arc,
            f'{{{const.NS_LINK}}}loc': self.l_loc,
            f'{{{const.NS_LINK}}}label': self.l_resource,
            f'{{{const.NS_FORMULA_MESSAGE}}}message': self.l_resource,
            f'{{{const.NS_GEN_LABEL}}}label': self.l_resource,
            f'{{{const.NS_LINK}}}reference': self.l_reference,
            f'{{{const.NS_GEN_REF}}}reference': self.l_reference,
            f'{{{const.NS_TABLE}}}table': self.l_table,
            f'{{{const.NS_TABLE}}}breakdown': self.l_breakdown,
            f'{{{const.NS_TABLE}}}ruleNode': self.l_rule_node,
            f'{{{const.NS_TABLE}}}conceptRelationshipNode': self.l_concept_relationship_node,
            f'{{{const.NS_TABLE}}}dimensionRelationshipNode': self.l_dimensional_relationship_node,
            f'{{{const.NS_TABLE}}}aspectNode': self.l_aspect_node,
            f'{{{const.NS_VARIABLE}}}parameter': self.l_parameter,
            f'{{{const.NS_VALIDATION}}}assertionSet': self.l_ass,
            f'{{{const.NS_VALUE_ASSERTION}}}valueAssertion': self.l_va,
            f'{{{const.NS_EXISTANCE_ASSERTION}}}existenceAssertion': self.l_ea,
            f'{{{const.NS_CONSISTENCY_ASSERTION}}}consistencyAssertion': self.l_ca,
            f'{{{const.NS_DIMENSION_FILTER}}}explicitDimension': self.l_filter,
            f'{{{const.NS_DIMENSION_FILTER}}}typedDimension': self.l_filter,
        }
        self.conn_methods = {
            'Concept=>Resource': self.conn_cr,
            'Resource=>Resource': self.conn_rr,
            'Resource=>String': self.conn_rstr,
            'Concept=>Concept': self.conn_cc,
            'RoleType=>Resource': self.conn_rtr,
            'ArcroleType=>Resource': self.conn_artr,
            'Concept=>RoleType': self.conn_crt,
            'Concept=>ArcroleType': self.conn_cart
        }

        """ Locators indexed by unique identifier """
        self.locators = {}
        """ Locators by href """
        self.locators_by_href = {}
        """ Arcs indexed by from property """
        self.arcs_from = {}
        """ Arcs indexed by to property """
        self.arcs_to = {}
        """ All labelled resources indexed by global identifier """
        self.resources = {}
        #def __init__(self, location=None, container_pool=None, parsers=None, root=None, esef_filing_root = None):
        super(XLink, self).__init__(e, parsers, esef_filing_root = esef_filing_root)
        self.role = e.attrib.get(f'{{{const.NS_XLINK}}}role')

    def l_xlink(self, e):
        self.l_children(e)

    def l_resource(self, e):
        resource.Resource(e, self)

    def l_reference(self, e):
        ref = resource.Resource(e, self)
        ref.origin = e  # Tricky assignment of origin to save memory

    def l_table(self, e):
        table.Table(e, self)

    def l_breakdown(self, e):
        breakdown.Breakdown(e, self)

    def l_rule_node(self, e):
        rule_node.RuleNode(e, self)

    def l_aspect_node(self, e):
        aspect_node.AspectNode(e, self)

    def l_concept_relationship_node(self, e):
        cr_node.ConceptRelationshipNode(e, self)

    def l_dimensional_relationship_node(self, e):
        dr_node.DimensionalRelationshipNode(e, self)

    def l_arc(self, e):
        arc.Arc(e, self)

    def l_loc(self, e):
        loc = locator.Locator(e, self)
        url = loc.url
        #logger.debug(f"taxonomy.xlink l_loc() calling add_reference: url: {url}, self.linkbase.base: {self.linkbase.base}, self.esef_filing_root: {self.esef_filing_root}")
        self.linkbase.pool.add_reference(url, self.linkbase.base, self.esef_filing_root)
        #logger.debug(f"Added reference: {url} to {self.linkbase.base} with esef_filing_root: {self.esef_filing_root}")
    def l_parameter(self, e):
        parameter.Parameter(e, self)

    def l_ass(self, e):
        assertion_set.AssertionSet(e, self)

    def l_va(self, e):
        value_assertion.ValueAssertion(e, self)

    def l_ea(self, e):
        existence_assertion.ExistenceAssertion(e, self)

    def l_ca(self, e):
        consistency_assertion.ConsistencyAssertion(e, self)

    def l_filter(self, e):
        filter.Filter(e, self)

    def compile(self):
        for arc_list in [a for a in self.arcs_from.values()]:
            for a in arc_list:
                from_objects = self.identify_objects(a.xl_from)
                if from_objects is None:
                    # print('Cannot resolve arc.from: ', a.xl_from, 'in', self.linkbase.location)
                    continue
                to_objects = self.identify_objects(a.xl_to)
                if to_objects is None:
                    # print('Cannot resolve arc.to: ', a.xl_to, 'in', self.linkbase.location)
                    continue
                for obj_from in from_objects:
                    for obj_to in to_objects:
                        self.try_connect_objects(a, obj_from, obj_to)

    def try_connect_objects(self, a, obj_from, obj_to):
        key = f'{self.get_obj_type(obj_from)}=>{self.get_obj_type(obj_to)}'
        method = self.conn_methods.get(key, None)
        if method is None:
            print('Unknown object types combination: ', key)
            return
        method(a, obj_from, obj_to)

    def conn_cr(self, a, c, res):
        r_list = c.resources.get(res.name, None)
        if r_list is None:
            r_list = {}
            c.resources[res.name] = r_list
        r_list.setdefault(self.get_resource_key(res), []).append(res)  # Multiple resources of the same type may be related

    def conn_cc(self, a, c_from, c_to):
        key = f'{a.arcrole}|{a.xl_from}'
        is_root = key not in self.arcs_to
        bs_key = f'{a.name}|{a.arcrole}|{self.role}'
        bs = self.linkbase.pool.current_taxonomy.base_sets.get(bs_key, None)
        if bs is None:
            bs = base_set.BaseSet(a.name, a.arcrole, self.role)
            self.linkbase.pool.current_taxonomy.base_sets[bs_key] = bs
        if is_root and c_from not in bs.roots:
            bs.roots.append(c_from)
        # Populate concept child and parent sets
        c_from.chain_dn.setdefault(bs_key, []).append(data_wrappers.BaseSetNode(c_to, 0, a, False, c_to.get_label()))
        c_to.chain_up.setdefault(bs_key, []).append(data_wrappers.BaseSetNode(c_from, 0, a, False, c_from.get_label()))

    def conn_rr(self, a, r_from, r_to):
        if not isinstance(r_from, assertion_set.AssertionSet):
            r_to.parent = r_from
        r_to.order = a.order
        if isinstance(r_to, breakdown.Breakdown):
            r_to.axis = a.axis
        r_from.nested.setdefault(r_to.name, {}).setdefault(self.get_resource_key(r_to), []).append(r_to)

    def conn_rstr(self, a, ass, sev):
        if isinstance(ass, assertion.Assertion):
            ass.severity = sev

    def conn_rtr(self, a, rt, res):
        res.parent = rt
        rt.labels.setdefault(res.name, {}).setdefault(self.get_resource_key(res), []).append(res)

    def conn_artr(self, a, art, res):
        res.parent = art
        art.labels.setdefault(res.name, {}).setdefault(self.get_resource_key(res), []).append(res)

    def conn_crt(self, a, c, rt):
        c.resources.setdefault(rt.name, {}).setdefault(rt.role_uri, []).append(rt)

    def conn_cart(self, a, c, art):
        c.resources.setdefault(art.name, {}).setdefault(art.arcrole_uri, []).append(art)

    """ Identifies a list of objects referred by a XLabel identifier
        xbrl is the from, or to attribute of the arc """
    def identify_objects(self, xlbl):
        # Seek by XLabel directly in current link
        res = self.resources.get(xlbl, None)
        if res is not None:
            return res
        # Seek role type by roleUri in taxonomy
        rt = self.linkbase.pool.current_taxonomy.role_types.get(xlbl, None)
        if rt is not None:
            return [rt]
        # Seek arcrole type by roleUri in taxonomy
        art = self.linkbase.pool.current_taxonomy.arcrole_types.get(xlbl, None)
        if art is not None:
            return [art]
        loc = self.locators.get(xlbl, None)
        if loc is None:
            return None
        if loc.url == const.URL_ASSERTION_SEVERITIES:
            return [loc.fragment_identifier]  # Directly assign severity to assertion
        href = urllib.parse.unquote(util.reduce_url(loc.href))
        # Seek for a concept
        c = self.linkbase.pool.current_taxonomy.concepts.get(href, None)
        if c is not None:
            return [c]
        # Seek global resource by XPointer
        res = self.linkbase.pool.current_taxonomy.resources.get(href, None)
        if res is not None:
            return [res]
        # Seek role type by XPointer
        rt = self.linkbase.pool.current_taxonomy.role_types_by_href.get(href, None)
        if rt is not None:
            return [rt]
        # Seek arcrole type by XPointer
        art = self.linkbase.pool.current_taxonomy.arcrole_types_by_href.get(href, None)
        if art is not None:
            return [art]

    def get_resource_key(self, res):
        return f'{res.lang}|{res.role}' if res.lang or res.role else res.xlabel

    def get_obj_type(self, obj):
        if isinstance(obj, str):
            return 'String'
        if isinstance(obj, concept.Concept):
            return 'Concept'
        if isinstance(obj, resource.Resource):
            return 'Resource'
        if isinstance(obj, roletype.RoleType):
            return 'RoleType'
        if isinstance(obj, arcroletype.ArcroleType):
            return 'ArcroleType'
```
