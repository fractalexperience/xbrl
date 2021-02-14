from destiller import weaver


class HtmlMaker:
    def __init__(self, data_pool):
        self.handlers = {
            'concept': self.r_concept,
            'concepts': self.r_concepts,
            'base_set': self.r_base_set,
            'base_sets': self.r_base_sets
        }
        self.weaver = weaver.Weaver(data_pool, self.handlers)

    def render(self, name):
        render_method = self.handlers.get(name)
        if not render_method:
            return
        render_method()

    def r_base_sets(self):
        self.html_header('Base Sets')
        print('<table border="1" cellspacing="0" cellpadding="3">')
        self.weaver.loop_base_sets()
        print('</table>')
        self.html_footer()

    def r_concepts(self):
        self.html_header('Concepts')
        self.html_footer()

    @staticmethod
    def html_header(title):
        print('<html>')
        print('<body>')

    @staticmethod
    def html_footer():
        print('</body>')
        print('</html>')

    @staticmethod
    def r_concept(concept, level):
        lbl = concept.get_label()
        print(f'<tr>'
              f'<td style="text-indent: {level * 10}">{concept.qname if not lbl else lbl.text}</td>'
              f'</tr>')

    @staticmethod
    def r_base_set(bs, level):
        parts = bs[0].split('|')
        print(f'<tr style="color: White; background-color: Navy;"><td>'
              f'{parts[0]}<br/>'
              f'{parts[1]}<br/>'
              f'{parts[2]}</td></tr>')