class PrimaryItem:
    def __init__(self, concept, container_dr_set):
        self.concept = concept
        self.container_dr_set = container_dr_set
        self.is_usable = True
        self.target_role = None
        self.nested_primary_items = {}

    def compile(self):
        pass

