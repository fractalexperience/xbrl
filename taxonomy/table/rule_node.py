from xbrl.taxonomy.table import def_node, str_node
from xbrl.base import data_wrappers


class RuleNode(def_node.DefinitionNode):
    """ Implements a rule node """
    def __init__(self, e, container_xlink=None):
        abst = e.attrib.get('abstract')
        self.is_abstract = abst is not None and abst.lower() in ['true', '1']
        merg = e.attrib.get('merge')
        self.is_merged = merg is not None and merg.lower() in ['true', '1']
        super().__init__(e, container_xlink)

    def compile(self, names=None, lvl=0, s_node=None):
        sn = str_node.StructureNode(s_node, self, self.is_merged)
        super().compile(names, lvl, sn)

