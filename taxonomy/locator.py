from xbrl.base import ebase, const, util
import os


class Locator(ebase.XmlElementBase):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        href = e.attrib.get(f'{{{const.NS_XLINK}}}href')
        if href.startswith('#'):
            href = f'{self.xlink.linkbase.location}{href}'
        elif href.startswith('..'):
            href = os.path.join(self.xlink.linkbase.base, href)
            href = href.replace('\\', '/')
        elif not href.startswith('http') and self.xlink is not None:
            href = os.path.join(self.xlink.linkbase.base, href)
            href = href.replace('\\', '/')
        self.href = util.reduce_url(href)
        self.label = e.attrib.get(f'{{{const.NS_XLINK}}}label')
        self.url = self.href[:self.href.find('#')]
        self.fragment_identifier = self.href[self.href.find('#')+1:]
        if self.xlink is not None:
            self.xlink.locators[self.label] = self
            self.xlink.locators_by_href[self.href] = self

