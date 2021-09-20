from builtins import isinstance

from xbrl.taxonomy.table import breakdown, aspect_node, rule_node, cr_node, dr_node, str_node, layout, cell
from xbrl.engines import base_reporter
from xbrl.base import data_wrappers, const


class TableReporter(base_reporter.BaseReporter):
    def __init__(self, t, d):
        super().__init__(t, d)
        """ Structures corresponding to compiled tables. 
            Key is table Id, value is the corresponding  x,y,z structure """
        self.structures = {}
        self.headers = {}
        self.layouts = {}
        self.current_layout = None
        self.current_z = None
        self.current_y = None
        self.current_x = None
        self.resource_names = ['breakdown', 'ruleNode', 'aspectNode', 'conceptRelationshipNode',
                               'dimensionRelationshipNode']

    def compile_table_id(self, table_id):
        self.compile_table(self.taxonomy.tables.get(table_id, None))

    def compile_table(self, t):
        if t is None:
            return
        struct = self.structures.setdefault(t.xlabel, {})
        self.walk(t, None, struct, None, t.nested, 0)
        for axis, s_lst in struct.items():
            for sn in s_lst:
                depth = self.get_max_depth(sn, 0)
                self.set_uniform_depth(sn, 0, depth)
        self.compile_headers(struct, t)

    def compile_headers(self, struct, t):
        headers = self.headers.setdefault(t.xlabel, {})
        self.populate_headers(headers, struct, t)

    def populate_headers(self, matrix, struct, t):
        # Generate one header per axis
        for axis, s_lst in struct.items():
            header = matrix.setdefault(axis, {})
            for sn in s_lst:
                depth = self.get_max_depth(sn, 0)
                for lvl in range(depth + 1):
                    header.setdefault(lvl, [])
                self.calculate_header(header, sn, 0, axis, t.parent_child_order)
            # Calculate span
            depth = max(header)
            last_row = header.get(depth, None)
            if last_row is None:
                continue
            for sn in last_row:
                sn.increment_span()

    def calculate_header(self, header, sn, lvl, axis, pco):
        maxlvl = max(header)
        if isinstance(sn.origin, breakdown.Breakdown):
            pco = sn.origin.parent_child_order
        # childrent-first case
        if pco is not None and pco == 'children-first' and sn.nested is not None:
            for snn in sn.nested:
                self.calculate_header(header, snn, lvl + 1, axis, pco)
        if not sn.is_fake and not isinstance(sn.origin, breakdown.Breakdown):
            header[lvl].append(sn)
        tlvl = lvl + 1
        if not sn.is_abstract \
                or (axis == 'y' and not isinstance(sn.origin, breakdown.Breakdown)) \
                or (axis == 'y' and isinstance(sn.origin, breakdown.Breakdown) and sn.origin.is_open):
            # Propagate fake structure nodes down to the tree
            while tlvl <= maxlvl:
                if not sn.is_fake and tlvl <= maxlvl:
                    header[tlvl].append(sn.get_fake_copy())
                tlvl += 1
        if sn.nested is None or (pco is not None and pco == 'children-first'):
            return
        for snn in sn.nested:
            self.calculate_header(header, snn, lvl + 1, axis, pco)

    def get_max_depth(self, sn, depth):
        if sn.nested is None:
            return depth
        depths = [self.get_max_depth(s, depth + 1) for s in sn.nested]
        m_depth = max(depths)
        return m_depth

    def set_uniform_depth(self, sn, lvl, depth):
        if lvl == depth or sn is None:
            return
        if sn.nested is None:
            # Generate a fake structure node just to balance the tree
            new_sn = sn.get_fake_copy()
            self.set_uniform_depth(new_sn, lvl + 1, depth)
            return
        for nested_sn in sn.nested:
            self.set_uniform_depth(nested_sn, lvl + 1, depth)

    def walk(self, tbl, axis, struct, node, dct, lvl):
        for name in filter(lambda n: n in dct, self.resource_names):
            # Flatten the result list of lists.
            l = [res for r_lst in dct.get(name).values() for res in r_lst]
            for r in sorted(l, key=lambda re: 0 if re.order is None else re.order.zfill(10)):
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
        new_node = str_node.StructureNode(parent=None, origin=r, grayed=True, lvl=lvl, abst=True)
        new_struct.append(new_node)
        self.walk(tbl, r.axis, new_struct, new_node, r.nested, lvl + 1)

    def process_aspect_node(self, tbl, axis, struct, parent_node, r, lvl):
        tbl.open_axes.add(axis)
        p = parent_node
        while p:
            if isinstance(p.origin, breakdown.Breakdown):
                p.origin.is_open = True
            p = p.parent

        new_node = str_node.StructureNode(parent=parent_node, origin=r, grayed=True, lvl=lvl)
        self.walk(tbl, axis, struct, new_node, r.nested, lvl + 1)

    def process_rule_node(self, tbl, axis, struct, parent_node, r, lvl):
        tbl.has_rc_labels = r.get_rc_label() is not None
        tbl.has_db_labels = r.get_db_label() is not None
        new_node = str_node.StructureNode(parent=parent_node, origin=r, grayed=r.is_merged, lvl=lvl,
                                          abst=r.is_abstract)
        for tag, rs in r.rule_sets.items():
            new_node.constraint_set.setdefault(tag, {}).update(rs)  # Copy any available restrictions from rule node
        self.walk(tbl, axis, struct, new_node, r.nested, lvl + 1)

    def process_cr_node(self, tbl, axis, struct, parent_sn, r, lvl):
        bs = self.taxonomy.base_sets.get(f'{r.arc_name}|{r.arcrole}|{r.role}', None)
        if bs is None:  # This should not happen actually
            new_node = str_node.StructureNode(parent=parent_sn, origin=r, grayed=False, lvl=lvl)
            self.walk(tbl, axis, struct, new_node, r.nested, lvl + 1)
            return
        effective_roots = self.get_effective_roots(bs, r)
        generations = None if r.generations is None else int(r.generations)
        # TODO: Handle other types of formula axis
        if r.formula_axis in ['child', 'child-or-self']:
            generations = 1
        use_parent = True if r.formula_axis.endswith('-or-self') else False
        for effective_root in effective_roots:
            self.tree_walk(tbl, axis, struct, r, bs, parent_sn, effective_root, generations, 0, lvl, use_parent)

    def get_effective_roots(self, bs, r):
        effective_roots = []
        for rsrc in r.relationship_sources:
            if rsrc == 'xfi:root':
                effective_roots += bs.roots
            else:
                effective_root = self.taxonomy.concepts_by_qname.get(rsrc, None)
                if effective_root is not None:
                    effective_roots.append(effective_root)
        return effective_roots

    def tree_walk(self, tbl, axis, struct, r, bs, parent_sn, concept, generations, cr_walk_lvl, lvl, use_parent):
        new_sn = parent_sn
        is_cr = isinstance(r, cr_node.ConceptRelationshipNode)
        if use_parent:
            new_sn = str_node.StructureNode(parent=parent_sn, origin=r, grayed=False, lvl=lvl, concept=concept,
                                            abst=is_cr and concept.abstract)
            if is_cr:
                new_sn.add_constraint('concept', concept.qname)
            else:
                new_sn.add_constraint(r.dimension, concept.qname)
        if generations is not None and generations < cr_walk_lvl:
            return
        cbs_dn = concept.chain_dn.get(bs.get_key(), None)
        if cbs_dn is None:
            return
        for node in sorted(cbs_dn, key=lambda t: 0 if t.Arc.order is None else float(t.Arc.order)):
            self.tree_walk(tbl, axis, struct, r, bs, new_sn, node.Concept, generations, cr_walk_lvl + 1, lvl + 1, True)

    def process_dr_node(self, tbl, axis, struct, parent_sn, r, lvl):
        bs = self.taxonomy.base_sets.get(f'definitionArc|{const.XDT_DIMENSION_DOMAIN_ARCROLE}|{r.role}', None)
        if bs is None:  # This should not happen actually
            new_node = str_node.StructureNode(parent=parent_sn, origin=r, grayed=False, lvl=lvl)
            self.walk(tbl, axis, struct, new_node, r.nested, lvl + 1)
            return
        root_members = bs.get_members(start_concept=r.dimension, include_head=False)
        generations = None if r.generations is None else int(r.generations)
        # TODO: Handle other types of formula axis
        if r.formula_axis in ['child', 'child-or-self']:
            generations = 1
        use_parent = True if r.formula_axis.endswith('-or-self') else False
        for root_member in root_members:
            eff_role = root_member.Arc.target_role \
                if root_member.Arc is not None and root_member.Arc.target_role is not None else r.role
            bs_dm = self.taxonomy.base_sets.get(f'definitionArc|{const.XDT_DOMAIN_MEMBER_ARCROLE}|{eff_role}', None)
            if bs_dm is None:
                continue
            effective_roots = self.get_effective_roots(bs_dm, r)
            for effective_root in effective_roots:
                self.tree_walk(tbl, axis, struct, r, bs_dm, parent_sn, effective_root, generations, 0, lvl, use_parent)

    def compile_all(self):
        for t in self.taxonomy.tables.values():
            self.compile_table(t)

    def init_output_table(self, title=None):
        self.init_output(title, styles={
            '.xbrl_fact': 'background-color: White;',
            '.xbrl_grayed': 'background-color: #d0d0d0;',
            '.xbrl_header': 'background-color: #d0ffd0;',
            '.xbrl_header_abstract': 'background-color: PaleGreen;',
            '.xbrl_rc': 'background-color: Khaki;',
            '.xbrl_lu': 'background-color: PaleGreen;',
            '.xbrl_fake': 'background-color: #e0ffe0;',
            '.xbrl_other': 'background-color: Yellow;'
        })

    def render_templates_html(self, table_ids=None, show_constraints=False, add_html_head=True):
        ids = [tid for tid in self.taxonomy.tables.keys()] \
            if table_ids is None else [table_ids] \
            if isinstance(table_ids, str) else table_ids
        if add_html_head:
            self.init_output_table()
        else:
            self.content = []  # Just clears the content
        for tid in ids:
            lo = self.layouts.get(tid, None)
            if lo is None:
                return ''
            cpt = tid if lo.label == tid else f'{tid} - {lo.label}'
            self.add(f'<h3>{cpt}</h3>')
            for cz in lo.cells:
                self.init_table()
                for cy in cz:
                    self.add('<tr>')
                    for cx in cy:
                        self.add(f'<td{cx.get_colspan()}{cx.get_rowspan()}{cx.get_indent()}{cx.get_class()}>')
                        self.add('' if cx.is_fact or cx.is_fake else cx.get_label())
                        if show_constraints:
                            self.render_cell_constraints_html(cx)
                        self.add('</td>')
                    self.add('</tr>')
                self.finalize_table()
        if add_html_head:
            self.finalize_output()
        return ''.join(self.content)

    def render_cell_constraints_html(self, tc):
        if tc is None or not tc.constraints:
            return
        self.init_table()
        for c in sorted(tc.constraints.values(), key=lambda c: c.Dimension):
            self.add(
                f'<tr><td>{c.Dimension}</td><td>{("*" if c.Member is None else c.Member)}</td><td>{c.Axis}</td></tr>')
        self.finalize_table()

    def get_dpm_map(self, tid):
        lo = self.layouts.get(tid, None)
        if lo is None:
            return None
        # Flatten the 3D list and choose only fact cells
        f_cells = [c for lz in lo.cells for ly in lz for c in ly if c.is_fact]
        custom_dimensions = sorted(set(d for dims in [
            [] if c.constraints is None else c.constraints for c in f_cells] for d in dims if d != 'concept'))
        dpm_map = data_wrappers.DpmMap(tid, custom_dimensions, {}, set([a for a in lo.open_dimensions.values()]))
        for c in f_cells:
            cco = c.constraints.get('concept', None)
            concept = None if cco is None else self.taxonomy.concepts_by_qname.get(cco.Member, None)
            members = ['*' if m is None else m for m in
                       [c.constraints.get(dim, data_wrappers.Constraint(dim, 'N/A', None)).Member
                        for dim in sorted(custom_dimensions)]]
            dpm_map.Mappings[c.get_address()] = dict(zip(
                [*data_wrappers.DpmMapMandatoryDimensions, *custom_dimensions, 'grayed'],
                [c.get_label(),
                 None if concept is None else concept.qname,
                 None if concept is None else concept.data_type,
                 None if concept is None else concept.period_type,
                 *members, c.is_grayed]))
        return dpm_map

    def render_map_html(self, table_ids=None, add_html_head=True):
        table_ids = self.taxonomy.tables.keys() if table_ids is None else [table_ids] if isinstance(table_ids, str) else table_ids
        if add_html_head:
            self.init_output_table()
        else:
            self.content = []  # Just clears the content
        for tid in table_ids:
            lo = self.layouts.get(tid, None)
            if lo is None:
                continue
            dpm_map = self.get_dpm_map(tid)
            dims = data_wrappers.DpmMapMandatoryDimensions + dpm_map.Dimensions
            self.init_table(columns=['Address', *dims], cls_head='xbrl_header')
            for address, mapping in dpm_map.Mappings.items():
                self.add_tr(address, *[mapping.get(d, '-') for d in dims])
            self.finalize_table()
        if add_html_head:
            self.finalize_output()
        return ''.join(self.content)

    def do_layout(self, table_ids=None):
        ids = self.taxonomy.tables.keys() if table_ids is None else [table_ids] \
            if isinstance(table_ids, str) else table_ids

        for tid in ids:
            headers = self.headers.get(tid, None)
            if headers is None:
                continue
            tbl = self.taxonomy.tables.get(tid, None)
            # Create a layout for table
            self.current_layout = self.layouts.setdefault(tid, layout.Layout(tbl.get_label(), tbl.get_rc_label()))
            # Prepare dictionary of closed headers and ensure that each one has at least one member
            hdr, h_open, h_closed = {}, {}, {}
            for axis in ['x', 'y', 'z']:
                h = headers.get(axis, {})
                if not h:
                    h.setdefault(1, []).append(str_node.StructureNode(None, None, False))
                hdr[axis] = h
                h_open[axis] = [sn for sn in h[max(h)] if isinstance(sn.origin, aspect_node.AspectNode)]
                sn_closed = [sn for sn in h[max(h)] if not isinstance(sn.origin, aspect_node.AspectNode)]
                if not sn_closed:
                    sn_closed = [str_node.StructureNode(None, None, False)]
                h_closed[axis] = sn_closed

            self.combine_aspect_nodes(h_closed, h_open)
            self.lay_zyx(tbl, hdr, h_open, h_closed)
        return self.current_layout

    def combine_constraints(self, sn1, sn2):
        for tag, c_set in sn2.constraint_set.items():
            for asp, mem in c_set.items():
                sn1.constraint_set.setdefault(tag, {})[asp] = mem

    def combine_aspect_nodes(self, h_closed, h_open):
        for axis, closed_nodes in h_closed.items():
            open_nodes = h_open.get(axis, None)
            if open_nodes is None:
                continue
            for cn in closed_nodes:
                for on in open_nodes:
                    if not isinstance(on.origin, aspect_node.AspectNode):
                        continue
                    cn.constraint_set.setdefault('default', {})[on.origin.aspect] = None

    def new_table(self):
        self.current_z = []
        self.current_layout.cells.append(self.current_z)

    def new_row(self):
        self.current_y = []
        self.current_z.append(self.current_y)

    def new_cell(self, c):
        self.current_x = c
        self.current_y.append(c)

    def lay_zyx(self, tbl, hdr, h_open, h_closed):
        for snz in h_closed['z']:
            if snz.is_abstract:
                continue
            self.new_table()
            self.lay_yx(tbl, snz, hdr, h_open, h_closed)

    def lay_yx(self, tbl, snz, hdr, h_open, h_closed):
        for row, hx in hdr['x'].items():
            self.new_row()
            if row == 0:
                # Left upper cell
                colspan = len(h_open['y']) + (1 if h_closed['y'] else 0) + (1 if tbl.has_rc_labels else 0)
                rowspan = len(hdr['x']) + (1 if tbl.has_rc_labels else 0)
                self.new_cell(cell.Cell(label=tbl.get_rc_label(), colspan=colspan, rowspan=rowspan, is_header=True,
                                        html_class='xbrl_lu'))
            # X-Headers
            for snx in hx:
                if isinstance(snx.origin, breakdown.Breakdown) and snx.origin.is_open \
                        or isinstance(snx.origin, aspect_node.AspectNode):
                    continue
                colspan = snx.span if row == snx.level else 1
                cls = 'xbrl_fake' if snx.is_fake else 'xbrl_header'
                gry = snx.is_fake or snx.is_abstract
                self.new_cell(cell.Cell(label=snx.get_caption(False), colspan=colspan, is_header=True,
                                        html_class=cls, is_fake=snx.is_fake))
        # Optional RC header
        self.new_row()
        for snx in h_closed['x']:
            if snx.is_abstract:
                continue
            self.new_cell(cell.Cell(label='' if snx.origin is None else snx.origin.get_rc_label(),
                                    is_header=True, html_class='xbrl_rc'))
        self.lay_y(tbl, snz, h_open, h_closed)

    def lay_y(self, tbl, snz, h_open, h_closed):
        if h_open['y']:
            # Extra header for open-y nodes
            self.new_row()
            if h_closed['y']:
                # Extra cell for closed-Y nodes if any
                self.new_cell(cell.Cell(html_class='xbrl_header'))
            for sno in h_open['y']:
                self.new_cell(cell.Cell(label=sno.get_rc_caption(), html_class='xbrl_header'))
            if tbl.has_rc_labels:
                # Extra cell for RC labels if any
                self.new_cell(cell.Cell(html_class='xbrl_rc'))
            # Filling row with empty cells for extra open-Y header
            for snx in h_closed['x']:
                if snx.is_abstract:
                    continue
                self.new_cell(cell.Cell(html_class='xbrl_other'))
        cnt = -1
        for sny in h_closed['y']:
            cnt += 1
            self.lay_y_agg(tbl, snz, sny, h_open, h_closed, cnt)

    def lay_y_agg(self, tbl, snz, sny, h_open, h_closed, position):
        rc = set({})
        self.new_row()
        if h_open['y']:
            self.lay_open_y_header(h_open['y'], rc)
        if sny is not None:
            self.lay_closed_y_header(sny, rc)
        if tbl.has_rc_labels:
            self.new_cell(cell.Cell(label=" ".join(rc), html_class='xbrl_rc'))
        self.lay_tbl_body(snz, sny, h_closed['x'], position)

    def lay_open_y_header(self, open_y, rc):
        for sno in open_y:
            rc.add(sno.origin.get_rc_label())
            self.new_cell(cell.Cell(html_class='xbrl_header'))

    def lay_closed_y_header(self, sny, rc):
        sny_rc_cap = sny.origin.get_rc_label() if sny.origin is not None else ""
        rc.add(sny_rc_cap)
        cls = f'xbrl_header_abstract' if sny.is_abstract else 'xbrl_header'
        self.new_cell(cell.Cell(label=sny.get_caption(False), indent=sny.level * 10, html_class=cls))

    def lay_tbl_body(self, snz, sny, closed_x, position):
        r_code = None if sny.origin is None else sny.origin.get_rc_label()
        if not r_code:
            r_code = f'r{position}'
        cnt = -1
        for snx in closed_x:
            if snx.is_abstract:
                continue
            cnt += 1
            c_code = snx.origin.get_rc_label() if snx.origin is not None else ''
            if not c_code:
                c_code = f'c{cnt}'
            cls = 'xbrl_grayed' if sny.is_abstract else 'xbrl_fact'
            lbl = f'{sny.get_caption().strip()}/{snx.get_caption().strip()}'
            c = cell.Cell(label=lbl, html_class=cls, is_fact=True,
                          r_code=r_code, c_code=c_code, is_grayed=sny.is_abstract)
            self.new_cell(c)
            self.lay_constraint_set({'x': snx, 'y': sny, 'z': snz}, c)
            if not self.validate(c):
                c.is_grayed = True
                c.html_classes.add('xbrl_grayed')

    def lay_constraint_set(self, dct, c):
        for axis, sn in dct.items():
            constraints = sn.constraint_set.get('default', {})
            parent = sn.origin
            while parent is not None:
                c_set = parent.get_constraints()
                if c_set is not None:
                    for a, m in c_set.items():
                        if a not in constraints:
                            constraints[a] = m
                parent = parent.parent
            c.add_constraints(constraints, axis)
            # Add open dimensions to layout
            for asp in [a for a, m in constraints.items() if m is None]:
                self.current_layout.open_dimensions[asp] = axis
            # Check if there is a tag selector and add additional constraints for matching rule set
            if sn.origin is not None \
                    and isinstance(sn.origin, rule_node.RuleNode) \
                    and sn.origin.tag_selector is not None:
                for tagged_constraints in [s.origin.rule_sets[sn.origin.tag_selector] for s in dct.values()
                                           if s.origin is not None
                                              and isinstance(s.origin, rule_node.RuleNode)
                                              and s.origin.tag_selector in s.origin.rule_sets]:
                    c.add_constraints(tagged_constraints, axis)

    """ Calculates the 'grayed' property based on XDT constraints. If there is at least one dimensional relationship set
        matching constraints, then grayed is false, otherwise true."""
    def validate(self, c):
        if not self.current_layout.rc_code:
            return True
        constraint = c.constraints.get('concept', None)
        if constraint is None:
            return False  # Every data point must have a concept constraint
        concept = self.taxonomy.concepts_by_qname.get(constraint.Member, None)
        if concept is None:
            return False  # The concept must be available in taxonomy
        drs_for_pi = self.taxonomy.idx_pi_drs.get(concept.qname, None)
        if drs_for_pi is None:
            return False  # the concept must be a primary item and it must be connected to at least one DRS
        drs_for_tbl = [drs for drs in drs_for_pi
                       if self.current_layout.rc_code in drs.bs_start.role  # EBA/EIOPA specific
                       or self.current_layout.rc_code.replace(' ', '_') in drs.bs_start.role]  # Exception for EBA
        if not drs_for_tbl:
            return False
        valid_drs = [drs for drs in drs_for_tbl if self.validate_drs(c, drs)]
        if not valid_drs:
            return False
        return True

    def validate_drs(self, c, drs):
        checklist = {asp: co for asp, co in c.constraints.items() if asp != 'concept'}
        for hc in drs.hypercubes.values():
            for dim in hc.dimensions.values():
                constraint = checklist.get(dim.concept.qname, None)
                if constraint is None:
                    if dim.members is not None \
                            and [m for m in dim.members.values() if m.qname in self.taxonomy.default_members]:
                        # There is a dimension in DRS, which is not in cell. constraints, but it has a default member
                        # and can be skipped
                        continue
                    else:
                        # There is a dimension in DRS, which is not in cell constraints and this dimension
                        # has no default member
                        return False
                if constraint.Member is None:
                    del checklist[dim.concept.qname]  # This is an open dimension and so it matches
                    continue
                for mem in dim.members.values():
                    if mem.qname == constraint.Member:
                        del checklist[dim.concept.qname]
                        break
        return False if checklist else True
