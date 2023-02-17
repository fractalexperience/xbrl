import xbrl.taxonomy.table.str_node
from xbrl.base import data_wrappers


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
        if origin and isinstance(origin, xbrl.taxonomy.table.str_node.StructureNode):
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

    def get_address(self):
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
