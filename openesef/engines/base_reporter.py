from openesef.engines import html_helper


class BaseReporter(html_helper.HtmlHelper):
    def __init__(self, t, d):
        super().__init__()
        self.taxonomy = t
        self.document = d
