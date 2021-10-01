from xbrl.taxonomy import concept, linkbase, roletype, arcroletype, simple_type, item_type, tuple_type
from xbrl.base import fbase, const, element, util
import os


class Schema(fbase.XmlFileBase):
    def __init__(self, location, container_pool):
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
        """ Complex types with simple content """
        self.item_types = {}
        """ Complex types with complex content """
        self.tuple_types = {}

        self.pool = container_pool
        resolved_location = util.reduce_url(location)
        if self.pool is not None:
            self.pool.discovered[location] = True
        super().__init__(resolved_location, container_pool, parsers)
        if self.pool is not None:
            self.pool.schemas[resolved_location] = self

    def l_schema(self, e):
        self.target_namespace = e.get('targetNamespace')
        self.target_namespace_prefix = self.namespaces_reverse.get(self.target_namespace, None)
        # Load files referenced in schemaLocation attribute
        for uri, href in self.schema_location_parts.items():
            self.pool.add_reference(href, self.base)
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
        lb = linkbase.Linkbase(self.location, self.pool, e)
        self.pool.linkbases[self.location] = lb
        self.pool.current_taxonomy.attach_linkbase(self.location, lb)

    def l_linkbase_ref(self, e):
        href = e.get(f'{{{const.NS_XLINK}}}href')
        if not href.startswith('http'):
            href = util.reduce_url(os.path.join(self.base, href).replace('\\', '/'))
        self.linkbase_refs[href] = e
        self.pool.add_reference(href, self.base)

    def l_roletype(self, e):
        roletype.RoleType(e, self)

    def l_arcroletype(self, e):
        arcroletype.ArcroleType(e, self)

    def l_import(self, e):
        href = e.get('schemaLocation')
        self.imports[href] = e
        self.pool.add_reference(href, self.base)
