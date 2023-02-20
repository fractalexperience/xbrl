from xbrl.taxonomy.table import aspect_node
from xbrl.taxonomy.table import dr_node
from xbrl.taxonomy.table import cr_node
from xbrl.base import const


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

        self.r_code = None
        self.c_code = None
        self.cells = []

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
        if not self.origin:
            return ''
        display_label = self.origin.get_label(lang=lang)
        if not display_label:
            display_label = self.origin.xlabel if use_id else ''
        if self.concept:
            display_label = self.concept.get_label(lang=lang)
        if isinstance(self.origin, dr_node.DimensionalRelationshipNode):
            display_label_tot = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_TOTAL)
            if display_label_tot:
                display_label = display_label_tot
        elif isinstance(self.origin, cr_node.ConceptRelationshipNode):
            if any([s for s in self.origin.relationship_sources if 'PeriodStart' in s]):
                display_label_start = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_PERIOD_START)
                if display_label_start:
                    display_label = display_label_start
            if any([s for s in self.origin.relationship_sources if 'PeriodEnd' in s]):
                description_end = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_PERIOD_END)
                if description_end:
                    display_label = description_end
        return display_label


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
        cloned = StructureNode(parent=self, origin=self.origin, grayed=True, lvl=self.level, fake=True,
                               abst=self.is_abstract, concept=self.concept)
        for tag, dct in self.constraint_set.items():
            cloned.constraint_set.setdefault(tag, {}).update(dct)
        return cloned
