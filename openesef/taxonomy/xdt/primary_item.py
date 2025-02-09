class PrimaryItem:
    def __init__(self, concept, container_dr_set, arc=None, lvl=0):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.target_role = arc.target_role if arc else None
        self.level = lvl
        """ All hypercube definitions related to that primary item - all and notAll """
        self.hypercubes = {}
