from xbrl.taxonomy.table import tlb_resource


class Breakdown(tlb_resource.TableResource):
    """ Implements a XBRL table breakdown"""

    def __init__(self, e, container_xlink=None):
        self.parent_child_order = e.attrib.get('parentChildOrder')
        self.axis = None
        self.is_open = False
        self.is_closed = False
        super().__init__(e, container_xlink)
