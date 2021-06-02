from xbrl.taxonomy.table import def_node, str_node


class AspectNode(def_node.DefinitionNode):
    """ Implements an aspect node """
    def __init__(self, e, container_xlink=None):
        self.aspects = {}
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            self.aspects[e2.tag.split('}')[1]] = e2.text

    def compile(self, names=None, lvl=0, s_node=None):
        sn = str_node.StructureNode(s_node, self)
        super().compile(names, lvl, sn)

