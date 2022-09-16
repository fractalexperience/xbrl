from xbrl.base import data_wrappers, const


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

    """
    start_concept - Concept to be considered root of the branch. If None, then processing starts from hierarchy root.
    include_head - Flag whether to include root of the branch into the result set.
    s_groups - List of substitution groups to be included in processing. If it is None, then all are processed.
    """
    def get_members(self, start_concept=None, include_head=True, s_groups=None):
        members = []
        for r in self.roots:
            self.get_branch_members(r, members, start_concept, include_head, False, 0, None, [r], s_groups)
        return members

    def get_branch_members(
            self, concept, members, start_concept, inc_head,
            flag_include, level, related_arc, stack, s_groups=None):
        if concept is None:
            return
        trigger_include = (not start_concept and level == 0) or (start_concept and start_concept == concept.qname)
        new_flag_include = flag_include or trigger_include

        cbs_dn = concept.chain_dn.get(self.get_key(), None)
        is_leaf = True if cbs_dn is None else False
        if (trigger_include and inc_head) or flag_include:
            members.append(data_wrappers.BaseSetNode(concept, level, related_arc, is_leaf))

        if cbs_dn is None:
            return
        # Recursion
        lst = sorted([n for n in cbs_dn if n.Concept not in stack],
                   key=lambda t: 0 if t.Arc.order is None else float(t.Arc.order))
        used = set()
        balance = None
        for node in lst:
            if node.Concept.qname in used or (s_groups is not None and node.Concept.substitution_group not in s_groups):
                continue
            if balance is None:
                balance = node.Concept.balance  # Set only first time
            used.add(node.Concept.qname)
            stack.append(node.Concept)
            self.get_branch_members(
                node.Concept, members, start_concept, inc_head, new_flag_include, level + 1, node.Arc, stack, s_groups)
            stack.remove(node.Concept)

    def get_langs(self):
        langs = set()
        lbls = [n.Concept.resources.get('label', {}) for n in self.get_members()]
        for dct in lbls:
            for v in dct.values():
                for lbl in v:
                    langs.add(lbl.lang)
        return langs

    def info(self):
        rts = ','.join([r.qname for r in self.roots])
        return '\n'.join([
            f'Arc name: {self.arc_name}',
            f'Arc role: {self.arcrole}',
            f'Role: {self.role}',
            f'Roots: {rts}'])
