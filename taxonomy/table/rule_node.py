from xbrl.taxonomy import resource


class RuleNode(resource.Resource):
    """ Implements a rule node """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
