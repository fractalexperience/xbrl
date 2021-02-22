class Ixbrl:
    """ Implements an iXbrl model """
    def __init__(self, e):
        self.idx_name = {}
        self.idx_attr = {}
        self.idx_attr_value = {}
        self.idx_name_attr_value = {}
        self.index(e)

    def index(self, e):
        """ Populates indixes """
        pass

    def strip(self):
        """ Serializes native XBRL """
        pass
