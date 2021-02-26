from xbrl import fbase, linkbase, const, concept, element
import os


class Schema(fbase.XmlFileBase):
    def __init__(self, location, container_pool, container_taxonomy):
        self.target_namespace = ''
        self.target_namespace_prefix = ''
        parsers = {
            f'{{{const.NS_XS}}}schema': self.l_schema,
            f'{{{const.NS_XS}}}annotation': self.l_annotation,
            f'{{{const.NS_XS}}}appinfo': self.l_appinfo,
            f'{{{const.NS_XS}}}import': self.l_import,
            f'{{{const.NS_LINK}}}linkbaseRef': self.l_linkbase_ref,
            f'{{{const.NS_XS}}}element': self.l_element,
        }
        self.imports = {}
        self.linkbase_refs = {}
        self.role_types = {}
        self.arcrole_types = {}
        self.elements = {}  # Elements, which are not concepts
        self.taxonomy = container_taxonomy
        self.pool = container_pool
        super().__init__(location, container_pool, parsers)
        if self.taxonomy is not None:
            self.taxonomy.schemas[location] = self
        if self.pool is not None:
            self.pool.schemas[location] = self

    def l_schema(self, e):
        self.target_namespace = e.get('targetNamespace')
        self.target_namespace_prefix = self.namespaces_reverse.get(self.target_namespace, None)
        self.l_children(e)

    def l_element(self, e):
        sgr = e.attrib.get('substitutionGroup')
        if sgr is not None:
            c = concept.Concept(e, self)
        else:
            elem = element.Element(e, self)

    def l_annotation(self, e):
        self.l_children(e)

    def l_appinfo(self, e):
        self.l_children(e)

    def l_linkbase_ref(self, e):
        href = e.get(f'{{{const.NS_XLINK}}}href')
        if not href.startswith('http'):
            href = self.pool.resolver.reduce_url(os.path.join(self.base, href).replace('\\', '/'))
        self.linkbase_refs[href] = e
        if href in self.pool.discovered:
            return
        self.pool.discovered[href] = False
        lb = self.pool.linkbases.get(href, None)
        if lb is None:
            lb = linkbase.Linkbase(href, self.pool, self.taxonomy)
            self.pool.discovered[href] = True

    def l_roletype(self, e):
        pass

    def l_arcroletype(self, e):
        pass

    def l_import(self, e):
        href = e.get('schemaLocation')
        if not href.startswith('http'):
            href = self.pool.resolver.reduce_url(os.path.join(self.base, href).replace('\\', '/'))
        self.imports[href] = e
        if href in self.pool.discovered:
            return
        self.pool.discovered[href] = False
        sh = self.pool.schemas.get(href, None)
        if sh is None:
            sh = Schema(href, self.pool, self.taxonomy)
            self.pool.discovered[href] = True
