from xbrl.taxonomy import resource


class DimensionalRelationshipNode(resource.Resource):
    """ Implements a dimensional relationship """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
