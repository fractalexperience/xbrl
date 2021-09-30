from xbrl.taxonomy.table import def_node
from xbrl.base import const


class ConceptRelationshipNode(def_node.DefinitionNode):
    """ Implements a concept relationship node """
    def __init__(self, e, container_xlink=None):
        self.relationship_sources = []
        self.role = None
        self.arcrole = None
        self.formula_axis = 'descendant-or-self'
        self.generations = None
        self.link_name = None
        self.arc_name = const.ARC_PRESENTATION
        super().__init__(e, container_xlink)
        self.detail_parsers = {
            f'{{{const.NS_TABLE}}}relationshipSource': self.l_rel_src,
            f'{{{const.NS_TABLE}}}relationshipSourceExpression': self.l_rel_src,
            f'{{{const.NS_TABLE}}}linkrole': self.l_linkrole,
            f'{{{const.NS_TABLE}}}linkroleExpression': self.l_linkrole,
            f'{{{const.NS_TABLE}}}arcrole': self.l_arcrole,
            f'{{{const.NS_TABLE}}}arcroleExpression': self.l_arcrole,
            f'{{{const.NS_TABLE}}}formulaAxis': self.l_axis,
            f'{{{const.NS_TABLE}}}formulaAxisExpression': self.l_axis,
            f'{{{const.NS_TABLE}}}generations': self.l_generations,
            f'{{{const.NS_TABLE}}}generationsExpression': self.l_generations,
            f'{{{const.NS_TABLE}}}linkname': self.l_linkname,
            f'{{{const.NS_TABLE}}}linknameExpression': self.l_linkname,
            f'{{{const.NS_TABLE}}}arcname': self.l_arcname,
            f'{{{const.NS_TABLE}}}arcnameExpression': self.l_arcname
        }
        self.dependencies = {
            const.PARENT_CHILD_ARCROLE: const.ARC_PRESENTATION,
            const.SUMMATION_ITEM_ARCROLE: const.ARC_CALCULATION,
            const.GENERAL_SPECIAL_ARCROLE: const.ARC_DEFINITION,
            const.ESSENCE_ALIAS_ARCROLE: const.ARC_DEFINITION,
            const.SIMILAR_TUPLE_ARCROLE: const.ARC_DEFINITION,
            const.REQUIRES_ELEMENT_ARCROLE: const.ARC_DEFINITION,
            const.XDT_DOMAIN_MEMBER_ARCROLE: const.ARC_DEFINITION
        }
        self.load_details(e)

    def l_arcname(self, e):
        self.arc_name = e.text

    def l_linkname(self, e):
        self.link_name = e.text

    def l_generations(self, e):
        self.generations = e.text

    def l_axis(self, e):
        self.formula_axis = e.text

    def l_arcrole(self, e):
        self.arcrole = e.text
        self.arc_name = self.dependencies.get(self.arcrole, const.ARC_PRESENTATION)

    def l_linkrole(self, e):
        self.role = e.text

    def l_rel_src(self, e):
        self.relationship_sources.append(e.text)
