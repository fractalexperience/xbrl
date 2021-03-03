import os
import zipfile
from lxml import etree as lxml
from xbrl import const, util


class TaxonomyPackage:
    """ Implements taxonomy package functionality """
    def __init__(self, location):
        self.location = location
        if not os.path.exists(location):
            return
        """ Entry points is a list of tuples with following structure: (prefix, location, description) """
        self.entrypoints = []
        """ Key is element name, value is element text. """
        self.properties = {}
        self.files = {}
        self.redirects = {}
        with zipfile.ZipFile(location) as z:
            zil = z.infolist()
            package_file = [f for f in zil if f.filename.endswith('META-INF/taxonomyPackage.xml')][0]
            with z.open(package_file) as zf:
                package = lxml.XML(zf.read())
                for e in package.iterchildren():
                    if e.tag == f'{{{const.NS_TAXONOMY_PACKAGE}}}entryPoints':
                        self.l_entrypoints(e)
                    elif not len(e):  # second level
                        name = util.get_local_name(str(e.tag))
                        self.properties[name] = e.text
            catalog_file = [f for f in zil if f.filename.endswith('META-INF/catalog.xml')][0]
            with z.open(catalog_file) as cf:
                catalog = lxml.XML(cf.read())
                self.l_redirects(catalog)
            self.compile(zil)

    def compile(self, zip_infos):
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
        o = []
        o.append('Properties')
        o.append('----------')
        for p in self.properties.items():
            o.append(f'{p[0]}: {p[1]}')
        o.append('Entry points')
        o.append('------------')
        for ep in self.entrypoints:
            o.append(f'{ep[0]}, {ep[1]}, {ep[2]}')
        o.append('Redirects')
        o.append('---------')
        for rd in self.redirects.items():
            o.append(f'{rd[0]} => {rd[1]}')
        return '\n'.join(o)