

class Integrator:
    """ This class encapsulates functionality for manipulating instance documents such as import and render as well as
        some set operations on the set of facts such as union, intersection etc. """
    def __init__(self):
        self.reported = None

    def xid_import(self, xid):
        """ Reads a XBRL instance and sorts facts into 'bags' corresponding to tables in the taxonomy.
            If there are no tables in taxonomy, it stores the facts in one bag called 'ALL' """
