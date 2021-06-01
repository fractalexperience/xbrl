from xbrl.taxonomy.table import def_node, str_node
from xbrl.base import data_wrappers


class AspectNode(def_node.DefinitionNode):
    """ Implements an aspect node """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)

    def compile(self, names=None, lvl=0, s_node=None):
        sn = str_node.StructureNode(s_node, self)
        super().compile(names, lvl, sn)
