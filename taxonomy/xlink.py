from xbrl.taxonomy import arc, base_set, locator, resource
from xbrl.base import ebase, const, util
import urllib.parse


class XLink(ebase.XmlElementBase):
    """ Represents an extended link """
    def __init__(self, e, container_linkbase):
        self.linkbase = container_linkbase
        parsers = {
            'default': self.l_xlink,
            f'{{{const.NS_LINK}}}labelArc': self.l_arc,
            f'{{{const.NS_LINK}}}definitionArc': self.l_arc,
            f'{{{const.NS_LINK}}}presentationArc': self.l_arc,
            f'{{{const.NS_LINK}}}calculationArc': self.l_arc,
            f'{{{const.NS_LINK}}}loc': self.l_loc,
            f'{{{const.NS_LINK}}}label': self.l_label
        }
        self.locators = {}  # Locators indexed by unique identifier
        self.arcs_from = {}  # Arcs indexed by from property
        self.arcs_to = {}  # Arcs indexed by to property
        self.resources = {}  # All labelled resources indexed by global identifier
        super(XLink, self).__init__(e, parsers)
        self.role = e.attrib.get(f'{{{const.NS_XLINK}}}role')

    def l_xlink(self, e):
        self.l_children(e)

    def l_label(self, e):
        res = resource.Resource(e, self)

    def l_arc(self, e):
        a = arc.Arc(e, self)

    def l_loc(self, e):
        loc = locator.Locator(e, self)
        url = loc.url
        self.linkbase.pool.add_reference(url, self.linkbase.base, self.linkbase.taxonomy)

    def compile(self):
        for arc_list in [a[1] for a in self.arcs_from.items()]:
            for a in arc_list:
                loc = self.locators.get(a.xl_from, None)
                if loc is None:
                    continue
                href = urllib.parse.unquote(util.reduce_url(loc.href))
                c = self.linkbase.taxonomy.concepts.get(href, None)
                if c is None:
                    print(f'Unresolved "from" locator: {loc.href}')
                    return
                reslist = self.resources.get(a.xl_to, None)
                if reslist is not None:
                    for res in reslist:
                        cres = c.resources.get(res.name, None)
                        if cres is None:
                            cres = {}
                            c.resources[res.name] = cres
                        key = f'{res.lang}|{res.role}'
                        util.u_dct_list(cres, key, res)  # Multiple resources of the same type may be related
                    continue
                # if no resources are connected, try to find inter-concept relations
                loc2 = self.locators.get(a.xl_to, None)
                if loc2 is None:
                    continue
                href2 = urllib.parse.unquote(util.reduce_url(loc2.href))
                c2 = self.linkbase.taxonomy.concepts.get(href2, None)
                if c2 is None:
                    print(f'Unresolved "to" locator: {loc2.href}')
                    return
                is_root = a.xl_from not in self.arcs_to
                bs_key = f'{a.name}|{a.arcrole}|{self.role}'
                bs = self.linkbase.taxonomy.base_sets.get(bs_key, None)
                if bs is None:
                    bs = base_set.BaseSet(a.name, a.arcrole, self.role)
                    self.linkbase.taxonomy.base_sets[bs_key] = bs
                if is_root and not c in bs.roots:
                    bs.roots.append(c)

                # Populate concept child and parent sets
                util.u_dct_list(c.chain_dn, bs_key, (c2, a))
                util.u_dct_list(c2.chain_up, bs_key, (c, a))
