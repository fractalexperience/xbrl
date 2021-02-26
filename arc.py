from xbrl import const
from xbrl import ebase
from xbrl import util


class Arc(ebase.XmlElementBase):
    def __init__(self, e, container_xlink = None):
        self.xlink = container_xlink
        super().__init__(e)
        self.xl_from = e.attrib.get(f'{{{const.NS_XLINK}}}from')
        self.xl_to = e.attrib.get(f'{{{const.NS_XLINK}}}to')
        self.arcrole = e.attrib.get(f'{{{const.NS_XLINK}}}arcrole')
        self.order = e.attrib.get('order')
        self.priority = e.attrib.get('priority')
        self.use = e.attrib.get('use')
        self.weight = e.attrib.get('weight')
        self.preferredLabel = e.attrib.get('preferredLabel')
        if self.xlink is not None:
            util.u_dct_list(self.xlink.arcs_from, self.xl_from, self)
            util.u_dct_list(self.xlink.arcs_to, self.xl_to, self)
