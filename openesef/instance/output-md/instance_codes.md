# Project Structure
```
📦 openesef/instance
    ├── 📄 .DS_Store
    ├── 📄 __init__.py
    ├── 📄 context.py
    ├── 📄 dei.py
    ├── 📄 fact.py
    ├── 📄 footnote.py
    ├── 📄 instance.py
    ├── 📄 m_xbrl.py
    └── 📄 unit.py
```

#  Project Contents
## __init__.py
```py
from . import m_xbrl
from . import footnote
from . import instance
from . import fact
from . import context
from . import unit
from . import dei
```

## context.py
```py
from ..base import ebase, const


class Context(ebase.XmlElementBase):
    def __init__(self, e):
        self.descriptors = {}
        self.period_instant = None
        self.period_start = None
        self.period_end = None
        self.entity_scheme = ''
        self.entity_identifier = ''
        self.segment = None
        self.scenario = None
        self.dimensional_container = None # To be set further during parsing
        self.segment_non_xdt = {}
        self.scenario_non_xdt = {}
        parsers = {
            f'{{{const.NS_XBRLI}}}context': self.l_context,
            f'{{{const.NS_XBRLI}}}period': self.l_period,
            f'{{{const.NS_XBRLI}}}entity': self.l_entity,
            f'{{{const.NS_XBRLI}}}identifier': self.l_entity_identifier,
            f'{{{const.NS_XBRLI}}}segment': self.l_segment,
            f'{{{const.NS_XBRLI}}}scenario': self.l_scenario,
            f'{{{const.NS_XBRLDI}}}explicitMember': self.l_member,
            f'{{{const.NS_XBRLDI}}}typedMember': self.l_member
        }
        super().__init__(e, parsers)
    def __repr__(self):
        return f"Context(entity_scheme={self.entity_scheme}, entity_identifier={self.entity_identifier}, period={self.get_period_string()}, descriptors={self.descriptors})"
    def l_context(self, e):
        self.l_children(e)

    def l_period(self, e):
        for e in e.iterchildren():
            if e.tag == f'{{{const.NS_XBRLI}}}instant':
                self.period_instant = e.text.strip()
            elif e.tag == f'{{{const.NS_XBRLI}}}startDate':
                self.period_start = e.text.strip()
            elif e.tag == f'{{{const.NS_XBRLI}}}endDate':
                self.period_end = e.text.strip()

    def l_entity(self, e):
        self.l_children(e)

    def l_entity_identifier(self, element):
        self.entity_identifier = element.text
        self.entity_scheme = element.attrib.get("scheme")

    def l_segment(self, e):
        self.segment = {}
        self.dimensional_container = self.segment
        self.l_children(e)

    def l_scenario(self, e):
        self.scenario = {}
        self.dimensional_container = self.scenario
        self.l_children(e)

    def l_member(self, e):
        dimension = e.attrib.get("dimension")
        self.dimensional_container[dimension] = e
        self.descriptors[dimension] = e

    def get_period_string(self):
        if self.period_instant:
            return self.period_instant
        return f'{self.period_start}/{self.period_end}'

    def get_xdt_signature(self):
        return "|".join(sorted([f'{k}#{self.descriptors.get(k).text}' for k in self.descriptors]))

    def get_simplified_signature(self):
        return "|".join(sorted([f'{k}' for k in self.descriptors]))

    def get_signature(self):
        return "|".join([
            f'entity#{self.entity_scheme}:{self.entity_identifier}',
            f'period#{self.get_period_string()}',
            self.get_xdt_signature()
        ])

    def get_member(self, dim):
        """ Returns dimension member for a specified dimension QName. """
        if not self.descriptors:
            return None
        e = self.descriptors.get(dim)
        if e is None:
            return None
        if e.tag == f'{{{const.NS_XBRLDI}}}explicitMember':
            return e.text
        if e.tag == f'{{{const.NS_XBRLDI}}}typedMember':
            o = []
            for e2 in e.iterchildren():  # Should be only one
                o.append(e2.text)
            return ''.join(o)
        return None
```

