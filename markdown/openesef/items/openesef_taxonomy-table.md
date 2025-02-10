# taxonomy/table Contents
## taxonomy/table/__init__.py
```py
from . import def_node
from . import breakdown
from . import dr_node
from . import rule_node
from . import cell
from . import layout
from . import cr_node
from . import str_node
from . import tlb_resource
from . import aspect_node
from . import table
```

## taxonomy/table/aspect_node.py
```py
from ...taxonomy.table import def_node, str_node
from ...base import const


class AspectNode(def_node.DefinitionNode):
    """ Implements an aspect node """
    def __init__(self, e, container_xlink=None):
        self.aspect = None
        self.filters = {}
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_TABLE}}}dimensionAspect':
                self.aspect = e2.text
                continue
            self.aspect = e2.tag.split('}')[1]

    def get_constraints(self, tag='default'):
        return {self.aspect: None}
```

## taxonomy/table/breakdown.py
```py
from ...taxonomy.table import tlb_resource


class Breakdown(tlb_resource.TableResource):
    """ Implements a XBRL table breakdown"""

    def __init__(self, e, container_xlink=None):
        self.parent_child_order = e.attrib.get('parentChildOrder')
        self.axis = None
        self.is_open = False
        self.is_closed = False
        super().__init__(e, container_xlink)
```

## taxonomy/table/cell.py
```py
from ...taxonomy.table import str_node
from ...base import data_wrappers


class Cell:
    def __init__(self, constraints=None, label=None, colspan=1, rowspan=1, indent=0,
                 is_header=False, is_fact=False, is_fake=False, is_grayed=False,
                 html_class=None, r_code=None, c_code=None, origin=None):
        self.label = label
        self.is_header = is_header
        self.is_fact = is_fact
        self.is_fake = is_fake
        self.is_grayed = is_grayed
        self.colspan = colspan
        self.rowspan = rowspan
        self.indent = indent
        self.c_code = c_code
        self.r_code = r_code
        self.html_classes = None if html_class is None else set(html_class.split(' '))
        # Final version of constraints
        self.constraints = {} if constraints is None else constraints
        if origin and isinstance(origin, str_node.StructureNode):
            origin.cells.append(self)

    def add_constraints(self, constraints, axis):
        for asp, mem in constraints.items():
            self.add_constraint(asp, mem, axis)

    def add_constraint(self, asp, mem, axis):
        if self.constraints is None:
            self.constraints = {}
        self.constraints[asp] = data_wrappers.Constraint(asp, mem, axis)

    def add_class(self, cls):
        if self.html_classes is None:
            self.html_classes = set({})
        self.html_classes.add(cls)

    def get_address(self, open_x=False, open_y=False, open_z=False):
        if open_y:
            return self.c_code  # If the table is open-Y, then we only take the column code as address
        return f'{self.r_code}.{self.c_code}'

    def get_class(self):
        if self.html_classes is None:
            return ''
        return f' class="{" ".join(self.html_classes)}"'

    def get_label(self):
        return '' if self.label is None else self.label

    def get_indent(self):
        if self.indent == 0:
            return ''
        return f' style="text-indent: {self.indent}px;"'

    def get_colspan(self):
        if self.colspan == 1:
            return ''
        return f' colspan="{self.colspan}"'

    def get_rowspan(self):
        if self.rowspan == 1:
            return ''
        return f' rowspan="{self.rowspan}"'
```

