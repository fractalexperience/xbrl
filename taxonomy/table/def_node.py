from xbrl.taxonomy.table import tlb_resource


class DefinitionNode(tlb_resource.TableResource):
    """ Implements a definition node """
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
