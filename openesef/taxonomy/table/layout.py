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
