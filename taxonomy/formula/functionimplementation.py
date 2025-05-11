from xbrl.taxonomy import resource
from xbrl.base import const
import lxml.etree

class FunctionImplementation(resource.Resource):
    """ Implements custom function implementation """
    def __init__(self, e, container_xlink=None):

        self.steps = {}
        self.inputs = []
        self.outputs = []

        for e2 in e.iterchildren():
            if e2 is lxml.etree._Comment:
                continue
            if e2.tag == f'{{{const.NS_CUSTOM_FUNCTION}}}input':
                nm = e2.attrib.get('name')
                self.inputs.append(nm)
            if e2.tag == f'{{{const.NS_CUSTOM_FUNCTION}}}step':
                nm = e2.attrib.get('name')
                expr = e2.text
                self.steps[nm] = expr
            if e2.tag == f'{{{const.NS_CUSTOM_FUNCTION}}}output':
                p = e2.text
                self.outputs.append(p)

        super().__init__(e, container_xlink)
        container_xlink.linkbase.pool.current_taxonomy.resources[self.xlabel] = self


