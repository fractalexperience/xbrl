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
