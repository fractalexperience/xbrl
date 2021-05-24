from xbrl.taxonomy import resource


class Table(resource.Resource):
    """ Implements a XBRL table """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        container_xlink.linkbase.taxonomy.tables[self.xlabel] = self

    def compile(self):
        breakdowns = self.nested.get('breakdown')
        if not breakdowns:
            return
