class HtmlHelper:
    """ Minimalistic utility to create HTML renders. """
    def __init__(self):
        self.title = None
        self.styles = None
        self.content = []
        # self.add_header()

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

    def init_table(self, columns=None, cls=None, attributes=None, cls_head=None, cls_body=None):
        if attributes is None:
            attributes = {'border': '1', 'cellspacing':'0', 'cellpadding': '3'}
        snip = ''.join(f'{k}="{v}" ' for k, v in attributes.items())
        self.content.append(f'<table {snip} class="{cls}">')
        self.add_th(columns, cls_head)
        cls_body_str ='' if cls_body is None else f' class="{cls_body}"'
        self.add(f'<tbody{cls_body_str}>')

    def add_th(self, columns, cls=None):
        if columns is None:
            return
        cls_str = '' if cls is None else f' class="{cls}"'
        self.add(f'<thead{cls_str}><tr><th>{"</th><th>".join(columns)}</th></tr></thead>')

    def add(self, *s):
        for tok in s:
            if not tok:
                continue
            if isinstance(tok, str):
                self.content.append(tok)
                continue
            self.content.append(''.join([t for t in tok if t is not None]))

    def add_tr(self, *s):
        self.add('<tr>')
        for tok in s:
            if tok is None:
                self.add('<td>&nbsp;</td>')
                continue
            if isinstance(tok, str):
                if tok.startswith('<td'):
                    self.add(tok)
                    continue
                self.add(f'<td>{tok}</td>')
                continue
            self.add('<td>', '</td><td>'.join([t if t is not None else '&nbsp;' for t in tok]), '</td>')
        self.add('</tr>')

    def finalize_table(self):
        self.content.append('</tbody></table>')

    def finalize_output(self):
        self.content.append('</body></html>')

    def save_as(self, filename):
        with open(filename, 'wt', encoding="utf-8") as f:
            f.write('\n'.join(self.content))
