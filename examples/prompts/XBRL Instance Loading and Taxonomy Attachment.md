# Q1: Explain to me in detail how `data_pool.add_instance_location(location, attach_taxonomy=True)` calls the next method in pool and the next all the way along. Code: ```import os, zipfile, functools

from lxml import etree as lxml

from xbrl.base import resolver, util

from xbrl.taxonomy import taxonomy, schema, tpack, linkbase

from xbrl.instance import instance

class Pool(resolver.Resolver):

    def __init__(self, cache_folder=None, output_folder=None, alt_locations=None):

        super().__init__(cache_folder, output_folder)

        self.taxonomies = {}

        self.current_taxonomy = None

        self.current_taxonomy_hash = None

        self.discovered = {}

        self.schemas = {}

        self.linkbases = {}

        self.instances = {}

        """ Alternative locations. If set, this is used to resolve Qeb references to alternative (existing) URLs. """

        self.alt_locations = alt_locations

        """ Index of all packages in the cache/taxonomy_packages folder by entrypoint """

        self.packaged_entrypoints = {}

        self.packaged_locations = None

        """ Currently opened taxonomy packages """

        self.active_packages = {}

        """ Currently opened archive, where files can be read from - optional."""

        self.active_file_archive = None

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

            self.index_package(tpack.TaxonomyPackage(pf))

    def index_package(self, package):

        for ep in package.entrypoints:

            eps = ep.Urls

            for path in eps:

                self.packaged_entrypoints[path] = package.location

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

    def add_taxonomy(self, entry_points):

        ep_list = entry_points if isinstance(entry_points, list) else [entry_points]

        # self.packaged_locations = {}

        for ep in ep_list:

            # if self.active_file_archive and ep in self.active_file_archive.namelist():

            #     self.packaged_locations[ep] = (self.active_file_archive, ep)

            # else:

            self.add_packaged_entrypoints(ep)

        key = ','.join(entry_points)

        if key in self.taxonomies:

            return self.taxonomies[key]  # Previously loaded

        taxonomy.Taxonomy(ep_list, self)  # Sets the new taxonomy as current

        self.taxonomies[key] = self.current_taxonomy

        self.packaged_locations = None

        return self.current_taxonomy

    def add_packaged_entrypoints(self, ep):

        pf = self.packaged_entrypoints.get(ep)

        if not pf:

            return  # Not found

        pck = self.active_packages.get(pf, None)

        if pck is None:

            pck = tpack.TaxonomyPackage(pf)

            pck.compile()

        self.index_package_files(pck)

    def index_package_files(self, pck):

        if self.packaged_locations is None:

            self.packaged_locations = {}

        for pf in pck.files.items():

            self.packaged_locations[pf[0]] = (pck, pf[1])  # A tuple

    """ Stores a taxonomy package from a Web location to local taxonomy package repository """

    def cache_package(self, location):

        package = tpack.TaxonomyPackage(location, self.taxonomies_folder)

        self.index_packages()

        return package

    """ Adds a taxonomy package provided in the location parameter, creates a taxonomy 

        using all entrypoints in the package and returns the taxonomy object. """

    def add_package(self, location):

        package = self.cache_package(location)

        self.active_packages[location] = package

        entry_points = [f for ep in package.entrypoints for f in ep.Urls]

        tax = self.add_taxonomy(entry_points)

        return tax

    def add_reference(self, href, base):

        if href is None:

            return

        """ Loads schema or linkbase depending on file type. TO IMPROVE!!! """

        allowed_extensions = ('xsd', 'xml', 'json')

        if not href.split('.')[-1] in allowed_extensions:  # if pairs in

            return

        if 'http://xbrl.org' in href or 'http://www.xbrl.org' in href:

            return  # Basic schema objects are predefined.

        # Artificially replace the reference - only done for very specific purposes.

        if self.alt_locations and href in self.alt_locations:

            href = self.alt_locations[href]

        if not href.startswith('http'):

            href = util.reduce_url(os.path.join(base, href).replace(os.path.sep, '/'))

        key = f'{self.current_taxonomy_hash}_{href}'

        if key in self.discovered:

            return

        self.discovered[key] = False

        # print(href)

        if href.endswith(".xsd"):

            sh = self.schemas.get(href, schema.Schema(href, self))

            self.current_taxonomy.attach_schema(href, sh)

        else:

            lb = self.linkbases.get(href, linkbase.Linkbase(href, self))

            self.current_taxonomy.attach_linkbase(href, lb)

    @staticmethod

    def check_create_path(existing_path, part):

        new_path = os.path.join(existing_path, part)

        if not os.path.exists(new_path):

            os.mkdir(new_path)

        return new_path

    def save_output(self, content, filename):

        if os.path.sep in filename:

            functools.reduce(self.check_create_path, filename.split(os.path.sep)[:-1], self.output_folder)

        location = os.path.join(self.output_folder, filename)

        with open(location, 'wt', encoding="utf-8") as f:

            f.write(content)

