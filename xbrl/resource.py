from xbrl import const
from xbrl import ebase
from xbrl import util


class Resource(ebase.XmlElementBase):
    def __init__(self, e, container_xlink = None):
        self.xlink = container_xlink
        super().__init__(e)
        self.label = e.attrib.get(f'{{{const.NS_XLINK}}}label')
        self.role = e.attrib.get(f'{{{const.NS_XLINK}}}role')
        self.text = e.text
        if self.xlink is not None:
            util.u_dct_list(self.xlink.resources, self.label, self)


