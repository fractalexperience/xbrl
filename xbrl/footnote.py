from xbrl import ebase
from xbrl import const


class Footnote(ebase.XmlElementBase):
    def __init__(self, element):
        super(Footnote, self).__init__(element)
        self.value = element.text
        self.role = element.attrib.get(f'{{{const.NS_XLINK}}}role')
        self.facts = []