## dei.py
```py
# instance/dei.py
from lxml import etree
from datetime import date
from .. import fbase  # Assuming fbase.py is in the parent directory

class Context(object):
    """A simulated Enum class to represent 2 different contexts: Instant and Duration"""
    Duration, Instant = range(2)

class DEI(object):
    """
    DEI stands for Document and Entity Information. For each XBRL report, there will be a section for DEI,
    and this class is to provide easy access to those commonly-defined DEI attributes.
    """
    pool = set()

    def __init__(self, name):
        if name and isinstance(name, str):
            self.name = name
            DEI.pool.add(name)  # Use DEI.pool instead of self.pool
            self.fact_name = 'dei:{0}'.format(self.name)
        else:
            raise ValueError('Given name is not a string')

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self.name)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return None

    @classmethod
    def all(cls):
        """Returns a tuple which contains all members"""
        return tuple(getattr(cls, d) for d in DEI.pool if not d.startswith('__'))


DEI.AmendmentFlag = DEI('AmendmentFlag')
DEI.CurrentFiscalYearEndDate = DEI('CurrentFiscalYearEndDate')
DEI.DocumentFiscalPeriodFocus = DEI('DocumentFiscalPeriodFocus')
DEI.DocumentFiscalYearFocus = DEI('DocumentFiscalYearFocus')
DEI.DocumentPeriodEndDate = DEI('DocumentPeriodEndDate')
DEI.DocumentType = DEI('DocumentType')
DEI.EntityCentralIndexKey = DEI('EntityCentralIndexKey')
DEI.EntityCommonStockSharesOutstanding = DEI('EntityCommonStockSharesOutstanding')
DEI.EntityCurrentReportingStatus = DEI('EntityCurrentReportingStatus')
DEI.EntityFilerCategory = DEI('EntityFilerCategory')
DEI.EntityPublicFloat = DEI('EntityPublicFloat')
DEI.EntityRegistrantName = DEI('EntityRegistrantName')
DEI.EntityVoluntaryFilers = DEI('EntityVoluntaryFilers')
DEI.EntityWellKnownSeasonedIssuer = DEI('EntityWellKnownSeasonedIssuer')
DEI.TradingSymbol = DEI('TradingSymbol')


class XBRLDocument(fbase.XmlFileBase):  # Inherit from fbase.XmlFileBase
    """
    This class represents an XBRL XML file from SEC EDGAR.
    """

    def __init__(self, url):
        """
        This url can be a local file path or a http url points to the xml file
        """
        super().__init__(url)  # Initialize the base class
        self.url = url
        try:
            # self.doc_root = etree.parse(url).getroot() # Handled by XmlFileBase
            self.doc_root = self.xml_root  # Use the parsed XML from XmlFileBase
        except IOError as err:
            raise err
        self.nsmap = {}
        for key in self.doc_root.nsmap.keys():
            if key:
                self.nsmap[key] = self.doc_root.nsmap[key]
        self.nsmap['xbrli'] = 'http://www.xbrl.org/2003/instance'
        self.nsmap['xlmns'] = 'http://www.xbrl.org/2003/instance'

        self.fiscal_year = 0
        self.fiscal_period_end_date = None
        self.dei = {}
        self._determine_dei()

        self.context_instant = ''
        self.context_duration = ''
        self._find_contexts()

    def _determine_dei(self):
        """For all DEI, fetch the value from XBRL xml and put it in self.dei"""
        for dei in DEI.all():
            fact_name = dei.fact_name
            nodes = self.doc_root.xpath('//{0}'.format(fact_name), namespaces=self.nsmap)
            value = nodes[0].text if nodes and len(nodes) > 0 else ''
            if not value:
                value = ''
            self.dei[dei] = value

        if not self.dei[DEI.TradingSymbol] or self.dei[DEI.TradingSymbol] == '':
            self.dei[DEI.TradingSymbol] = self.url.split('/')[-1].split('.')[0].split('-')[0].upper()

        tokens = self.dei[DEI.DocumentPeriodEndDate].split('-')
        tokens = tuple(int(x) for x in tokens)
        self.fiscal_period_end_date = date(tokens[0], tokens[1], tokens[2])

        if not self.dei[DEI.DocumentFiscalYearFocus]:
            self.dei[DEI.DocumentFiscalYearFocus] = self.fiscal_period_end_date.year

        self.fiscal_year = int(self.dei[DEI.DocumentFiscalYearFocus])

    def _find_contexts(self):
        """Find instant and duration contextRef"""
        context_instant = ''
        context_duration = ''
        END_DATE = str(self.fiscal_period_end_date)
        document_type = self.dei[DEI.DocumentType]

        for node in self.doc_root.xpath("//*[local-name() = 'context']"):
            entity_node = None
            period_node = None

            for child in node.getchildren():
                tag = child.tag[child.tag.find('}') + 1:]
                if tag == 'entity':
                    entity_node = child
                elif tag == 'period':
                    period_node = child

            if len(entity_node.getchildren()) != 1:
                continue

            if not 'identifier' in entity_node.getchildren()[0].tag:
                continue

            if len(period_node.getchildren()) == 1:
                instant_node = period_node.getchildren()[0]
                if instant_node.text != END_DATE:
                    continue
                context_instant = node.get('id')

            elif len(period_node.getchildren()) == 2:
                start_date_node = period_node.getchildren()[0]
                end_date_node = period_node.getchildren()[1]
                if end_date_node.text != END_DATE:
                    continue

                if 'Q' in document_type:
                    year, month = self.fiscal_period_end_date.year, self.fiscal_period_end_date.month
                    start_month = 12 if (month - 2) % 12 == 0 else (month - 2) % 12
                    start_year = year - 1 if month <= 2 else year
                    filter_text1 = '{0}-{1:02d}'.format(start_year, start_month)

                    start_month = 12 if (month - 3) % 12 == 0 else (month - 3) % 12
                    start_year = year - 1 if month <= 3 else year
                    filter_text2 = '{0}-{1:02d}'.format(start_year, start_month)

                    if filter_text1 not in start_date_node.text and filter_text2 not in start_date_node.text:
                        continue

                context_duration = node.get('id')

        self.context_instant = context_instant
        self.context_duration = context_duration

    def _get_elementlist(self, fact_name, context_type=Context.Duration):
        """
        In an XBRL xml document, there will be multiple context defined, but only 1 instant context and 1 duration context for current year.
        """
        ret = []
        if context_type == Context.Duration:
            main, secondary = self.context_duration, self.context_instant
        elif context_type == Context.Instant:
            main, secondary = self.context_instant, self.context_duration

        ret.extend(self.doc_root.xpath("//{0}[@contextRef='{1}']".format(fact_name, main), namespaces=self.nsmap))

        if len(ret) == 0:
            ret.extend(self.doc_root.xpath("//{0}[@contextRef='{1}']".format(fact_name, secondary), namespaces=self.nsmap))

        return tuple(ret)

    def get_fact_value(self, fact_name):
        """Given fact_name, return the text for that fact. If not found, return empty string"""
        ret = self._get_elementlist(fact_name)
        return ret[0].text if ret else ''

    def get_dei_value(self, dei_item):
        """A convenience method to get the DEI value from self.dei"""
        if not isinstance(dei_item, DEI):
            raise ValueError('Given dei_item is not of type DEI')
        if dei_item not in self.dei:
            return ''
        return self.dei[dei_item]
```

