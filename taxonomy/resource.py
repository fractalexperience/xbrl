from xbrl.base import ebase, const, util


class Resource(ebase.XmlElementBase):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        self.nested = {}
        super().__init__(e)
        self.xlabel = e.attrib.get(f'{{{const.NS_XLINK}}}label')
        self.role = e.attrib.get(f'{{{const.NS_XLINK}}}role')
        self.text = e.text
        self.parent = None  # Parent resource if any - e.g. a table
        self.order = 0  # Order in the structure taken from arc
        if self.xlink is not None:
            self.xlink.resources.setdefault(self.xlabel, []).append(self)

    def get_label(self):
        return util.get_label(self.nested)

    def get_rc_label(self):
        return util.get_rc_label(self.nested)

    def get_db_label(self):
        return util.get_db_label(self.nested)
