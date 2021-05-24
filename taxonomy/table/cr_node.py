from xbrl.taxonomy import resource


class ConceptRelationshipNode(resource.Resource):
    """ Implements a concept relationship node """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
