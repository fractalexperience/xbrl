from xbrl.base import data_wrappers, const
import os, json


class Cube:
    def __init__(self):
        self.lexic = set()  # Unique lexic
        self.idx = {}  # Index of lexic
        self.idr = {}  # Reverse index
        self.semantics = {}  # Semantics
        self.labels = {}  # Dictionary with labels
        self.pairs = {}  # All combinations of dimension+member values together with corresponding facts
        self.facts = set()

    def add_lex(self, t):
        self.lexic.add(t)
        i = self.idr.setdefault(t, len(self.lexic))
        self.idx[i] = t
        return i

    def add_mem(self, d, m):
        i_d = self.add_lex(d)
        i_m = self.add_lex(m)
        self.semantics.setdefault(i_d, set()).add(i_m)
        return f'{i_d}.{i_m}'

    def process_dimensional_container(self, container, signature, xid):
        for dim, e in container.items():
            self.handle_concept(dim, xid)  # Add label for dimension concept
            dimfull = xid.taxonomy.resolve_qname(dim)
            if e.tag == f'{{{const.NS_XBRLDI}}}explicitMember':
                memfull = xid.taxonomy.resolve_qname(e.text)
                signature.add(self.add_mem(dimfull, memfull))
                self.handle_concept(e.text, xid)  # Add label for member concept
            elif e.tag == f'{{{const.NS_XBRLDI}}}typedMember':
                for e2 in e.iterchildren():
                    signature.add(self.add_mem(dimfull, f'{(e2.tag.replace("{","").replace("}",":"))}|{e2.text}'))

    def handle_concept(self, qname, xid):
        pref = qname.split(':')[0] if ':' in qname else None
        if pref is None:
            return
        namespace = xid.taxonomy.resolve_prefix(pref)
        nm = qname.split(':')[1] if ':' in qname else qname
        concept = xid.taxonomy.concepts_by_qname.get(qname, None)
        if concept is None:
            return
        self.add_label(self.add_lex(f'{namespace}:{nm}'), concept.get_label())

    def add_label(self, key, label):
        if key is None or label is None:
            return
        self.labels[key] = label

    def add_fact(self, fct, xid):
        signature = set()
        signature.add(self.add_mem('metric', f'{fct.namespace}:{fct.name}'))
        self.handle_concept(fct.qname, xid)
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
                self.process_dimensional_container(fct.context.scenario, signature, xid)
            if fct.context.segment:
                self.process_dimensional_container(fct.context.segment, signature, xid)
        # Add fact to global index of facts
        f = data_wrappers.OimFact(f'f{len(self.facts)}', '|'.join(sorted(signature)), fct.value)
        self.facts.add(f)
        for k in signature:
            self.pairs.setdefault(k, set()).add(f)

    def save(self, fold):
        if not os.path.exists(fold):
            os.mkdir(fold)
        json.dump(self.idx, open(os.path.join(fold, 'idx.json'), 'w'))
        json.dump(self.idr, open(os.path.join(fold, 'idr.json'), 'w'))
        json.dump(self.labels, open(os.path.join(fold, 'lbl.json'), 'w'))
        nsem = {}
        for k, v in self.semantics.items():
            nsem[k] = [it for it in v]
        json.dump(nsem, open(os.path.join(fold, 'sem.json'), 'w'))
        for k, factset in self.pairs.items():
            json.dump([f for f in factset], open(os.path.join(fold, f'{k}.json'), 'w'))
