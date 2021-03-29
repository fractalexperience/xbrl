import urllib.request
from lxml import etree as lxml
from xbrl.base import ebase, util


class XmlFileBase(ebase.XmlElementBase):
    def __init__(self, location=None, container_pool=None, parsers=None, root=None):
        if parsers is None:
            parsers = {}
        self.pool = container_pool
        self.namespaces = {}  # Key is the prefix and value is the URI
        self.namespaces_reverse = {}  # Key is the UrI and value is the prefix
        if location:  # Loading from a location is prioritized
            self.location = util.reduce_url(location)
            self.base = self.location.replace('\\', '/')[:location.rfind("/")]
            root = self.get_root()
        if root is None:
            return
        self.l_namespaces(root)
        super().__init__(root, parsers)

    def get_root(self):
        """ If the location can be found in an open package, then extract it from the package """
        url = self.location
        if self.pool and self.pool.packaged_locations:
            t = self.pool.packaged_locations.get(url)
            if t:
                pck = t[0]
                content = pck.get_url(url)
                return lxml.XML(content)
        """ If there is a resolver, download and cache the resource and load it. """
        filename = url
        if self.pool and self.pool.resolver:
            filename = self.pool.resolver.cache(url)
        elif url.startswith('http://') or url.startswith('https://'):
            filename, headers = urllib.request.urlretrieve(url)
        dom = lxml.parse(filename)
        return dom.getroot()

    def l_namespaces(self, e):
        for prefix in filter(lambda x: x is not None, e.nsmap):
            uri = e.nsmap[prefix]
            self.namespaces[prefix] = uri
            self.namespaces_reverse[uri] = prefix

    def l_namespaces_rec(self, e):
        if not isinstance(e, lxml._Element):
            return
        self.l_namespaces(e)
        for e2 in e.iterchildren():
            self.l_namespaces_rec(e2)
