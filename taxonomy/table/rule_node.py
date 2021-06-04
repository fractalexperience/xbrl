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
        self.rule_parsers = {
            f'{{{const.NS_FORMULA}}}concept': self.l_formula_concept,
            f'{{{const.NS_FORMULA}}}explicitDimension': self.l_explicit_dimension
        }
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_TABLE}}}ruleSet':
                name = e2.attrib.get('tag')
                for e3 in e2.iterchildren():
                    self.l_rule_set(e3, name)
            else:
                self.l_rule_set(e2, 'default')

    def l_rule_set(self, e, rule_set_name):
        restrictions = self.rule_sets.setdefault(rule_set_name, {})
        method = self.rule_parsers.get(e.tag, None)
        if method is None:
            print(f'Unknown rule: {e.tag}')
            return
        method(e, restrictions)

    def l_formula_concept(self, e, restrictions):
        for e2 in e.iterchildren():
            if e2.tag != f'{{{const.NS_FORMULA}}}qname':
                print(f'Unknown element in formula:concept rule {e2.tag}')
                continue
            restrictions['concept'] = e2.text

    def l_explicit_dimension(self, e, restrictions):
        dimension_qname = e.attrib.get('dimension')
        if dimension_qname is None:
            print('Missing dimension in formula:explicitDimension rule')
        for e2 in e.iterchildren():
            if e2.tag != f'{{{const.NS_FORMULA}}}member':
                print(f'Unknown element in formula:explicitDimension rule {e2.tag}')
                continue
            for e3 in e2.iterchildren():
                if e3.tag != f'{{{const.NS_FORMULA}}}qname':
                    print(f'Unknown element in formula:member element {e3.tag}')
                    continue
                restrictions[dimension_qname] = e3.text

    def compile(self, names=None, lvl=0, s_node=None):
        sn = str_node.StructureNode(s_node, self, self.is_merged)
        super().compile(names, lvl, sn)

