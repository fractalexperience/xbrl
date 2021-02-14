from xbrl import ebase


class Unit(ebase.XmlElementBase):
    def __init__(self, e):
        self.measure = []
        self.numerator = []
        self.denominator = []
        self.active_measure_list = self.measure
        parsers = {
            '{http://www.xbrl.org/2003/instance}measure': self.load_measure,
            '{http://www.xbrl.org/2003/instance}divide': self.load_divide,
            '{http://www.xbrl.org/2003/instance}unitNumerator': self.load_numerator,
            '{http://www.xbrl.org/2003/instance}unitDenominator': self.load_denominator
        }
        super().__init__(e, parsers)

    def load_measure(self, e):
        self.active_measure_list.append(e)

    def load_numerator(self, e):
        self.active_measure_list = self.numerator
        self.l_children(e)

    def load_denominator(self, e):
        self.active_measure_list = self.denominator
        self.l_children(e)

    def load_divide(self, e):
        self.l_children(e)

    def get_aspect_value(self):
        if self.measure:
            return ",".join([m.text for m in self.measure])
        else:
            num = ",".join(m.text for m in self.numerator)
            den = ",".join(m.text for m in self.denominator)
            return f'{num}/{den}'
