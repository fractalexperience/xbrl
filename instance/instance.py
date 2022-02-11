from xbrl.instance import m_xbrl
from xbrl.base import fbase, const
from xbrl.ixbrl import m_ixbrl
from lxml import etree as lxml


class Instance(fbase.XmlFileBase):
    def __init__(self, location=None, container_pool=None, root=None):
        self.pool = container_pool
        self.taxonomy = None
        self.xbrl = None
        self.ixbrl = None
        parsers = {
            f'{{{const.NS_XHTML}}}html': self.l_ixbrl,
            f'{{{const.NS_XBRLI}}}xbrl': self.l_xbrl
        }
        if location:
            self.location = location
        super().__init__(location, container_pool, parsers, root)

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        return f"""Namespaces: {len(self.namespaces)}
Schema references: {len(self.xbrl.schema_refs)}
Linkbase references: {len(self.xbrl.linkbase_refs)}
Contexts: {len(self.xbrl.contexts)}
Units: {len(self.xbrl.units)}
Facts: {len(self.xbrl.facts)}
Footnotes: {len(self.xbrl.footnotes)}
Filing Indicators: {len(self.xbrl.filing_indicators)}"""

    def l_xbrl(self, e):
        self.xbrl = m_xbrl.XbrlModel(e, self)

    def l_ixbrl(self, e):
        self.ixbrl = m_ixbrl.IxbrlModel(e, self)
        # Recursive read all namespaces, because in some cases namespace prefixes
        # are defined deeper in the XML structure.
        self.l_namespaces_rec(e)
        self.ixbrl.strip()
        s = ''.join(self.ixbrl.output)
        parser = lxml.XMLParser(huge_tree=True)
        root = lxml.XML(s, parser)
        self.l_xbrl(root)

    def to_xml(self):
        return self.ixbrl.to_xml() if self.ixbrl else self.xbrl.to_xml() if self.xbrl else None


