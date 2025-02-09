from openesef.taxonomy.table import tlb_resource


class DefinitionNode(tlb_resource.TableResource):
    """ Implements a definition node """
    def __init__(self, e, container_xlink=None):
        self.detail_parsers = None
        super().__init__(e, container_xlink)

    def load_details(self, e):
        for e2 in e.iterchildren():
            method = self.detail_parsers.get(e2.tag, None)
            if method is None:
                print(f'Unknown CR element: {e2.tag}')
                return
            method(e2)
