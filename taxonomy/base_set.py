from xbrl.base import defs


class BaseSet:
    def __init__(self, arc_name, arcrole, role):
        self.arc_name = arc_name
        self.arcrole = arcrole
        self.role = role
        self.roots = []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def get_key(self):
        return f'{self.arc_name}|{self.arcrole}|{self.role}'

    def get_members(self, start_concept=None, include_head=True):
        members = []
        for r in self.roots:
            self.get_branch_members(r, members, start_concept, include_head, False, 0)
        return members

    def get_branch_members(self, concept, members, start_concept, include_head, flag_include, level):
        if concept is None:
            return
        trigger_include = (not start_concept and level==0) or (start_concept and start_concept == concept.qname)
        new_flag_include = flag_include or trigger_include
        if (trigger_include and include_head) or flag_include:
            members.append(defs.ConceptWrapper(concept, level))
        cbs_dn = concept.chain_dn.get(self.get_key(), None)
        if cbs_dn is None:
            return
        for tup in sorted(cbs_dn, key=lambda t: t[1].order):
            cdn = tup[0]
            self.get_branch_members(cdn, members, start_concept, include_head, new_flag_include, level+1)

    def info(self):
        rts = ','.join([r.qname for r in self.roots])
        return '\n'.join([
            f'Arc name: {self.arc_name}',
            f'Arc role: {self.arcrole}',
            f'Role: {self.role}',
            f'Roots: {rts}'])
