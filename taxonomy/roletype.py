from xbrl.base import ebase, const


class RoleType(ebase.XmlElementBase):
    def __init__(self, e, container_schema=None):
        self.schema = container_schema
        self.definition = None
        self.role_uri = e.attrib.get('roleURI')
        self.used_on = []
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
