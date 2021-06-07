from xbrl.taxonomy.table import breakdown, aspect_node, rule_node, cr_node, dr_node, str_node


class TableEngine:
    def __init__(self, t, d=None):
        self.taxonomy = t
        self.document = d
        """ Structures corresponding to compiled tables. 
            Key is table Id, value is the corresponding  x,y,z structure """
        self.structures = {}
        self.headers = {}
        self.cells = {}
        self.resource_names = ['breakdown', 'ruleNode', 'aspectNode',
                               'conceptRelationshipNode', 'dimensionRelationshipNode']

    def compile_cells(self, t):
        """ Returns a 3 dimensional array with table cells. """
        pass

    def compile_table(self, t):
        struct = self.structures.setdefault(t.xlabel, {})
        self.walk(struct, None, t.nested, 0)
        for s_lst in struct.values():
            depth = max([self.get_max_depth(sn, 0) for sn in s_lst])
            for sn in s_lst:
                self.set_uniform_depth(sn, 0, depth)
        self.compile_headers(struct, t)

    def compile_headers(self, struct, t):
        headers = self.headers.setdefault(t.xlabel, {})
        self.populate_headers(headers, struct)

    def populate_headers(self, matrix, struct):
        # Generate one header per axis
        for axis, s_lst in struct.items():
            header = matrix.setdefault(axis, {})
            for sn in s_lst:
                self.calculate_header(header, sn, 0)
            # Calculate span
            depth = max(header)
            last_row = header.get(depth, None)
            if last_row is None:
                continue
            for sn in last_row:
                sn.increment_span()

    def calculate_header(self, header, sn, lvl):
        header.setdefault(lvl, []).append(sn)
        if sn.nested is None:
            return
        for snn in sn.nested:
            self.calculate_header(header, snn, lvl+1)

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
            new_sn = str_node.StructureNode(sn, sn.origin, True)
            self.set_uniform_depth(new_sn, lvl+1, depth)
            return
        for nested_sn in sn.nested:
            self.set_uniform_depth(nested_sn, lvl+1, depth)  # Do not generate new node

    def walk(self, struct, node, dct, lvl):
        for name in filter(lambda n: n in dct, self.resource_names):
            for r in [res for r_lst in dct.get(name).values() for res in r_lst]:  # Flatten the result list of lists.
                # print('-'*lvl, r.xlabel, f'[{r.get_rc_label()}]',  r.get_label())
                if isinstance(r, breakdown.Breakdown):
                    self.process_breakdown_node(struct, r, lvl)
                elif isinstance(r, aspect_node.AspectNode):
                    self.process_aspect_node(struct, node, r, lvl)
                elif isinstance(r, rule_node.RuleNode):
                    self.process_rule_node(struct, node, r, lvl)
                elif isinstance(r, cr_node.ConceptRelationshipNode):
                    self.process_cr_node(struct, node, r, lvl)
                elif isinstance(r, dr_node.DimensionalRelationshipNode):
                    self.process_dr_node(struct, node, r, lvl)

    def process_breakdown_node(self, struct, r, lvl):
        new_struct = struct.setdefault(r.axis, [])  # Creates a new structure for that axis (if not available)
        new_node = str_node.StructureNode(None, r, True)
        new_struct.append(new_node)
        self.walk(new_struct, new_node, r.nested, lvl+1)

    def process_aspect_node(self, struct, parent_node, r, lvl):
        # aspect_values = None if self.document is None else self.document.xbrl.aspect_values.get(r.aspect, None)
        aspect_values = None  # TODO: Reconsider calcualtion of aspect values and combine constraints in aspect nodes
        if aspect_values is None:  # No document attached, or no aspect values for that dimension - one empty node
            new_node = str_node.StructureNode(parent_node, r, True)
            self.walk(struct, new_node, r.nested, lvl+1)
            return
        # for aspect_value in aspect_values:
        #     new_node = str_node.StructureNode(parent_node, r)
        #     new_node.add_constraint(r.aspect, aspect_value)
        #     self.walk(struct, new_node, r.nested, lvl+1)

    def process_rule_node(self, struct, parent_node, r, lvl):
        new_node = str_node.StructureNode(parent_node, r, r.is_merged)
        for tag, rs in r.rule_sets.items():
            new_node.constraint_set.setdefault(tag, {}).update(rs)  # Copy any available restrictions from rule node
        self.walk(struct, new_node, r.nested, lvl+1)

    def process_cr_node(self, struct, parent_node, r, lvl):
        new_node = str_node.StructureNode(parent_node, r, False)
        self.walk(struct, new_node, r.nested, lvl+1)

    def process_dr_node(self, struct, parent_node, r, lvl):
        new_node = str_node.StructureNode(parent_node, r, False)
        self.walk(struct, new_node, r.nested, lvl+1)

    def compile_all(self):
        for t in self.taxonomy.tables.values():
            self.compile_table(t)

    def compile_table_id(self, table_id):
        t = self.taxonomy.tables.get(table_id, None)
        if t is None:
            return
        self.compile_table(t)
