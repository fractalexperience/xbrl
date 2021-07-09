from xbrl.base import data_wrappers


class Cell:
    def __init__(self, constraints=None, label=None, colspan=1, rowspan=1, indent=0, is_header=False, is_fact=False,
                 html_class=None, rc_code=None):
        self.label = label
        self.is_header = is_header
        self.is_fact = is_fact
        self.colspan = colspan
        self.rowspan = rowspan
        self.indent = indent
        self.rc_code = rc_code
        self.html_classes = None if html_class is None else set(html_class.split(' '))
        # Final version of constraints
        self.constraints = constraints

    def add_constraint(self, asp, mem, axis):
        if self.constraints is None:
            self.constraints = {}
        self.constraints[asp] = data_wrappers.Constraint(asp, mem, axis)

    def add_class(self, cls):
        if self.html_classes is None:
            self.html_classes = set({})
        self.html_classes.add(cls)

    def get_class(self):
        if self.html_classes is None:
            return ''
        return f' class="{" ".join(self.html_classes)}"'

    def get_label(self):
        return '' if self.label is None else self.label

    def get_indent(self):
        if self.indent == 0:
            return ''
        return f' style="text-indent: {self.indent}"'

    def get_colspan(self):
        if self.colspan == 1:
            return ''
        return f' colspan="{self.colspan}"'

    def get_rowspan(self):
        if self.rowspan==1:
            return ''
        return f' rowspan="{self.rowspan}"'
