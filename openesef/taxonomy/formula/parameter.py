from ...taxonomy import resource


class Parameter(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        self.name = e.attrib.get('name')
        self.select = e.attrib.get('select')
        self.data_type = e.attrib.get('as')
        container_xlink.linkbase.pool.current_taxonomy.parameters[self.xlabel] = self
