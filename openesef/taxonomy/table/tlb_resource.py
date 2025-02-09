from openesef.taxonomy import resource


class TableResource(resource.Resource):
    """ Implements a Table Linkbase resource """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)

    def get_constraints(self, tag='default'):
        return None
