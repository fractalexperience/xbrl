from xbrl.taxonomy.formula import assertion


class ExistenceAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        self.test = e.attrib.get('test')
        container_xlink.resources.setdefault(self.xlabel, []).append(self)
        container_xlink.linkbase.pool.current_taxonomy.existence_assertions[self.xlabel] = self