## fact.py
```py
from openesef.base import ebase


class Fact(ebase.XmlElementBase):
    def __init__(self, default_id, e):
        self.context_ref = e.attrib.get('contextRef')
        self.context = None
        self.unit_ref = e.attrib.get('unitRef')
        self.unit = None
        self.decimals = e.attrib.get('decimals')
        self.precision = e.attrib.get('precision')
        self.value = e.text
        self.footnotes = []
        self.nested_facts = {}
        self.counter = 0
        parsers = {'default': self.l_nested}
        super().__init__(e, parsers, assign_origin=True)
        if self.id is None:
            self.id = default_id

    def l_nested(self, e):
        self.counter += 1
        for e2 in e.iterchildren():
            fct = Fact(f'{self.id}.{self.counter}', e2)
            self.nested_facts[fct.id] = fct
```

## footnote.py
```py
from ..taxonomy import resource


class Footnote(resource.Resource):
    def __init__(self, e):
        super(Footnote, self).__init__(e, assign_origin=True)
        self.facts = []
```

## instance.py
```py
import os
from openesef.instance import m_xbrl
from openesef.base import fbase, const
from openesef.ixbrl import m_ixbrl
from openesef.instance import dei
from lxml import etree as lxml


class Instance(fbase.XmlFileBase):
    def __init__(self, location=None, container_pool=None, root=None, esef_filing_root=None, memfs=None):
        self.pool = container_pool
        self.taxonomy = None
        self.xbrl = None
        self.ixbrl = None
        self.esef_filing_root = esef_filing_root
        parsers = {
            f'{{{const.NS_XHTML}}}html': self.l_ixbrl,
            f'{{{const.NS_XBRLI}}}xbrl': self.l_xbrl
        }
        self.location = location
        
        #20250302 trying to incorporate dei.py into instance.py
        self.xbrl_document = dei.XBRLDocument(location) # Create an instance of XBRLDocument
        self.dei = self.xbrl_document.dei # Access DEI information
        
        super().__init__(location, container_pool, parsers, root, esef_filing_root=esef_filing_root, memfs=memfs)

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        return f"""Namespaces: {len(self.namespaces)}
Schema references: {len(self.xbrl.schema_refs)}
Linkbase references: {len(self.xbrl.linkbase_refs)}
Contexts: {len(self.xbrl.contexts)}
Units: {len(self.xbrl.units)}
Facts: {len(self.xbrl.facts)}
Footnotes: {len(self.xbrl.footnotes)}
Filing Indicators: {len(self.xbrl.filing_indicators)}"""

    def l_xbrl(self, e):
        self.xbrl = m_xbrl.XbrlModel(e, self)

    def l_ixbrl(self, e):
        self.ixbrl = m_ixbrl.IxbrlModel(e, self)
        # Recursive read all namespaces, because in some cases namespace prefixes
        # are defined deeper in the XML structure.
        self.l_namespaces(e)
        # self.l_namespaces_rec(e, target_tags=[
        #     f'{{{const.NS_IXBRL}}}nonNumeric',
        #     f'{{{const.NS_IXBRL}}}nonFraction'])
        self.ixbrl.strip()
        s = ''.join(self.ixbrl.output)
        parser = lxml.XMLParser(huge_tree=True)
        root = lxml.XML(s, parser)
        self.l_xbrl(root)

    def to_xml(self):
        return self.ixbrl.to_xml() if self.ixbrl else self.xbrl.to_xml() if self.xbrl else None
```

