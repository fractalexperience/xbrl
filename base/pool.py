import os, tempfile, zipfile
from lxml import etree as lxml
from xbrl.base import resolver, util
from xbrl.taxonomy import taxonomy, schema, tpack, linkbase
from xbrl.instance import instance


class Pool(resolver.Resolver):
    def __init__(self, cache_folder=None, output_folder=None):
        super().__init__(cache_folder, output_folder)
        self.taxonomies = {}
        self.discovered = {}
        self.schemas = {}
        self.linkbases = {}
        self.instances = {}
        self.packaged_entrypoints = {}  # Index of all packages in the cache/taxonomy_packages folder by entrypoint
        self.packaged_locations = None
        self.active_packages = {}  # Currently opened taxonomy packages

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        return '\n'.join([
            f'Taxonomies: {len(self.taxonomies)}',
            f'Instance documents: {len(self.instances)}',
            f'Taxonomy schemas: {len(self.schemas)}',
            f'Taxonomy linkbases: {len(self.linkbases)}'])

    def index_packages(self):
        """ Index the content of taxonomy packages found in cache/taxonomies/ """
        package_files = [os.path.join(r, file) for r, d, f in
                         os.walk(self.taxonomies_folder) for file in f if file.endswith('.zip')]
        for pf in package_files:
            pck = tpack.TaxonomyPackage(pf)
            for ep in pck.entrypoints:
                eps = ep.Urls
                for path in eps:
                    self.packaged_entrypoints[path] = pf

    def add_instance_location(self, location, key=None, attach_taxonomy=True):
        xid = instance.Instance(location=location, container_pool=self)
        if key is None:
            key = location
        self.add_instance(xid, key, attach_taxonomy)
        return xid

    def add_instance_archive(self, archive_location, filename, key=None, attach_taxonomy=False):
        if not os.path.exists(archive_location):
            return
        archive = zipfile.ZipFile(archive_location)
        zil = archive.infolist()
        xid_file = [f for f in zil if f.filename.endswith(filename)][0]
        with archive.open(xid_file) as xf:
            root = lxml.XML(xf.read())
            return self.add_instance_element(root, xid_file if key is None else key, attach_taxonomy)

    def add_instance_element(self, e, key=None, attach_taxonomy=False):
        xid = instance.Instance(container_pool=self, root=e)
        if key is None:
            key = e.tag
        self.add_instance(xid, key, attach_taxonomy)
        return xid

    def add_instance(self, xid, key=None, attach_taxonomy=False):
        if key is None:
            key = xid.location_ixbrl
        self.instances[key] = xid
        if attach_taxonomy and xid.xbrl is not None:
            # Ensure that if schema references are relative, the location base for XBRL document is added to them
            entry_points = [e if e.startswith('http') else os.path.join(xid.base, e).replace('\\', '/')
                            for e in xid.xbrl.schema_refs]
            tax = self.add_taxonomy(entry_points)
            xid.taxonomy = tax

    def add_schema(self, location, container_taxonomy):
        sh = schema.Schema(location, self, container_taxonomy)
        self.schemas[location] = sh
        if container_taxonomy is None:
            return
        container_taxonomy.schemas[location] = sh

    def add_taxonomy(self, entry_points):
        ep_list = entry_points if isinstance(entry_points, list) else [entry_points]
        self.packaged_locations = {}
        for ep in ep_list:
            pf = self.packaged_entrypoints.get(ep)
            if not pf:
                continue
            pck = tpack.TaxonomyPackage(pf)
            pck.compile()
            for pf in pck.files.items():
                self.packaged_locations[pf[0]] = (pck, pf[1])  # A tuple
        tax = taxonomy.Taxonomy(ep_list, self)
        key = ','.join(entry_points)
        self.taxonomies[key] = tax
        self.packaged_locations = None
        return tax

    """ Stores a taxonomy package from a Web location to local taxonomy package repository """
    def cache_package(self, location):
        package = tpack.TaxonomyPackage(location, self.taxonomies_folder)
        self.index_packages()
        return package

    """ Adds a taxonomy package provided in the location parameter, creates a taxonomy 
        using all entrypoints in the package and returns the taxonomy object. """
    def add_package(self, location):
        package = self.cache_package(location)
        entry_points = {f for ep in package.entrypoints for f in ep.Urls}
        tax = self.add_taxonomy(entry_points)
        return tax

    def add_reference(self, href, base, tax):
        """ Loads schema or linkbase depending on file type. TO IMPROVE!!! """
        if not href.startswith('http'):
            href = util.reduce_url(os.path.join(base, href).replace(os.path.sep, '/'))
        if href in self.discovered:
            return
        self.discovered[href] = False
        if href.endswith(".xsd"):
            sh = self.schemas.get(href, None)
            if not sh:
                schema.Schema(href, self, tax)
        else:
            lb = self.linkbases.get(href, None)
            if not lb:
                linkbase.Linkbase(href, self, tax)
