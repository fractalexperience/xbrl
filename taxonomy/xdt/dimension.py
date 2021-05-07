class Dimension:
    def __init__(self, concept, container_dr_set, target_role=None):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.target_role = target_role
        self.is_explicit = True if self.concept.typed_domain_ref is None else False
        self.members = {} if self.is_explicit else None
