from xbrl.base import data_wrappers
class Cube:
    def __init__(self):
        self.lexic = set()  # Unique lexic
        self.idx = {}  # Index of lexic
        self.idr = {}  # Reverse index
        self.semantic = {}  # Semantics
        # self.content = {}  # Content
        self.pairs = {}  # All combinations of dimension+member values together with corresponding facts

    def add_lex(self, t):
        self.lexic.add(t)
        i = self.idr.setdefault(t, len(self.lexic))
        self.idx[i] = t
        return i

    def add_mem(self, d, m):
        i_d = self.add_lex(d)
        i_m = self.add_lex(m)
        self.semantic.setdefault(i_d, set()).add(i_m)
        return f'{i_d}.{i_m}'

    def add_fact(self, fct):
        signature = set()
        signature.add(self.add_mem('metric', f'{fct.namespace}:{fct.name}'))
        if fct.decimals:
            signature.add(self.add_mem('decimals', f'{fct.decimals}'))
        if fct.precision:
            signature.add(self.add_mem('precision', f'{fct.precision}'))
        if fct.unit:
            signature.add(self.add_mem('unit', f'{fct.unit.get_aspect_value()}'))
        if fct.context:
            signature.add(self.add_mem('entity', f'{fct.context.entity_scheme}:{fct.context.entity_identifier}'))
            signature.add(self.add_mem('period', f'{fct.context.get_period_string()}'))
            if fct.context.scenario:
                pass
            if fct.context.segment:
                pass
        # Add fact to global index of facts
        f = data_wrappers.OimFact('|'.join(sorted(signature)), fct.value)
        # self.content.setdefault(f.Signature, set()).add(f)
        for k in signature:
            self.pairs.setdefault(k, set()).add(f)

