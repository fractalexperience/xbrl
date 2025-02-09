import json
import os
import tempfile
from openesef.base import archiver
from openesef.base import data_wrappers, const


class Cube:
    def __init__(self, folder=None):
        self.work_folder = folder if folder else tempfile.gettempdir()
        if not os.path.exists(self.work_folder):
            os.mkdir(self.work_folder)
        self.lexic = set()  # Unique lexic
        self.idx = {}  # Index of lexic
        self.idr = {}  # Reverse index

        self.dim_mem = {}  # Semantics - Key is dimension code, value is the set of members
        self.mem_dim = {}  # Semantics - Key is member code. value is the set of dimensions
        self.dim_dim = {}  # Dimension to other dimensions
        self.mem_mem = {}  # Member to other members

        self.labels = {}  # Dictionary with labels
        self.pairs = {}  # All combinations of dimension+member values together with corresponding facts
        self.facts = set()
        self.idx_ent_dim = {}  # Key is entity code, value is a set of all related dimensions
        self.idx_ent_mem = {}  # Key is entity code, value is a set of all related members for all dimensions
        self.archiver = archiver.Archiver(self.work_folder, length=2)

    def add_lex(self, t):
        self.lexic.add(t)
        i = self.idr.setdefault(t, len(self.lexic))
        self.idx[i] = t
        return i

    def add_mem(self, d, m, ent):
        """ Populates lexic, semantics and relationship entity-dimension/entity-member"""
        i_d = self.add_lex(d)
        i_m = self.add_lex(m)
        i_ent = self.add_lex(ent)
        # Key is dimension code, member is the set of members
        self.dim_mem.setdefault(i_d, set()).add(i_m)
        self.mem_dim.setdefault(i_m, set()).add(i_d)

        self.idx_ent_dim.setdefault(i_ent, set()).add(i_d)
        self.idx_ent_mem.setdefault(i_ent, set()).add(i_m)
        return f'{i_d}.{i_m}'

    def process_dimensional_container(self, container, signature, xid, ent):
        for dim, e in container.items():
            self.handle_concept(dim, xid)  # Add label for dimension concept
            dimfull = xid.taxonomy.resolve_qname(dim)
            if e.tag == f'{{{const.NS_XBRLDI}}}explicitMember':
                memfull = xid.taxonomy.resolve_qname(e.text)
                signature.add(self.add_mem(dimfull, memfull, ent))
                self.handle_concept(e.text, xid)  # Add label for member concept
            elif e.tag == f'{{{const.NS_XBRLDI}}}typedMember':
                for e2 in e.iterchildren():
                    signature.add(
                        self.add_mem(dimfull, f'{(e2.tag.replace("{", "").replace("}", ":"))}|{e2.text}', ent))

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
        if fct.context is None or fct.value is None or fct.unit is None:  # Skip non numeric facts - TO RECONSIDER
            return
        ent = f'{fct.context.entity_scheme}:{fct.context.entity_identifier}'
        signature = set()
        signature.add(self.add_mem('metric', f'{fct.namespace}:{fct.name}', ent))
        self.handle_concept(fct.qname, xid)

        if fct.decimals:
            signature.add(self.add_mem('decimals', f'{fct.decimals}', ent))
        if fct.precision:
            signature.add(self.add_mem('precision', f'{fct.precision}', ent))
        if fct.unit:
            signature.add(self.add_mem('unit', f'{fct.unit.get_aspect_value()}', ent))

        signature.add(self.add_mem('entity', ent, ent))
        signature.add(self.add_mem('period', f'{fct.context.get_period_string()}', ent))
        if fct.context.scenario:
            self.process_dimensional_container(fct.context.scenario, signature, xid, ent)
        if fct.context.segment:
            self.process_dimensional_container(fct.context.segment, signature, xid, ent)

        # Add fact to global index of facts
        f = data_wrappers.OimFact(f'f{len(self.facts)}', '|'.join(sorted(signature)), fct.value)
        self.facts.add(f)
        for k in signature:
            self.pairs.setdefault(k, set()).add(f)

    def save(self):
        self.archiver.open()
        # Key is integer code, value is the lexic part
        self.archiver.store_content('idx.json', json.dumps(self.idx))
        # Key is the lexic part, value is the integer code
        self.archiver.store_content('idr.json', json.dumps(self.idr))
        # Identifiers resolved to labels
        self.archiver.store_content('lbl.json', json.dumps(self.labels))
        # Relationships entity-dimension
        # Key is the code of entity dimension, value is the set of all belonging dimensions
        ent_dim = {}
        for k, v in self.idx_ent_dim.items():
            ent_dim[k] = [d for d in v]
        self.archiver.store_content('ent_dim.json', json.dumps(ent_dim))
        # Relationships entity-member
        # Key is the key of entity dimension, value is the set of all belonging members of any other dimension
        ent_mem = {}
        for k, v in self.idx_ent_mem.items():
            ent_mem[k] = [m for m in v]
        self.archiver.store_content('ent_mem.json', json.dumps(ent_dim))
        # Semantics
        # Key is dimension code, value is the list of all belonging members
        dim_mem = {}
        for k, v in self.dim_mem.items():
            dim_mem[k] = [it for it in v]
        self.archiver.store_content('dim_mem.json', json.dumps(dim_mem))
        # Key is member code, value is the set of related dimensions
        mem_dim = {}
        for k, v in self.mem_dim.items():
            mem_dim[k] = [it for it in v]
        self.archiver.store_content('mem_dim.json', json.dumps(mem_dim))
        # Fact sets
        # Key is the combination of dimension.member (resolved to codes). Value is the collection of all belonging facts
        for k, factset in self.pairs.items():
            self.archiver.store_content(f'{k}.json', json.dumps([f for f in factset]))

        self.archiver.close()

    def load(self):
        pass
        # idx_filename = os.path.join(path, 'idx.json')
        # if not os.path.exists(idx_filename):
        #     return
        # with open(idx_filename, 'r') as f:
        #     self.idx = json.load(f)
        # with open(os.path.join(path, 'idr.json'), 'r') as f:
        #     self.idr = json.load(f)
        # with open(os.path.join(path, 'lbl.json'), 'r') as f:
        #     self.labels = json.load(f)
        # with open(os.path.join(path, 'ent_dim.json'), 'r') as f:
        #     nent_dim = json.load(f)
        # for k, v in nent_dim.items():
        #     self.idx_ent_dim.setdefault(k, set()).update(v)
        # with open(os.path.join(path, 'ent_mem.json'), 'r') as f:
        #     nent_mem = json.load(f)
        # for k, v in nent_mem.items():
        #     self.idx_ent_mem.setdefault(k, set()).update(v)
        # archive = ZipFile(os.path.join(path, 'data.zip'))
        # for it in archive.filelist:
        #     with archive.open(it.filename) as f:
        #         k = it.filename.replace('.json', '')
        #         fact_list = json.load(f)
        #         for fl in fact_list:
        #             df = data_wrappers.OimFact(fl[0], fl[1], fl[2])
        #             self.pairs.setdefault(k, set()).add(f)
        # archive.close()
