from xbrl.taxonomy import resource
from xbrl.base import const
import lxml.etree


class CustomFunction(resource.Resource):
    """ Implements a custom function """
    def __init__(self, e, container_xlink=None):

        self.function_name = e.attrib.get('name')
        self.output = e.attrib.get('output')
        self.inputs = []
        self.implementation = None

        for e2 in e.iterchildren():
            if e2 is lxml.etree._Comment:
                continue
            if e2.tag == f'{{{const.NS_VARIABLE}}}input':
                ty = e2.attrib.get('type')
                self.inputs.append(ty)

        super().__init__(e, container_xlink)
        container_xlink.linkbase.pool.current_taxonomy.resources[self.xlabel] = self
