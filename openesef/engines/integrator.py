class Integrator:
    """ This class encapsulates functionality for manipulating instance documents such as import and render as well as
        some set operations on the set of facts such as union, intersection etc. """

    def __init__(self):
        self.tlb_reporter = None
        self.reported = None
        self.idx_signatures = None
        """ Groups of facts - each corresponding to a particular table. """
        self.bags = None
        """ Key is the fact signature, value is table ID """
        self.sig_tid = None
        """ Key is the table ID, value is dictionary signature => mapping """
        self.tid_sig_mapping = None
        """ Set of all open dimension QNames in all tables """
        self.open_dimensions = None
        """ Set of all closed dimension QNames in all tables """
        self.closed_dimensions = None

    def create_signatures(self, xid):
        tax = xid.taxonomy
        eng = self.tlb_reporter.TableReporter(tax, None)
        ids = sorted(tax.tables)
        self.sig_tid, self.tid_sig_mapping, self.open_dimensions, self.closed_dimensions = {}, {}, set(), set()
        for tid in ids:
            eng.compile_table_id(tid)
            lo = eng.do_layout(tid)
            dpm_map = eng.get_dpm_map(tid)
            for k, m in dpm_map.Mappings.items():
                concept = m.get('Metrics')
                m['address'] = k
                if concept is None:
                    continue
                sig_met = f'concept#{concept}'
                sig_dim = '|'.join(sorted([f'{dim}#{mem}' for dim, mem in m.items() if ':' in dim and mem != 'N/A']))
                open_dim = [dim for dim, mem in m.items() if ':' in dim and mem == '*']
                closed_dim = [dim for dim, mem in m.items() if ':' in dim and mem != '*']
                self.open_dimensions.update(open_dim)
                self.closed_dimensions.update(closed_dim)
                sig = '|'.join([sig_met, sig_dim]) if sig_dim else sig_met
                self.sig_tid[sig] = tid
                self.tid_sig_mapping.setdefault(tid, {}).setdefault('signatures', {})[sig] = m
                self.tid_sig_mapping.setdefault(tid, {}).setdefault('open_dimensions', set()).update(open_dim)

    def create_fact_index(self, xid):
        if self.idx_signatures is None:
            fidx = {}
        for fid, f in xid.xbrl.facts.items():
            concept = xid.taxonomy.concepts_by_qname.get(f.qname)
            context = f.context
            parts = set()
            for dim, e in context.descriptors.items():
                mem = '*' if dim in self.open_dimensions else e.text
                parts.add(f'{dim}#{mem}')
            sig_met = f'concept#{concept.qname}'
            sig_dim = '|'.join(sorted(parts))
            fsig = '|'.join([sig_met, sig_dim]) if sig_dim else sig_met
            self.idx_signatures.setdefault(fsig, set()).add(f)

    def xid_import(self, xid):
        """ Reads a XBRL instance and sorts facts into 'bags' corresponding to tables in the taxonomy.
            If there are no tables in taxonomy, it stores the facts in one bag called 'ALL' """
        xid.xbrl.compile()
        self.create_signatures(xid)
        if self.bags is None:
            self.bags = {}
        for fsig, fset in self.idx_signatures.items():
            tid = self.sig_tid.get(fsig, 'ALL')
            self.bags.setdefault(tid, {})[fsig] = fset
