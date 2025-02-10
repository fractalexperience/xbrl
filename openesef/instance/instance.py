import os
from ..instance import m_xbrl
from ..base import fbase, const
from ..ixbrl import m_ixbrl
from lxml import etree as lxml


class Instance(fbase.XmlFileBase):
    def __init__(self, location=None, container_pool=None, root=None, esef_filing_root=None):
        self.pool = container_pool
        self.taxonomy = None
        self.xbrl = None
        self.ixbrl = None
        self.esef_filing_root = esef_filing_root
        parsers = {
            f'{{{const.NS_XHTML}}}html': self.l_ixbrl,
            f'{{{const.NS_XBRLI}}}xbrl': self.l_xbrl
        }
        self.location = location

        super().__init__(location, container_pool, parsers, root, esef_filing_root=esef_filing_root)

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
        self.l_namespaces(e)
        # self.l_namespaces_rec(e, target_tags=[
        #     f'{{{const.NS_IXBRL}}}nonNumeric',
        #     f'{{{const.NS_IXBRL}}}nonFraction'])
        self.ixbrl.strip()
        s = ''.join(self.ixbrl.output)
        parser = lxml.XMLParser(huge_tree=True)
        root = lxml.XML(s, parser)
        self.l_xbrl(root)

    def to_xml(self):
        return self.ixbrl.to_xml() if self.ixbrl else self.xbrl.to_xml() if self.xbrl else None


