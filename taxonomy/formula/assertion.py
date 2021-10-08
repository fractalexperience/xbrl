from xbrl.taxonomy import resource


class Assertion(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.severity = 'ERROR'
        super().__init__(e, container_xlink)
        self.implicit_filtering = e.attrib.get('implicitFiltering')
        self.aspect_model = e.attrib.get('aspectModel')
