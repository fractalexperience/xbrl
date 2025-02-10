from ...taxonomy.formula import assertion


class ExistenceAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        self.test = e.attrib.get('test')
        container_xlink.linkbase.pool.current_taxonomy.existence_assertions[self.xlabel] = self
