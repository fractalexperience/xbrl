from xbrl.base import ebase, const, util


class Resource(ebase.XmlElementBase):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        self.xlabel = e.attrib.get(f'{{{const.NS_XLINK}}}label')
        self.role = e.attrib.get(f'{{{const.NS_XLINK}}}role')
        self.text = e.text
        if self.xlink is not None:
            self.xlink.resources.setdefault(self.xlabel, []).append(self)
            if self.id:
                href = f'{self.xlink.linkbase.location}#{self.id}'
                self.xlink.linkbase.taxonomy.resources[href] = self
        self.nested = {}

    def get_label(self):
        return util.get_label(self.nested)

    def get_rc_label(self):
        return util.get_rc_label(self.nested)

    def get_db_label(self):
        return util.get_db_label(self.nested)
