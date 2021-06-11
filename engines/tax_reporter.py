from xbrl.engines import html_helper


class TaxonomyReporter(html_helper.HtmlHelper):
    def __init__(self, t=None, d=None):
        self.taxonomy = t
        self.document = d
        super().__init__()

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
