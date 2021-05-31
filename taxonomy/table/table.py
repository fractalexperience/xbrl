from xbrl.taxonomy.table import tlb_resource, str_node


class Table(tlb_resource.TableResource):
    """ Implements a XBRL table """
    def __init__(self, e, container_xlink=None):
        self.headers = {}
        self.structure = {}
        super().__init__(e, container_xlink)
        container_xlink.linkbase.taxonomy.tables[self.xlabel] = self

    def compile(self, names=None, lvl=0, s_node=None):
        super().compile(['breakdown'])
        for s_lst in self.structure.values():
            depth = max([self.get_max_depth(sn, 0) for sn in s_lst])
            for sn in s_lst:
                self.set_uniform_depth(sn, 0, depth)
        # for header in self.headers.values():
        #     last_row = [row for row in header.values()][-1]
        #     for sn in last_row:
        #         sn.resource.increment_span()

    def get_max_depth(self, sn, depth):
        if sn.nested is None:
            return depth
        depths = [self.get_max_depth(s, depth+1) for s in sn.nested]
        m_depth = max(depths)
        return m_depth

    def set_uniform_depth(self, sn, lvl, depth):
        if lvl == depth or sn is None:
            return
        if sn.nested is None:
            new_sn = str_node.StructureNode(sn, None)
            self.set_uniform_depth(new_sn, lvl+1, depth)
            return
        for nested_sn in sn.nested:
            self.set_uniform_depth(nested_sn, lvl+1, depth)  # Do not generate new node
