from xbrl.base import const, element, util, data_wrappers
from lxml import etree as lxml


class ItemType(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        self.restrictions = []
        self.base = None
        unique_id = f'{self.namespace}:{self.name}'
        self.schema.item_types[unique_id] = self
        self.l_restrictions(e)

    def l_restrictions(self, e):
        for e2 in e.iterchildren():
            if isinstance(e2, lxml._Comment):
                continue
            if e2.tag != f'{{{const.NS_XS}}}simpleContent':
                continue
            for e3 in e2.iterchildren():
                if isinstance(e3, lxml._Comment):
                    continue
                if e3.tag != f'{{{const.NS_XS}}}restriction':
                    print('Unknown simpleContent element: ', e3.tag)
                    continue
                self.base = e3.attrib.get('base')
                for e4 in e3.iterchildren():
                    if isinstance(e4, lxml._Comment):
                        continue
                    self.restrictions.append(data_wrappers.XsdRestriction(
                            util.get_local_name(e4.tag), e4.attrib.get('value')))
