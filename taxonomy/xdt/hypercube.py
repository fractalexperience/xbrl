class Hypercube:
    def __init__(self, concept, container_dr_set, arc=None):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.primary_item = None
        self.target_role = arc.target_role
        self.dimensions = {}
