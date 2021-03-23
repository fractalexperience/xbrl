from xbrl.taxonomy import schema, xlink
from xbrl.base import fbase, const, util
import os


class Linkbase(fbase.XmlFileBase):
    def __init__(self, location, container_pool, container_taxonomy):
        parsers = {
            f'{{{const.NS_LINK}}}linkbase': self.l_linkbase,
            f'{{{const.NS_LINK}}}calculationLink': self.l_link,
            f'{{{const.NS_LINK}}}presentationLink': self.l_link,
            f'{{{const.NS_LINK}}}definitionLink': self.l_link,
            f'{{{const.NS_LINK}}}labelLink': self.l_link,
            f'{{{const.NS_LINK}}}referenceLink': self.l_link,
            f'{{{const.NS_GEN}}}link': self.l_link,  # Generic link
            f'{{{const.NS_LINK}}}roleRef': self.l_role_ref,
            f'{{{const.NS_LINK}}}arcroleRef': self.l_arcrole_ref
        }
        self.role_refs = {}
        self.arcrole_refs = {}
        self.taxonomy = container_taxonomy
        self.pool = container_pool
        self.links = []
        resolved_location = util.reduce_url(location)
        super().__init__(resolved_location, container_pool, parsers)
        if self.taxonomy is not None:
            self.taxonomy.linkbases[resolved_location] = self
        if self.pool is not None:
            self.pool.linkbases[resolved_location] = self

    def l_linkbase(self, e):
        self.l_children(e)

    def l_link(self, e):
        xl = xlink.XLink(e, self)
        self.links.append(xl)

    ''' Effectively reading roleRef and arcroleRef is the same thing here, 
        because it only dicovers the correspondign schema '''
    def l_arcrole_ref(self, e):
        self.l_ref(e)

    def l_role_ref(self, e):
        self.l_ref(e)

    def l_ref(self, e):
        if self.pool is None and self.taxonomy is None:
            return
        xpointer = e.get(f'{{{const.NS_XLINK}}}href')
        href = xpointer[:xpointer.find('#')]
        fragment_identifier = xpointer[xpointer.find('#')+1:]
        self.l_fbase(href)

    ''' Loads schema or linkbase depending on file type. TO IMPROVE!!! '''
    def l_fbase(self, href):
        if not href.startswith('http'):
            href = util.reduce_url(os.path.join(self.base, href).replace('\\', '/'))
        if href in self.pool.discovered:
            return
        self.pool.discovered[href] = False
        if href.endswith(".xsd"):
            self.l_nested_schema(href)
        else:
            self.l_nested_linkbase(href)

    def l_nested_linkbase(self, href):
        lb = self.pool.linkbases.get(href, None)
        if lb is None:
            lb = Linkbase(href, self.pool, self.taxonomy)
            self.pool.discovered[href] = True

    def l_nested_schema(self, href):
        sh = self.pool.schemas.get(href, None)
        if sh is None:
            sh = schema.Schema(href, self.pool, self.taxonomy)
            self.pool.discovered[href] = True
