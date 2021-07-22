from xbrl.base import fbase, const, util
from xbrl.taxonomy import xlink


class Linkbase(fbase.XmlFileBase):
    def __init__(self, location, container_pool, root=None):
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
        self.refs = set({})
        self.pool = container_pool
        self.links = []
        resolved_location = util.reduce_url(location)
        if self.pool is not None:
            self.pool.discovered[location] = True
        super().__init__(resolved_location, container_pool, parsers, root)
        if self.pool is not None:
            self.pool.linkbases[resolved_location] = self

    def l_linkbase(self, e):
        # Load files referenced in schemaLocation attribute
        for uri, href in self.schema_location_parts.items():
            self.pool.add_reference(href, self.base)
        self.l_children(e)

    def l_link(self, e):
        xl = xlink.XLink(e, self)
        self.links.append(xl)

    ''' Effectively reading roleRef and arcroleRef is the same thing here, 
        because it only discovers the corresponding schema '''
    def l_arcrole_ref(self, e):
        self.l_ref(e)

    def l_role_ref(self, e):
        self.l_ref(e)

    def l_ref(self, e):
        if self.pool is None:
            return
        xpointer = e.attrib.get(f'{{{const.NS_XLINK}}}href')
        if xpointer.startswith('#'):
            href = self.location
        else:
            href = xpointer[:xpointer.find('#')]
        fragment_identifier = xpointer[xpointer.find('#')+1:]
        self.refs.add(href)
        self.pool.add_reference(href, self.base)
