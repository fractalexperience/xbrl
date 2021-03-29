import os
import zipfile
from lxml import etree as lxml
from xbrl.base import const, resolver, util


class TaxonomyPackage:
    """ Implements taxonomy package functionality """
    def __init__(self, location, cache_folder=None):
        self.cache_folder = cache_folder if cache_folder else '../cache'
        self.archive = None
        self.location = location
        if location.startswith('http'):
            # Downlaod the taxonomy package and save in the cache folder
            cache_manager = resolver.Resolver(os.path.join(self.cache_folder, 'taxonomies'))
            self.location = cache_manager.cache(location)
        """ Entry points is a list of tuples with following structure: (prefix, location, description) """
        self.entrypoints = []
        """ Key is element name, value is element text. """
        self.properties = {}
        self.files = None
        self.redirects = {}
        if not os.path.exists(self.location):
            return
        self.archive = zipfile.ZipFile(self.location)
        self.init()

    def __del__(self):
        if self.archive:
            self.archive.close()

    def init(self):
        zil = self.archive.infolist()
        package_file = [f for f in zil if f.filename.endswith('META-INF/taxonomyPackage.xml')][0]
        with self.archive.open(package_file) as zf:
            package = lxml.XML(zf.read())
            for e in package.iterchildren():
                if e.tag == f'{{{const.NS_TAXONOMY_PACKAGE}}}entryPoints'\
                            or e.tag == f'{{{const.NS_TAXONOMY_PACKAGE_PR}}}entryPoints':
                    self.l_entrypoints(e)
                elif not len(e):  # second level
                    name = util.get_local_name(str(e.tag))
                    self.properties[name] = e.text
        catalog_file = [f for f in zil if f.filename.endswith('META-INF/catalog.xml')][0]
        with self.archive.open(catalog_file) as cf:
            catalog = lxml.XML(cf.read())
            self.l_redirects(catalog)

    def get_url(self, url):
        """ Reads the binary content of a file addressed by a URL. """
        if not self.files:
            self.compile()
        key = self.files.get(url)
        if not key:
            return None
        with self.archive.open(key) as f:
            return f.read()

    def compile(self):
        self.files = {}
        zip_infos = self.archive.infolist()
        # Index files by calculating effective URL based on catalog
        root = zip_infos[0].filename.split('/')[0]
        for fn in [zi.filename for zi in zip_infos if not zi.is_dir()]:
            f1 = fn.replace(root, '..')
            for redirect in self.redirects.items():
                if f1.startswith(redirect[1]):
                    url = f1.replace(redirect[1], redirect[0])
                    self.files[url] = fn

    def l_redirects(self, ce):
        for e in ce.iterchildren():
            if e.tag != f'{{{const.NS_OASIS_CATALOG}}}rewriteURI':
                continue
            url = e.attrib.get('uriStartString')
            redirect = e.attrib.get('rewritePrefix')
            self.redirects[url] = redirect

    def l_entrypoints(self, ep):
        for e in ep.iterchildren():
            if e.tag == f'{{{const.NS_TAXONOMY_PACKAGE}}}entryPoint':
                prefix = None
                ep = None
                desc = None
                for e2 in e.iterchildren():
                    if e2.tag == f'{{{const.NS_TAXONOMY_PACKAGE}}}entryPointDocument':
                        ep = e2.attrib.get('href')
                    elif e2.tag == f'{{{const.NS_TAXONOMY_PACKAGE}}}name':
                        prefix = e2.text
                    elif e2.tag == f'{{{const.NS_TAXONOMY_PACKAGE}}}description':
                        desc = e2.text
                self.entrypoints.append((prefix, ep, desc))

    def info(self):
        o = ['Properties', '----------']
        for p in self.properties.items():
            o.append(f'{p[0]}: {p[1]}')
        o.append('\nEntry points')
        o.append('------------')
        for ep in self.entrypoints:
            o.append(f'{ep[0]}, {ep[1]}, {ep[2]}')
        o.append('\nRedirects')
        o.append('---------')
        for rd in self.redirects.items():
            o.append(f'{rd[0]} => {rd[1]}')
        return '\n'.join(o)
