from xbrl.taxonomy import resource


class Breakdown(resource.Resource):
    """ Implements a XBRL table breakdown"""
    def __init__(self, e, container_xlink=None):
        self.parent_child_order = e.attrib.get('parentChildOrder')
        self.axis = None
        self.order = 0
        super().__init__(e, container_xlink)
