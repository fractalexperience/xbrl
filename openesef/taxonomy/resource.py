from ..base import ebase, const, util


class Resource(ebase.XmlElementBase):
    def __init__(self, e, container_xlink=None, assign_origin=False):
        self.xlink = container_xlink
        self.nested = {}
        super().__init__(e, assign_origin=assign_origin)
        self.xlabel = e.attrib.get(f'{{{const.NS_XLINK}}}label')
        self.role = e.attrib.get(f'{{{const.NS_XLINK}}}role')
        self.text = e.text
        self.parent = None  # Parent resource if any - e.g. a table
        self.order = 0  # Order in the structure taken from arc
        if self.xlink is not None:
            self.xlink.resources.setdefault(self.xlabel, []).append(self)

    def get_label(self, lang='en', role='/label'):
        return util.get_label(self.nested, lang, role)

    def get_rc_label(self):
        return util.get_rc_label(self.nested)

    def get_db_label(self):
        return util.get_db_label(self.nested)

    def get_languages(self):
        return set([lbl.lang
                    for kind, res_dict in self.nested.items()
                    for key_label, list_labels in res_dict.items()
                    for lbl in list_labels if kind == 'label'])
