from lxml import etree as lxml
from xbrl import const, util


class XmlElementBase:
    def __init__(self, e, parsers=None):
        self.origin = e
        self.parsers = parsers if parsers else {}
        self.name = util.get_local_name(str(e.tag))
        self.prefix = e.prefix
        self.qname = f'{self.prefix}:{self.name}' if self.prefix else self.name
        self.namespace = util.get_namespace(str(e.tag))
        fid = e.attrib.get('id')
        if fid is not None:
            self.id = fid
        self.lang = None if e is None else e.attrib.get(f'{{{const.NS_XML}}}lang')
        self.load(e)

    def load(self, e):
        if isinstance(e, lxml._Comment):
            return
        method = self.parsers.get(e.tag)
        if method is None:
            self.l_default(e)
        else:
            method(e)

    def l_children(self, e):
        for e2 in e.iterchildren():
            self.load(e2)

    def serialize(self):
        output = [f'<{self.qname}']
        self.serialize_attributes(output)
        if len(self.origin):
            output.append('>')
            for e2 in self.origin.iterchildren():
                eb2 = XmlElementBase(e2)
                output.append(eb2.serialize())
            output.append(f'</{self.qname}>')
        else:
            if not self.origin.text:
                output.append("/>")
            else:
                output.append(f'>{self.origin.text}</{self.qname}>')
        return ''.join(output)

    def serialize_attributes(self, output):
        for a in self.origin.attrib.items():
            a_value = a[1]
            a_name = util.get_local_name(a[0])
            a_uri = util.get_namespace(a[0])
            a_qname = a_name
            if a_uri:
                a_prefix = self.origin.nsmap.get(a_uri)
                a_qname = f'{a_prefix}:{a_name}'
            output.append(f' {a_qname}="{a_value}"')

    def l_default(self, e):
        default_method = self.parsers.get('default')
        if default_method is not None:
            default_method(e)
