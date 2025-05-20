from xbrl.base import ebase


class Fact(ebase.XmlElementBase):
    def __init__(self, default_id, e):
        self.context_ref = e.attrib.get('contextRef') if e is not None else None
        self.context = None
        self.unit_ref = e.attrib.get('unitRef') if e is not None else None
        self.unit = None
        self.decimals = e.attrib.get('decimals') if e is not None else None
        self.precision = e.attrib.get('precision') if e is not None else None
        self.value = e.text if e is not None else None
        self.footnotes = []
        self.nested_facts = {}
        self.counter = 0
        parsers = {'default': self.l_nested}
        super().__init__(e, parsers, assign_origin=True)
        if self.id is None:
            self.id = default_id

    def l_nested(self, e):
        self.counter += 1
        for e2 in e.iterchildren():
            fct = Fact(f'{self.id}.{self.counter}', e2)
            self.nested_facts[fct.id] = fct
