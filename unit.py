from xbrl import ebase, const


class Unit(ebase.XmlElementBase):
    def __init__(self, e):
        self.measure = []
        self.numerator = []
        self.denominator = []
        self.active_measure_list = self.measure
        parsers = {
            f'{{{const.NS_XBRLI}}}measure': self.l_measure,
            f'{{{const.NS_XBRLI}}}divide': self.l_divide,
            f'{{{const.NS_XBRLI}}}unitNumerator': self.l_numerator,
            f'{{{const.NS_XBRLI}}}unitDenominator': self.l_denominator
        }
        super().__init__(e, parsers)

    def l_measure(self, e):
        self.active_measure_list.append(e)

    def l_numerator(self, e):
        self.active_measure_list = self.numerator
        self.l_children(e)

    def l_denominator(self, e):
        self.active_measure_list = self.denominator
        self.l_children(e)

    def l_divide(self, e):
        self.l_children(e)

    def get_aspect_value(self):
        if self.measure:
            return ','.join([m.text for m in self.measure])
        else:
            num = ','.join(m.text for m in self.numerator)
            den = ','.join(m.text for m in self.denominator)
            return f'{num}/{den}'
