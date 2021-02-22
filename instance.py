from xbrl import const
from xbrl import fbase
from xbrl import context
from xbrl import unit
from xbrl import fact
from xbrl import locator
from xbrl import footnote
from xbrl import arc


class Instance(fbase.XmlFileBase):
    def __init__(self, location=None, container_pool=None):
        self.linkbase_refs = []
        self.schema_refs = []
        self.contexts = {}
        self.units = {}
        self.facts = {}
        self.footnotes = {}
        self.footnote_links = []
        self.locators = {}
        self.arcs = []
        self.filing_indicators = []
        self.pool = container_pool
        self.taxonomy = None
        self.parsers = {
            'default': self.load_fact,
            f'{{{const.NS_XHTML}}}html': self.load_ixbrl,
            f'{{{const.NS_XBRLI}}}xbrl': self.load_xbrl,
            f'{{{const.NS_XBRLI}}}context': self.load_context,
            f'{{{const.NS_XBRLI}}}unit': self.load_unit,
            f'{{{const.NS_LINK}}}schemaRef': self.load_schema_ref,
            f'{{{const.NS_LINK}}}linkbaseRef': self.load_linkbase_ref,
            f'{{{const.NS_LINK}}}footnoteLink': self.load_footnote_link,
            f'{{{const.NS_LINK}}}footnote': self.load_footnote,
            f'{{{const.NS_LINK}}}loc': self.load_locator,
            f'{{{const.NS_LINK}}}footnoteArc': self.load_arc,
            f'{{{const.NS_FIND}}}fIndicators': self.load_filing_indicators,
            f'{{{const.NS_FIND}}}filingIndicator': self.load_filing_indicator
        }
        if location is not None:
            self.location = location
            super().__init__(location, container_pool, self.parsers)
            self.compile()

    def load_xbrl(self, e):
        self.l_children(e)

    def load_ixbrl(self, e):
        pass

    def load_schema_ref(self, e):
        href = e.attrib.get('{http://www.w3.org/1999/xlink}href')
        self.schema_refs.append(href)

    def load_linkbase_ref(self, e):
        href = e.attrib.get('{http://www.w3.org/1999/xlink}href')
        self.linkbase_refs.append(href)

    def load_context(self, e):
        ctx = context.Context(e)
        self.contexts[ctx.id] = ctx

    def load_unit(self, e):
        uni = unit.Unit(e)
        self.units[uni.id] = uni

    def load_fact(self, e):
        fct = fact.Fact(len(self.facts) + 1, e)
        self.facts[fct.id] = fct

    def load_footnote(self, e):
        fn = footnote.Footnote(e)
        self.footnotes[fn.xlabel] = fn

    def load_locator(self, e):
        loc = locator.Locator(e)
        self.locators[loc.label] = loc

    def load_arc(self, e):
        a = arc.Arc(e)
        self.arcs.append(a)

    def load_footnote_link(self, e):
        self.footnote_links.append(e)

    def load_filing_indicators(self, e):
        self.l_children(e)

    def load_filing_indicator(self, e):
        self.filing_indicators.append(e)

    def compile(self):
        # Set references to contexts
        for fid in self.facts:
            fct = self.facts.get(fid)
            if fct.context_ref is not None:
                ctx = self.contexts.get(fct.context_ref)
                if ctx is not None:
                    fct.context = ctx
            if fct.unit_ref is not None:
                uni = self.units.get(fct.unit_ref)
                if uni is not None:
                    fct.unit = uni
        # Set links between facts and footnotes
        for footnote_link in self.footnote_links:
            self.locators = {}
            self.arcs = []
            self.l_children(footnote_link)
        # Traversing arcs
        for a in self.arcs:
            loc = self.locators.get(a.xl_from)
            if loc is None:
                continue
            fct = self.facts.get(loc.fragment_identifier)
            fn = self.footnotes.get(a.xl_to)
            if fct is None or fn is None:
                continue
            fct.footnotes.append(fn)
            fn.facts.append(fct)
        self.locators = None
        self.arcs = None

    def info(self):
        return f'''Namespaces: {len(self.namespaces)}
Schema references: {len(self.schema_refs)}
Linkbase references: {len(self.linkbase_refs)}
Contexts: {len(self.contexts)}
Units: {len(self.units)}
Facts: {len(self.facts)}
Footnotes: {len(self.footnotes)}
Filing Indicators: {len(self.filing_indicators)}
'''


