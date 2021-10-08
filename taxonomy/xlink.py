from xbrl.taxonomy import arc, base_set, locator, resource, concept, roletype, arcroletype
from xbrl.taxonomy.formula import parameter, value_assertion, existence_assertion, consistency_assertion, assertion, \
    filter, assertion_set
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
            f'{{{const.NS_VALIDATION}}}assertionSet': self.l_ass,
            f'{{{const.NS_VALUE_ASSERTION}}}valueAssertion': self.l_va,
            f'{{{const.NS_EXISTANCE_ASSERTION}}}existenceAssertion': self.l_ea,
            f'{{{const.NS_CONSISTENCY_ASSERTION}}}consistencyAssertion': self.l_ca,
            f'{{{const.NS_DIMENSION_FILTER}}}explicitDimension': self.l_filter,
            f'{{{const.NS_DIMENSION_FILTER}}}typedDimension': self.l_filter,
        }
        self.conn_methods = {
            'Concept=>Resource': self.conn_cr,
            'Resource=>Resource': self.conn_rr,
            'Resource=>String': self.conn_rstr,
            'Concept=>Concept': self.conn_cc,
            'RoleType=>Resource': self.conn_rtr,
            'ArcroleType=>Resource': self.conn_artr,
            'Concept=>RoleType': self.conn_crt,
            'Concept=>ArcroleType': self.conn_cart
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

    def l_ass(self, e):
        assertion_set.AssertionSet(e, self)

    def l_va(self, e):
        value_assertion.ValueAssertion(e, self)

    def l_ea(self, e):
        existence_assertion.ExistenceAssertion(e, self)

    def l_ca(self, e):
        consistency_assertion.ConsistencyAssertion(e, self)

    def l_filter(self, e):
        filter.Filter(e, self)

    def compile(self):
        for arc_list in [a for a in self.arcs_from.values()]:
            for a in arc_list:
                from_objects = self.identify_objects(a.xl_from)
                if from_objects is None:
                    print('Cannot resolve arc.from: ', a.xl_from, 'in', self.linkbase.location)
                    return
                to_objects = self.identify_objects(a.xl_to)
                if to_objects is None:
                    print('Cannot resolve arc.to: ', a.xl_to, 'in', self.linkbase.location)
                    return
                for obj_from in from_objects:
                    for obj_to in to_objects:
                        self.try_connect_objects(a, obj_from, obj_to)

    def try_connect_objects(self, a, obj_from, obj_to):
        key = f'{self.get_obj_type(obj_from)}=>{self.get_obj_type(obj_to)}'
        method = self.conn_methods.get(key, None)
        if method is None:
            print('Unknown object types combination: ', key)
            return
        method(a, obj_from, obj_to)

    def conn_cr(self, a, c, res):
        r_list = c.resources.get(res.name, None)
        if r_list is None:
            r_list = {}
            c.resources[res.name] = r_list
        r_list.setdefault(self.get_resource_key(res), []).append(res)  # Multiple resources of the same type may be related

    def conn_cc(self, a, c_from, c_to):
        key = f'{a.arcrole}|{a.xl_from}'
        is_root = key not in self.arcs_to
        bs_key = f'{a.name}|{a.arcrole}|{self.role}'
        bs = self.linkbase.pool.current_taxonomy.base_sets.get(bs_key, None)
        if bs is None:
            bs = base_set.BaseSet(a.name, a.arcrole, self.role)
            self.linkbase.pool.current_taxonomy.base_sets[bs_key] = bs
        if is_root and c_from not in bs.roots:
            bs.roots.append(c_from)
        # Populate concept child and parent sets
        c_from.chain_dn.setdefault(bs_key, []).append(data_wrappers.BaseSetNode(c_to, 0, a))
        c_to.chain_up.setdefault(bs_key, []).append(data_wrappers.BaseSetNode(c_from, 0, a))

    def conn_rr(self, a, r_from, r_to):
        r_to.parent = r_from
        r_to.order = a.order
        if isinstance(r_to, breakdown.Breakdown):
            r_to.axis = a.axis
        r_from.nested.setdefault(r_to.name, {}).setdefault(self.get_resource_key(r_to), []).append(r_to)

    def conn_rstr(self, a, ass, sev):
        if isinstance(ass, assertion.Assertion):
            ass.severity = sev

    def conn_rtr(self, a, rt, res):
        res.parent = rt
        rt.labels.setdefault(res.name, {}).setdefault(self.get_resource_key(res), []).append(res)

    def conn_artr(self, a, art, res):
        res.parent = art
        art.labels.setdefault(res.name, {}).setdefault(self.get_resource_key(res), []).append(res)

    def conn_crt(self, a, c, rt):
        c.resources.setdefault(rt.name, {}).setdefault(rt.role_uri, []).append(rt)

    def conn_cart(self, a, c, art):
        c.resources.setdefault(art.name, {}).setdefault(art.arcrole_uri, []).append(art)

    """ Identifies a list of objects referred by a XLabel identifier
        xbrl is the from, or to attribute of the arc """
    def identify_objects(self, xlbl):
        # Seek by XLabel directly in current link
        res = self.resources.get(xlbl, None)
        if res is not None:
            return res
        # Seek role type by roleUri in taxonomy
        rt = self.linkbase.pool.current_taxonomy.role_types.get(xlbl, None)
        if rt is not None:
            return [rt]
        # Seek arcrole type by roleUri in taxonomy
        art = self.linkbase.pool.current_taxonomy.arcrole_types.get(xlbl, None)
        if art is not None:
            return [art]
        loc = self.locators.get(xlbl, None)
        if loc is None:
            return None
        if loc.url == const.URL_ASSERTION_SEVERITIES:
            return [loc.fragment_identifier]  # Directly assign severity to assertion
        href = urllib.parse.unquote(util.reduce_url(loc.href))
        # Seek for a concept
        c = self.linkbase.pool.current_taxonomy.concepts.get(href, None)
        if c is not None:
            return [c]
        # Seek global resource by XPointer
        res = self.linkbase.pool.current_taxonomy.resources.get(href, None)
        if res is not None:
            return [res]
        # Seek role type by XPointer
        rt = self.linkbase.pool.current_taxonomy.role_types_by_href.get(href, None)
        if rt is not None:
            return [rt]
        # Seek arcrole type by XPointer
        art = self.linkbase.pool.current_taxonomy.arcrole_types_by_href.get(href, None)
        if art is not None:
            return [art]

    def get_resource_key(self, res):
        return f'{res.lang}|{res.role}' if res.lang or res.role else res.xlabel

    def get_obj_type(self, obj):
        if isinstance(obj, str):
            return 'String'
        if isinstance(obj, concept.Concept):
            return 'Concept'
        if isinstance(obj, resource.Resource):
            return 'Resource'
        if isinstance(obj, roletype.RoleType):
            return 'RoleType'
        if isinstance(obj, arcroletype.ArcroleType):
            return 'ArcroleType'
