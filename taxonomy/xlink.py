from xbrl.taxonomy import arc, base_set, locator, resource
from xbrl.taxonomy.formula import parameter, value_assertion, existence_assertion, consistency_assertion
from xbrl.base import ebase, const, util, data_wrappers
from xbrl.taxonomy.table import table, breakdown, rule_node, cr_node, dr_node, aspect_node
import urllib.parse


class XLink(ebase.XmlElementBase):
    """ Represents an extended link """
    def __init__(self, e, container_linkbase):
        self.linkbase = container_linkbase
        parsers = {
            'default': self.l_xlink,
            f'{{{const.NS_GEN}}}arc': self.l_arc,
            f'{{{const.NS_LINK}}}labelArc': self.l_arc,
            f'{{{const.NS_LINK}}}referenceArc': self.l_arc,
            f'{{{const.NS_LINK}}}definitionArc': self.l_arc,
            f'{{{const.NS_LINK}}}presentationArc': self.l_arc,
            f'{{{const.NS_LINK}}}calculationArc': self.l_arc,
            f'{{{const.NS_TABLE}}}tableBreakdownArc': self.l_arc,
            f'{{{const.NS_TABLE}}}breakdownTreeArc': self.l_arc,
            f'{{{const.NS_TABLE}}}aspectNodeFilterArc': self.l_arc,
            f'{{{const.NS_TABLE}}}tableFilterArc': self.l_arc,
            f'{{{const.NS_TABLE}}}tableParameterArc': self.l_arc,
            f'{{{const.NS_TABLE}}}definitionNodeSubtreeArc': self.l_arc,
            f'{{{const.NS_LINK}}}loc': self.l_loc,
            f'{{{const.NS_LINK}}}label': self.l_resource,
            f'{{{const.NS_FORMULA_MESSAGE}}}message': self.l_resource,
            f'{{{const.NS_GEN_LABEL}}}label': self.l_resource,
            f'{{{const.NS_LINK}}}reference': self.l_reference,
            f'{{{const.NS_GEN_REF}}}reference': self.l_reference,
            f'{{{const.NS_TABLE}}}table': self.l_table,
            f'{{{const.NS_TABLE}}}breakdown': self.l_breakdown,
            f'{{{const.NS_TABLE}}}ruleNode': self.l_rule_node,
            f'{{{const.NS_TABLE}}}conceptRelationshipNode': self.l_concept_relationship_node,
            f'{{{const.NS_TABLE}}}dimensionRelationshipNode': self.l_dimensional_relationship_node,
            f'{{{const.NS_TABLE}}}aspectNode': self.l_aspect_node,
            f'{{{const.NS_VARIABLE}}}parameter': self.l_parameter,
            f'{{{const.NS_VALUE_ASSERTION}}}valueAssertion': self.l_va,
            f'{{{const.NS_EXISTANCE_ASSERTION}}}existenceAssertion': self.l_ea,
            f'{{{const.NS_CONSISTENCY_ASSERTION}}}consistencyAssertion': self.l_ca,
        }
        """ Locators indexed by unique identifier """
        self.locators = {}
        """ Locators by href """
        self.locators_by_href = {}
        """ Arcs indexed by from property """
        self.arcs_from = {}
        """ Arcs indexed by to property """
        self.arcs_to = {}
        """ All labelled resources indexed by global identifier """
        self.resources = {}
        super(XLink, self).__init__(e, parsers)
        self.role = e.attrib.get(f'{{{const.NS_XLINK}}}role')

    def l_xlink(self, e):
        self.l_children(e)

    def l_resource(self, e):
        resource.Resource(e, self)

    def l_reference(self, e):
        ref = resource.Resource(e, self)
        ref.origin = e  # Tricky assignment of origin to save memory

    def l_table(self, e):
        table.Table(e, self)

    def l_breakdown(self, e):
        breakdown.Breakdown(e, self)

    def l_rule_node(self, e):
        rule_node.RuleNode(e, self)

    def l_aspect_node(self, e):
        aspect_node.AspectNode(e, self)

    def l_concept_relationship_node(self, e):
        cr_node.ConceptRelationshipNode(e, self)

    def l_dimensional_relationship_node(self, e):
        dr_node.DimensionalRelationshipNode(e, self)

    def l_arc(self, e):
        arc.Arc(e, self)

    def l_loc(self, e):
        loc = locator.Locator(e, self)
        url = loc.url
        self.linkbase.pool.add_reference(url, self.linkbase.base)

    def l_parameter(self, e):
        parameter.Parameter(e, self)

    def l_va(self, e):
        value_assertion.ValueAssertion(e, self)

    def l_ea(self, e):
        existence_assertion.ExistenceAssertion(e, self)

    def l_ca(self, e):
        consistency_assertion.ConsistencyAssertion(e, self)

    def compile(self):
        for arc_list in [a for a in self.arcs_from.values()]:
            for a in arc_list:
                loc = self.locators.get(a.xl_from, None)
                if loc is not None:
                    self.try_connect_concept(a, loc)
                    continue
                self.try_connect_resource(a)

    def try_connect_resource(self, a):
        from_resources = self.resources.get(a.xl_from, None)
        if from_resources is None:
            return

        for res in from_resources:
            nested_list = self.resources.get(a.xl_to, None)
            if nested_list is None:
                continue
            for res2 in nested_list:
                res2.parent = res
                res2.order = a.order
                key = f'{res2.lang}|{res2.role}' if res2.lang or res2.role else res2.xlabel
                if isinstance(res2, breakdown.Breakdown):
                    res2.axis = a.axis
                res.nested.setdefault(res2.name, {}).setdefault(key, []).append(res2)

    def try_connect_global_resource(self, a, loc):
        href = util.reduce_url(loc.href)
        res = self.linkbase.pool.current_taxonomy.resources.get(href, None)
        if res is None:
            self.try_connect_role_type(a, href)
            return
        resource_list = self.resources.get(a.xl_to, None)
        if resource_list is not None:
            for res2 in resource_list:
                res2.parent = res
                key = f'{res2.lang}|{res2.role}' if res2.lang or res2.role else res2.xlabel
                res.nested.setdefault(res2.name, {}).setdefault(key, []).append(res2)

    def try_connect_role_type(self, a, href):
        rt = self.linkbase.pool.current_taxonomy.role_types_by_href.get(href, None)
        if rt is None:
            self.try_connect_arcrole_type(a, href)
            return
        self.add_res_list(a, rt)

    def try_connect_arcrole_type(self, a, href):
        art = self.linkbase.pool.current_taxonomy.arcrole_types_by_href.get(href, None)
        if art is None:
            print('Cannot resolve href: ', href)
            # TODO - handle also XBRL Formula cases
            return
        self.add_res_list(a, art)

    def add_res_list(self, a, obj):
        resource_list = self.resources.get(a.xl_to, None)
        if resource_list is not None:
            for res2 in resource_list:
                res2.parent = obj
                key = f'{res2.lang}|{res2.role}' if res2.lang or res2.role else res2.xlabel
                obj.labels.setdefault(res2.name, {}).setdefault(key, []).append(res2)

    def try_connect_concept(self, a, loc):
        href = urllib.parse.unquote(util.reduce_url(loc.href))
        c = self.linkbase.pool.current_taxonomy.concepts.get(href, None)
        if c is None:
            self.try_connect_global_resource(a, loc)
            return
        resource_list = self.resources.get(a.xl_to, None)
        if resource_list is not None:
            for res in resource_list:
                c_resources = c.resources.get(res.name, None)
                if c_resources is None:
                    c_resources = {}
                    c.resources[res.name] = c_resources
                key = f'{res.lang}|{res.role}'
                c_resources.setdefault(key, []).append(res)  # Multiple resources of the same type may be related
            return
        # if no resources are connected, try to find inter-concept relations
        loc2 = self.locators.get(a.xl_to, None)
        if loc2 is None:
            return
        href2 = urllib.parse.unquote(util.reduce_url(loc2.href))
        c2 = self.linkbase.pool.current_taxonomy.concepts.get(href2, None)
        if c2 is None:
            self.try_connect_resource_concept(c, href2)
            return
        key = f'{a.arcrole}|{a.xl_from}'
        is_root = key not in self.arcs_to
        bs_key = f'{a.name}|{a.arcrole}|{self.role}'
        bs = self.linkbase.pool.current_taxonomy.base_sets.get(bs_key, None)
        if bs is None:
            bs = base_set.BaseSet(a.name, a.arcrole, self.role)
            self.linkbase.pool.current_taxonomy.base_sets[bs_key] = bs
        if is_root and c not in bs.roots:
            bs.roots.append(c)
        # Populate concept child and parent sets
        c.chain_dn.setdefault(bs_key, []).append(data_wrappers.BaseSetNode(c2, 0, a))
        c2.chain_up.setdefault(bs_key, []).append(data_wrappers.BaseSetNode(c, 0, a))

    def try_connect_resource_concept(self, c, href):
        res = self.linkbase.pool.current_taxonomy.resources.get(href, None)
        if res is None:
            self.try_connect_roletype(c, href)
            return
        key = f'{res.lang}|{res.role}' if res.lang is not None and res.role is not None else res.xlabel
        c.resources.setdefault(res.name, {}).setdefault(key, []).append(res)

    def try_connect_roletype(self, c, href):
        rt = self.linkbase.pool.current_taxonomy.role_types.get(href, None)
        if rt is None:
            return
        c.resources.setdefault(rt.name, {}).setdefault(rt.role_uri, []).append(rt)
