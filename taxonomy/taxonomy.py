from xbrl.base import const, defs


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
        """ Dimension defaults """
        self.defaults = {}
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
            f'Concepts: {len(self.concepts)}',
            f'Hierarchies: {len(self.base_sets)}'])

    def load(self):
        for ep in self.entry_points:
            self.pool.add_reference(ep, '', self)

    def get_bs_roots(self, arc_name, role, arcrole):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}')
        if not bs:
            return None
        return bs.roots

    def get_bs_members(self, arc_name, role, arcrole, start_concept=None, include_head=True):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}')
        if not bs:
            return None
        return bs.get_members(start_concept, include_head)

    def get_enumerations(self):
        enumerations = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enumerations.get(key)
            if not e:
                members = self.get_bs_members('definitionArc',c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE)
                e = defs.Enumeration(key, [], [m.Concept for m in members])
                enumerations[key] = e
            e.Concepts.append(c)
        return enumerations

    def compile(self):
        for lb in self.linkbases.items():
            for xl in lb[1].links:
                xl.compile()
        for it in self.base_sets.items():
            bs = it[1]
            if bs.arc_name != 'definitionArc':
                continue
            if bs.arcrole == const.XDT_DIMENSION_DEFAULT_ARCROLE:
                pass
