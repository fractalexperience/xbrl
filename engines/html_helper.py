class HtmlHelper:
    """ Minimalistic utility to create HTML renders. """
    def __init__(self):
        self.title = None
        self.styles = None
        self.content = []
        self.add_header()

    def init_output(self, title=None, styles=None):
        self.content = []
        self.title = title
        self.styles = styles
        self.add_header()

    def add_header(self):
        self.content.append('<html><head><meta charset="utf-8"/>')
        if self.title is not None:
            self.content.append(f'<title>{self.title}</title>')
        if self.styles is not None:
            for kwd, sty in self.styles.items():
                self.content.append(f'<style>{kwd} {{{sty}}}</style>')
        self.content.append('</head>')
        self.content.append('<body>')
        if self.title is not None:
            self.content.append(f'<h1>{self.title}</h1>')

    def init_table(self, columns=None):
        self.content.append('<table border="1" cellspacing="0" cellpadding="5">')
        if columns is None:
            return
        self.content.append('<tr>')
        for c in columns:
            self.content.append(f'<th>{c}</th>')
        self.content.append('</tr>')

    def add(self, *s):
        for tok in s:
            if isinstance(tok, str):
                self.content.append(tok)
                continue
            self.content.append(''.join(tok))

    def finalize_table(self):
        self.content.append('</table>')

    def finalize_output(self):
        self.content.append('</body></html>')

    def save_as(self, filename):
        with open(filename, 'wt', encoding="utf-8") as f:
            f.write('\n'.join(self.content))