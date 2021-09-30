from xbrl.taxonomy import resource


class Assertion(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        self.implicit_filtering = e.attrib.get('implicitFiltering')
        self.aspect_model = e.attrib.get('aspectModel')
