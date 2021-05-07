import xbrl.taxonomy.xdt.hypercube
from xbrl.taxonomy.xdt import primary_item, hypercube, dimension
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
        key = f'{self.bs_start.arc_name}|{const.XDT_DOMAIN_MEMBER_ARCROLE}|{self.bs_start.role}'
        cbs_dn = pi.concept.chain_dn.get(key, None)
        if cbs_dn is None:
            return
        for node in sorted(cbs_dn, key=lambda t: t.Arc.order):
            pi_nested = primary_item.PrimaryItem(node.Concept, self, node.Arc.target_role)
            pi.nested_primary_items[pi_nested.concept.qname] = pi_nested
            self.process_primary_item(pi_nested)

    def populate_hypercubes(self, pi):
        if pi.target_role:
            bs_hc = self.taxonomy.base_sets.get(f'{self.bs_start.arc_name}|{pi.target_role}|{{{const.XDT_ALL_ARCROLE}}}')
            if bs_hc is None:
                bs_hc = self.taxonomy.base_sets.get(f'{self.bs_start.arc_name}|{pi.target_role}|{{{const.XDT_NOTALL_ARCROLE}}}')
        else:
            bs_hc = self.bs_start
        hypercubes = bs_hc.get_members(include_head=False)
        for hc in [xbrl.taxonomy.xdt.hypercube.Hypercube(t.Concept, self, t.Arc.target_role) for t in hypercubes]:
            pi.hypercubes[hc.concept.qname] = hc
            role = hc.target_role if hc.target_role else bs_hc.role
            key = f'{bs_hc.arc_name}|{const.XDT_HYPERCUBE_DIMENSION_ARCROLE}|{role}'
            self.populate_dimensions(hc, key)

    def populate_dimensions(self, hc, key):
        bs_dim = self.taxonomy.base_sets.get(key)
        if bs_dim is None:
            return
        dimensions = bs_dim.get_members(include_head=False)
        for dim in [xbrl.taxonomy.xdt.dimension.Dimension(t.Concept, self, t.Arc.target_role) for t in dimensions]:
            hc.dimensions[dim.concept.qname] = dim
            role = dim.target_role if dim.target_role else bs_dim.role
            key = f'{bs_dim.arc_name}|{const.XDT_DIMENSION_DOMAIN_ARCROLE}|{role}'
            self.populate_members(dim, key)

    def populate_members(self, dim, key):
        bs_mem = self.taxonomy.base_sets.get(key)
        if bs_mem is None:
            return
        members = bs_mem.get_members(include_head=False)
        for mem in members:
            dim.members[mem.Concept.qname] = mem.Concept

    def info(self):
        return self.bs_start.get_key()



