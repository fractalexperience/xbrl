from xbrl.taxonomy.table import def_node


class ConceptRelationshipNode(def_node.DefinitionNode):
    """ Implements a concept relationship node """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
