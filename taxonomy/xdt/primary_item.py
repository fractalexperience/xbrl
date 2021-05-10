class PrimaryItem:
    def __init__(self, concept, container_dr_set, arc=None):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.target_role = arc.target_role if arc else None
        """ All hypercube definitions related to that primary item - all and notAll """
        self.hypercubes = {}
