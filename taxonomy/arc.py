from xbrl.base import ebase, const, util


class Arc(ebase.XmlElementBase):
    def __init__(self, e, container_xlink=None):
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
        u = e.attrib.get(f'{{{const.NS_XBRLDT}}}usable')
        self.usable = True if not u else u
        self.target_role = e.attrib.get(f'{{{const.NS_XBRLDT}}}targetRole')
        self.axis = e.attrib.get('axis')  # for tableBreakdownArc
        if self.xlink is not None:
            self.xlink.arcs_from.setdefault(f'{self.arcrole}|{self.xl_from}', []).append(self)
            self.xlink.arcs_to.setdefault(f'{self.arcrole}|{self.xl_to}', []).append(self)