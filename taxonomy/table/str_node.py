from xbrl.taxonomy.table import aspect_node


class StructureNode:
    def __init__(self, parent, origin, grayed=False, lvl=0):
        """ Parent structure node in the hierarchy """
        self.parent = parent
        """ Resource, which is the origin of this structure node """
        self.origin = origin
        self.span = 0
        self.level = lvl
        self.grayed = grayed
        self.nested = None
        """ Contains the untagged (tag='default') and tagged constraint sets for the node. """
        self.constraint_set = {}
        if self.parent is not None:
            if parent.nested is None:
                parent.nested = []
            self.parent.nested.append(self)

    def increment_span(self):
        self.span += 1
        if self.parent is None:
            return
        self.parent.increment_span()

    def add_constraint(self, aspect, value, tag='default'):
        self.constraint_set.setdefault(tag, {})[aspect] = value

    def get_caption(self):
        if self.origin is not None:
            cap = self.origin.get_label()
            return cap if cap else f'{self.origin.xlabel}'
        return ''

    def get_aspect_caption(self):
        return self.origin.aspect if isinstance(self.origin, aspect_node.AspectNode) else self.origin.xlabel

    def get_rc_caption(self):
        if self.origin is not None:
            cap = self.origin.get_rc_label()
            return cap if cap else self.get_aspect_caption()
        return ''

    def get_db_caption(self):
        if self.origin is not None:
            cap = self.origin.get_db_label()
            return cap if cap else self.get_aspect_caption()
        return ''
