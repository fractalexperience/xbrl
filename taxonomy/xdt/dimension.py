class Dimension:
    def __init__(self, concept, container_dr_set, arc=None):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.target_role = arc.target_role if arc else None
        self.members = {} if self.concept.is_explicit_dimension else None
