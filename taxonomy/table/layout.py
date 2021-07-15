class Layout:
    def __init__(self, lbl, rc):
        self.label = lbl
        self.rc_code = rc
        # Each cell here corresponds to a table
        self.cells = []
        # Open dimensions per axis
        self.open_dimensions = {}