## m_xbrl.py
```py
from openesef.instance import fact, footnote, unit, context
from openesef.taxonomy import arc, locator
from openesef.base import ebase, const, util


class XbrlModel(ebase.XmlElementBase):
    def __init__(self, e, container_instance):
        self.instance = container_instance
        if e is None:
            return
        self.linkbase_refs = set([])
        self.schema_refs = set([])
        self.contexts = {}
        self.contexts_hashed = {}  # Key is the hash code based on full context signature, value is the context object
        self.units = {}
        self.units_hashed = {}
        self.facts = {}
        self.footnotes = {}
        self.footnote_links = []
        self.locators = {}
        self.arcs = []
        self.filing_indicators = []
        self.taxonomy = None
        self.output = None
        """ List of available aspects. """
        self.aspects = set({})
        """ Key is the aspect name, value is the list of belonging values """
        self.aspect_values = {}
        self.parsers = {
            'default': self.l_fact,
            f'{{{const.NS_XBRLI}}}xbrl': self.l_xbrl,
            f'{{{const.NS_XBRLI}}}context': self.l_context,
            f'{{{const.NS_XBRLI}}}unit': self.l_unit,
            f'{{{const.NS_LINK}}}schemaRef': self.l_schema_ref,
            f'{{{const.NS_LINK}}}linkbaseRef': self.l_linkbase_ref,
            f'{{{const.NS_LINK}}}footnoteLink': self.l_footnote_link,
            f'{{{const.NS_LINK}}}footnote': self.l_footnote,
            f'{{{const.NS_LINK}}}loc': self.l_locator,
            f'{{{const.NS_LINK}}}footnoteArc': self.load_arc,
            f'{{{const.NS_FIND}}}fIndicators': self.l_filing_indicators,
            f'{{{const.NS_FIND}}}filingIndicator': self.l_filing_indicator
        }
        # Helper dictionaries for merge process
        self.map_ctx = {}  # Map contextRef of merged fact to new contextRef
        self.map_uni = {}  # Map unitRef of merged fact to new unitRef

        super().__init__(e, self.parsers)
        self.compile()

    def l_xbrl(self, e):
        self.l_children(e)

    def l_schema_ref(self, e):
        href = e.attrib.get('{http://www.w3.org/1999/xlink}href')
        self.schema_refs.add(href)

    def l_linkbase_ref(self, e):
        href = e.attrib.get('{http://www.w3.org/1999/xlink}href')
        self.linkbase_refs.add(href)

    def l_context(self, e):
        ctx = context.Context(e)
        asp = 'entityIdentifierAspect'
        self.aspects.add(asp)
        # Note that entity scheme is ignored here. We presume that all identifiers are inside the same namespace.
        self.aspect_values.setdefault(asp, set({})).add(ctx.entity_identifier)
        asp = 'periodAspect'
        self.aspects.add(asp)
        self.aspect_values.setdefault(asp, set({})).add(ctx.get_period_string())
        for d, m in ctx.descriptors.items():  # Descriptors contains XML elements as item values
            self.aspects.add(d)
            self.aspect_values.setdefault(d, set({})).add(m.text if m.tag.endswith('explicitMember') else m[0].text)
        self.contexts[ctx.id] = ctx

    def l_unit(self, e):
        uni = unit.Unit(e)
        asp = 'unitAspect'
        self.aspects.add(asp)
        self.aspect_values.setdefault(asp, set({})).add(uni.get_aspect_value())
        self.units[uni.id] = uni

    def l_fact(self, e):
        fct = fact.Fact(len(self.facts) + 1, e)
        asp = 'conceptAspect'
        self.aspects.add(asp)
        self.aspect_values.setdefault(asp, set({})).add(fct.qname)
        self.facts[fct.id] = fct

    def l_footnote(self, e):
        fn = footnote.Footnote(e)
        self.footnotes[fn.xlabel] = fn

    def l_locator(self, e):
        loc = locator.Locator(e)
        self.locators[loc.label] = loc

    def load_arc(self, e):
        a = arc.Arc(e)
        self.arcs.append(a)

    def l_footnote_link(self, e):
        self.footnote_links.append(e)

    def l_filing_indicators(self, e):
        self.l_children(e)

    def l_filing_indicator(self, e):
        self.filing_indicators.append(e)

    def compile(self):
        # Set references to contexts
        for fct in self.facts.values():
            fct.context = self.contexts.get(fct.context_ref, None)
            fct.unit = self.units.get(fct.unit_ref, None)
        # Set links between facts and footnotes
        for footnote_link in self.footnote_links:
            self.locators = {}
            self.arcs = []
            self.l_children(footnote_link)
        # Traversing arcs
        if self.arcs:
            for a in self.arcs:
                loc = self.locators.get(a.xl_from)
                if loc is None:
                    continue
                fct = self.facts.get(loc.fragment_identifier, None)
                fn = self.footnotes.get(a.xl_to)
                if fct is None or fn is None:
                    continue
                fct.footnotes.append(fn)
                fn.facts.append(fct)
        self.locators = None
        self.arcs = None

    def index_hashed(self):
        self.contexts_hashed = {}
        for ctx in self.contexts.values():
            sig_hash = util.get_hash(ctx.get_signature())
            self.contexts_hashed[sig_hash] = ctx

        self.units_hashed = {}
        for uni in self.units.values():
            sig_hash = util.get_hash(uni.get_aspect_value())
            self.units_hashed[sig_hash] = uni

    def merge(self, xid):
        self.index_hashed()
        self.merge_contexts(xid)
        self.merge_units(xid)
        self.merge_facts(xid)
        # TODO: Merge footnotes and references

    def merge_facts(self, xid):
        # Merge facts
        for fct in xid.facts.values():
            if fct.context_ref in self.map_ctx:
                fct.context_ref = self.map_ctx[fct.context_ref]
            fct.context = self.contexts.get(fct.context_ref, None)
            if fct.unit_ref in self.map_uni:
                fct.unit_ref = self.map_uni[fct.unit_ref]
            fct.unit = self.units.get(fct.unit_ref, None)
            if fct.id in self.facts:
                new_fct_id = f'f{(len(self.facts)+1)}'
                fct.id = new_fct_id
            self.facts[fct.id] = fct

    def merge_units(self, xid):
        self.map_uni = {}  # Map unitRef of merged fact to new unitRef
        # Merge units of new instance document into its own units
        for uid, uni in xid.units.items():
            msr = uni.get_aspect_value()
            uni_hash = util.get_hash(msr)
            if uid in self.units:
                # There is already an unit with the same id
                # Try to find an existing unit with the same signature
                existing_uni = self.units.get(uni_hash, None)
                if existing_uni is None:
                    # We create a new id
                    uni.id = uni_hash
                    self.units[uni_hash] = uni
                    self.units_hashed[uni_hash] = uni
                    self.map_uni[uni.id] = uni_hash
                else:
                    # Replace unitRef
                    self.map_uni[uni.id] = existing_uni.id
            else:
                # Just add merged unit to current document
                self.units[uni.id] = uni
                self.units_hashed[uni_hash] = uni

    def merge_contexts(self, xid):
        self.map_ctx = {}  # Map contextRef of merged fact to new contextRef
        for cid, ctx in xid.contexts.items():
            sig_hash = util.get_hash(ctx.get_signature())
            if cid in self.contexts:
                # There is already a context with that id - Replace contextRef
                # Try to find a context with identical signature
                existing_ctx = self.contexts_hashed.get(sig_hash, None)
                if existing_ctx is None:
                    # If there is no existing context with that signature, we create a new id for the merged context
                    # and add it to contexts in current document
                    ctx.id = sig_hash
                    self.contexts[sig_hash] = ctx
                    self.contexts_hashed[sig_hash] = ctx
                    self.map_ctx[ctx.id] = sig_hash
                else:
                    # If there is an existing context with that signature, we just replace the context ref
                    self.map_ctx[ctx.id] = existing_ctx.id
            else:
                # Add the merged context to current document
                self.contexts[ctx.id] = ctx
                self.contexts_hashed[sig_hash] = ctx

    def serialize(self):
        self.output = []
        self.output.append(const.XML_START)
        self.output.append(f'<xbrl xmlns="{const.NS_XBRLI}" ')
        for ns in self.instance.namespaces.items():
            self.output.append(f'xmlns:{ns[0]}="{ns[1]}" ')
        self.output.append('>')
        self.serialize_refs()
        self.serialize_contexts()
        self.serialize_units()
        self.serialize_facts()
        self.serialize_footnotes()
        self.output.append('</xbrl>')

    def serialize_footnotes(self):
        if not len(self.footnotes):
            return
        self.output.append(
            f'<link:footnoteLink xlink:role="{const.ROLE_LINK}" xlink:type="extended">')
        # First pass - just collect facts
        facts = set([])
        for it in self.footnotes.items():
            f = it[1]
            for fct in f.facts:
                facts.add(fct)
        # Serialize locators for facts
        for fct in facts:
            self.output.append(f'<link:loc xlink:href="#{fct.id}" xlink:label="{fct.id}" xlink:type="locator"/>')
        # Second pass - serialize footnotes
        for it in self.footnotes.items():
            f = it[1]
            self.output.append(f.serialize())
            # Serialize fact-footnote arcs
            for fct in f.facts:
                self.output.append(
                    f'<link:footnoteArc xlink:arcrole="{const.FACT_FOOTNOTE_ARCROLE}" '
                    f'xlink:from="{fct.id}" xlink:to="{f.id}" xlink:type="arc"/>')
        self.output.append(f'</link:footnoteLink>')

    def serialize_units(self):
        for it in self.units.items():
            u = it[1]
            self.output.append(u.serialize())

    def serialize_facts(self):
        for it in self.facts.items():
            f = it[1]
            self.output.append(f.serialize())

    def serialize_refs(self):
        for r in self.schema_refs:
            self.output.append(f'<link:schemaRef xlink:href="{r}" xlink:type="simple"/>')
        for r in self.linkbase_refs:
            self.output.append(f'<link:linkbaseRef xlink:href="{r}" xlink:type="simple"/>')

    def serialize_dimensional_container(self, dc, name):
        self.output.append(f'<{name}>')
        for it in dc.items():
            e = it[1]
            eb = ebase.XmlElementBase(e, assign_origin=True)
            self.output.append(eb.serialize())
        self.output.append(f'</{name}>')

    def serialize_contexts(self):
        for pair in self.contexts.items():
            c = pair[1]
            self.output.append(f'<context id="{c.id}">')
            self.output.append(f'<entity>')
            self.output.append(f'<identifier scheme="{c.entity_scheme}">{c.entity_identifier}</identifier>')
            if c.segment:
                self.serialize_dimensional_container(c.segment, 'segment')
            self.output.append(f'</entity>')
            self.output.append(f'<period>')
            if c.period_instant:
                self.output.append(f'<instant>{c.period_instant}</instant>')
            else:
                self.output.append(f'<startDate>{c.period_start}</startDate>')
                self.output.append(f'<endDate>{c.period_end}</endDate>')
            self.output.append(f'</period>')
            if c.scenario:
                self.serialize_dimensional_container(c.scenario, 'scenario')
            self.output.append(f'</entity>')
            self.output.append(f'</context>')

    def to_xml(self):
        self.serialize()
        return ''.join(self.output)
```

