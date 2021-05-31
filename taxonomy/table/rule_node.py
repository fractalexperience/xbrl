from xbrl.taxonomy.table import def_node, str_node
from xbrl.base import data_wrappers


class RuleNode(def_node.DefinitionNode):
    """ Implements a rule node """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)

    def compile(self, names=None, lvl=0, s_node=None):
        # header.setdefault(lvl, []).append(data_wrappers.StructureNode(self, 'sn_rn'))
        sn = str_node.StructureNode(s_node, self)
        super().compile(names, lvl, sn)

