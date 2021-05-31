from xbrl.taxonomy.table import tlb_resource, str_node
from xbrl.base import data_wrappers


class Breakdown(tlb_resource.TableResource):
    """ Implements a XBRL table breakdown"""

    def __init__(self, e, container_xlink=None):
        self.parent_child_order = e.attrib.get('parentChildOrder')
        self.axis = None
        self.order = 0
        super().__init__(e, container_xlink)

    def compile(self, names=None, lvl=0, header=None, s_node=None):
        header = self.parent.headers.setdefault(self.axis, {})
        structure = self.parent.structure.setdefault(self.axis, [])
        names = ['ruleNode', 'aspectNode', 'conceptRelationshipNode', 'dimensionRelationshipNode']
        sn = str_node.StructureNode(None, self)
        structure.append(sn)
        return super().compile(names, 0, sn)
