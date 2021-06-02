from xbrl.taxonomy.table import def_node, str_node
from xbrl.base import const
from xbrl.base import data_wrappers


class RuleNode(def_node.DefinitionNode):
    """ Implements a rule node """
    def __init__(self, e, container_xlink=None):
        abst = e.attrib.get('abstract')
        self.is_abstract = abst is not None and abst.lower() in ['true', '1']
        merg = e.attrib.get('merge')
        self.is_merged = merg is not None and merg.lower() in ['true', '1']
        self.rule_sets = {'default': {}}
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_TABLE}}}ruleSet':
                name = e2.attrib.get('tag')
                for e3 in e2.iterchildren():
                    self.l_restrictions(e3, name)
            else:
                self.l_restrictions(e2, 'default')

    def l_restrictions(self, e, rule_set_name):
        restrictions = self.rule_sets.setdefault(rule_set_name, {})
        restrictions[]

    def compile(self, names=None, lvl=0, s_node=None):
        sn = str_node.StructureNode(s_node, self, self.is_merged)
        super().compile(names, lvl, sn)

