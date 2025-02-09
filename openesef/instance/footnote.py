from openesef.taxonomy import resource


class Footnote(resource.Resource):
    def __init__(self, e):
        super(Footnote, self).__init__(e, assign_origin=True)
        self.facts = []
