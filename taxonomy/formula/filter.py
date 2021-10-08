from xbrl.taxonomy import resource


class Filter(resource.Resource):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
