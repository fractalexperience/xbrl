from docutils.nodes import table
from xbrl.taxonomy.table import table
from xbrl.taxonomy import resource


class TableEngine:
    def __init__(self, t, d=None):
        self.taxonomy = t
        self.document = d
        """ Structures corresponding to compiled tables. 
            Key is table Id, value is the corresponding  x,y,z structure """
        self.structures = {}
        self.resource_names = ['breakdown', 'ruleNode', 'aspectNode',
                               'conceptRelationshipNode', 'dimensionRelationshipNode']

    def compile_table(self, t):
        struct = self.structures.setdefault(t.xlabel, {})
        self.compile(struct, t.nested, 0)

    def compile(self, struct, dct, lvl):
        for name in filter(lambda n: n in dct, self.resource_names):
            for r in [res for r_lst in dct.get(name).values() for res in r_lst]:  # Flatten the result list of lists.
                print('-'*lvl, r.xlabel, f'[{r.get_rc_label()}]',  r.get_label())
                self.compile(struct, r.nested, lvl+1)

    def compile_all(self):
        for t in self.taxonomy.tables.values():
            self.compile_table(t)

    def compile_table_id(self, table_id):
        t = self.taxonomy.tables.get(table_id, None)
        if t is None:
            return
