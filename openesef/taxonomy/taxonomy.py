from openesef.base import const, data_wrappers, util
from openesef.taxonomy.xdt import dr_set
#from io import StringIO, BytesIO

from openesef.util.util_mylogger import setup_logger #util_mylogger
import logging 
if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.taxonomy") 

import traceback


class Taxonomy:
    """ entry_points is a list of entry point locations
        cache_folder is the place where to store cached Web resources """
    def __init__(self, entry_points, container_pool, esef_filing_root = None, in_memory_content = {}, memfs=None):
        self.entry_points = entry_points
        self.pool = container_pool
        self.pool.current_taxonomy = self
        self.pool.current_taxonomy_hash = util.get_hash(','.join(entry_points)) if entry_points else None
        self.esef_filing_root = esef_filing_root  # Add ESEF location path
        self.in_memory_content = in_memory_content or {} # Dictionary to store in-memory content
        self.memfs = memfs
        # All schemas indexed by resolved location 
        self.schemas = {}
        # All linkbases indexed by resolved location 
        self.linkbases = {}
        self.processing_schemas = set()  # Track schemas being processed to prevent loops
        # All concepts  indexed by full id - target namespace + id 
        self.concepts = {}
        # All concepts indexed by QName
        self.concepts_by_qname = {}
        # General elements, which are not concepts 
        self.elements = {}
        self.elements_by_id = {}
        # All base set objects indexed by base set key 
        self.base_sets = {}
        # Dimension defaults - Key is dimension QName, value is default member concept 
        self.defaults = {}
        # Default Members - Key is the default member QName, value is the corresponding dimension concept. 
        self.default_members = {}
        # Dimensional Relationship Sets 
        self.dr_sets = {}
        # Excluding Dimensional Relationship Sets 
        self.dr_sets_excluding = {}
        # Key is primary item QName, value is the list of dimensional relationship sets, where it participates. 
        self.idx_pi_drs = {}
        # Key is the Qname of the dimensions. Value is the set of DR keys, where this dimension participates 
        self.idx_dim_drs = {}
        # Key is the QName of the hypercube. Value is the set of DR Keys, where this hypercube participates. 
        self.idx_hc_drs = {}
        # Key is the QName of the member. Value is the set of DR keys, where this member participates. 
        self.idx_mem_drs = {}
        # All table resources in taxonom 
        self.tables = {}
        # All role types in all schemas 
        self.role_types = {}
        self.role_types_by_href = {}
        # All arcrole types in all schemas 
        self.arcrole_types = {}
        self.arcrole_types_by_href = {}
        # Global resources - these, which have an id attribute 
        self.resources = {}
        # All locators 
        self.locators = {}
        # All parameters 
        self.parameters = {}
        # All assertions by type 
        self.value_assertions = {}
        self.existence_assertions = {}
        self.consistency_assertions = {}
        # Assertion Sets 
        self.assertion_sets = {}
        # Simple types 
        self.simple_types = {}
        # Complex types with simple content. Key is the QName, value is the item type object. 
        self.item_types = {}
        # Complex types with simple content. Key is the unique identifier, value is the item type object. 
        self.item_types_by_id = {}
        # Complex types with complex content: Key is qname, value is the tuple type object 
        self.tuple_types = {}
        # Complex types with complex content: Key is unique identifier, value is the tuple type object 
        self.tuple_types_by_id = {}
        if entry_points:
            self.load()
            self.compile()

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        return '\n'.join([
            f'Schemas: {len(self.schemas)}',
            f'Linkbases: {len(self.linkbases)}',
            f'Role Types: {len(self.role_types)}',
            f'Arcrole Types: {len(self.arcrole_types)}',
            f'Concepts: {len(self.concepts)}',
            f'Item Types: {len(self.item_types)}',
            f'Tuple Types: {len(self.tuple_types)}',
            f'Simple Types: {len(self.simple_types)}',
            f'Labels: {sum([0 if not "label" in c.resources else len(c.resources["label"]) for c in self.concepts.values()])}',
            f'References: {sum([0 if not "reference" in c.resources else len(c.resources["reference"]) for c in self.concepts.values()])}',
            f'Hierarchies: {len(self.base_sets)}',
            f'Dimensional Relationship Sets: {len(self.base_sets)}',
            f'Dimensions: {len([c for c in self.concepts.values() if c.is_dimension])}',
            f'Hypercubes: {len([c for c in self.concepts.values() if c.is_hypercube])}',
            f'Enumerations: {len([c for c in self.concepts.values() if c.is_enumeration])}',
            f'Enumerations Sets: {len([c for c in self.concepts.values() if c.is_enumeration_set])}',
            f'Table Groups: {len([c for c in self.concepts.values() if "table" in c.resources])}',
            f'Tables: {len(self.tables)}',
            f'Parameters: {len(self.parameters)}',
            f'Assertion Sets: {len(self.assertion_sets)}',
            f'Value Assertions: {len(self.value_assertions)}',
            f'Existence Assertions: {len(self.existence_assertions)}',
            f'Consistency Assertions: {len(self.consistency_assertions)}'
        ])

    def _process_entry_point(self, entry_point):
        """Process a single entry point, tracking schema loading status"""
        if entry_point in self.processing_schemas:
            return  # Skip if already processing this schema
            
        self.processing_schemas.add(entry_point)
        try:
            # Load the schema
            #schema_obj = self.container_pool.add_schema(entry_point, self.esef_filing_root)
            schema_obj = self.pool.add_schema(location=entry_point, 
                                              esef_filing_root=self.esef_filing_root, 
                                              memfs=self.memfs)
            if schema_obj:
                self.schemas[entry_point] = schema_obj
        except Exception as e:
            logger.error(f'Taxonomy._process_entry_point(): Error processing {entry_point}: {e}')
            traceback.print_exc(limit=10)
        finally:
            self.processing_schemas.remove(entry_point)

    def load(self):
        for ep in self.entry_points:
            logger.debug(f'Taxonomy.load(): Loading {ep} with self.esef_filing_root={self.esef_filing_root}')
            logger.debug(f'Calling self.pool.add_reference(...) with href = {ep}, base = "", esef_filing_root = {self.esef_filing_root}')
            # Check if we have in-memory content
            if self.in_memory_content and ep in self.in_memory_content:
                logger.debug(f'Loading {ep} from memory')
                content = self.in_memory_content[ep]
                self.pool.add_reference_from_string(content, ep, '')
            else:
                logger.debug(f'Loading {ep} from file/URL')
                #self.pool.add_reference(href=ep, base='', esef_filing_root=self.esef_filing_root)

                self.pool.add_reference(href = ep, 
                                    base = '', 
                                    esef_filing_root = self.esef_filing_root,
                                    memfs = self.memfs)
            self._process_entry_point(ep)

    def add_in_memory_content(self, location, content):
        """Add content to be loaded from memory for a specific location"""
        self.in_memory_content[location] = content


    def resolve_prefix(self, pref):
        for sh in self.schemas.values():
            ns = sh.namespaces.get(pref, None)
            if ns is not None:
                return ns
        return None

    def resolve_qname(self, qname):
        pref = qname.split(':')[0] if ':' in qname else ''
        ns = self.resolve_prefix(pref)
        nm = qname.split(':')[1] if ':' in qname else qname
        return f'{ns}:{nm}'

    def attach_schema(self, href, sh):
        if href in self.schemas:
            return
        self.schemas[href] = sh
        for key, imp in sh.imports.items():
            logger.debug(f'Taxonomy.attach_schema(): Adding import {key} from {sh.base} with self.esef_filing_root={self.esef_filing_root}')
            logger.debug(f'Calling self.pool.add_reference(...) with href = {key}, base = {sh.base}, esef_filing_root = {self.esef_filing_root}')
            self.pool.add_reference(href = key, 
                                    base = sh.base, 
                                    esef_filing_root = self.esef_filing_root,
                                    memfs = self.memfs)
        for key, ref in sh.linkbase_refs.items():
            logger.debug(f'Taxonomy.attach_schema(): Adding linkbase {key} from {sh.base} with self.esef_filing_root={self.esef_filing_root}') 
            logger.debug(f'Calling self.pool.add_reference(...) with href = {key}, base = {sh.base}, esef_filing_root = {self.esef_filing_root}')
            self.pool.add_reference(href = key, 
                                    base = sh.base, 
                                    esef_filing_root = self.esef_filing_root,
                                    memfs = self.memfs)

    def attach_linkbase(self, href, lb):
        if href in self.linkbases:
            return
        self.linkbases[href] = lb
        for href in lb.refs:
            logger.debug(f'Taxonomy.attach_linkbase(): Adding reference {href} from {lb.base} with self.esef_filing_root={self.esef_filing_root}')
            logger.debug(f'Calling self.pool.add_reference(...) with href = {href}, base = {lb.base}, esef_filing_root = {self.esef_filing_root}')
            self.pool.add_reference(href = href, 
                                    base = lb.base, 
                                    esef_filing_root = self.esef_filing_root,
                                    memfs = self.memfs)

    def get_bs_roots(self, arc_name, role, arcrole):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}')
        if not bs:
            return None
        return bs.roots

    def get_bs_members(self, arc_name, role, arcrole, start_concept=None, include_head=True):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}', None)
        if not bs:
            return None
        return bs.get_members(start_concept, include_head)

    def get_enumerations(self):
        enumerations = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enumerations.get(key)
            if not e:
                members = self.get_bs_members('definitionArc', c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE, c.domain, c.head_usable)
                e = data_wrappers.Enumeration(key, [], [] if members is None else [m.Concept for m in members])
                enumerations[key] = e
            e.Concepts.append(c)
        return enumerations

    def get_enumeration_sets(self):
        enum_sets = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationSetItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enum_sets.get(key)
            if not e:
                members = self.get_bs_members('definitionArc', c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE, c.domain, c.head_usable)
                if members is None:
                    continue
                e = data_wrappers.Enumeration(key, [], [m.Concept for m in members])
                enum_sets[key] = e
            e.Concepts.append(c)
        return enum_sets

    def compile(self):
        self.compile_schemas()
        self.compile_linkbases()
        self.compile_defaults()
        self.compile_dr_sets()

    def compile_schemas(self):
        for sh in self.schemas.values():
            for c in sh.concepts.values():
                self.concepts_by_qname[c.qname] = c
                if c.id is not None:
                    key = f'{sh.location}#{c.id}'  # Key to search from locator href
                    self.concepts[key] = c
            for key, e in sh.elements.items():
                self.elements[key] = e
            for key, e in sh.elements_by_id.items():
                self.elements_by_id[key] = e
            for key, art in sh.arcrole_types.items():
                self.arcrole_types[key] = art
                self.arcrole_types_by_href[f'{sh.location}#{art.id}'] = art
            for key, rt in sh.role_types.items():
                self.role_types[key] = rt
                self.role_types_by_href[f'{sh.location}#{rt.id}'] = rt

            for key, it in sh.item_types.items():
                self.item_types[key] = it
            for key, it in sh.item_types_by_id.items():
                self.item_types_by_id[key] = it
            for key, tt in sh.tuple_types.items():
                self.tuple_types[key] = tt
            for key, tt in sh.tuple_types_by_id.items():
                self.tuple_types_by_id[key] = tt

            for key, st in sh.simple_types.items():
                self.simple_types[key] = st

    def compile_linkbases(self):
        # Pass 1 - Index global objects
        for lb in self.linkbases.values():
            for xl in lb.links:
                for key, loc in xl.locators_by_href.items():
                    self.locators[key] = loc
                for key, l_res in xl.resources.items():
                    for res in l_res:
                        if res.id:
                            href = f'{xl.linkbase.location}#{res.id}'
                            self.resources[href] = res
        # Pass 2 - Connect resources to each other
        for lb in self.linkbases.values():
            for xl in lb.links:
                xl.compile()

    def compile_defaults(self):
        # key = f'definitionArc|{const.XDT_DIMENSION_DEFAULT_ARCROLE}|{const.ROLE_LINK}'
        frag = f'definitionArc|{const.XDT_DIMENSION_DEFAULT_ARCROLE}'
        for key, bs in self.base_sets.items():
            if frag not in key:
                continue
            bs = self.base_sets.get(key, None)
        # if bs is None:
        #     return
            for dim in bs.roots:
                chain_dn = dim.chain_dn.get(key, None)
                if chain_dn is None:
                    continue
                for def_node in chain_dn:
                    self.defaults[dim.qname] = def_node.Concept.qname
                    self.default_members[def_node.Concept.qname] = dim.qname

    def compile_dr_sets(self):
        for bs in [bs for bs in self.base_sets.values() if bs.arc_name == 'definitionArc']:
            if bs.arcrole == const.XDT_DIMENSION_DEFAULT_ARCROLE:
                self.add_default_member(bs)
                continue
            if bs.arcrole == const.XDT_ALL_ARCROLE:
                self.add_drs(bs, self.dr_sets)
                continue
            if bs.arcrole == const.XDT_NOTALL_ARCROLE:
                self.add_drs(bs, self.dr_sets_excluding)
                continue

    def add_drs(self, bs, drs_collection):
        drs = dr_set.DrSet(bs, self)
        drs.compile()
        drs_collection[bs.get_key()] = drs

    def add_default_member(self, bs):
        for d in bs.roots:
            members = bs.get_members(start_concept=d, include_head=False)
            if not members:
                continue
            for m in members:
                self.defaults[d.qname] = m
                self.default_members[m.qname] = d

    def get_prefixes(self):
        return set(c.prefix for c in self.concepts.values())

    def get_languages(self):
        return set([r.lang for k, r in self.resources.items() if r.name == 'label'])
