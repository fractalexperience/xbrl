from xbrl.taxonomy.table import def_node, str_node
from xbrl.base import const


class AspectNode(def_node.DefinitionNode):
    """ Implements an aspect node """
    def __init__(self, e, container_xlink=None):
        self.aspect = None
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_TABLE}}}dimensionAspect':
                self.aspect = e2.text
                continue
            self.aspect = e2.tag.split('}')[1]

    def get_constraints(self, tag='default'):
        return {self.aspect: None}
