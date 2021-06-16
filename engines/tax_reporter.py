from xbrl.engines import html_helper
from lxml import etree as lxml


class TaxonomyReporter(html_helper.HtmlHelper):
    def __init__(self, t=None, d=None):
        self.taxonomy = t
        self.document = d
        super().__init__()

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
