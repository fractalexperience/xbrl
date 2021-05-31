from xbrl.taxonomy import resource


class TableResource(resource.Resource):
    """ Implements a Table Linkbase resource """
    def __init__(self, e, container_xlink=None):
        self.span = 0
        super().__init__(e, container_xlink)

    def compile(self, names=None, lvl=0, s_node=None):
        # print('-'*lvl, self.xlabel, f'[{self.get_rc_label()}]',  self.get_label())
        dct = self.nested
        for name in filter(lambda n: n in dct, names):
            for r in [res for r_lst in dct.get(name).values() for res in r_lst]:  # Flatten the result list of lists.
                r.compile(names, lvl+1, s_node)
