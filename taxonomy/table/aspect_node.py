from xbrl.taxonomy import resource


class AspectNode(resource.Resource):
    """ Implements an aspect node """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)