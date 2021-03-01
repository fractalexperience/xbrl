import os
from xbrl import resolver, instance, taxonomy, schema


class Pool:
    def __init__(self, cache_folder=None):
        self.cache_folder = cache_folder
        if cache_folder is not None:
            self.resolver = resolver.Resolver(cache_folder)
        self.taxonomies = {}
        self.discovered = {}
        self.schemas = {}
        self.linkbases = {}
        self.instances = {}

    def add_instance(self, location, key=None, attach_taxonomy=False):
        xid = instance.Instance(location=location, container_pool=self)
        if key is None:
            key = location
        self.instances[key] = xid
        if attach_taxonomy and xid.xbrl is not None:
            # Ensure that if schema references are relative, the location base for XBRL document is added to them
            entry_points = [e if e.startswith('http') else os.path.join(xid.base,e).replace('\\', '/')
                            for e in xid.xbrl.schema_refs]
            tax = self.add_taxonomy(entry_points)
            xid.taxonomy = tax

    def add_schema(self, location, container_taxonomy):
        sh = schema.Schema(location, container_taxonomy)
        self.schemas[location] = sh
        if container_taxonomy is None:
            return
        container_taxonomy.schemas[location] = sh

    def add_taxonomy(self, entry_points):
        tax = taxonomy.Taxonomy(entry_points, self)
        key = ",".join(entry_points)
        self.taxonomies[key] = tax
        return tax

    def info(self):
        return f'''Instance documents: {len(self.instances)}
Taxonomy schemas: {len(self.schemas)}
Taxonomy linkbases: {len(self.linkbases)}
'''
