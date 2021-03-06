from xbrl.taxonomy.table import tlb_resource, str_node


class Table(tlb_resource.TableResource):
    """ Implements a XBRL table """
    def __init__(self, e, container_xlink=None):
        # These attributes will be set during compilation
        # self.headers = {}
        # self.structure = {}
        self.has_rc_labels = False
        self.has_db_labels = False
        self.open_axes = set({})
        super().__init__(e, container_xlink)
        container_xlink.linkbase.taxonomy.tables[self.xlabel] = self

    def get_label(self):
        lbl = super().get_label()
        return self.xlabel if lbl is None else lbl

    def get_rc_label(self):
        rc = super().get_rc_label()
        return '' if rc is None else rc

    def get_db_label(self):
        db = super().get_db_label()
        return '' if db is None else db
