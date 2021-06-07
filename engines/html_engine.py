class HtmlEngine():
    """ Minimalistic utility to create HTML renders. """
    def __init__(self, title=None):
        self.title = title
        self.output = []

    def add_header(self):
        self.output.append('<html><head><meta charset="utf-8"/>')
        if self.title is not None:
            self.output.append(f'<title>{self.title}</title>')
        self.output.append('<style>th {color: #ffffa0; background-color: Navy; border-color: Silver; text-align: center;}</style>')
        self.output.append('</head>')
        self.output.append('<body>')
        if self.title is not None:
            self.output.append(f'<h1>{self.title}</h1>')

    def add_table(self, columns=None):
        self.output.append('<table border="1" cellspacing="0" cellpadding="5">')
        if columns is None:
            return
        self.output.append('<tr>')
        for c in columns:
            self.output.append(f'<th>{c}</th>')
        self.output.append('</tr>')

    def add(self, *s):
        for tok in s:
            if isinstance(tok, str):
                self.output.append(tok)
                continue
            self.output.append(''.join(tok))

    def finalize_table(self):
        self.output.append('</table>')

    def finalize(self):
        self.output.append('</body></html>')

    def save(self, filename):
        with open(filename, 'wt') as f:
            f.write('\n'.join(self.output))