## unit.py
```py
from ..base import ebase, const


class Unit(ebase.XmlElementBase):
    def __init__(self, e):
        self.measure = []
        self.numerator = []
        self.denominator = []
        self.active_measure_list = self.measure
        parsers = {
            f'{{{const.NS_XBRLI}}}unit': self.l_unit,
            f'{{{const.NS_XBRLI}}}measure': self.l_measure,
            f'{{{const.NS_XBRLI}}}divide': self.l_divide,
            f'{{{const.NS_XBRLI}}}unitNumerator': self.l_numerator,
            f'{{{const.NS_XBRLI}}}unitDenominator': self.l_denominator
        }
        super().__init__(e, parsers, assign_origin=True)

    def l_unit(self, e):
        self.l_children(e)

    def l_measure(self, e):
        self.active_measure_list.append(e)

    def l_numerator(self, e):
        self.active_measure_list = self.numerator
        self.l_children(e)

    def l_denominator(self, e):
        self.active_measure_list = self.denominator
        self.l_children(e)

    def l_divide(self, e):
        self.l_children(e)

    def get_aspect_value(self):
        if self.measure:
            return ','.join([m.text for m in self.measure])
        else:
            num = ','.join(m.text for m in self.numerator)
            den = ','.join(m.text for m in self.denominator)
            return f'{num}/{den}'
```
