from xbrl.base import data_wrappers


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
            self.get_branch_members(r, members, start_concept, include_head, False, 0, None)
        return members

    def get_branch_members(
            self, concept, members, start_concept, include_head, flag_include, level, related_arc):
        if concept is None:
            return
        trigger_include = (not start_concept and level == 0) or (start_concept and start_concept == concept.qname)
        new_flag_include = flag_include or trigger_include
        if (trigger_include and include_head) or flag_include:
            members.append(data_wrappers.BaseSetNode(concept, level, related_arc))
        cbs_dn = concept.chain_dn.get(self.get_key(), None)
        if cbs_dn is None:
            return
        for node in sorted(cbs_dn, key=lambda t: 0 if t.Arc.order is None else float(t.Arc.order)):
            self.get_branch_members(
                node.Concept, members, start_concept, include_head, new_flag_include, level+1, node.Arc)

    def info(self):
        rts = ','.join([r.qname for r in self.roots])
        return '\n'.join([
            f'Arc name: {self.arc_name}',
            f'Arc role: {self.arcrole}',
            f'Role: {self.role}',
            f'Roots: {rts}'])