## taxonomy/table/cr_node.py
```py
from ...taxonomy.table import def_node
from ...base import const


class ConceptRelationshipNode(def_node.DefinitionNode):
    """ Implements a concept relationship node """
    def __init__(self, e, container_xlink=None):
        self.relationship_sources = []
        self.role = None
        self.arcrole = None
        self.formula_axis = 'descendant-or-self'
        self.generations = None
        self.link_name = None
        self.arc_name = const.ARC_PRESENTATION
        super().__init__(e, container_xlink)
        self.detail_parsers = {
            f'{{{const.NS_TABLE}}}relationshipSource': self.l_rel_src,
            f'{{{const.NS_TABLE}}}relationshipSourceExpression': self.l_rel_src,
            f'{{{const.NS_TABLE}}}linkrole': self.l_linkrole,
            f'{{{const.NS_TABLE}}}linkroleExpression': self.l_linkrole,
            f'{{{const.NS_TABLE}}}arcrole': self.l_arcrole,
            f'{{{const.NS_TABLE}}}arcroleExpression': self.l_arcrole,
            f'{{{const.NS_TABLE}}}formulaAxis': self.l_axis,
            f'{{{const.NS_TABLE}}}formulaAxisExpression': self.l_axis,
            f'{{{const.NS_TABLE}}}generations': self.l_generations,
            f'{{{const.NS_TABLE}}}generationsExpression': self.l_generations,
            f'{{{const.NS_TABLE}}}linkname': self.l_linkname,
            f'{{{const.NS_TABLE}}}linknameExpression': self.l_linkname,
            f'{{{const.NS_TABLE}}}arcname': self.l_arcname,
            f'{{{const.NS_TABLE}}}arcnameExpression': self.l_arcname
        }
        self.dependencies = {
            const.PARENT_CHILD_ARCROLE: const.ARC_PRESENTATION,
            const.SUMMATION_ITEM_ARCROLE: const.ARC_CALCULATION,
            const.GENERAL_SPECIAL_ARCROLE: const.ARC_DEFINITION,
            const.ESSENCE_ALIAS_ARCROLE: const.ARC_DEFINITION,
            const.SIMILAR_TUPLE_ARCROLE: const.ARC_DEFINITION,
            const.REQUIRES_ELEMENT_ARCROLE: const.ARC_DEFINITION,
            const.XDT_DOMAIN_MEMBER_ARCROLE: const.ARC_DEFINITION
        }
        self.load_details(e)

    def l_arcname(self, e):
        self.arc_name = e.text

    def l_linkname(self, e):
        self.link_name = e.text

    def l_generations(self, e):
        self.generations = e.text

    def l_axis(self, e):
        self.formula_axis = e.text

    def l_arcrole(self, e):
        self.arcrole = e.text
        self.arc_name = self.dependencies.get(self.arcrole, const.ARC_PRESENTATION)

    def l_linkrole(self, e):
        self.role = e.text

    def l_rel_src(self, e):
        self.relationship_sources.append(e.text)
```

## taxonomy/table/def_node.py
```py
from ...taxonomy.table import tlb_resource


class DefinitionNode(tlb_resource.TableResource):
    """ Implements a definition node """
    def __init__(self, e, container_xlink=None):
        self.detail_parsers = None
        super().__init__(e, container_xlink)

    def load_details(self, e):
        for e2 in e.iterchildren():
            method = self.detail_parsers.get(e2.tag, None)
            if method is None:
                print(f'Unknown CR element: {e2.tag}')
                return
            method(e2)
```

## taxonomy/table/dr_node.py
```py
from ...taxonomy.table import def_node
from ...base import const


class DimensionalRelationshipNode(def_node.DefinitionNode):
    """ Implements a dimensional relationship node """
    def __init__(self, e, container_xlink=None):
        self.relationship_sources = []
        self.role = None
        self.formula_axis = 'descendant-or-self'
        self.generations = None
        self.dimension = None
        super().__init__(e, container_xlink)
        self.detail_parsers = {
            f'{{{const.NS_TABLE}}}relationshipSource': self.l_rel_src,
            f'{{{const.NS_TABLE}}}relationshipSourceExpression': self.l_rel_src,
            f'{{{const.NS_TABLE}}}dimension': self.l_dimension,
            f'{{{const.NS_TABLE}}}linkrole': self.l_linkrole,
            f'{{{const.NS_TABLE}}}linkroleExpression': self.l_linkrole,
            f'{{{const.NS_TABLE}}}formulaAxis': self.l_axis,
            f'{{{const.NS_TABLE}}}formulaAxisExpression': self.l_axis,
            f'{{{const.NS_TABLE}}}generations': self.l_generations,
            f'{{{const.NS_TABLE}}}generationsExpression': self.l_generations
        }
        self.load_details(e)

    def l_axis(self, e):
        self.formula_axis = e.text

    def l_generations(self, e):
        self.generations = e.text

    def l_linkrole(self, e):
        self.role = e.text

    def l_dimension(self, e):
        self.dimension = e.text

    def l_rel_src(self, e):
        self.relationship_sources.append(e.text)
```

