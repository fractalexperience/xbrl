from lxml import etree as lxml
from xbrl import const


class XmlElementBase:
    def __init__(self, e, parsers=None):
        if parsers is None:
            parsers = {}
        tag = str(e.tag)
        self.name = tag[tag.find('}')+1:]
        self.prefix = e.prefix
        self.qname = f'{self.prefix}:{self.name}'
        self.namespace = tag[1:tag.find('}')]
        fid = e.attrib.get('id')
        if fid is not None:
            self.id = fid
        self.lang = None if e is None else e.attrib.get(f'{{{const.NS_XML}}}lang')
        self.parsers = parsers
        self.load(e)

    def load(self, e):
        if isinstance(e, lxml._Comment):
            return
        method = self.parsers.get(e.tag)
        if method is None:
            self.l_default(e)
        else:
            method(e)

    def l_children(self, e):
        for e2 in e.iterchildren():
            self.load(e2)

    def l_default(self, e):
        default_method = self.parsers.get('default')
        if default_method is not None:
            default_method(e)