if __name__ == "__main__":

    

    esef_filing_root="/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/"

    filename="reports/sap-2022-12-31-DE.xhtml"

    data_pool = Pool(cache_folder="../data/xbrl_cache")

    location = os.path.join(esef_filing_root, filename)

    data_pool.add_instance_location(location, attach_taxonomy=True)

```
Let's break down the execution flow of `data_pool.add_instance_location(location, attach_taxonomy=True)` within the provided code.

1. **`add_instance_location(self, location, key=None, attach_taxonomy=True)`**: This method is called with a `location` (path to the instance document), an optional `key`, and `attach_taxonomy=True`.  It creates an `Instance` object: [1](https://github.com/fractalexperience/xbrl/blob/master/examples/ixbrl_processing/sec_cik_1000177_20-f.py)

   ```python
   xid = instance.Instance(location=location, container_pool=self)
   ```

2. **`instance.Instance(location, container_pool)`**:  The `Instance` constructor (located in the `instance.py` file, not shown in your provided code snippet) parses the instance document at the given `location`. It extracts information like the schema references (`schema_refs`) and the base URL.

3. **Back in `add_instance_location`**:  If no `key` is provided, it defaults to the `location` itself. The method then calls `add_instance` [1](https://github.com/fractalexperience/xbrl/blob/master/examples/ixbrl_processing/sec_cik_1000177_20-f.py):

   ```python
   self.add_instance(xid, key, attach_taxonomy)
   ```

4. **`add_instance(self, xid, key=None, attach_taxonomy=False)`**: This method stores the `Instance` object (`xid`) in the `instances` dictionary using the provided `key`. [1](https://github.com/fractalexperience/xbrl/blob/master/examples/ixbrl_processing/sec_cik_1000177_20-f.py)

5. **Attaching the Taxonomy (Conditional)**: The crucial part is the conditional block that handles taxonomy attachment: [1](https://github.com/fractalexperience/xbrl/blob/master/examples/ixbrl_processing/sec_cik_1000177_20-f.py)

   ```python
   if attach_taxonomy and xid.xbrl is not None:
       # ...
   ```

   Since `attach_taxonomy` is `True` in our initial call, this block is executed if the instance document contains XBRL data (`xid.xbrl` is not `None`).

6. **Processing Schema References**: Inside the conditional block, the code prepares the entry points for the taxonomy: [1](https://github.com/fractalexperience/xbrl/blob/master/examples/ixbrl_processing/sec_cik_1000177_20-f.py)

   ```python
   entry_points = [e if e.startswith('http') else os.path.join(xid.base, e).replace('\\', '/')
                   for e in xid.xbrl.schema_refs]
   tax = self.add_taxonomy(entry_points)
   xid.taxonomy = tax
   ```

   It iterates through the schema references (`xid.xbrl.schema_refs`) extracted from the instance document.  If a reference is relative, it's converted to an absolute URL using the base URL (`xid.base`).

7. **`add_taxonomy(self, entry_points)`**: This method is called with the list of `entry_points`. It checks if the taxonomy has already been loaded. If not, it creates a new `Taxonomy` object: [1, 2, 3](https://github.com/fractalexperience/xbrl/blob/master/examples/ixbrl_processing/sec_cik_1000177_20-f.py)[https://github.com/fractalexperience/xbrl/blob/master/examples/taxonomy_browsing/eiopa-250-dr_sets.py)[https://github.com/fractalexperience/xbrl/blob/master/examples/taxonomy_discovery/us-gaap-2021-package-std.py)

   ```python
   taxonomy.Taxonomy(ep_list, self)  # Sets the new taxonomy as current
   ```

8. **`taxonomy.Taxonomy(entry_points, pool)`**: The `Taxonomy` constructor (in `taxonomy.py`, not provided) processes the entry points, which are URLs to schema files.  It fetches and parses these schemas, and recursively processes any imported or included schemas or linkbases using the `add_reference` method of the `Pool` object.

9. **`add_reference(self, href, base)`**: This method handles loading schemas and linkbases. It checks if the reference has already been discovered. If not, it creates a `Schema` or `Linkbase` object and attaches it to the current taxonomy. [1](https://github.com/fractalexperience/xbrl/blob/master/examples/ixbrl_processing/sec_cik_1000177_20-f.py) This process continues recursively until all related schemas and linkbases are loaded.


This detailed explanation clarifies the step-by-step execution flow, highlighting how methods interact and data is processed within the `Pool` and `Taxonomy` classes.  If you have the `instance.py` and `taxonomy.py` files, I can provide an even more precise breakdown.
# Q2: after running it, is `self.schemas = {}` still an empty dictionary?
No, `self.schemas` will not be empty after running `data_pool.add_instance_location(location, attach_taxonomy=True)` if the instance document at the given `location` references any XBRL schemas.

Here's why:

1. **Instance Parsing**: The `instance.Instance` constructor parses the instance document and identifies the schemas referenced within it (stored in `xid.xbrl.schema_refs`).

2. **Taxonomy Attachment**: If `attach_taxonomy` is True (as it is in your example), the `add_instance` method calls `add_taxonomy` with the list of schema references (entry points).

3. **Taxonomy Creation**: The `taxonomy.Taxonomy` constructor iterates through these entry points.

4. **Schema Loading**: For each entry point that ends with ".xsd", the `add_reference` method is called.  Inside `add_reference`, this line creates a `Schema` object:

   ```python
   sh = self.schemas.get(href, schema.Schema(href, self))
   ```

   If a `Schema` object for that `href` doesn't already exist in `self.schemas`, a new one is created and added to the dictionary.

5. **Recursive Loading**: The `Schema` constructor itself might then discover and load further schemas (through `<xs:import>` or `<xs:include>` elements). Each newly discovered schema will be added to `self.schemas`.

Therefore, after the process completes, `self.schemas` will contain all the schemas directly or indirectly referenced by the instance document.
# Q3: when does it call self.add_reference()?
In the `fractalexperience/xbrl` repository, the `self.add_reference()` method of the `Pool` class is called within the following contexts:

1. **Within the `Pool.add_reference()` method itself (recursive calls):** When processing a schema or linkbase, `add_reference` might encounter further references to other schemas or linkbases (e.g., through `<xs:import>` or `<xs:include>` in schemas, or `<link:linkbaseRef>` in linkbases). In such cases, `add_reference` calls itself recursively to load these nested dependencies.

2. **Within the `Schema` constructor (`taxonomy/schema.py`):**  When a new `Schema` object is created, its constructor iterates through any `<xs:import>` and `<xs:include>` elements. For each such element, it calls `self.container_pool.add_reference()` to load the referenced schema.

3. **Within the `Linkbase` constructor (`taxonomy/linkbase.py`):** Similar to schemas, when a new `Linkbase` object is created, its constructor iterates through any `<link:linkbaseRef>` elements and calls `self.container_pool.add_reference()` to load the referenced linkbase.

4. **Within the `Taxonomy` constructor (`taxonomy/taxonomy.py`):** The `Taxonomy` constructor uses `add_reference` indirectly. It calls `self.container_pool.load_schemas_linkbases()`, which in turn calls `add_reference` for each schema and linkbase reference found within the taxonomy.


In summary, `add_reference` is central to the process of resolving and loading the network of interconnected schemas and linkbases that make up an XBRL taxonomy. It's called directly within the `Pool` class and indirectly through the constructors of `Schema`, `Linkbase`, and `Taxonomy` objects.
