import urllib.request
from lxml import etree as lxml
from xbrl import ebase


class XmlFileBase(ebase.XmlElementBase):
    def __init__(self, location=None, container_pool=None, parsers=None):
        if parsers is None:
            parsers = {}
        self.pool = container_pool
        self.location = location
        self.base = location.replace('\\', '/')[:location.rfind("/")]
        self.namespaces = {}  # Key is the prefix and value is the URI
        self.namespaces_reverse = {}  # Key is the UrI and value is the prefix
        if self.location is None:
            return  # Nothing to load
        filename = self.location
        if self.pool is not None and self.pool.resolver is not None:
            filename = self.pool.resolver.cache(self.location)
        elif self.location.startswith('http://') or self.location.startswith('https://'):
            filename, headers = urllib.request.urlretrieve(self.location)
        dom = lxml.parse(filename)
        root = dom.getroot()
        self.l_root(root)
        super().__init__(root, parsers)

    def l_root(self, e):
        for prefix in filter(lambda x: x is not None, e.nsmap):
            uri = e.nsmap[prefix]
            self.namespaces[prefix] = uri
            self.namespaces_reverse[uri] = prefix
