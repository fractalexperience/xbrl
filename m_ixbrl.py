from xbrl import const
from xbrl import ebase
from xbrl import util
import math
from lxml import etree as lxml


class IxbrlModel(ebase.XmlElementBase):
    """ Implements an iXbrl model """
    def __init__(self, e, container_instance):
        self.instance = container_instance
        self.idx_n = {}  # iXBRL elements by element name
        self.idx_a = {}  # iXBRL elements by attribute name
        self.idx_na = {}  # iXBRL elements by element name and attribute name
        self.idx_av = {}  # iXBRL elements by attribute name and attribute value
        self.idx_nav = {}  # iXBRL elements by element name, attribute name and attribute value
        self.output = None
        self.prefixes = {}
        self.allowed_reference_names = [
            f'{{{const.NS_LINK}}}schemaRef',
            f'{{{const.NS_LINK}}}linkbaseRef']
        super().__init__(e)
        self.index(e)

    def index(self, e):
        """ Populates indixes """
        if e.tag.startswith(f'{{{const.NS_IXBRL}}}'):
            self.index_element(e)
        for e2 in e.iterchildren():
            self.index(e2)

    def index_element(self, e):
        eb = ebase.XmlElementBase(e)
        key_name = eb.name
        util.u_dct_list(self.idx_n, key_name, eb)
        for a in e.attrib.items():
            key_a = f'{a[0]}'
            util.u_dct_list(self.idx_a, key_a, eb)
            key_na = f'{eb.name}|{a[0]}'
            util.u_dct_list(self.idx_na, key_na, eb)
            key_av = f'{a[0]}|{a[1]}'
            util.u_dct_list(self.idx_av, key_av, eb)
            key_nav = f'{eb.name}|{a[0]}|{a[1]}'
            util.u_dct_list(self.idx_nav, key_nav, eb)

    def strip(self):
        """ Serializes native XBRL """
        self.output = []
        self.prefixes = {}
        self.output.append(const.XML_START)
        self.output.append(f'<xbrl xmlns="{const.NS_XBRLI}" ')
        for ns in self.instance.namespaces.items():
            self.output.append(f'xmlns:{ns[0]}="{ns[1]}" ')
        self.output.append('>')
        self.strip_refs()
        self.output.append('</xbrl>')

    def to_xml(self):
        if not self.output:
            self.strip()
        return ''.join(self.output)

    def strip_refs(self):
        refs = self.idx_n.get('references')
        if not refs:
            return
        for r in refs:
            self.strip_ref(r.origin)

    def strip_ref(self, e):
        for e2 in e.iterchildren():
            if e2.tag not in self.allowed_reference_names:
                continue
            self.serialize_ix_element(e2, self.output)

    def get_full_content(self, e, stack):
        if e is None or e.tag == f'{{{const.NS_IXBRL}}}exclude':
            return ''
        is_escaped = False
        continued_at = None
        for a in e.attrib.items():
            if a[0] == 'escape':
                is_escaped = a[1] == 'true' or a[1] == '1'
            elif a[0] == 'continuedAt':
                continued_at = a[1].Trim()
        if is_escaped:
            return util.escape_xml(e.text)

        result = []
        for e2 in e.iterchildren():
            result.append(self.get_full_content(e2, stack))

        continuations = self.idx_nav.get(f'continuation|id|{continued_at}')
        if continued_at and continuations:
            for continuation in continuations:
                if continuation in stack:
                    continue
                stack.append(continuation)
                result.append(self.get_full_content(continuation, stack))
                stack.pop()
        return util.escape_xml(''.join(result))

    def to_canonical_format(self, text, frmt):
        return text  # TODO - implement format

    def normalize_numeric_content(self, e):
        value = self.get_full_content(e, [])
        frmt = e.attrib.get('format')
        scle = e.attrib.get('scale')
        result = self.to_canonical_format(value, frmt)
        if scle:
            return value * math.pow(10, scle)
        return result

    def get_inherited_attribute(self, e, name, initial='', concatenate_parent=False):
        if e is None:
            return initial
        value = e.attrib.get(name)
        if value and not concatenate_parent:
            return value
        parent = e.getparent()
        return self.get_inherited_attribute(parent, name, f'{value if value and concatenate_parent else ""}{initial}', concatenate_parent)

    def serialize_ix_element(self, e, output):
        text_content = self.get_full_content(e, [e])
        eb = ebase.XmlElementBase(e)
        self.prefixes[eb.prefix] = True
        output.append(f'<{eb.qname}')
        for a in e.attrib.items():
            value = a[1]
            aname = util.get_local_name(a[0])
            auri = util.get_namespace(a[0])
            qname = aname
            if aname == 'href':
                xml_base = self.get_inherited_attribute(e, "xml:base", '', True)
                value = f'{xml_base}{value}'
            if auri:
                aprefix = self.instance.namespaces_reverse.get(auri)
                if aprefix:
                    self.prefixes[aprefix] = True
                    qname = f'{aprefix}:{aname}'
            output.append(f' {qname}="{value}"')
        cnt_children = 0
        inner_output = []
        for e2 in e.iterchildren():
            cnt_children += 1
            self.serialize_ix_element(e2, inner_output)

        if cnt_children == 0:
            if not text_content == 0:
                output.append("/>")
            else:
                output.append(f'>{text_content}</{eb.qname}>')
        else:
            output.append('>')
            for l in inner_output:
                output.append(l)
            output.append(f'</{eb.qname}>')