## taxonomy/table/layout.py
```py
class Layout:
    def __init__(self, lbl, rc):
        self.label = lbl
        self.rc_code = rc
        # Each cell here corresponds to a table
        self.cells = []
        # Open dimensions per axis
        self.open_dimensions = {}

    def is_open_x(self):
        return any([ax for ax in self.open_dimensions.values() if ax == 'x'])

    def is_open_y(self):
        return any([ax for ax in self.open_dimensions.values() if ax == 'y'])

    def is_open_z(self):
        return any([ax for ax in self.open_dimensions.values() if ax == 'z'])
```

## taxonomy/table/rule_node.py
```py
from ...taxonomy.table import def_node, str_node
from ...base import const
import lxml.etree


class RuleNode(def_node.DefinitionNode):
    """ Implements a rule node """
    def __init__(self, e, container_xlink=None):
        abst = e.attrib.get('abstract')
        self.is_abstract = abst is not None and abst.lower() in ['true', '1']
        merg = e.attrib.get('merge')
        self.is_merged = merg is not None and merg.lower() in ['true', '1']
        self.tag_selector = e.attrib.get('tagSelector')
        self.rule_sets = {'default': {}}
        self.rule_parsers = {
            f'{{{const.NS_FORMULA}}}concept': self.l_formula_concept,
            f'{{{const.NS_FORMULA}}}period': self.l_formula_period,
            f'{{{const.NS_FORMULA}}}unit': self.l_formula_unit,
            f'{{{const.NS_FORMULA}}}explicitDimension': self.l_explicit_dimension
        }
        super().__init__(e, container_xlink)
        for e2 in e.iterchildren():
            if e2 is lxml.etree._Comment:
                continue
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
            restrictions['concept'] = e2.text.strip()

    def l_formula_unit(self, e, restrictions):
        numerator = []
        denominator = []
        for e2 in e.iterchildren():
            if e2.tag == f'{{{const.NS_FORMULA}}}multiplyBy':
                numerator.append(self.get_measure(e2))
            elif e2.tag == f'{{{const.NS_FORMULA}}}divideBy':
                denominator.append(self.get_measure(e2))
            else:
                print(f'Unknown element {e2.tag} under formula:unit')
        numerator_str = '*'.join(numerator) if numerator else '1'
        denominator_str = '*'.join(denominator) if denominator else ''
        separator = '/' if denominator else ''
        restrictions['measure'] = f'{numerator_str}{separator}{denominator_str}'

    def get_measure(self, e):
        msr = e.attrib.get('measure')
        # Specific case for QName representation of a measure. TODO: Replace with XPath function
        if msr.startswith('QName'):
            msr = msr.split('(')[1].split(')')[0].split(',')[1].replace("'", "").replace('"', '')
        return msr

    def l_formula_period(self, e, restrictions):
        for e2 in e.iterchildren():
            p = ''
            if e2.tag == f'{{{const.NS_FORMULA}}}instant':
                p = e2.attrib.get('value')
            elif e2.tag == f'{{{const.NS_FORMULA}}}duration':
                start = e2.attrib.get('start')
                end = e2.attrib.get('end')
                p = f'{start}/{end}'
            restrictions['period'] = p

    def l_explicit_dimension(self, e, restrictions):
        dimension_qname = e.attrib.get('dimension')
        if dimension_qname is None:
            print('Missing dimension in formula:explicitDimension rule')
        for e2 in e.iterchildren():
            if e2.tag != f'{{{const.NS_FORMULA}}}member':
                print(f'Unknown element in formula:explicitDimension rule {e2.tag}')
                continue
            for e3 in e2.iterchildren():
                if e3.tag == f'{{{const.NS_FORMULA}}}qname':
                    restrictions[dimension_qname] = e3.text.strip()
                elif e3.tag == f'{{{const.NS_FORMULA}}}qnameExpression':
                    restrictions[dimension_qname] = e3.text.strip()  # TODO: Evaluate parameters
                else:
                    print(f'Unknown element in formula:member element {e3.tag}')

    def get_constraints(self, tag='default'):
        constraints = {}
        c_set = self.rule_sets.get(tag, None)
        if c_set is not None:
            for asp, mem in c_set.items():
                constraints[asp] = mem
        return constraints
```

