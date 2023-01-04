from xbrl.taxonomy.table import aspect_node


class StructureNode:
    def __init__(self, parent, origin, grayed=False, lvl=0, fake=False, abst=False, concept=None):
        """ Parent structure node in the hierarchy """
        self.parent = parent
        """ Resource, which is the origin of this structure node """
        self.origin = origin
        self.span = 0
        self.level = lvl
        self.is_grayed = grayed
        self.is_fake = fake
        self.is_abstract = abst
        self.nested = None
        self.concept = concept
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

    def get_caption(self, use_id=True, lang='en'):
        if self.concept is not None:
            cap = self.concept.get_label(lang=lang)
            return cap if cap else self.concept.qname
        if self.origin is not None:
            cap = self.origin.get_label(lang=lang)
            return cap if cap else f'{self.origin.xlabel}' if use_id else ''
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

    def get_fake_copy(self):
        cloned = StructureNode(parent=self, origin=self.origin, grayed=True, lvl=self.level+1, fake=True,
                             abst=self.is_abstract, concept=self.concept)
        for tag, dct in self.constraint_set.items():
            cloned.constraint_set.setdefault(tag, {}).update(dct)
        return cloned
