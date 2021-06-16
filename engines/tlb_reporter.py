from xbrl.taxonomy.table import breakdown, aspect_node, rule_node, cr_node, dr_node, str_node
from xbrl.engines import base_reporter


class TableReporter(base_reporter.BaseReporter):
    def __init__(self, t, d):
        super().__init__(t, d)
        """ Structures corresponding to compiled tables. 
            Key is table Id, value is the corresponding  x,y,z structure """
        self.structures = {}
        self.headers = {}
        self.cells = {}
        self.resource_names = ['breakdown', 'ruleNode', 'aspectNode', 'conceptRelationshipNode', 'dimensionRelationshipNode']

    def compile_cells(self, t):
        """ Returns a 3 dimensional array with table cells. """
        pass

    def compile_table(self, t):
        struct = self.structures.setdefault(t.xlabel, {})
        self.walk(t, None, struct, None, t.nested, 0)
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

    def walk(self, tbl, axis, struct, node, dct, lvl):
        for name in filter(lambda n: n in dct, self.resource_names):
            for r in [res for r_lst in dct.get(name).values() for res in r_lst]:  # Flatten the result list of lists.
                # print('-'*lvl, r.xlabel, f'[{r.get_rc_label()}]',  r.get_label())
                if isinstance(r, breakdown.Breakdown):
                    self.process_breakdown_node(tbl, struct, r, lvl)
                elif isinstance(r, aspect_node.AspectNode):
                    self.process_aspect_node(tbl, axis, struct, node, r, lvl)
                elif isinstance(r, rule_node.RuleNode):
                    self.process_rule_node(tbl, axis, struct, node, r, lvl)
                elif isinstance(r, cr_node.ConceptRelationshipNode):
                    self.process_cr_node(tbl, axis, struct, node, r, lvl)
                elif isinstance(r, dr_node.DimensionalRelationshipNode):
                    self.process_dr_node(tbl, axis, struct, node, r, lvl)

    def process_breakdown_node(self, tbl, struct, r, lvl):
        new_struct = struct.setdefault(r.axis, [])  # Creates a new structure for that axis (if not available)
        new_node = str_node.StructureNode(None, r, True)
        new_struct.append(new_node)
        self.walk(tbl, r.axis, new_struct, new_node, r.nested, lvl+1)

    def process_aspect_node(self, tbl, axis, struct, parent_node, r, lvl):
        tbl.open_axes.add(axis)
        # aspect_values = None if self.document is None else self.document.xbrl.aspect_values.get(r.aspect, None)
        aspect_values = None  # TODO: Reconsider calcualtion of aspect values and combine constraints in aspect nodes
        if aspect_values is None:  # No document attached, or no aspect values for that dimension - one empty node
            new_node = str_node.StructureNode(parent_node, r, True)
            self.walk(tbl, axis, struct, new_node, r.nested, lvl+1)
            return
        # for aspect_value in aspect_values:
        #     new_node = str_node.StructureNode(parent_node, r)
        #     new_node.add_constraint(r.aspect, aspect_value)
        #     self.walk(struct, new_node, r.nested, lvl+1)

    def process_rule_node(self, tbl, axis, struct, parent_node, r, lvl):
        tbl.has_rc_labels = r.get_rc_label() is not None
        tbl.has_db_labels = r.get_db_label() is not None
        new_node = str_node.StructureNode(parent_node, r, r.is_merged)
        for tag, rs in r.rule_sets.items():
            new_node.constraint_set.setdefault(tag, {}).update(rs)  # Copy any available restrictions from rule node
        self.walk(tbl, axis, struct, new_node, r.nested, lvl+1)

    def process_cr_node(self, tbl, axis, struct, parent_node, r, lvl):
        new_node = str_node.StructureNode(parent_node, r, False)
        self.walk(tbl, axis, struct, new_node, r.nested, lvl+1)

    def process_dr_node(self, tbl, axis, struct, parent_node, r, lvl):
        new_node = str_node.StructureNode(parent_node, r, False)
        self.walk(tbl, axis, struct, new_node, r.nested, lvl+1)

    def compile_all(self):
        for t in self.taxonomy.tables.values():
            self.compile_table(t)

    def compile_table_id(self, table_id):
        t = self.taxonomy.tables.get(table_id, None)
        if t is None:
            return
        self.compile_table(t)

    def render_html(self):
        self.init_output()
        for tid, headers in self.headers.items():
            tbl = self.taxonomy.tables.get(tid, None)
            self.add(['<h3>', tbl.get_label(), '</h3>'])
            self.init_table()
            hdrz = headers.get('z', None)
            hdry = headers.get('y', None)
            hdrx = headers.get('x', None)
            if hdrx is None or hdry is None:
                self.add(f'<tr><td><p class="err">Invalid table definition {tbl.xlabel}. Cannot render.</p></td></tr>')
            if hdrz is None:
                hdrz = {}
                sn = str_node.StructureNode(None, None, False)
                hdrz.setdefault(1, []).append(sn)
            self.render_zyx(tbl, hdrz, hdry, hdrx)
            self.finalize_table()
        self.finalize_output()
        return ''.join(self.content)

    def render_zyx(self, tbl, hdrz, hdry, hdrx):
        lowest_z = hdrz[max(hdrz)]
        for snz in lowest_z:
            self.render_yx(tbl, snz, hdry, hdrx)

    def render_yx(self, tbl, snz, hdry, hdrx):
        closed_x = [snx for snx in hdrx[max(hdrx)] if not isinstance(snx.origin, aspect_node.AspectNode)]
        open_x = [snx for snx in hdrx[max(hdrx)] if isinstance(snx.origin, aspect_node.AspectNode)]
        open_y = [sny for sny in hdry[max(hdry)] if isinstance(sny.origin, aspect_node.AspectNode)]
        closed_y = [sny for sny in hdry[max(hdry)] if not isinstance(sny.origin, aspect_node.AspectNode)]

        for row, hx in hdrx.items():
            self.add('<tr>')
            if row == 0:
                colspan = len(open_y)+(1 if closed_y else 0)+(1 if tbl.has_rc_labels else 0)
                rowspan = len(hdrx)+(1 if tbl.has_rc_labels else 0)
                self.add(f'<td colspan="{colspan}" rowspan="{rowspan}">{tbl.get_rc_label()}</td>')
            for snx in hx:
                cs = f' colspan="{snx.span}"' if snx.span > 1 else ''
                self.add(f'<td{cs}>{("" if snx.grayed else snx.origin.get_label())}</td>')
            self.add('</tr>')
        # Optional RC header
        for snx in closed_x:
            self.add(f'<td>{(snx.origin.get_rc_label())}</td>')
        self.render_y(tbl, snz, closed_y, open_y, closed_x, open_x)

    def render_y(self, tbl, snz, closed_y, open_y, closed_x, open_x):
        if open_y:
            # Extra header for open-y nodes
            self.add('<tr>')
            if closed_y:
                self.add('<td>&nbsp;</td>')  # Extra cell for closed-Y nodes if any
            for sno in open_y:
                self.add(f'<td>{sno.get_rc_caption()}</td>')
            if tbl.has_rc_labels:
                self.add('<td>&nbsp;</td>')
            self.add('</tr>')
        if closed_y:
            for snc in closed_y:
                self.render_y_agg(tbl, snz, snc, open_y, closed_x, open_x)
        else:
            self.render_y_agg(tbl, snz, None, open_y, closed_x, open_x)

    def render_y_agg(self, tbl, snz, snyc, open_y, closed_x, open_x):
        rc = set({})
        self.add('<tr>')
        if snyc is not None:
            sny_cap = snyc.origin.get_label() if snyc.origin is not None else ""
            sny_rc_cap = snyc.origin.get_rc_label() if snyc.origin is not None else ""
            rc.add(sny_rc_cap)
            self.add(f'<td style="text-indent:{snyc.level * 10};">{sny_cap}</td>')

        if open_y:
            for sno in open_y:
                rc.add(sno.origin.get_rc_label())
                self.add(f'<td></td>')
        if tbl.has_rc_labels:
            self.add(f'<td>{" ".join(rc)}</td>')
        self.render_tpl_body(tbl, snz, snyc, open_y, closed_x, open_x)
        self.add('</tr>')

    def render_tpl_body(self, tbl, snz, snyc, open_y, closed_x, open_x):
        for snxc in closed_x:
            # TODO: Show restrictions
            self.add('<td>')
            self.init_table()
            self.render_constraint_set(snz, 'z')
            self.render_constraint_set(snyc, 'y')
            for snyo in open_y:
                self.render_constraint_set(snyo, 'y')
            self.render_constraint_set(snxc, 'x')
            for snxo in open_x:
                self.render_constraint_set(snxo, 'x')
            self.finalize_table()
            self.add('</td>')

    def render_constraint_set(self, sn, axis):
        if sn is None:
            return
        constraints = {}
        parent = sn.origin
        while parent is not None:
            c_set = parent.get_constraints()
            if c_set is not None:
                for a, m in c_set.items():
                    if a not in constraints:
                        constraints[a] = m
            parent = parent.parent

        for asp, mem in constraints.items():
            self.add(f'<tr><td>{asp}</td><td>{"*" if mem is None else mem}</td><td>{axis}</td></tr>')

    def combine_constraints(self, sn1, sn2):
        for tag, c_set in sn2.constraint_set.items():
            for asp, mem in c_set.items():
                sn1.constraint_set.setdefault(tag, {})[asp] = mem
