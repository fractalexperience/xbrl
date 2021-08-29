from xbrl.taxonomy.table import def_node
from xbrl.base import const


class ConceptRelationshipNode(def_node.DefinitionNode):
    """ Implements a concept relationship node """
    def __init__(self, e, container_xlink=None):
        self.relationship_sources = []
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_TABLE}}}relationshipSource':
                self.relationship_sources.append(e2.text)
