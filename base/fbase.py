import urllib.request, os
from lxml import etree as lxml
from xbrl.base import ebase, util, const


class XmlFileBase(ebase.XmlElementBase):
    def __init__(self, location=None, container_pool=None, parsers=None, root=None):
        if parsers is None:
            parsers = {}
        self.pool = container_pool
        self.namespaces = {}  # Key is the prefix and value is the URI
        self.namespaces_reverse = {}  # Key is the UrI and value is the prefix
        self.schema_location_parts = {}
        self.base = ''
        if location:
            self.location = util.reduce_url(location)
            # self.base = self.location.replace('\\', '/')[:location.rfind("/")]
            self.base = os.path.split(location)[0]
            if root is None:  # Only parsing file again the root element is not explicitly passed
                root = self.get_root()
        if root is None:
            return
        # Predefined
        self.namespaces['xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        self.namespaces_reverse['http://www.w3.org/2001/XMLSchema-instance'] = 'xsi'
        self.l_namespaces(root)
        self.l_schema_location(root)
        super().__init__(root, parsers)

    def get_root(self):
        """ If the location can be found in an open package, then extract it from the package """
        url = self.location
        if self.pool and self.pool.packaged_locations:
            t = self.pool.packaged_locations.get(url)
            if t:
                pck = t[0]
                content = pck.get_url(url)
                p = lxml.XMLParser(huge_tree=True)
                try:
                    return lxml.XML(content, parser=p)
                except Exception:
                    s = content.decode('utf-8')
                    s = s.replace('\n', '')  # Try to correct eventually broken lines
                    root = lxml.XML(bytes(s, encoding='utf-8'), parser=p)
                    return root
        filename = url
        if self.pool:
            filename = self.pool.cache(url)
        elif url.startswith('http://') or url.startswith('https://'):
            filename, headers = urllib.request.urlretrieve(url)
        dom = lxml.parse(filename)
        return dom.getroot()

    def l_schema_location(self, e):
        sl = e.attrib.get(f'{{{const.NS_XSI}}}schemaLocation')
        if not sl:
            return
        parts = util.normalize(sl).split(' ')
        cnt = -1
        odds = []
        evens = []
        for p in parts:
            cnt += 1
            if cnt % 2:
                evens.append(p)
            else:
                odds.append(p)
        self.schema_location_parts = dict(zip(odds, evens))

    def l_namespaces(self, e):
        for prefix in filter(lambda x: x is not None, e.nsmap):
            uri = e.nsmap[prefix]
            self.namespaces[prefix] = uri
            self.namespaces_reverse[uri] = prefix

    def l_namespaces_rec(self, e, target_tags=None):
        if not isinstance(e, lxml._Element):
            return
        if target_tags is None or e.tag in target_tags:
            self.l_namespaces(e)
        for e2 in e.iterchildren():
            self.l_namespaces_rec(e2)
