from xbrl.taxonomy import resource


class AssertionSet(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.assertions = {}
        self.tables = {}
        super().__init__(e, container_xlink)
        container_xlink.linkbase.pool.current_taxonomy.assertion_sets[container_xlink.linkbase.location] = self
