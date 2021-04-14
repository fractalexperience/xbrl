from xbrl.base import ebase, const
import os


class Locator(ebase.XmlElementBase):
    def __init__(self, e, container_xlink = None):
        self.xlink = container_xlink
        super().__init__(e)
        href = e.attrib.get(f'{{{const.NS_XLINK}}}href')
        if not href.startswith('http') and self.xlink is not None:
            href = f'{os.path.join(self.xlink.linkbase.base, href)}'
            href = href.replace('\\','/')
        self.href = href
        self.label = e.attrib.get(f'{{{const.NS_XLINK}}}label')
        self.url = self.href[:self.href.find('#')]
        self.fragment_identifier = self.href[self.href.find('#')+1:]
        if self.xlink is not None:
            self.xlink.locators[self.label] = self
