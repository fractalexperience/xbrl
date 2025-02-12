class Hypercube:
    def __init__(self, concept, container_dr_set, arc=None):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.primary_item = None
        self.target_role = arc.target_role
        self.dimensions = {}

    def has_signature(self, signature):
        """ Check if the hypercube includes a specific signature """
        parts = signature.split('|')
        for part in parts:
            dim_qname = part.split('#')[0]
            mem_qname = part.split('#')[1]
            dim = self.dimensions.get(dim_qname)
            if dim is None or dim.members is None:
                return False  # No matching dimension
            mem = dim.members.get(mem_qname)
            if mem is None:
                return False  # No matching member
        return True

    def num_signatures(self):
        """ Calculates the number of signatures for the hypercube """
        if self.dimensions is None:
            return 0
        return sum([0 if d is None or d.members is None else len(d.members) for d in self.dimensions.values()])
