from xbrl.taxonomy import resource


class Table(resource.Resource):
    """ Implements a XBRL table """

    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        container_xlink.linkbase.taxonomy.tables[self.xlabel] = self

    def compile(self):
        print()
        print('Compiling', self.xlabel)
        names = ['breakdown', 'ruleNode', 'aspectNode', 'conceptRelationshipNode', 'dimensionRelationshipNode']
        self.walk(names, self.nested, 0)

    def walk(self, names, dct, lvl):
        for name in names:
            lst = dct.get(name, None)
            if not lst:
                continue
            for rlst in lst.values():
                for r in rlst:
                    print('-'*lvl, r.xlabel, f'[{r.get_rc_label()}]',  r.get_label())
                    self.walk(names, r.nested, lvl+1)
