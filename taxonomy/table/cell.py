from xbrl.base import data_wrappers


class Cell:
    def __init__(self, constraints=None, label=None, colspan=1, rowspan=1, indent=0, is_header=False, is_fact=False):
        self.label = label
        self.is_header = is_header
        self.is_fact = is_fact
        self.colspan = colspan
        self.rowspan = rowspan
        self.indent = indent
        # Final version of constraints
        self.constraints = constraints

    def add_constraint(self, asp, mem, axis):
        if self.constraints is None:
            self.constraints = {}
        self.constraints[asp] = data_wrappers.Constraint(asp, mem, axis)
