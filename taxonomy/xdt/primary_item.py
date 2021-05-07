class PrimaryItem:
    def __init__(self, concept, container_dr_set, target_role=None):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.is_usable = True
        self.target_role = target_role
        """ Child items of that primary item in the starting domain-member base set. """
        self.nested_primary_items = {}
        """ All hypercube definitions related to that primary item - all and notAll """
        self.hypercubes = {}

    def compile(self):
        pass

