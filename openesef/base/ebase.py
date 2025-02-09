from lxml import etree as lxml
from openesef.base import const, util



import logging

# Get a logger.  __name__ is a good default name.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# # Check if handlers already exist and clear them to avoid duplicates.
# if logger.hasHandlers():
#     logger.handlers.clear()

# # Create a handler for console output.
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)

# # Create a formatter.
# log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# formatter = logging.Formatter(log_format)

# # Set the formatter on the handler.
# handler.setFormatter(formatter)

# # Add the handler to the logger.
# logger.addHandler(handler)

class XmlElementBase:
    def __init__(self, e, parsers=None, assign_origin=False, esef_filing_root=None):
        self.origin = e if assign_origin else None
        self.parsers = parsers if parsers else {}
        self.name = util.get_local_name(str(e.tag))
        self.prefix = e.prefix
        self.qname = f'{self.prefix}:{self.name}' if self.prefix else self.name
        self.namespace = util.get_namespace(str(e.tag))
        self.id = e.attrib.get('id')
        self.lang = None if e is None else e.attrib.get(f'{{{const.NS_XML}}}lang')
        self.esef_filing_root = esef_filing_root
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
        if self.origin is None:
            return None
        if self.origin.tag is lxml.Comment:
            return f'<!-- {self.origin.text} -->'
        output = [f'<{self.qname}']
        self.serialize_attributes(output)
        if len(self.origin):
            output.append('>')
            if self.origin.text:
                output.append(self.origin.text)
            for e2 in self.origin.iterchildren():
                eb2 = XmlElementBase(e2, parsers=None, assign_origin=True)
                output.append(eb2.serialize())
                if e2.tail:
                    output.append(e2.tail)
            if self.origin.tail:
                output.append(self.origin.tail)
            output.append(f'</{self.qname}>')
        else:
            if not self.origin.text:
                output.append("/>")
            else:
                output.append(f'>{util.escape_xml(self.origin.text)}</{self.qname}>')
        return ''.join(output)

    def serialize_attributes(self, output):
        for a in self.origin.attrib.items():
            a_value = a[1]
            a_name = util.get_local_name(a[0])
            a_uri = util.get_namespace(a[0])
            a_qname = a_name
            if a_uri:
                plist = [p for p, u in self.origin.nsmap.items() if u == a_uri]
                a_prefix = plist[0] if plist else 'ns1'
                a_qname = f'{a_prefix}:{a_name}'
            output.append(f' {a_qname}="{a_value}"')

    def l_default(self, e):
        default_method = self.parsers.get('default')
        if default_method is not None:
            default_method(e)
