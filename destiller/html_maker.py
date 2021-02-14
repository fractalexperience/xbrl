from destiller import weaver


class HtmlMaker:
    def __init__(self, data_pool):
        render_methods = {
            'node': self.r_concept,
            'base_set': self.r_base_set
        }
        self.weaver = weaver.Weaver(data_pool, render_methods)

    @staticmethod
    def r_concept(concept, level):
        lbl = concept.get_label()
        print(f'<tr>'
              f'<td style="text-indent: {level * 10}">{lbl.text}<br/><small><tt>{concept.qname}</tt></small></td>'
              f'</tr>')

    def r_base_set(self, bs, level):
        print(f'<tr><td>{bs[0]}</td></tr>')