from xbrl.taxonomy.table import def_node
from xbrl.base import const


class DimensionalRelationshipNode(def_node.DefinitionNode):
    """ Implements a dimensional relationship node """
    def __init__(self, e, container_xlink=None):
        self.relationship_sources = []
        self.role = None
        self.formula_axis = 'descendant-or-self'
        self.generations = None
        self.dimension = None
        super().__init__(e, container_xlink)
        self.detail_parsers = {
            f'{{{const.NS_TABLE}}}relationshipSource': self.l_rel_src,
            f'{{{const.NS_TABLE}}}relationshipSourceExpression': self.l_rel_src,
            f'{{{const.NS_TABLE}}}dimension': self.l_dimension,
            f'{{{const.NS_TABLE}}}linkrole': self.l_linkrole,
            f'{{{const.NS_TABLE}}}linkroleExpression': self.l_linkrole,
            f'{{{const.NS_TABLE}}}formulaAxis': self.l_axis,
            f'{{{const.NS_TABLE}}}formulaAxisExpression': self.l_axis,
            f'{{{const.NS_TABLE}}}generations': self.l_generations,
            f'{{{const.NS_TABLE}}}generationsExpression': self.l_generations
        }
        self.load_details(e)

    def l_axis(self, e):
        self.formula_axis = e.text

    def l_generations(self, e):
        self.generations = e.text

    def l_linkrole(self, e):
        self.role = e.text

    def l_dimension(self, e):
        self.dimension = e.text

    def l_rel_src(self, e):
        self.relationship_sources.append(e.text)
