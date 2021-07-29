from xbrl.base import ebase, const


class ArcroleType(ebase.XmlElementBase):
    def __init__(self, e, container_schema=None):
        self.schema = container_schema
        self.definition = None
        self.arcrole_uri = e.attrib.get('arcroleURI')
        self.cycles_allowed = e.attrib.get('cyclesAllowed')
        self.used_on = []
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
