from xbrl.taxonomy.formula import assertion


class ConsistencyAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        self.strict = e.attrib.get('strict')
        self.abs_radius = e.attrib.get('absoluteAcceptanceRadius')
        self.prop_radius = e.attrib.get('proportionalAcceptanceRadius')
        container_xlink.resources.setdefault(self.xlabel, []).append(self)
        container_xlink.linkbase.pool.current_taxonomy.consistency_assertions[self.xlabel] = self
