from openesef.base import ebase, const


class Context(ebase.XmlElementBase):
    def __init__(self, e):
        self.descriptors = {}
        self.period_instant = None
        self.period_start = None
        self.period_end = None
        self.entity_scheme = ''
        self.entity_identifier = ''
        self.segment = None
        self.scenario = None
        self.dimensional_container = None # To be set further during parsing
        self.segment_non_xdt = {}
        self.scenario_non_xdt = {}
        parsers = {
            f'{{{const.NS_XBRLI}}}context': self.l_context,
            f'{{{const.NS_XBRLI}}}period': self.l_period,
            f'{{{const.NS_XBRLI}}}entity': self.l_entity,
            f'{{{const.NS_XBRLI}}}identifier': self.l_entity_identifier,
            f'{{{const.NS_XBRLI}}}segment': self.l_segment,
            f'{{{const.NS_XBRLI}}}scenario': self.l_scenario,
            f'{{{const.NS_XBRLDI}}}explicitMember': self.l_member,
            f'{{{const.NS_XBRLDI}}}typedMember': self.l_member
        }
        super().__init__(e, parsers)

    def l_context(self, e):
        self.l_children(e)

    def l_period(self, e):
        for e in e.iterchildren():
            if e.tag == f'{{{const.NS_XBRLI}}}instant':
                self.period_instant = e.text.strip()
            elif e.tag == f'{{{const.NS_XBRLI}}}startDate':
                self.period_start = e.text.strip()
            elif e.tag == f'{{{const.NS_XBRLI}}}endDate':
                self.period_end = e.text.strip()

    def l_entity(self, e):
        self.l_children(e)

    def l_entity_identifier(self, element):
        self.entity_identifier = element.text
        self.entity_scheme = element.attrib.get("scheme")

    def l_segment(self, e):
        self.segment = {}
        self.dimensional_container = self.segment
        self.l_children(e)

    def l_scenario(self, e):
        self.scenario = {}
        self.dimensional_container = self.scenario
        self.l_children(e)

    def l_member(self, e):
        dimension = e.attrib.get("dimension")
        self.dimensional_container[dimension] = e
        self.descriptors[dimension] = e

    def get_period_string(self):
        if self.period_instant:
            return self.period_instant
        return f'{self.period_start}/{self.period_end}'

    def get_xdt_signature(self):
        return "|".join(sorted([f'{k}#{self.descriptors.get(k).text}' for k in self.descriptors]))

    def get_simplified_signature(self):
        return "|".join(sorted([f'{k}' for k in self.descriptors]))

    def get_signature(self):
        return "|".join([
            f'entity#{self.entity_scheme}:{self.entity_identifier}',
            f'period#{self.get_period_string()}',
            self.get_xdt_signature()
        ])

    def get_member(self, dim):
        """ Returns dimension member for a specified dimension QName. """
        if not self.descriptors:
            return None
        e = self.descriptors.get(dim)
        if e is None:
            return None
        if e.tag == f'{{{const.NS_XBRLDI}}}explicitMember':
            return e.text
        if e.tag == f'{{{const.NS_XBRLDI}}}typedMember':
            o = []
            for e2 in e.iterchildren():  # Should be only one
                o.append(e2.text)
            return ''.join(o)
        return None
