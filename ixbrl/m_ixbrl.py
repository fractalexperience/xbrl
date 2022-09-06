from xbrl.base import ebase, const, util
from xbrl.ixbrl import m_format
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
        self.idx_tuple_content = set([]) # All elements, which are inside tuple content
        self.output = None
        self.prefixes = {}
        self.followed = {}  # Followed continuations
        self.allowed_reference_names = [
            f'{{{const.NS_LINK}}}schemaRef',
            f'{{{const.NS_LINK}}}linkbaseRef']
        self.formatter = m_format.Formatter()
        super().__init__(e)
        self.index(e)

    def index(self, e, level=0):
        """ Populates indixes """
        if isinstance(e, lxml._ProcessingInstruction) or isinstance(e, lxml._Comment):
            return
        if e.tag.startswith(f'{{{const.NS_IXBRL}}}') or e.tag.startswith(f'{{{const.NS_IXBRL_2008}}}'):
            self.index_element(e)
        for e2 in e.iterchildren():
            self.index(e2, level+1)

    def index_element(self, e):
        eb = ebase.XmlElementBase(e, parsers=None, assign_origin=True)
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
        self.strip_resources()
        self.strip_non_fraction()
        self.strip_non_numeric()
        self.output.append('</xbrl>')

    def to_xml(self):
        if not self.output:
            self.strip()
        return ''.join(self.output)

    def strip_non_numeric(self):
        non_numerics = self.idx_n.get('nonNumeric')
        if not non_numerics:
            return
        cnt = 0
        for nn in non_numerics:
            cnt += 1
            if nn in self.idx_tuple_content:
                continue
            name = nn.origin.attrib.get('name')
            if not name or nn.origin is None:
                continue
            cref = nn.origin.attrib.get('contextRef')
            part1 = f'{(nn.origin.text if nn.origin.text else "")}' if len(nn.origin) else ''
            rest = self.get_full_content(nn.origin, [])
            content = util.escape_xml(f'{part1}{rest}')
            self.output.append(f'<{name} contextRef="{cref}">{content}</{name}>')

    def strip_non_fraction(self):
        non_fractions = self.idx_n.get('nonFraction')
        if not non_fractions:
            return
        for nf in non_fractions:
            if nf in self.idx_tuple_content:
                continue
            name = nf.origin.attrib.get('name')
            if not name:
                continue
            cref = nf.origin.attrib.get('contextRef')
            uref = nf.origin.attrib.get('unitRef')
            prec = nf.origin.attrib.get('precision')
            deci = nf.origin.attrib.get('decimals')
            rounding = f' decimals="{deci}"' if deci else f' precision="{prec}"' if prec else ''
            text = self.normalize_numeric_content(nf.origin)
            self.output.append(f'<{name} contextRef="{cref}" unitRef="{uref}" {rounding}>{text}</{name}>')

    def strip_resources(self):
        resources = self.idx_n.get('resources')
        if not resources:
            return
        for r in resources:
            for e2 in r.origin.iterchildren():
                if isinstance(e2, lxml._ProcessingInstruction) or isinstance(e2, lxml._Comment):
                    continue
                e2b = ebase.XmlElementBase(e2, parsers=None, assign_origin=True)
                if e2b.namespace != const.NS_XBRLI:
                    continue
                self.output.append(e2b.serialize())

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
            self.serialize_ix_element(e2)

    def get_full_content(self, e, stack):
        if e is None or str(e.tag).endswith('exclude'):
            return ''
        is_escaped = False
        continued_at = None
        for a in e.attrib.items():
            if a[0] == 'escape':
                is_escaped = a[1] == 'true' or a[1] == '1'
            elif a[0] == 'continuedAt':
                continued_at = a[1].strip()
        if is_escaped:
            return util.escape_xml(e.text)
        result = []
        if len(e):
            for e2 in e.iterchildren():
                result.append(self.get_full_content(e2, stack))
        else:
            if e.text:
                result.append(e.text)

            # TODO - Verify this with normative examples
            # if e.tail and e.tag == f'{{{const.NS_IXBRL}}}nonNumeric':
            #     result.append(e.tail)

        continuations = self.idx_nav.get(f'continuation|id|{continued_at}')
        if continued_at and continuations:
            for continuation in continuations:
                if continued_at in self.followed:
                    continue
                if continuation in stack:
                    continue
                self.followed[continued_at] = continuation
                stack.append(continuation)
                result.append(self.get_full_content(continuation.origin, stack))
                stack.pop()
        return ''.join(result)

    def to_canonical_format(self, text, frmt):
        if not frmt:
            return text
        return self.formatter.apply_format(text, frmt)  # TODO: Maybe return empty value and stop process

    def normalize_numeric_content(self, e):
        value = self.get_full_content(e, [])
        frmt = e.attrib.get('format')
        scle = e.attrib.get('scale')
        sign = e.attrib.get('sign')
        sgn = '' if sign is None else sign
        # This gives a tuple where the first member is the formatted value and the second is the error message
        formatted = self.to_canonical_format(value, frmt)
        try:
            fstr = f'{formatted}'
            if scle:
                f = float(formatted)
                s = float(scle)
                fstr = f'{f * math.pow(10, s)}'
            fstr = fstr[:-2] if fstr[-2:] == '.0' else fstr
            return f'{sgn}{fstr}'
            # return f'{sgn}{formatted}'
        except Exception as ex:
            return f'{sgn}{value}'

    def get_inherited_attribute(self, e, name, initial='', concatenate_parent=False):
        if e is None:
            return initial
        value = e.attrib.get(name)
        if value and not concatenate_parent:
            return value
        parent = e.getparent()
        return self.get_inherited_attribute(parent, name, f'{value if value and concatenate_parent else ""}{initial}', concatenate_parent)

    def serialize_ix_element(self, e):
        if e.tag is lxml.Comment:
            return
        text_content = self.get_full_content(e, [e])
        eb = ebase.XmlElementBase(e, parsers=None, assign_origin=True)
        self.prefixes[eb.prefix] = True
        self.output.append(f'<{eb.qname}')
        self.serialize_ix_attributes(eb)
        if len(e):
            self.output.append('>')
            for e2 in e.iterchildren():
                self.serialize_ix_element(e2)
            self.output.append(f'</{self.qname}>')
        else:
            if text_content and self.origin:
                self.output.append(f'>{self.origin.text}</{self.qname}>')
            else:
                self.output.append("/>")

    def serialize_ix_attributes(self, eb):
        for a in eb.origin.attrib.items():
            value = a[1]
            a_name = util.get_local_name(a[0])
            a_uri = util.get_namespace(a[0])
            a_qname = a_name
            if a_name == 'href':
                xml_base = self.get_inherited_attribute(eb.origin, "xml:base", '', True)
                value = f'{xml_base}{value}'
            if a_uri:
                aprefix = self.instance.namespaces_reverse.get(a_uri)
                if aprefix:
                    self.prefixes[aprefix] = True
                    a_qname = f'{aprefix}:{a_name}'
            self.output.append(f' {a_qname}="{value}"')
