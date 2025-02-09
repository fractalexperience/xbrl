import os
import zipfile
from lxml import etree as lxml
from openesef.base import const, resolver, util, data_wrappers


import logging

# Get a logger.  __name__ is a good default name.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# # Check if handlers already exist and clear them to avoid duplicates.
# if logger.hasHandlers():
#     logger.handlers.clear()

# # Create a handler for console output.
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)

# # Create a formatter.
# log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# formatter = logging.Formatter(log_format)

# # Set the formatter on the handler.
# handler.setFormatter(formatter)

# # Add the handler to the logger.
# logger.addHandler(handler)


class TaxonomyPackage(resolver.Resolver):
    """ Implements taxonomy package functionality """
    def __init__(self, location=None, cache_folder=None, output_folder=None, archive=None, esef_filing_root=None):
        super().__init__(cache_folder, output_folder)
        self.archive = archive
        self.location = location
        self.esef_filing_root = esef_filing_root
        if self.location and self.location.startswith('http'):
            # Download the taxonomy package and save in the cache folder
            self.location = self.cache(location)
        """ Entry points is a list of tuples with following structure: (prefix, location, description) """
        self.entrypoints = []
        """ Key is element name, value is element text. """
        self.properties = {}
        """ List of superseded packages, each represented by ts URL. """
        self.superseded_packages = []
        """ List of XBRL reports included in the package """
        self.reports = []
        self.files = None
        self.redirects = {}
        self.redirects_reduced = None
        self.catalog_location = None
        if self.location and os.path.exists(self.location):
            self.archive = zipfile.ZipFile(self.location)
            self.init()

    def __del__(self):
        if self.archive:
            self.archive.close()

    def init(self):
        zil = self.archive.infolist()
        package_files = [f for f in zil if f.filename.endswith('META-INF/taxonomyPackage.xml')]
        if len(package_files) == 0:
            return
        package_file = package_files[0]
        with self.archive.open(package_file) as zf:
            package = lxml.XML(zf.read())
            for e in package.iterchildren():
                if str(e.tag).endswith('entryPoints'):
                    self.l_entrypoints(e)
                elif str(e.tag).endswith('supersededTaxonomyPackages'):
                    self.l_superseded(e)
                elif not len(e):  # second level
                    name = util.get_local_name(str(e.tag))
                    self.properties[name] = e.text
        zi_catalog = [f for f in zil if f.filename.endswith('META-INF/catalog.xml')][0]
        self.catalog_location = os.path.dirname(zi_catalog.filename)
        with self.archive.open(zi_catalog) as cf:
            catalog = lxml.XML(cf.read())
            self.l_redirects(catalog)
        self.reports = [f for f in zil if '/reports/' in f.filename]

    def get_url(self, url):
        """ Reads the binary content of a file addressed by a URL. """
        if not self.files:
            self.compile()
        logger.debug(f"Trying to get URL: {url}")    
        file_path = self.files.get(url)
        if not file_path:
            return None
        if self.archive is not None:
            try:
                with self.archive.open(file_path) as f:
                    return f.read()
            except KeyError:
                # Handle cases where the file is not directly in the archive
                # but within a subdirectory specified by 
                logger.debug(f"File not found in archive: {url}")
                if self.esef_filing_root:
                    resolved_path = os.path.join(self.esef_filing_root, url)
                    if os.path.exists(resolved_path):
                        with open(resolved_path, 'rb') as f:
                            return f.read()
                return None  # Or raise an exception if appropriate
        return bytes(file_path, encoding='utf-8')

    def get_hash(self):
        return util.get_hash(self.location)

    def compile(self):
        self.files = {}
        if not self.archive:
            return        
        zip_infos = self.archive.infolist()
        if not zip_infos:
            return
        # Index files by calculating effective URL based on catalog
        root = zip_infos[0].filename.split('/')[0]  # Root of the archive file
        # Add files from esef_filing_root if provided
        if self.esef_filing_root:
            for root, _, files in os.walk(self.esef_filing_root):
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), self.esef_filing_root)
                    self.files[file_path] = file_path

        for fn in [zi.filename for zi in zip_infos if not zi.is_dir()]:
            matched_redirects = [(u, r) for u, r in self.redirects_reduced.items() if fn.startswith(r)]

            self.files[fn] = fn
            if not matched_redirects:
                # self.files[fn] = fn
                continue


            file_root = matched_redirects[0][1]
            rewrite_prefix = matched_redirects[0][0]
            url = fn.replace(file_root, rewrite_prefix)
            self.files[url] = fn

    def l_redirects(self, ce):
        for e in ce.iterchildren():
            if e.tag != f'{{{const.NS_OASIS_CATALOG}}}rewriteURI':
                continue
            url = e.attrib.get('uriStartString')
            rewrite_prefix = e.attrib.get('rewritePrefix')
            self.redirects[url] = rewrite_prefix
        # Reduce redirects according to position of catalog.xml
        self.redirects_reduced = dict([(u, util.reduce_url(os.path.join(self.catalog_location, r)))
                                       for u, r in self.redirects.items()])

    def l_entrypoints(self, ep):
        for e in ep.iterchildren():
            if str(e.tag).endswith('entryPoint'):
                prefix = None
                ep = []
                desc = None
                for e2 in e.iterchildren():
                    if str(e2.tag).endswith('entryPointDocument'):
                        href = e2.attrib.get('href')
                        ep.append(href)
                    elif str(e2.tag).endswith('name'):
                        prefix = e2.text
                    elif str(e2.tag).endswith('description'):
                        desc = e2.text
                self.entrypoints.append(data_wrappers.EntryPoint(prefix, ep, desc, util.get_hash(''.join(ep))))

    def l_superseded(self, ep):
        for e in ep.iterchildren():
            if str(e.tag).endswith('taxonomyPackageRef'):
                self.superseded_packages.append(e.text)

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        o = ['Properties', '----------']
        for prop, value in self.properties.items():
            o.append(f'{prop}: {value}')
        o.append('\nEntry points')
        o.append('------------')
        for ep in self.entrypoints:
            o.append(f'{ep.Name}, {",".join(ep.Urls)}, {ep.Description}')
        o.append('\nRedirects\n---------')
        for start_string, rewrite_prefix in self.redirects.items():
            o.append(f'{start_string} => {rewrite_prefix}')
        if self.superseded_packages:
            o.append('\nSuperseded Packages\n-------------------')
            o.append('\n'.join(self.superseded_packages))
        return '\n'.join(o)
