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
