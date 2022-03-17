from xbrl.base import const, element, util


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
