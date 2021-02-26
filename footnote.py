from xbrl import const
from xbrl import resource


class Footnote(resource.Resource):
    def __init__(self, element):
        super(Footnote, self).__init__(element)
        self.facts = []
