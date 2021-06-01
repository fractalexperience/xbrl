class StructureNode:
    def __init__(self, parent, resource, grayed=False):
        """ Parent structure node in the hierarchy """
        self.parent = parent
        """ Resource, which is the origin of this structure node """
        self.origin = resource
        self.span = 0
        self.grayed = grayed
        self.nested = None
        if self.parent is not None:
            if parent.nested is None:
                parent.nested = []
            self.parent.nested.append(self)

    def increment_span(self):
        self.span += 1
        if self.parent is None:
            return
        self.parent.increment_span()
