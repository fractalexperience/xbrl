from xbrl.base import const, data_wrappers
from xbrl.taxonomy.xdt import dr_set


class Taxonomy:
    """ entry_points is a list of entry point locations
        cache_folder is the place where to store cached Web resources """
    def __init__(self, entry_points, container_pool):
        self.entry_points = entry_points
        self.pool = container_pool
        """ All schemas indexed by resolved location """
        self.schemas = {}
        """ All linkbases indexed by resolved location """
        self.linkbases = {}
        """ All concepts  indexed by full id - target namespace + id """
        self.concepts = {}
        """ All concepts indexed by QName"""
        self.concepts_by_qname = {}
        """ General elements, which are not concepts """
        self.elements = {}
        """ All base set objects indexed by base set key """
        self.base_sets = {}
        """ Dimension defaults - Key is dimension QName, value is default member concept """
        self.defaults = {}
        """ Default Members - Key is the default member QName, value is the corresponding dimension concept. """
        self.default_members = {}

        """ Dimensional Relationship Sets """
        self.dr_sets = {}
        """ Excluding Dimensional Relationship Sets """
        self.dr_sets_excluding = {}

        """ Key is primary item QName, value is the list of dimensional relationship sets, where it participates. """
        self.idx_pi_drs = {}
        """ Key is the Qname of the dimensions. Value is the set of DR keys, where this dimension participates """
        self.idx_dim_drs = {}
        """ Key is the QName of the hypercube. Value is the set of DR Keys, where this hypercube participates. """
        self.idx_hc_drs = {}
        """ Key is the QName of the member. Value is the set of DR keys, where this member participates. """
        self.idx_mem_drs = {}

        """ All table resources in taxonomy """
        self.tables = {}
        """ All role types in all schemas """
        self.role_types = {}
        """ All arcrole types in all schemas """
        self.arcrole_types = {}
        """ Global resources - these, which have an id attribute """
        self.resources = {}
        """ All locators """
        self.locators = {}

        self.load()
        self.compile()

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        return '\n'.join([
            f'Schemas: {len(self.schemas)}',
            f'Linkbases: {len(self.linkbases)}',
            f'Role Types: {len(self.role_types)}',
            f'Arcrole Types: {len(self.arcrole_types)}',
            f'Concepts: {len(self.concepts)}',
            f'Labels: {sum([0 if not "label" in c.resources else len(c.resources["label"]) for c in self.concepts.values()])}',
            f'References: {sum([0 if not "reference" in c.resources else len(c.resources["reference"]) for c in self.concepts.values()])}',
            f'Hierarchies: {len(self.base_sets)}',
            f'Dimensional Relationship Sets: {len(self.base_sets)}',
            f'Dimensions: {len([c for c in self.concepts.values() if c.is_dimension])}',
            f'Hypercubes: {len([c for c in self.concepts.values() if c.is_hypercube])}',
            f'Enumerations: {len([c for c in self.concepts.values() if c.is_enumeration])}',
            f'Enumerations Sets: {len([c for c in self.concepts.values() if c.is_enumeration_set])}',
            f'Table Groups: {len([c for c in self.concepts.values() if "table" in c.resources])}',
            f'Tables: {len(self.tables)}'
        ])

    def load(self):
        for ep in self.entry_points:
            self.pool.add_reference(ep, '', self)

    def get_bs_roots(self, arc_name, role, arcrole):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}')
        if not bs:
            return None
        return bs.roots

    def get_bs_members(self, arc_name, role, arcrole, start_concept=None, include_head=True):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}', None)
        if not bs:
            return None
        return bs.get_members(start_concept, include_head)

    def get_enumerations(self):
        enumerations = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enumerations.get(key)
            if not e:
                members = self.get_bs_members('definitionArc',c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE, c.domain, c.head_usable)
                e = data_wrappers.Enumeration(key, [], [m.Concept for m in members])
                enumerations[key] = e
            e.Concepts.append(c)
        return enumerations

    def get_enumeration_sets(self):
        enum_sets = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationSetItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enum_sets.get(key)
            if not e:
                members = self.get_bs_members('definitionArc', c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE, c.domain, c.head_usable)
                if members is None:
                    continue
                e = data_wrappers.Enumeration(key, [], [m.Concept for m in members])
                enum_sets[key] = e
            e.Concepts.append(c)
        return enum_sets

    def compile(self):
        self.compile_linkbases()
        self.compile_dr_sets()

    def compile_linkbases(self):
        for lb in self.linkbases.values():
            for xl in lb.links:
                xl.compile()

    def compile_dr_sets(self):
        for bs in self.base_sets.values():
            if bs.arc_name != 'definitionArc':
                continue
            if bs.arcrole == const.XDT_DIMENSION_DEFAULT_ARCROLE:
                self.add_default_member(bs)
                continue
            if bs.arcrole == const.XDT_ALL_ARCROLE:
                self.add_drs(bs, self.dr_sets)
                continue
            if bs.arcrole == const.XDT_NOTALL_ARCROLE:
                self.add_drs(bs, self.dr_sets_excluding)
                continue

    def add_drs(self, bs, drs_collection):
        drs = dr_set.DrSet(bs, self)
        drs.compile()
        drs_collection[bs.get_key()] = drs

    def add_default_member(self, bs):
        for d in bs.roots:
            members = bs.get_members(start_concept=d, include_head=False)
            if not members:
                continue
            for m in members:
                self.defaults[d.qname] = m
                self.default_members[m.qname] = d
