from xbrl import ebase
from xbrl import const


class Context(ebase.XmlElementBase):
    def __init__(self, e):
        self.descriptors = {}
        self.period_instant = None
        self.period_start = None
        self.period_end = None
        self.entity_scheme = ''
        self.entity_identifier = ''
        self.segment = {}
        self.scenario = {}
        self.dimensional_container = None # To be set further during parsing
        self.segment_non_xdt = {}
        self.scenario_non_xdt = {}
        parsers = {
            f'{{{const.NS_XBRLI}}}context': self.load_context,
            f'{{{const.NS_XBRLI}}}period': self.load_period,
            f'{{{const.NS_XBRLI}}}entity': self.load_entity,
            f'{{{const.NS_XBRLI}}}identifier': self.load_entity_identifier,
            f'{{{const.NS_XBRLI}}}segment': self.load_segment,
            f'{{{const.NS_XBRLI}}}scenario': self.load_scenario,
            f'{{{const.NS_XBRLDI}}}explicitMember': self.load_member,
            f'{{{const.NS_XBRLDI}}}typedMember': self.load_member
        }
        super().__init__(e, parsers)

    def load_context(self, e):
        pass

    def load_period(self, e):
        for e in e.iterchildren():
            if e.tag == f'{{{const.NS_XBRLI}}}instant':
                self.period_instant = e.text
            elif e.tag == f'{{{const.NS_XBRLI}}}startDate':
                self.period_start = e.text
            elif e.tag == f'{{{const.NS_XBRLI}}}endDate':
                self.period_end = e.text

    def load_entity(self, e):
        self.l_children(e)

    def load_entity_identifier(self, element):
        self.entity_identifier = element.text
        self.entity_scheme = element.attrib.get("scheme")

    def load_segment(self, e):
        self.dimensional_container = self.segment
        self.l_children(e)

    def load_scenario(self, e):
        self.dimensional_container = self.scenario
        self.l_children(e)

    def load_member(self, e):
        dimension = e.attrib.get("dimension")
        self.dimensional_container[dimension] = e
        self.descriptors[dimension] = e

    def get_period_string(self):
        if self.period_instant:
            return self.period_instant
        return f'{self.period_start}/{self.period_end}'

    def get_xdt_signature(self):
        return "|".join([f'{k}#{self.descriptors.get(k).text}' for k in self.descriptors])

    def get_simplified_signature(self):
        return "|".join([f'{k}' for k in self.descriptors])

    def get_signature(self):
        return "|".join([
            f'entity#{self.entity_scheme}:{self.entity_identifier}',
            f'period#{self.get_period_string()}',
            self.get_xdt_signature()
        ])
