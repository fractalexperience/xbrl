from xbrl.taxonomy.xdt import primary_item
from xbrl.base import util, const


class DrSet:
    """ Dimensional Relationship Set """
    def __init__(self, start_base_set, container_taxonomy):
        self.bs_start = start_base_set
        self.taxonomy = container_taxonomy
        self.root_primary_items = []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def compile(self):
        for c in self.bs_start.roots:
            pi = primary_item.PrimaryItem(c, self)
            self.root_primary_items.append(pi)
        for pi in self.root_primary_items:
            self.process_primary_item(pi)

    def process_primary_item(self, pi):
        self.taxonomy.idx_pi_drs.setdefault(pi.concept.qname, []).append(pi)
        self.populate_hypercubes(pi)
        cbs_dn = pi.concept.chain_dn.get(self.bs_start.get_key(), None)
        if cbs_dn is None:
            return
        for node in sorted(cbs_dn, key=lambda t: t.Arc.order):
            pi_nested = primary_item.PrimaryItem(node.Concept, self)
            pi.nested_primary_items[pi_nested.concept.qname] = pi_nested
            self.process_primary_item(pi_nested)

    def populate_hypercubes(self, pi):
        if pi.target_role:
            bs_hc = self.taxonomy.base_sets.get(f'{self.bs_start.arc_name}|{pi.target_role}|{{{const.XDT_ALL_ARCROLE}}}')
            if bs_hc is None:
                bs_hc = self.taxonomy.base_sets.get(f'{self.bs_start.arc_name}|{pi.target_role}|{{{const.XDT_NOTALL_ARCROLE}}}')
        else:
            bs_hc = self.bs_start
        print(bs_hc)


    def info(self):
        return self.bs_start.get_key()



