from xbrl.taxonomy import schema
from xbrl.base import const


class Taxonomy:
    """ entry_points is a list of entry point locations
        cache_folder is the place where to store cached Web resources """
    def __init__(self, entry_points, container_pool):
        self.entry_points = entry_points
        self.pool = container_pool
        self.schemas = {}
        self.linkbases = {}
        self.concepts = {}
        self.concepts_by_qname = {}
        self.base_sets = {}
        self.defaults = {}
        self.load()
        self.compile()

    def load(self):
        for ep in self.entry_points:
            self.pool.add_reference(ep, '', self)

    def bs_roots(self, arc_name, role, arcrole):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}')
        if not bs:
            return None
        return bs.roots

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

    def info(self):
        return '\n'.join([
             f'Schemas: {len(self.schemas)}',
             f'Linkbases: {len(self.linkbases)}',
             f'Concepts: {len(self.concepts)}',
             f'Hierarchies: {len(self.base_sets)}'])
