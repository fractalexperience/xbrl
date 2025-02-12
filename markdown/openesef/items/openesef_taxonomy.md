# taxonomy Contents
## taxonomy/__init__.py
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

## taxonomy/arc.py
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

## taxonomy/arcroletype.py
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

## taxonomy/base_set.py
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

## taxonomy/concept.py
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

## taxonomy/item_type.py
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

## taxonomy/linkbase.py
```py
from ..base import fbase, const, util
from ..taxonomy import xlink

import logging

# Get a logger.  __name__ is a good default name.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
```

## taxonomy/locator.py
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

## taxonomy/resource.py
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

## taxonomy/roletype.py
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

## taxonomy/schema.py
```py
from ..taxonomy import concept, linkbase, roletype, arcroletype, simple_type, item_type, tuple_type
from ..base import fbase, const, element, util
import os

import logging

# Get a logger.  __name__ is a good default name.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
```

## taxonomy/simple_type.py
```py
from ..base import const, element, util


class SimpleType(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        unique_id = f'{self.namespace}:{self.name}'
        self.schema.simple_types[unique_id] = self
```

## taxonomy/taxonomy.py
```py
from ..base import const, data_wrappers, util
from ..taxonomy.xdt import dr_set

import logging
import traceback
# Get a logger.  __name__ is a good default name.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

class Taxonomy:
    """ entry_points is a list of entry point locations
        cache_folder is the place where to store cached Web resources """
    def __init__(self, entry_points, container_pool, esef_filing_root = None):
        self.entry_points = entry_points
        self.pool = container_pool
        self.pool.current_taxonomy = self
        self.pool.current_taxonomy_hash = util.get_hash(','.join(entry_points))
        self.esef_filing_root = esef_filing_root  # Add ESEF location path
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
            schema_obj = self.pool.add_schema(entry_point, self.esef_filing_root)
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
            self.pool.add_reference(href = ep, 
                                    base = '', 
                                    esef_filing_root = self.esef_filing_root)
            self._process_entry_point(ep)

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

## taxonomy/tpack.py
```py
import os
import zipfile
from lxml import etree as lxml
from ..base import const, resolver, util, data_wrappers


import logging

# Get a logger.  __name__ is a good default name.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

## taxonomy/tuple_type.py
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

## taxonomy/xlink.py
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
logger.setLevel(logging.DEBUG)

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
