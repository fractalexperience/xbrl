from xbrl.base import const, element, util


class Concept(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        self.period_type = e.attrib.get('periodType')
        self.balance = e.attrib.get('balance')
        self.data_type = e.attrib.get('type')
        self.domain = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}domain')
        self.linkrole = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}linkrole')
        hu = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}headUsable')
        self.head_usable = hu is not None and (hu.lower() == 'true' or hu == '1')
        self.typed_domain_ref = e.attrib.get(f'{{{const.NS_XBRLDT}}}typedDomainRef')
        self.is_dimension = self.substitution_group.endswith('dimensionItem')
        self.is_hypercube = self.substitution_group.endswith('hypercubeItem')
        self.is_explicit_dimension = True if self.is_dimension and self.typed_domain_ref is None else False
        self.is_enumeration = True if self.data_type and self.data_type.endswith('enumerationItemType') else False
        self.is_enumeration_set = True if self.data_type and self.data_type.endswith('enumerationSetItemType') else False
        self.resources = {}  # Related labels - first by lang and then by role
        self.references = {}  # Related reference resources
        self.chain_up = {}  # Related parent concepts. Key is the base set key, value is the list of parent concepts
        self.chain_dn = {}  # Related child concepts. Key is the base set key, value is the list of child concepts
        if self.id is not None:
            key = f'{self.schema.location}#{self.id}'  # Key to search from locator href
            self.schema.taxonomy.concepts[key] = self
            self.schema.taxonomy.concepts_by_qname[self.qname] = self

    def __str__(self):
        return self.qname

    def __repr__(self):
        return self.qname

    def get_label(self, lang='en', role='/label'):
        return util.get_label(self.resources, lang, role)

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