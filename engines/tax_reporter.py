from xbrl.engines import html_helper
from lxml import etree as lxml


class TaxonomyReporter(html_helper.HtmlHelper):
    def __init__(self, t=None, d=None):
        self.taxonomy = t
        self.document = d
        super().__init__()

    def r_role_types(self):
        self.init_output('Role Types')
        self.init_table(['roleUri', 'Definition', 'usedOn'])
        for rt in self.taxonomy.role_types.values():
            self.add(f'<tr><td>{rt.role_uri}</td><td>{rt.definition}</td><td>{",".join(rt.used_on)}</td></tr>')
        self.finalize_table()
        self.finalize_output()

    def r_arcrole_types(self):
        self.init_output('ArcRole Types')
        self.init_table(['arcroleUri', 'Definition', 'usedOn', 'cyclesAllowed'])
        for art in self.taxonomy.arcrole_types.values():
            self.add(f'<tr>'
                     f'<td>{art.arcrole_uri}</td><td>{art.definition}</td>'
                     f'<td>{",".join(art.used_on)}</td><td>{art.cycles_allowed}</td><'
                     f'tr>')
        self.finalize_table()
        self.finalize_output()

    def r_enumeration_sets(self):
        self.init_output('Enumeration Sets')
        enum_sets = self.taxonomy.get_enumeration_sets()
        for k, es in enum_sets.items():
            self.r_enumeration(es)
        self.finalize_output()

    def r_enumerations(self):
        self.init_output('Extensible Enumerations')
        enums = self.taxonomy.get_enumerations()
        for e in sorted(enums.values(), key=lambda e: e.Key):
            self.r_enumeration(e)
        self.finalize_output()

    def r_enumeration(self, e):
        parts = e.Key.split('|')
        linkrole = parts[0] if len(parts)>0 else ''
        domain = parts[1] if len(parts)>1 else ''
        head_usable = parts[2] if len(parts)>2 else ''
        self.add(f'<br/>Link role: <tt>{linkrole}</tt><br/>Domain: <tt>{domain}</tt><br/>Head Usable: <tt>{head_usable}</tt><br/>')
        self.init_table(['Label', 'QName'])
        self.add(f'<tr><th colspan="2">Concepts</th></tr>')
        for c in sorted(e.Concepts, key=lambda co: co.get_enum_label(linkrole)):
            self.add(f'<tr><td>{c.get_enum_label(linkrole)}</td><td><tt>{c.qname}</tt></td></tr>')
        self.add(f'<tr><th colspan="2">Members</th></tr>')
        for m in sorted(e.Members, key=lambda me: me.get_enum_label(linkrole)):
            self.add(f'<tr><td>{m.get_enum_label(linkrole)}</td><td><tt>{m.qname}</tt></td></tr>')
        self.finalize_table()

    def r_base_sets(self, arc_name, arcrole):
        self.init_output('Hierarchies Report')
        self.add(f'<hr/>Arc name: {arc_name}<br/>Arc role: {arcrole}<br/>')
        self.init_table(['definition', 'roleUri'])
        for bs in [bs for bs in self.taxonomy.base_sets.values() if bs.arc_name == arc_name and bs.arcrole == arcrole]:
            rt = self.taxonomy.role_types.get(bs.role, None)
            self.add(f'<tr><td>{rt.definition if rt else "n.a."}</td><td>{bs.role}</td></tr>')
        self.finalize_table()
        self.finalize_output()

    def r_base_set(self, arc_name, role, arcrole):
        rt = self.taxonomy.role_types.get(role, None)
        self.init_output(rt.definition if rt else 'Hierarchy Report')
        self.add(f'<hr/>Arc name: {arc_name}<br/>Arc role: {arcrole}<br/>Role: {role}<br/>')
        nodes = self.taxonomy.get_bs_members(arc_name, role, arcrole)
        self.add(f'Number of nodes: {len(nodes)}<br/>Max hierarchy depth: {max([n.Level for n in nodes])}')
        self.init_table(['Concept/QName'])
        for n in nodes:
            self.add(f'<tr><td>'
                     f'<div style="text-indent: {n.Level*20};">{n.Concept.get_label()}</div>'
                     f'<div style="text-indent: {n.Level*20};"><tt>{n.Concept.qname}</tt></div>'
                     f'</td></tr>')
        self.finalize_table()
        self.finalize_output()

    def r_concept(self, c):
        self.add(f'<br/><h4>{c.qname}</h4>')
        self.init_table()

        self.add('<tr><td>Properties</br/>')
        self.init_table(['property', 'value'])
        props = {'Name':c.name, 'Namespace':c.namespace,
                 'Prefix':c.prefix, 'Data Type':c.data_type,
                 'Substitution Group':c.substitution_group, 'Balance':c.balance,
                 'Nillable':c.nillable, 'Abstract':c.abstract}
        for cap, val in props.items():
            self.add(f'<tr><td>{cap}</td><td>{val}</td></tr>')
        self.add('</td></tr>')
        self.finalize_table()

        lbls = c.resources.get('label', None)
        if lbls is not None:
            self.add('<tr><td>Labels</br/>')
            self.init_table(['text', 'lang', 'role'])
            for k, llist in lbls.items():
                for lbl in llist:
                    self.add(f'<tr><td>{lbl.text}</td><td>{lbl.lang}</td><td>{lbl.role}</td></tr>')
            self.finalize_table()
            self.add('</td></tr>')

        refs = c.resources.get('reference', None)
        if refs is not None:
            self.add('<tr><td>References</br/>')
            self.init_table(['name', 'value', 'role'])
            for k, reflist in refs.items():
                for ref in reflist:
                    if ref.origin is None:
                        continue
                    for r in ref.origin.iterchildren():
                        self.add(f'<tr><td>{(r.tag[r.tag.find("}")+1:])}</td><td>{r.text}</td><td>{ref.role}</td></tr>')

            self.finalize_table()
            self.add('</td></tr>')

        self.finalize_table()

    def r_concepts(self, concepts):
        self.init_output()
        for c in concepts:
            self.r_concept(c)
        self.finalize_output()

    def r_package(self, tp):
        if not tp.files:
            tp.compile()

        """ Creates a report for the content of a taxonomy package.
        [tp] is the taxonomy package to be reported. """
        self.init_output('Taxonomy Package', {'td': 'vertical-align: top;'})

        self.add('<h2>Properties</h2>')
        self.init_table(['Property', 'Value'])
        for prop, value in tp.properties.items():
            self.add(f'<tr><th>{prop}</th><td>{value}</td></tr>')
        self.add(f'<tr><th>Number of files</th><td>{len(tp.files)}</td></tr>')
        folders = set([url[:url.rfind('/')+1] for url in tp.files])
        self.add(f'<tr><th>Number of folders</th><td>{len(folders)}</td></tr>')
        self.finalize_table()

        self.add('<h2>Entry points</h2>')
        self.init_table(['Code', 'Description', 'URL(s)'])
        for ep in tp.entrypoints:
            self.add(f'<tr><td>{ep.Name}</td><td>{ep.Description}</td><td>{"<br/>".join(ep.Urls)}</td></tr>')
        self.finalize_table()

        self.add('<h2>Redirects</h2>')
        self.init_table(['Start string', 'Rewrite prefix'])
        for start_string, rewrite_prefix in tp.redirects.items():
            self.add(f'<tr><td>{start_string}</td><td>{rewrite_prefix}</td></tr>')
        self.finalize_table()

        if tp.superseded_packages:
            self.add('<h2>Superseded Packages</h2>')
            self.init_table()
            self.add('<tr><td>', '</td></tr><tr><td>'.join(tp.superseded_packages), '</td></tr>')
            self.finalize_table()
        self.finalize_output()
