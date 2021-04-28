class DrSet:
    """ Dimensional Relationship Set """
    def __init__(self, start_base_set, container_taxonomy):
        self.bs_start = start_base_set
        self.taxonomy = container_taxonomy
        self.root_primary_items = []

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def compile(self):
        pass

    def info(self):
        return self.bs_start.get_key()