## taxonomy/table/str_node.py
```py
from ...taxonomy.table import aspect_node
from ...taxonomy.table import dr_node
from ...taxonomy.table import cr_node
from ...base import const


class StructureNode:
    def __init__(self, parent, origin, grayed=False, lvl=0, fake=False, abst=False, concept=None):
        """ Parent structure node in the hierarchy """
        self.parent = parent
        """ Resource, which is the origin of this structure node """
        self.origin = origin
        self.span = 0
        self.level = lvl
        self.is_grayed = grayed
        self.is_fake = fake
        self.is_abstract = abst
        self.nested = None
        self.concept = concept

        self.r_code = None
        self.c_code = None
        self.cells = []

        """ Contains the untagged (tag='default') and tagged constraint sets for the node. """
        self.constraint_set = {}
        if self.parent is not None:
            if parent.nested is None:
                parent.nested = []
            self.parent.nested.append(self)

    def increment_span(self):
        self.span += 1
        if self.parent is None:
            return
        self.parent.increment_span()

    def add_constraint(self, aspect, value, tag='default'):
        self.constraint_set.setdefault(tag, {})[aspect] = value

    def get_caption(self, use_id=True, lang='en'):
        if not self.origin:
            return ''
        display_label = self.origin.get_label(lang=lang)
        if not display_label:
            display_label = self.origin.xlabel if use_id else ''
        if self.concept:
            display_label = self.concept.get_label(lang=lang)
        if isinstance(self.origin, dr_node.DimensionalRelationshipNode):
            display_label_tot = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_TOTAL)
            if display_label_tot:
                display_label = display_label_tot
        elif isinstance(self.origin, cr_node.ConceptRelationshipNode):
            if any([s for s in self.origin.relationship_sources if 'PeriodStart' in s]):
                display_label_start = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_PERIOD_START)
                if display_label_start:
                    display_label = display_label_start
            if any([s for s in self.origin.relationship_sources if 'PeriodEnd' in s]):
                description_end = self.concept.get_label(lang=lang, role=const.ROLE_LABEL_PERIOD_END)
                if description_end:
                    display_label = description_end
        return display_label


    def get_aspect_caption(self):
        return self.origin.aspect if isinstance(self.origin, aspect_node.AspectNode) else self.origin.xlabel

    def get_rc_caption(self):
        if self.origin is not None:
            cap = self.origin.get_rc_label()
            return cap if cap else self.get_aspect_caption()
        return ''

    def get_db_caption(self):
        if self.origin is not None:
            cap = self.origin.get_db_label()
            return cap if cap else self.get_aspect_caption()
        return ''

    def get_fake_copy(self):
        cloned = StructureNode(parent=self, origin=self.origin, grayed=True, lvl=self.level, fake=True,
                               abst=self.is_abstract, concept=self.concept)
        for tag, dct in self.constraint_set.items():
            cloned.constraint_set.setdefault(tag, {}).update(dct)
        return cloned
```

## taxonomy/table/table.py
```py
from ...taxonomy.table import tlb_resource, str_node


class Table(tlb_resource.TableResource):
    """ Implements a XBRL table """
    def __init__(self, e, container_xlink=None):
        self.has_rc_labels = False
        self.has_db_labels = False
        self.open_axes = set({})
        self.open_dimensions = {}
        self.parent_child_order = e.attrib.get('parentChildOrder')
        super().__init__(e, container_xlink)
        container_xlink.linkbase.pool.current_taxonomy.tables[self.xlabel] = self

    def get_label(self, lang='en', role='/label'):
        lbl = super().get_label(lang, role)
        return self.xlabel if lbl is None else lbl

    def get_rc_label(self):
        rc = super().get_rc_label()
        return '' if rc is None else rc

    def get_rc_or_id(self):
        rc = super().get_rc_label()
        return rc if rc else self.xlabel

    def get_db_label(self):
        db = super().get_db_label()
        return '' if db is None else db
```

## taxonomy/table/tlb_resource.py
```py
from ...taxonomy import resource


class TableResource(resource.Resource):
    """ Implements a Table Linkbase resource """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)

    def get_constraints(self, tag='default'):
        return None
```
