from xbrl.base import ebase


class Element(ebase.XmlElementBase):
    def __init__(self, e, container_schema):
        super().__init__(e)
        self.schema = container_schema
        self.prefix = self.schema.target_namespace_prefix
        self.id = e.attrib.get('id', None)
        self.name = e.attrib.get('name', None)
        self.qname = f'{self.prefix}:{self.name}'
        self.unique_id = f'{{{self.schema.target_namespace}}}{self.name}'
        self.schema.elements[self.unique_id] = self
        self.substitution_group = e.attrib.get('substitutionGroup')
        nil = e.attrib.get('nillable')
        self.nillable = nil is not None and nil.lower() == 'true' or nil == '1'
        abstr = e.attrib.get('abstract')
        self.abstract = abstr is not None and abstr.lower() == 'true' or abstr == '1'
