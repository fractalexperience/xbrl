# Project Structure
```
📦 openesef/base
    ├── 📄 .DS_Store
    ├── 📄 __init__.py
    ├── 📄 archiver.py
    ├── 📄 const.py
    ├── 📄 cube.py
    ├── 📄 data_wrappers.py
    ├── 📄 ebase.py
    ├── 📄 element.py
    ├── 📄 fbase.py
    ├── 📄 pool.py
    ├── 📄 resolver.py
    ├── 📄 tax_to_pd.py
    ├── 📄 try_virtualfs.py
    └── 📄 util.py
```


#  Project Contents
## __init__.py
```py
# Import all base modules
from . import resolver
from . import pool
from . import const
from . import util
```

## archiver.py
```py
from zipfile import ZipFile, ZIP_DEFLATED
from openesef.base import util
import lxml.html as lhtml
import zlib
import os
import json


class Archiver:
    """ Basic class for storing content in ZIP archives """

    def __init__(self, zip_folder, length=3):
        self.zip_folder = zip_folder
        if not os.path.exists(self.zip_folder):
            os.mkdir(self.zip_folder)
        """ Length of archive ZIP files Because we have 16 possible characters for file name, the total number of 
        ZIP files is 16^length. For example 2 corresponds to 256 files, 3 corresponds to 4096 files etc. """
        self.archive_file_length = min(max(1, length), 4)
        """ All open archives."""
        self.zip_cache = {}
        """ All written file names."""
        self.written_hashes = set()
        """ Key is the original reference (inside HTML), value is the resolved content based hash. """
        self.map_id_hash = {}
        """ Temporary cache for HTMl files. """
        self.html_cache = {}

    def create_archive(self, file_hash):
        zfn = f'{os.path.join(self.zip_folder, file_hash)}.zip'
        if os.path.exists(zfn):
            os.remove(zfn)
        return ZipFile(zfn, 'w', compression=zlib.DEFLATED)

    def get_archive(self, filename, zip_prefix=None):
        if zip_prefix is None:
            zip_prefix = self.get_zip_prefix(filename)
        zip_path = os.path.join(self.zip_folder, f'{zip_prefix}.zip')
        archive = self.zip_cache.get(zip_prefix)
        if archive is not None:
            return archive
        if os.path.exists(zip_path):
            archive = ZipFile(zip_path, mode='a', compression=ZIP_DEFLATED, compresslevel=7)
        else:
            archive = self.create_archive(zip_prefix)
        self.zip_cache[zip_prefix] = archive
        return archive

    def get_zip_prefix(self, filename):
        hsh = util.get_sha1(filename)
        pref = hsh[:self.archive_file_length]
        return pref

    def store_content(self, filename, content, zip_prefix=None):
        archive = self.get_archive(filename, zip_prefix)
        if filename in self.written_hashes:
            return
        try:
            archive.writestr(filename, content)
            self.written_hashes.add(filename)
        except ValueError:
            print('Archive is closed')
        except Exception as ex:
            print(ex)

    def store_html(self, filename, content):
        if content is None:
            return
        s = content if isinstance(content, str) else (
            content.decode() if isinstance(content, bytes) else ''.join(content))
        self.html_cache[filename] = s

    def flush_html(self):
        # Index content hash map
        print('Index content hash map', len(self.html_cache), 'items')
        map_id_dom = {}
        for filename, s in self.html_cache.items():
            ext = '' if '.' not in filename else filename.split('.')[-1]
            content_hash = util.get_sha1(filename)
            if not s.startswith('<?xml'):
                try:
                    dom = lhtml.fromstring(s)
                    # Calculate a hash code based on content. IMPORTANT: We remove href attributes before calculating hash.
                    content_no_hrefs = lhtml.tostring(lhtml.rewrite_links(dom, lambda l: None))
                    content_hash = util.get_sha1(content_no_hrefs.decode())
                    map_id_dom[filename] = dom
                except:
                    continue
            self.map_id_hash[filename] = f'{content_hash}.{ext}'

        # Replace references inside HTML reports with content based hashes and save to ZIP archives
        print('Replace references inside HTML reports', len(self.html_cache), 'items')
        for filename, s in self.html_cache.items():
            content_reduced_hrefs = s
            dom = map_id_dom.get(filename)
            content_hash = self.map_id_hash.get(filename)
            if dom is not None:
                content_reduced_hrefs = lhtml.tostring(lhtml.rewrite_links(
                    dom, lambda l: self.map_id_hash.get(l, l) if '=' not in l else
                    l.split('=')[0] + '=' +
                    self.map_id_hash.get(l.split('=')[1] + '.html',
                                         self.map_id_hash.get(l.split('=')[1] + '.xml', '')).split('.')[0]))

            ext = '' if '.' not in filename else filename.split('.')[-1]
            new_filename = f'{content_hash}'
            # Store resolved HTML content
            self.store_content(new_filename, content_reduced_hrefs, new_filename[:self.archive_file_length])

    def close(self):
        # Store collected HTML files in the cache
        self.flush_html()
        # Flush content of ZIP archives
        for zip_id, archive in self.zip_cache.items():
            archive.close()
        self.zip_cache = {}
        # Clear HTMl cache
        self.html_cache = {}

        # with open(os.path.join(self.zip_folder, 'map.json'), "w") as f:
        #     json.dump(self.map_id_hash, f)
        # print('closed - written hashes: ', len(self.written_hashes))

    def open(self):
        files = [it.path for it in os.scandir(self.zip_folder) if it.path.endswith('zip')]
        # print(len(files), 'ZIP archives found')
        for file in files:
            archive = ZipFile(file, mode='r')
            pref = file.split(os.sep)[-1].split('.')[0]
            # self.zip_cache[pref] = archive
            self.written_hashes.update(set([f.filename for f in archive.filelist]))
            archive.close()
        # print('opened - written hashes: ', len(self.written_hashes))

    def reset_database(self):
        exts = ['zip']
        files = [i.path for i in os.scandir(self.zip_folder) if i.path.split('.')[-1] in exts]
        # Conversion to list is needed in order to execute the loop
        list(map(lambda z: os.remove(z), files))
        # print(len(files), f'files deleted from {self.zip_folder} folder')

    def read_content(self, filename):
        archive = self.get_archive(filename)
        try:
            with archive.open(filename, 'r') as f:
                return f.read().decode()
        except KeyError:
            return self.read_content_hash(filename)
        except Exception as ex:
            print(ex)
        return None

    def read_content_hash(self, filename):
        # Now try to find a hashed file name
        filename_resolved = self.map_id_hash.get(filename)
        if filename_resolved is None:
            return None
        archive = self.get_archive(filename_resolved)
        with archive.open(filename, 'r') as f:
            return f.read().decode()
```

## const.py
```py
# Namespaces
# Basic XML
NS_XML = 'http://www.w3.org/XML/1998/namespace'
NS_XS = 'http://www.w3.org/2001/XMLSchema'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
# XHTML
NS_XHTML = 'http://www.w3.org/1999/xhtml'
# IXBRL
NS_IXBRL = 'http://www.xbrl.org/2013/inlineXBRL'
NS_IXBRL_2008 = 'http://www.xbrl.org/2008/inlineXBRL'
NS_IXBRL_TRANSFORMATION = 'http://www.xbrl.org/inlineXBRL/transformation/2010-04-20'
# XLINK
NS_XLINK = 'http://www.w3.org/1999/xlink'
# Basic XBRL
NS_XBRLI = 'http://www.xbrl.org/2003/instance'
NS_LINK = 'http://www.xbrl.org/2003/linkbase'
NS_ISO4217 = 'http://www.xbrl.org/2003/iso4217'
# XBRL XDT
NS_XBRLDI = 'http://xbrl.org/2006/xbrldi'
NS_XBRLDT = 'http://xbrl.org/2005/xbrldt'
# Table Linkbase
NS_TABLE = 'http://xbrl.org/2014/table'
# EBA
NS_FIND = 'http://www.eurofiling.info/xbrl/ext/filing-indicators'
# Generic links
NS_GEN = 'http://xbrl.org/2008/generic'
# Generic labels
NS_GEN_LABEL = 'http://xbrl.org/2008/label'
# Generic references
NS_GEN_REF = 'http://xbrl.org/2008/reference'
# Taxonomy Package
NS_TAXONOMY_PACKAGE = 'http://xbrl.org/2016/taxonomy-package'
NS_TAXONOMY_PACKAGE_PR = 'http://xbrl.org/PR/2015-12-09/taxonomy-package'  # The old one
NS_OASIS_CATALOG = 'urn:oasis:names:tc:entity:xmlns:xml:catalog'
# Extensible Enumerations
NS_EXTENSIBLE_ENUMERATIONS = 'http://xbrl.org/2014/extensible-enumerations'
NS_EXTENSIBLE_ENUMERATIONS_2 = 'http://xbrl.org/2020/extensible-enumerations-2.0'
# OTHER
KNOWN_PROTOCOLS = ['http', 'https', 'ftp']
SUBSTITUTION_GROUPS = ['item', 'tuple']
# Arc names
ARC_PRESENTATION = 'presentationArc'
ARC_DEFINITION = 'definitionArc'
ARC_CALCULATION = 'calculationArc'
ARC_LABEL = 'labelArc'
ARC_REFERENCE = 'referenceArc'
ARC_FOOTNOTE = 'footnoteArc'
ARC_ARC = 'arc'
ARC_TABLE_BREAKDOWN = 'tableBreakdownArc'
ARC_BREAKDOWN_TREE = 'breakdownTreeArc'
ARC_TABLE_FILTER = 'tableFilterArc'
ARC_TABLE_PARAMETER = 'tableParameterArc'
ARC_DEFNODE_SUBTREE = 'definitionNodeSubtreeArc'
ARC_ASPECTNODE_FILTER = 'aspectNodeFilterArc'

# Extended link role
ROLE_LINK = 'http://www.xbrl.org/2003/role/link'
# Standard roles
ROLE_LABEL = 'http://www.xbrl.org/2003/role/label'
ROLE_LABEL_2008 = 'http://www.xbrl.org/2008/role/label'
ROLE_LABEL_TERSE = 'http://www.xbrl.org/2003/role/terseLabel'
ROLE_LABEL_VERBOSE = 'http://www.xbrl.org/2003/role/verboseLabel'
ROLE_LABEL_POSITIVE = 'http://www.xbrl.org/2003/role/positiveLabel'
ROLE_LABEL_POSITIVE_TERSE = 'http://www.xbrl.org/2003/role/positiveTerseLabel'
ROLE_LABEL_POSITIVE_VERBOSE = 'http://www.xbrl.org/2003/role/positiveVerboseLabel'
ROLE_LABEL_NEGATIVE = 'http://www.xbrl.org/2003/role/negativeLabel'
ROLE_LABEL_NEGATIVE_TERSE = 'http://www.xbrl.org/2003/role/negativeTerseLabel'
ROLE_LABEL_NEGATIVE_VERBOSE = 'http://www.xbrl.org/2003/role/negativeVerboseLabel'
ROLE_LABEL_ZERO = 'http://www.xbrl.org/2003/role/zeroLabel'
ROLE_LABEL_ZERO_TERSE = 'http://www.xbrl.org/2003/role/zeroTerseLabel'
ROLE_LABEL_ZERO_VERBOSE = 'http://www.xbrl.org/2003/role/zeroVerboseLabel'
ROLE_LABEL_PERIOD_START = 'http://www.xbrl.org/2003/role/periodStartLabel'
ROLE_LABEL_PERIOD_END = 'http://www.xbrl.org/2003/role/periodEndLabel'
ROLE_LABEL_DEFINITION = 'http://www.xbrl.org/2003/role/documentation'
ROLE_LABEL_DEFINITION_GUIDANCE = 'http://www.xbrl.org/2003/role/definitionGuidance'
ROLE_LABEL_DISCLOSURE_GUIDANCE = 'http://www.xbrl.org/2003/role/disclosureGuidance'
ROLE_LABEL_PRESENTATION_GUIDANCE = 'http://www.xbrl.org/2003/role/presentationGuidance'
ROLE_LABEL_TOTAL = 'http://www.xbrl.org/2003/role/totalLabel'
# EBA/EIOPA
ROLE_LABEL_RC = 'http://www.eurofiling.info/xbrl/role/rc-code'
ROLE_LABEL_DB = 'http://www.eba.europa.eu/xbrl/role/dpm-db-id'

# Reference roles
ROLE_REFERENCE = 'http://www.xbrl.org/2003/role/reference'
ROLE_REF_DEFINITION = 'http://www.xbrl.org/2003/role/definitionRef'
ROLE_REF_DISCLOSURE = 'http://www.xbrl.org/2003/role/disclosureRef'
ROLE_REF_MANDATORY_DISCLOSURE = 'http://www.xbrl.org/2003/role/mandatoryDisclosureRef'
ROLE_REF_RECOMMENDED_DISCLOSURE = 'http://www.xbrl.org/2003/role/recommendedDisclosureRef'
ROLE_REF_UNSPECIFIED_DISCLOSURE = 'http://www.xbrl.org/2003/role/unspecifiedDisclosureRef'
ROLE_REF_PRESENTATION = 'http://www.xbrl.org/2003/role/presentationRef'
ROLE_REF_MEASUREMENT = 'http://www.xbrl.org/2003/role/measurementRef'
ROLE_REF_COMMENTARY = 'http://www.xbrl.org/2003/role/commentaryRef'
ROLE_REF_EXAMPLE = 'http://www.xbrl.org/2003/role/exampleRef'
# Standard arcroles
# Fact-footnote
FACT_FOOTNOTE_ARCROLE = 'http://www.xbrl.org/2003/arcrole/fact-footnote'
# LabelResource
CONEPT_LABEL_ARCROLE = 'http://www.xbrl.org/2003/arcrole/concept-label'
# Reference
CONCEPT_REFERENCE_ARCROLE = 'http://www.xbrl.org/2003/arcrole/concept-reference'
# Presentation
PARENT_CHILD_ARCROLE = 'http://www.xbrl.org/2003/arcrole/parent-child'
# Calculation
SUMMATION_ITEM_ARCROLE = 'http://www.xbrl.org/2003/arcrole/summation-item'
# Definition
GENERAL_SPECIAL_ARCROLE = 'http://www.xbrl.org/2003/arcrole/general-special'
ESSENCE_ALIAS_ARCROLE = 'http://www.xbrl.org/2003/arcrole/essence-alias'
SIMILAR_TUPLE_ARCROLE = 'http://www.xbrl.org/2003/arcrole/similar-tuples'
REQUIRES_ELEMENT_ARCROLE = 'http://www.xbrl.org/2003/arcrole/requires-element'
# XDT
XDT_ALL_ARCROLE = 'http://xbrl.org/int/dim/arcrole/all'
XDT_NOTALL_ARCROLE = 'http://xbrl.org/int/dim/arcrole/notAll'
XDT_HYPERCUBE_DIMENSION_ARCROLE = 'http://xbrl.org/int/dim/arcrole/hypercube-dimension'
XDT_DIMENSION_DOMAIN_ARCROLE = 'http://xbrl.org/int/dim/arcrole/dimension-domain'
XDT_DOMAIN_MEMBER_ARCROLE = 'http://xbrl.org/int/dim/arcrole/domain-member'
XDT_DIMENSION_DEFAULT_ARCROLE = 'http://xbrl.org/int/dim/arcrole/dimension-default'
# Table Linkbase
TABLE_BREAKDOWN_ARCROLE = 'http://xbrl.org/arcrole/2014/table-breakdown'
BREAKDOWN_TREE_ARCROLE = 'http://xbrl.org/arcrole/2014/breakdown-tree'
TABLE_FILTER_ARCROLE = 'http://xbrl.org/arcrole/2014/table-filter'
TABLE_PARAMETER_ARCROLE = 'http://xbrl.org/arcrole/2014/table-parameter'
DEFINITIONNODE_SUBTREE_ARCROLE = 'http://xbrl.org/arcrole/2014/definition-node-subtree'
DEFINITIONNODE_SUBTREE_ARCROLE_2013 = 'http://xbrl.org/arcrole/PR/2013-12-18/definition-node-subtree'
ASPECTNODE_FILTER_ARCROLE = 'http://xbrl.org/arcrole/2014/aspect-node-filter'
ASPECTNODE_FILTER_ARCROLE_2013 = 'http://xbrl.org/arcrole/PR/2013-12-18/aspect-node-filter'
# Formula
NS_FORMULA = 'http://xbrl.org/2008/formula'
NS_VARIABLE = 'http://xbrl.org/2008/variable'
NS_ASPECT_TEST = 'http://xbrl.org/2008/variable/aspectTest'
NS_VALIDATION = 'http://xbrl.org/2008/validation'
NS_VALUE_ASSERTION = 'http://xbrl.org/2008/assertion/value'
NS_EXISTANCE_ASSERTION = 'http://xbrl.org/2008/assertion/existence'
NS_CONSISTENCY_ASSERTION = 'http://xbrl.org/2008/assertion/consistency'
NS_FORMULA_MESSAGE = 'http://xbrl.org/2010/message'

NS_DIMENSION_FILTER = 'http://xbrl.org/2008/filter/dimension'
# TODO - Add other filters

# XPath
NS_FUNCTION = 'http://www.w3.org/2005/xpath-functions'
# Assertions
ASSERTION_SET_ARCROLE = 'http://xbrl.org/arcrole/2008/assertion-set'
ASSERTION_UNSATISFIED_SEVERITY_ARCROLE = 'http://xbrl.org/arcrole/2016/assertion-unsatisfied-severity'
URL_ASSERTION_SEVERITIES = 'http://www.xbrl.org/2016/severities.xml'
# Xml fragment
XML_START = '<?xml version="1.0" ?>'

""" XML Schema types """
xsd_types = {
    'string': 's', 'boolean': 'b', 'float': 'n', 'double': 'n', 'decimal': 'n', 'duration': 'd',
    'dateTime': 'd', 'time': 'd', 'date': 'd', 'gYearMonth': 'd', 'gYear': 'd', 'gMonthDay': 'd',
    'gDay': 'd', 'gMonth': 'd', 'hexBinary': 'x', 'base64Binary': 'x', 'anyURI': 's', 'QName': 's',
    'NOTATION': 's', 'normalizedString': 's', 'token': 's', 'language': 's', 'IDREFS': 's',
    'ENTITIES': 's', 'NMTOKEN': 's', 'NMTOKENS': 's', 'Name': 's', 'NCName': 's', 'ID': 's',
    'IDREF': 's', 'ENTITY': 's', 'integer': 'n', 'nonPositiveInteger': 'n', 'negativeInteger': 'n',
    'long': 'n', 'int': 'n', 'short': 'n', 'byte': 'n', 'nonNegativeInteger': 'n', 'unsignedLong': 'n',
    'unsignedInt': 'n', 'unsignedShort': 'n', 'unsignedByte': 'n', 'positiveInteger': 'n'
    }
""" Human readable basic kinds """
xsd_kinds = {'s': 'String', 'n': 'Numeric', 'd': 'Date', 'b': 'Boolean', 'x': 'Binary'}

""" XBRL Basic types """
xbrl_types = {
    'decimalItemType': 'numeric',
    'floatItemType': 'numeric',
    'doubleItemType': 'numeric',
    'monetaryItemType': 'monetary',
    'sharesItemType': 'shares',
    'pureItemType': 'pure',
    'fractionItemType': 'fraction',
    'integerItemType': 'numeric',
    'nonPositiveIntegerItemType': 'numeric',
    'negativeIntegerItemType': 'numeric',
    'longItemType': 'numeric',
    'intItemType': 'numeric',
    'shortItemType': 'numeric',
    'byteItemType': 'numeric',
    'nonNegativeIntegerItemType': 'numeric',
    'unsignedLongItemType': 'numeric',
    'unsignedIntItemType': 'numeric',
    'unsignedShortItemType': 'numeric',
    'unsignedByteItemType': 'numeric',
    'positiveIntegerItemType': 'numeric',
    'stringItemType': 'string',
    'booleanItemType': 'boolean',
    'hexBinaryItemType': 'binary',
    'base64BinaryItemType': 'binary',
    'anyURIItemType': 'string',
    'QNameItemType': 'string',
    'durationItemType': 'time',
    'dateTimeItemType': 'date',
    'timeItemType': 'time',
    'dateItemType': 'date',
    'gYearMonthItemType': 'date',
    'gYearItemType': 'date',
    'gMonthDayItemType': 'date',
    'gDayItemType': 'date',
    'gMonthItemType': 'date',
    'normalizedString': 'string',
    'tokenItemType': 'string',
    'languageItemType': 'string',
    'NameItemType': 'string',
    'NCNameItemType': 'string'
}
graph_arcroles = (
    PARENT_CHILD_ARCROLE,
    SUMMATION_ITEM_ARCROLE,
    GENERAL_SPECIAL_ARCROLE,
    SIMILAR_TUPLE_ARCROLE,
    ESSENCE_ALIAS_ARCROLE,
    REQUIRES_ELEMENT_ARCROLE,
    # XDT_DOMAIN_MEMBER_ARCROLE,
    # XDT_ALL_ARCROLE,
    # XDT_NOTALL_ARCROLE,
    # XDT_DIMENSION_DOMAIN_ARCROLE,
    # XDT_DIMENSION_DEFAULT_ARCROLE,
    # XDT_HYPERCUBE_DIMENSION_ARCROLE
)
```

## cube.py
```py
import json
import os
import tempfile
from openesef.base import archiver
from openesef.base import data_wrappers, const


class Cube:
    def __init__(self, folder=None):
        self.work_folder = folder if folder else tempfile.gettempdir()
        if not os.path.exists(self.work_folder):
            os.mkdir(self.work_folder)
        self.lexic = set()  # Unique lexic
        self.idx = {}  # Index of lexic
        self.idr = {}  # Reverse index

        self.dim_mem = {}  # Semantics - Key is dimension code, value is the set of members
        self.mem_dim = {}  # Semantics - Key is member code. value is the set of dimensions
        self.dim_dim = {}  # Dimension to other dimensions
        self.mem_mem = {}  # Member to other members

        self.labels = {}  # Dictionary with labels
        self.pairs = {}  # All combinations of dimension+member values together with corresponding facts
        self.facts = set()
        self.idx_ent_dim = {}  # Key is entity code, value is a set of all related dimensions
        self.idx_ent_mem = {}  # Key is entity code, value is a set of all related members for all dimensions
        self.archiver = archiver.Archiver(self.work_folder, length=2)

    def add_lex(self, t):
        self.lexic.add(t)
        i = self.idr.setdefault(t, len(self.lexic))
        self.idx[i] = t
        return i

    def add_mem(self, d, m, ent):
        """ Populates lexic, semantics and relationship entity-dimension/entity-member"""
        i_d = self.add_lex(d)
        i_m = self.add_lex(m)
        i_ent = self.add_lex(ent)
        # Key is dimension code, member is the set of members
        self.dim_mem.setdefault(i_d, set()).add(i_m)
        self.mem_dim.setdefault(i_m, set()).add(i_d)

        self.idx_ent_dim.setdefault(i_ent, set()).add(i_d)
        self.idx_ent_mem.setdefault(i_ent, set()).add(i_m)
        return f'{i_d}.{i_m}'

    def process_dimensional_container(self, container, signature, xid, ent):
        for dim, e in container.items():
            self.handle_concept(dim, xid)  # Add label for dimension concept
            dimfull = xid.taxonomy.resolve_qname(dim)
            if e.tag == f'{{{const.NS_XBRLDI}}}explicitMember':
                memfull = xid.taxonomy.resolve_qname(e.text)
                signature.add(self.add_mem(dimfull, memfull, ent))
                self.handle_concept(e.text, xid)  # Add label for member concept
            elif e.tag == f'{{{const.NS_XBRLDI}}}typedMember':
                for e2 in e.iterchildren():
                    signature.add(
                        self.add_mem(dimfull, f'{(e2.tag.replace("{", "").replace("}", ":"))}|{e2.text}', ent))

    def handle_concept(self, qname, xid):
        pref = qname.split(':')[0] if ':' in qname else None
        if pref is None:
            return
        namespace = xid.taxonomy.resolve_prefix(pref)
        nm = qname.split(':')[1] if ':' in qname else qname
        concept = xid.taxonomy.concepts_by_qname.get(qname, None)
        if concept is None:
            return
        self.add_label(self.add_lex(f'{namespace}:{nm}'), concept.get_label())

    def add_label(self, key, label):
        if key is None or label is None:
            return
        self.labels[key] = label

    def add_fact(self, fct, xid):
        if fct.context is None or fct.value is None or fct.unit is None:  # Skip non numeric facts - TO RECONSIDER
            return
        ent = f'{fct.context.entity_scheme}:{fct.context.entity_identifier}'
        signature = set()
        signature.add(self.add_mem('metric', f'{fct.namespace}:{fct.name}', ent))
        self.handle_concept(fct.qname, xid)

        if fct.decimals:
            signature.add(self.add_mem('decimals', f'{fct.decimals}', ent))
        if fct.precision:
            signature.add(self.add_mem('precision', f'{fct.precision}', ent))
        if fct.unit:
            signature.add(self.add_mem('unit', f'{fct.unit.get_aspect_value()}', ent))

        signature.add(self.add_mem('entity', ent, ent))
        signature.add(self.add_mem('period', f'{fct.context.get_period_string()}', ent))
        if fct.context.scenario:
            self.process_dimensional_container(fct.context.scenario, signature, xid, ent)
        if fct.context.segment:
            self.process_dimensional_container(fct.context.segment, signature, xid, ent)

        # Add fact to global index of facts
        f = data_wrappers.OimFact(f'f{len(self.facts)}', '|'.join(sorted(signature)), fct.value)
        self.facts.add(f)
        for k in signature:
            self.pairs.setdefault(k, set()).add(f)

    def save(self):
        self.archiver.open()
        # Key is integer code, value is the lexic part
        self.archiver.store_content('idx.json', json.dumps(self.idx))
        # Key is the lexic part, value is the integer code
        self.archiver.store_content('idr.json', json.dumps(self.idr))
        # Identifiers resolved to labels
        self.archiver.store_content('lbl.json', json.dumps(self.labels))
        # Relationships entity-dimension
        # Key is the code of entity dimension, value is the set of all belonging dimensions
        ent_dim = {}
        for k, v in self.idx_ent_dim.items():
            ent_dim[k] = [d for d in v]
        self.archiver.store_content('ent_dim.json', json.dumps(ent_dim))
        # Relationships entity-member
        # Key is the key of entity dimension, value is the set of all belonging members of any other dimension
        ent_mem = {}
        for k, v in self.idx_ent_mem.items():
            ent_mem[k] = [m for m in v]
        self.archiver.store_content('ent_mem.json', json.dumps(ent_dim))
        # Semantics
        # Key is dimension code, value is the list of all belonging members
        dim_mem = {}
        for k, v in self.dim_mem.items():
            dim_mem[k] = [it for it in v]
        self.archiver.store_content('dim_mem.json', json.dumps(dim_mem))
        # Key is member code, value is the set of related dimensions
        mem_dim = {}
        for k, v in self.mem_dim.items():
            mem_dim[k] = [it for it in v]
        self.archiver.store_content('mem_dim.json', json.dumps(mem_dim))
        # Fact sets
        # Key is the combination of dimension.member (resolved to codes). Value is the collection of all belonging facts
        for k, factset in self.pairs.items():
            self.archiver.store_content(f'{k}.json', json.dumps([f for f in factset]))

        self.archiver.close()

    def load(self):
        pass
        # idx_filename = os.path.join(path, 'idx.json')
        # if not os.path.exists(idx_filename):
        #     return
        # with open(idx_filename, 'r') as f:
        #     self.idx = json.load(f)
        # with open(os.path.join(path, 'idr.json'), 'r') as f:
        #     self.idr = json.load(f)
        # with open(os.path.join(path, 'lbl.json'), 'r') as f:
        #     self.labels = json.load(f)
        # with open(os.path.join(path, 'ent_dim.json'), 'r') as f:
        #     nent_dim = json.load(f)
        # for k, v in nent_dim.items():
        #     self.idx_ent_dim.setdefault(k, set()).update(v)
        # with open(os.path.join(path, 'ent_mem.json'), 'r') as f:
        #     nent_mem = json.load(f)
        # for k, v in nent_mem.items():
        #     self.idx_ent_mem.setdefault(k, set()).update(v)
        # archive = ZipFile(os.path.join(path, 'data.zip'))
        # for it in archive.filelist:
        #     with archive.open(it.filename) as f:
        #         k = it.filename.replace('.json', '')
        #         fact_list = json.load(f)
        #         for fl in fact_list:
        #             df = data_wrappers.OimFact(fl[0], fl[1], fl[2])
        #             self.pairs.setdefault(k, set()).add(f)
        # archive.close()
```

## data_wrappers.py
```py
from collections import namedtuple
import enum

""" Data wrapper of the entryPoint element inside a taxonomy package. 
    Name: Official name, or code of the entry point.
    Urls: List of URLs for the Web resources needed for that entry point.
    Description: Some human readable explanation. """
EntryPoint = namedtuple('EntryPoint', 'Name,Urls,Description,Hash')

""" Enumeration refers to a base set composed of definition arcs with domain-member arcrole.
    Key: Base Set Role | Domain | Head Usable 
    Concepts: List of concepts having the same enumeration key.
    Members: List of concepts, which are members of the enumeration. """
Enumeration = namedtuple('Enumeration', 'Key,Concepts,Members')

""" Represents a node in a base set. 
    Concept: Reference to the concept object.
    Arc: Reference to the arc objects, which points to that concept. If the node is in the chain_dn collection, 
    then the arc's 'to' attribute points to the concept. If it is in the chain_up collection, then 
    the arc's 'from' attribute points to the concept.
    IsLeaf: True if the node does not have descendant nodes, otherwise False.
"""
BaseSetNode = namedtuple('BaseSetNode', 'Concept,Level,Arc,IsLeaf,Label')


""" Represents a constraint in a table cell.
    Dimension: The QName of the constraint dimension, or unit, period, entityIdentifier or entityScheme. 
    Member: The value of the member, which is a QName for explicit custom dimensions. 
    Axis: x,y or z depending on the axis where the constraint comes from. """
Constraint = namedtuple('Constraint', 'Dimension,Member,Axis')


""" Represents a restriction in a xsd:simpleType or xsd:complexType with simple content."""
XsdRestriction = namedtuple('Restriction', 'Name,Value')

""" Represents a DPM Map. DPM stands for DAta Point Model.
    Id: The identifier of the map. Normally this is the table id. 
    Dimensions: Set of all custom dimensions included in the map. Note that not all cells will include all dimensions.
    Mappings: A Dictionary of dictionaries where outer key is the address of the data point. 
              The value is a dictionary of constraints for the cell where key is the dimension (aspect) and the value
              is the value of the member. If the dimension is open, the member value is an asterisk (*). """
DpmMap = namedtuple('DpmMap', 'Id,Dimensions,Mappings,OpenAxes')

""" Represents a fact according OIM (Open Information Model) - the fact value + all associated aspects.  """
OimFact = namedtuple('OimFact', 'Id,Signature,Value')

DpmMapMandatoryDimensions = ['Label', 'Metrics', 'Data Type', 'Period Type']
Axis = enum.Enum('Axis', 'X Y Z')
```

## ebase.py
```py
from lxml import etree as lxml
from openesef.base import const, util



import logging

# Get a logger.  __name__ is a good default name.
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

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
            # Handle potential mem:// URLs in attributes
            if self.esef_filing_root and self.esef_filing_root.startswith('mem://'):
                if a_value.startswith('/'):
                    # Convert absolute paths to mem:// paths if needed
                    a_value = f"mem://{a_value.lstrip('/')}"
                elif not (a_value.startswith('http://') or 
                         a_value.startswith('https://') or 
                         a_value.startswith('mem://')):
                    # Convert relative paths to mem:// paths if needed
                    a_value = f"mem://{a_value}"
            
            a_name = util.get_local_name(a[0])
            a_uri = util.get_namespace(a[0])
            a_qname = a_name
            if a_uri:
                plist = [p for p, u in self.origin.nsmap.items() if u == a_uri]
                a_prefix = plist[0] if plist else 'ns1'
                a_qname = f'{a_prefix}:{a_name}'
            output.append(f' {a_qname}="{a_value}"')
            
            # a_name = util.get_local_name(a[0])
            # a_uri = util.get_namespace(a[0])
            # a_qname = a_name
            # if a_uri:
            #     plist = [p for p, u in self.origin.nsmap.items() if u == a_uri]
            #     a_prefix = plist[0] if plist else 'ns1'
            #     a_qname = f'{a_prefix}:{a_name}'
            # output.append(f' {a_qname}="{a_value}"')

    def l_default(self, e):
        default_method = self.parsers.get('default')
        if default_method is not None:
            default_method(e)
```

## element.py
```py
from ..base import ebase


class Element(ebase.XmlElementBase):
    def __init__(self, e, container_schema):
        super().__init__(e)
        self.schema = container_schema
        self.prefix = self.schema.target_namespace_prefix
        self.id = e.attrib.get('id', None)
        self.name = e.attrib.get('name', None)
        self.qname = f'{self.prefix}:{self.name}'
        self.unique_id = f'{{{self.schema.target_namespace}}}{self.name}'
        self.schema.elements[self.unique_id] = self
        if self.id is not None:
            self.schema.elements_by_id[self.id] = self
        self.substitution_group = e.attrib.get('substitutionGroup')
        nil = e.attrib.get('nillable')
        self.nillable = nil is not None and nil.lower() == 'true' or nil == '1'
        abstr = e.attrib.get('abstract')
        self.abstract = abstr is not None and abstr.lower() == 'true' or abstr == '1'
```

## fbase.py
```py
import urllib.request, os
from lxml import etree as lxml
from openesef.base import ebase, util, const
from fs.base import FS
from typing import Optional
import fs
import re
from openesef.util.util_mylogger import setup_logger #util_mylogger
import logging 
if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.base.fbase") 


# import logging

# # Get a logger.  __name__ is a good default name.
# logger = logging.getLogger(__name__)
# #logger.setLevel(logging.DEBUG)

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

class XmlFileBase(ebase.XmlElementBase):
    def __init__(self, location=None, container_pool=None, parsers=None, root=None, esef_filing_root = None, memfs: Optional[FS] = None):
        """
        root = None
        this_xb = XmlFileBase(None, container_pool, parsers, root, esef_filing_root)
        """
        if parsers is None:
            parsers = {}
        self.parsers = parsers
        self.pool = container_pool
        self.memfs = memfs
        # Check if root_path is a mem:// URL
        self.location = location
        self.is_memory_fs = False 
        if esef_filing_root:
            self.is_memory_fs = esef_filing_root.startswith("mem://")
        elif memfs:
            self.is_memory_fs = True
        elif location and "mem://" in location:
            self.is_memory_fs = True
        elif self.pool and self.pool.memfs:
            self.is_memory_fs = True
        self.location = location
        if self.is_memory_fs and memfs is None:
            # Create memory filesystem if not provided
            raise ValueError("XmlFileBase: memfs is None and is_memory_fs is True")
        if not self.is_memory_fs:
            logger.info(f"XmlFileBase: is_mem_fs=False! location={location}, is_memory_fs={self.is_memory_fs}")
        self.namespaces = {}  # Key is the prefix and value is the URI
        self.namespaces_reverse = {}  # Key is the UrI and value is the prefix
        self.schema_location_parts = {}
        self.base = ''
        self.esef_filing_root = esef_filing_root        
        if location:
            self.location = util.reduce_url(location)
            # self.base = self.location.replace('\\', '/')[:location.rfind("/")]
            self.base = os.path.split(location)[0]
            if root is None:  # Only parsing file again the root element is not explicitly passed
                root = self.get_root()
        if root is None:
            return
        # Predefined
        self.namespaces['xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        self.namespaces_reverse['http://www.w3.org/2001/XMLSchema-instance'] = 'xsi'
        self.l_namespaces(root)
        self.l_schema_location(root)
        #this_eb = ebase.XmlElementBase(e=None, parsers=None, assign_origin=False, esef_filing_root=None)
        #this_eb = ebase.XmlElementBase(e = root, parsers=parsers, assign_origin=False, esef_filing_root=esef_filing_root); #self = this_eb
        super().__init__(e = root, 
                         parsers = parsers, 
                         esef_filing_root=esef_filing_root)

    def get_root(self):
        """ If the location can be found in an open package, then extract it from the package """
        url = self.location
        # Handle packaged locations first
        if self.pool and self.pool.packaged_locations:
            t = self.pool.packaged_locations.get(url)
            if t:
                pck = t[0]
                content = pck.get_url(url)
                p = lxml.XMLParser(huge_tree=True)
                try:
                    return lxml.XML(content, parser=p)
                except Exception:
                    s = content.decode('utf-8')
                    s = s.replace('\n', '')  # Try to correct eventually broken lines
                    root = lxml.XML(bytes(s, encoding='utf-8'), parser=p)
                    return root

        # Handle memory filesystem
        if self.is_memory_fs and not "http" in url and not "file://" in url:
            if self.memfs is None:
                raise ValueError("XmlFileBase: self.is_memory_fs is True but  memfs is None")
            
            # Remove 'mem://' prefix to get the actual path
            mem_path = re.sub(r'^mem://', '', url)
            
            if self.memfs.exists(mem_path):
                with self.memfs.open(mem_path, 'rb') as f:
                    content = f.read()
                    p = lxml.XMLParser(huge_tree=True)
                    try:
                        return lxml.XML(content, parser=p)
                    except Exception:
                        s = content.decode('utf-8')
                        s = s.replace('\n', '')  # Try to correct eventually broken lines
                        root = lxml.XML(bytes(s, encoding='utf-8'), parser=p)
                        return root
            # else:
            #     raise FileNotFoundError(f"File {mem_path} not found in memory filesystem")

        # Handle regular filesystem and URLs
            logger.debug(f"XmlFileBase: get_root() did not find the file in memory filesystem; self.is_memory_fs = {self.is_memory_fs}; self.memfs.listdir('.') = {self.memfs.listdir('.')}")
        filename = url
        if self.pool:
            filename = self.pool.cache(url) # <- got the error
        elif url.startswith('http://') or url.startswith('https://'):
            filename, headers = urllib.request.urlretrieve(url)
        dom = lxml.parse(filename)
        return dom.getroot()

    def l_schema_location(self, e):
        sl = e.attrib.get(f'{{{const.NS_XSI}}}schemaLocation')
        if not sl:
            return
        parts = util.normalize(sl).split(' ')
        cnt = -1
        odds = []
        evens = []
        for p in parts:
            cnt += 1
            if cnt % 2:
                evens.append(p)
            else:
                odds.append(p)
        self.schema_location_parts = dict(zip(odds, evens))

    def l_namespaces(self, e):
        for prefix in filter(lambda x: x is not None, e.nsmap):
            uri = e.nsmap[prefix]
            self.namespaces[prefix] = uri
            self.namespaces_reverse[uri] = prefix

    def l_namespaces_rec(self, e, target_tags=None):
        if not isinstance(e, lxml._Element):
            return
        if target_tags is None or e.tag in target_tags:
            self.l_namespaces(e)
        for e2 in e.iterchildren():
            self.l_namespaces_rec(e2)
```

## pool.py
```py
"""
XBRL Pool Module Documentation

The Pool class serves as a central repository for managing XBRL taxonomies, instances, and related resources.
It inherits from Resolver class and provides functionality for loading, caching, and managing XBRL documents.

Key Features:
1. Taxonomy Management
   - Loading and caching taxonomies
   - Managing taxonomy packages
   - Handling multiple entry points

2. Instance Document Management
   - Loading instance documents from files, archives, or XML elements
   - Managing relationships between instances and taxonomies

3. Resource Management
   - Caching and resolving schemas and linkbases
   - Managing taxonomy packages
   - Handling alternative locations for resources

Class Attributes:
    taxonomies (dict): Stores loaded taxonomies
    current_taxonomy (Taxonomy): Reference to the currently active taxonomy
    current_taxonomy_hash (str): Hash identifier for the current taxonomy
    discovered (dict): Tracks discovered resources to prevent circular references
    schemas (dict): Stores loaded schema documents
    linkbases (dict): Stores loaded linkbase documents
    instances (dict): Stores loaded instance documents
    alt_locations (dict): Maps URLs to alternative locations
    packaged_entrypoints (dict): Maps entry points to package locations
    packaged_locations (dict): Maps locations to package contents
    active_packages (dict): Currently opened taxonomy packages
    active_file_archive (ZipFile): Currently opened archive file
"""
import sys



#import openesef
#print(openesef.__path__)
import os, zipfile, functools
from lxml import etree as lxml
from openesef.base import resolver, util
from openesef.taxonomy import taxonomy, schema, tpack, linkbase
#from openesef.taxonomy.linkbase import Linkbase
from openesef.instance import instance
import openesef
import gzip
from openesef.base import const, util
import os
#import tempfile
import zipfile
import functools
from pathlib import Path
import time
from typing import Optional, Dict, List, Union, Tuple
import traceback
import pathlib
from io import StringIO
import re 
import urllib.parse
from fs.base import FS
import fs
from openesef.util.util_mylogger import setup_logger #util_mylogger
import logging 
if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.base.pool") 


# import logging

# # Get a logger.  __name__ is a good default name.
# #logger = logging.getLogger(__name__)

# # Get the logger.  Don't create a new logger instance.
# logger = logging.getLogger("main.base.pool")
# #logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.ERROR)

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




class Pool(resolver.Resolver):
    def __init__(self, cache_folder=None, output_folder=None, alt_locations=None, esef_filing_root=None, max_error =0, memfs: Optional[FS] = None):
        """
        Initializes a new Pool instance
        Args:
            cache_folder (str): Path to cache directory
            output_folder (str): Path to output directory
            alt_locations (dict): Alternative URL mappings        
            esef_filing_root (str): Path to location of the ESEF structure
        """
        logger.info(f"\n\nInitializing Pool with cache_folder={cache_folder}, output_folder={output_folder}")
        if cache_folder is None:
            repo_cache_folder = Path(openesef.__file__).parent / "xbrl_schema"
            if os.path.exists(repo_cache_folder):
                if os.access(repo_cache_folder, os.W_OK):
                    cache_folder = repo_cache_folder
                    logger.info(f"Using repository cache folder: {cache_folder}")
            # if cache_folder is None:
            #     cache_folder = tempfile.gettempdir()
            #     logger.info(f"Using temporary cache folder: {cache_folder}")
        else:
            logger.info(f"Using provided cache folder: {cache_folder}")
        super().__init__(cache_folder, output_folder)
        self.taxonomies = {}
        self.current_taxonomy = None
        self.current_taxonomy_hash = None
        self.discovered = {}
        self.schemas = {}
        self.linkbases = {}
        self.instances = {}
        self.memfs = memfs
        if  memfs is None and esef_filing_root is not None and "mem://" in esef_filing_root: 
            raise ValueError("Pool: memfs is None and esef_filing_root is a memory URL")
        self.count_exceptions = 0
        # Alternative locations. If set, this is used to resolve Qeb references to alternative (existing) URLs. 
        self.alt_locations = alt_locations
        # Index of all packages in the cache/taxonomy_packages folder by entrypoint 
        self.packaged_entrypoints = {}
        self.packaged_locations = None
        # Currently opened taxonomy packages 
        self.active_packages = {}
        # Currently opened archive, where files can be read from - optional.
        self.active_file_archive = None
        self.esef_filing_root = esef_filing_root
        self.location = esef_filing_root
        self.co_domain = None
        self.max_error = max_error
    def __str__(self):
        return self.info()

    def check_count_exceptions(self):
        logger.debug(f"Checking count of exceptions: {self.count_exceptions}")
        logger.warning(f"Number of exceptions: {self.count_exceptions}")
        if self.count_exceptions > self.max_error:
            raise Exception(f"Number of exceptions exceeded {self.max_error}: {self.count_exceptions}")

    def __repr__(self):
        return self.info()

    def info(self):
        return '\n'.join([
            f'Taxonomies: {len(self.taxonomies)}',
            f'Instance documents: {len(self.instances)}',
            f'Taxonomy schemas: {len(self.schemas)}',
            f'Taxonomy linkbases: {len(self.linkbases)}',
            f"cache folder: {self.cache_folder}",
            ])

    def index_packages(self):
        """ Index the content of taxonomy packages found in cache/taxonomies/ """
        package_files = [os.path.join(r, file) for r, d, f in
                         os.walk(self.taxonomies_folder) for file in f if file.endswith('.zip')]
        for pf in package_files:
            self.index_package(tpack.TaxonomyPackage(pf))

    def index_package(self, package):
        """ Index the content of a taxonomy package """
        for ep in package.entrypoints:
            eps = ep.Urls
            for path in eps:
                self.packaged_entrypoints[path] = package.location

    def resolve_and_update_schema_refs(self, root, esef_filing_root):
        """
        Resolves and updates schemaRef elements within an ESEF context.
        Question: Why does it not change anything in `self` and no return values?
        """
        nsmap = {'link': const.NS_LINK}
        schema_refs = root.findall(".//link:schemaRef", namespaces=nsmap)
        logger.debug(f"  Calling resolve_and_update_schema_refs() with:\n    root {root} and esef_filing_root {esef_filing_root}")
        logger.debug(f"    found {len(schema_refs)} link(s) in schema_refs ")
        resolved_schemas = set()  # Keep track of resolved schemas

        for schema_ref in schema_refs:
            #schema_ref = schema_refs[0]; print(lxml.tostring(schema_ref))
            href = schema_ref.get(f'{{{const.NS_XLINK}}}href')
            if href:
                logger.debug(f"href found: {href}")
                resolved_href = self.resolve_esef_schema_ref(href, esef_filing_root)
                if resolved_href and resolved_href not in resolved_schemas:
                    schema_ref.set(f'{{{const.NS_XLINK}}}href', resolved_href)
                    resolved_schemas.add(resolved_href)  # Add to the set of resolved schemas
                    
                elif resolved_href in resolved_schemas:
                    logger.debug(f"    Skipping already resolved schema: {resolved_href}") # Skip if already resolved
                else:
                    logger.warning(f"    Could not resolve schema reference: {href}")
        logger.debug(f"")

    def resolve_esef_schema_ref(self, href, esef_filing_root):
        """Resolves schema references within an ESEF structure."""
        res_href = re.search(esef_filing_root + r"(.*)", href)
        if res_href:
            href_local = re.sub("file://", "", res_href.group(0))
            if os.path.isfile(href_local):
                resolved_href = pathlib.Path(href_local).as_uri()
                return resolved_href 
        else:
            resolved_path = os.path.abspath(os.path.join(esef_filing_root, href))
            if os.path.isfile(resolved_path):
                return pathlib.Path(resolved_path).as_uri()
            else:
                logger.warning(f"Schema file not found: {resolved_path}")
                return None
    def add_instance_stringio(self, contentio, key="instance", attach_taxonomy=True):
        """
        Adds an instance document from a StringIO object
        This function has yet to be implemented
        """
        xid = instance.Instance(location="stringIO", container_pool=self, esef_filing_root="")
        self.add_instance(xid, key, attach_taxonomy)
        return xid

    def add_instance_location(self, esef_filing_root, filename, key=None, attach_taxonomy=True):
        """
        Loads an instance document from a file location within an ESEF structure.
        """

        logger.debug(f"Starting to run with add_instance_location()! \n  esef_filing_root: {esef_filing_root}\n  filename: {filename}.")
        instance_location = os.path.join(esef_filing_root, filename)
        instance_location = os.path.abspath(instance_location)        
        logger.debug(f"  instance_location: {instance_location}")

        if key is None:
            key = instance_location
            logger.debug(f"  Setting key as instance_location (full local path).")

        # parser = lxml.XMLParser(huge_tree=True)
        # doc = lxml.parse(instance_location, parser=parser)
        # root = doc.getroot(); #lxml.tostring(root)[:100]
        # # Resolve schemaRefs relative to the *esef_filing_root*, not the instance file
        # self.resolve_and_update_schema_refs(root, esef_filing_root) # <= What does this do exactly???
        # # Write back the modified XML
        # doc.write(instance_location)

        xid = instance.Instance(location=instance_location, 
                container_pool=self, 
                esef_filing_root = esef_filing_root)
        #type(xid)

        try:            
            self.add_instance(xid, key, attach_taxonomy, esef_filing_root) # <= This causes the dead-lock endless loop.
            return xid

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            self.count_exceptions += 1
            self.check_count_exceptions()
            return None

    def add_instance_archive(self, archive_location, filename, key=None, attach_taxonomy=False):
        """
        Adds an XBRL instance from an archive file (supports both .zip and .gzip formats)
        
        Args:
            archive_location (str): Path to the archive file (.zip or .gzip)
            filename (str): Name of the file within the archive (for zip) or the original filename (for gzip)
            key (str, optional): Key to identify the instance. Defaults to None.
            attach_taxonomy (bool, optional): Whether to attach taxonomy. Defaults to False.
        
        Returns:
            Instance: The loaded XBRL instance or None if loading fails
        
        Raises:
            FileNotFoundError: If archive_location doesn't exist
            ValueError: If archive format is not supported
        """
        if not os.path.exists(archive_location):
            raise FileNotFoundError(f"Archive not found: {archive_location}")

        # Handle GZIP files
        if archive_location.endswith('.gzip'):
            try:
                with gzip.open(archive_location, 'rb') as gf:
                    content = gf.read()
                    root = lxml.XML(content)
                    return self.add_instance_element(
                        root,
                        filename if key is None else key,
                        attach_taxonomy
                    )
            except Exception as e:
                self.count_exceptions += 1
                self.check_count_exceptions()

                raise ValueError(f"Error processing gzip file: {str(e)}")

        # Handle ZIP files
        elif archive_location.endswith('.zip'):
            try:
                archive = zipfile.ZipFile(archive_location)
                zil = archive.infolist()
                xid_file = [f for f in zil if f.filename.endswith(filename)]
                
                if not xid_file:
                    raise ValueError(f"File {filename} not found in archive")
                    
                xid_file = xid_file[0]
                
                with archive.open(xid_file) as xf:
                    root = lxml.XML(xf.read())
                    return self.add_instance_element(
                        root,
                        xid_file if key is None else key,
                        attach_taxonomy
                    )
            except Exception as e:
                self.count_exceptions += 1
                self.check_count_exceptions()

                raise ValueError(f"Error processing zip file: {str(e)}")

        else:
            self.count_exceptions += 1
            self.check_count_exceptions()

            raise ValueError("Unsupported archive format. Use .zip or .gzip")
    
    def add_instance_element(self, e, key=None, attach_taxonomy=False):
        """
        Adds an instance document from an XML element
        Args:
            e (Element): XML element
            key (str): Optional identifier
            attach_taxonomy (bool): Whether to load associated taxonomy
        """
        xid = instance.Instance(container_pool=self, root=e, memfs=self.memfs)
        if key is None:
            key = e.tag
        self.add_instance(xid, key, attach_taxonomy)
        return xid

    def get_co_domain(self, esef_filing_root=None):
        if self.co_domain is None:
            for root, dirs, files in os.walk(esef_filing_root):
                #print(root, dirs, files)
                for dir in dirs:
                    if re.search(r"www.|.com|.de|.net", dir):
                        self.co_domain = dir
                        break
        return self.co_domain

    def get_co_xsd_local_path(self, ref, esef_filing_root):
        xsd_file_name = os.path.basename(ref)
        if self.co_domain:
            for root, dirs, files in os.walk(esef_filing_root):
                for file in files:
                    if re.search(xsd_file_name, file):
                        return os.path.join(root, file)  
        return ref
    def get_esef_local_path(self, ref, esef_filing_root):
        file_name = os.path.basename(ref)
        for root, dirs, files in os.walk(esef_filing_root):
                for file in files:
                    if re.search(file_name, file):
                        return os.path.join(root, file)  

    def add_instance(self, xid, key=None, attach_taxonomy=False, esef_filing_root=None, memfs=None): # Add esef_filing_root    
        """
        Adds an instance document to the pool
        Args:
            xid (Instance): The instance document to add
            key (str): Optional identifier
            attach_taxonomy (bool): Whether to load associated taxonomy
        """
        if key is None:
            #key = xid.location_ixbrl # < - AttributeError: 'Instance' object has no attribute 'location_ixbrl'
            key = xid.location

        self.instances[key] = xid # xid is of <class 'openesef.instance.instance.Instance'>
        if esef_filing_root and not self.co_domain:
            self.get_co_domain(esef_filing_root)
        if attach_taxonomy and xid.xbrl is not None:
            # Ensure that if schema references are relative, the location base for XBRL document is added to them
            if esef_filing_root is not None:
                entry_points = [  self.get_co_xsd_local_path(ref, esef_filing_root) if self.co_domain in ref  else ref for ref in xid.xbrl.schema_refs  ]
            entry_points = [ref if ref.startswith('http') or self.co_domain in ref else self.resolve_schema_ref(ref, xid.location)
                            for ref in entry_points]
            entry_points = [pathlib.Path(ep).as_uri() if os.path.isfile(ep) else ep for ep in entry_points]

            tax = self.add_taxonomy(entry_points, esef_filing_root, memfs) #<- here is the endless loop
            xid.taxonomy = tax

    def add_taxonomy(self, entry_points, esef_filing_root=None): # Add esef_filing_root
        """
        Adds a taxonomy from a list of entry points
        Args:
            entry_points (list): List of entry points
        Returns:
            Taxonomy: The loaded taxonomy object
        """
        logger.info("\n\Calling add_taxonomy(...):")
        ep_list = entry_points if isinstance(entry_points, list) else [entry_points]
        logger.info(f"Processing {len(ep_list)} entry points")

        # self.packaged_locations = {}
        for ep in ep_list:
            #ep = ep_list[0]
            #below is commented in original xbrl package.
            # if self.active_file_archive and ep in self.active_file_archive.namelist():
            #     self.packaged_locations[ep] = (self.active_file_archive, ep)
            # else:
            # For ESEF, try to resolve relative to esef_filing_root first
            if not ep.startswith(('http://', 'https://', 'file://')):
                potential_path = self.get_esef_local_path(ep, esef_filing_root)
                if potential_path and os.path.exists(potential_path):
                    ep = pathlib.Path(potential_path).as_uri()            
            
            self.add_packaged_entrypoints(ep) 

        key = ','.join(entry_points)
        logger.debug(f"Generated taxonomy key: {key}")

        if key in self.taxonomies:
            logger.debug(f"Taxonomy already loaded: {key}")
            return self.taxonomies[key]  # Previously loaded

        for ep in ep_list:
            logger.debug(f"ep: \n{ep}")

        #data_pool = Pool(cache_folder=CACHE_DIR, max_error=1); #self = data_pool
        #this_tax = taxonomy.Taxonomy(entry_points = [], container_pool = data_pool); self = this_tax
        #self = data_pool # when coming back
        this_tax = taxonomy.Taxonomy(entry_points=ep_list,
                          container_pool = self, 
                          esef_filing_root=esef_filing_root)  # <- endless loop
        # Sets the new taxonomy as current
        self.taxonomies[key] = self.current_taxonomy
        self.packaged_locations = None
        return self.current_taxonomy

    def add_packaged_entrypoints(self, ep): 
        """
        Adds packaged entry points
        Args:
            ep (str): Entry point
        Returns: None
        """
        pf = self.packaged_entrypoints.get(ep)
        if not pf:
            return  # Not found
        pck = self.active_packages.get(pf, None)
        if pck is None:
            pck = tpack.TaxonomyPackage(pf)
            pck.compile()
        self.index_package_files(pck)

    def index_package_files(self, pck):
        """
        Indexes files in a taxonomy package
        Args:
            pck (TaxonomyPackage): The taxonomy package object
        Returns: None
        """
        if self.packaged_locations is None:
            self.packaged_locations = {}
        for pf in pck.files.items():
            self.packaged_locations[pf[0]] = (pck, pf[1])  # A tuple

    def cache_package(self, location, esef_filing_root=None):
        """ 
        Stores a taxonomy package from a Web location to local taxonomy package repository 
        Args:
            location (str): Location of taxonomy package
        Returns:
            TaxonomyPackage: The loaded taxonomy package object
        """
        package = tpack.TaxonomyPackage(location, self.taxonomies_folder, esef_filing_root=esef_filing_root)
        self.index_packages()
        return package

    def _is_esef_package(self, package):
        """
        Checks if the given package is an ESEF taxonomy package
        Args:
            package: The taxonomy package to check
        Returns:
            bool: True if it's an ESEF package, False otherwise
        """
        # Check for typical ESEF package indicators
        if hasattr(package, 'meta_inf') and package.meta_inf:
            # Check for ESEF-specific metadata in taxonomyPackage.xml
            if hasattr(package.meta_inf, 'taxonomy_package'):
                meta = package.meta_inf.taxonomy_package
                # Check for ESEF identifiers in the metadata
                if any('esef' in str(identifier).lower() for identifier in meta.get('identifier', [])):
                    return True
        
        # Check for typical ESEF folder structure
        if hasattr(package, 'files'):
            file_paths = package.files.keys()
            has_reports = any('reports' in path.lower() for path in file_paths)
            has_taxonomy = any('taxonomy' in path.lower() for path in file_paths)
            if has_reports and has_taxonomy:
                return True
        
        return False    
    
    def add_package(self, location, esef_filing_root = None):
        """
        Adds a taxonomy package provided in the location parameter, creates a taxonomy 
        using all entrypoints in the package and returns the taxonomy object.
        Args:
            location (str): Location of taxonomy package
        Returns:
            Taxonomy: The loaded taxonomy object
        """
        package = self.cache_package(location, esef_filing_root)
        self.active_packages[location] = package
        entry_points = [f for ep in package.entrypoints for f in ep.Urls]
        # If we have a esef_filing_root and this is an ESEF package, resolve entry points
        if esef_filing_root and self._is_esef_package(package):
            resolved_entry_points = []
            for ep in entry_points:
                if not ep.startswith(('http://', 'https://', 'file://')):
                    # Try to find the entry point in the ESEF structure
                    for root, _, files in os.walk(esef_filing_root):
                        if os.path.basename(ep) in files:
                            resolved_path = os.path.join(root, os.path.basename(ep))
                            resolved_ep = pathlib.Path(resolved_path).as_uri()
                            resolved_entry_points.append(resolved_ep)
                            break
                    else:
                        # If not found, keep original
                        resolved_entry_points.append(ep)
                else:
                    resolved_entry_points.append(ep)
            entry_points = resolved_entry_points

        tax = self.add_taxonomy(entry_points, esef_filing_root=esef_filing_root)
        return tax

    def add_reference(self, href, base, esef_filing_root=None, memfs=None): # Add esef_filing_root
        """

        Loads referenced schema or linkbase
        Args:
            href (str): Reference URL
            base (str): Base URL for relative references
        Returns: None

        Calling add_reference(...): href:http://xbrl.fasb.org/srt/2018/elts/srt-2018-01-31.xsd from base:  and esef_filing_root: mem://
        """
        
        if href is None:
            return

        # Skip basic schema objects
        if any(domain in href for domain in ['http://xbrl.org', 'http://www.xbrl.org']):
            return
        elif re.search("xbrl.org", href):
            return
        # elif href.startswith("mem://"):
        #     logger.debug(f"Skipping reference: {href} because it is in memory")
        #     return

        if memfs is not None and self.memfs is None:
            self.memfs = memfs
        # Resolve the reference
        resolved_href = self._resolve_url(href, base, esef_filing_root)
        
        # Create a unique key that includes taxonomy context
        key = f'{self.current_taxonomy_hash}_{resolved_href}'
        
        # Check if already processed or processing
        if key in self.discovered:
            return
            
        # Mark as being processed
        self.discovered[key] = False

        if not esef_filing_root:
            logger.debug("No esef_filing_root provided, using self.esef_filing_root")
            esef_filing_root = self.esef_filing_root

        logger.debug(f"\n\nCalling add_reference(...): href:{href} from base: {base} and esef_filing_root: {esef_filing_root}")    

        # # Handle mem:// URLs
        # if esef_filing_root and esef_filing_root.startswith('mem://'):
        #     if not href.startswith(('http://', 'https://', 'mem://')):
        #         # Convert relative paths to mem:// paths
        #         if href.startswith('/'):
        #             href = f"mem://{href.lstrip('/')}"
        #         else:
        #             base_path = base[6:] if base.startswith('mem://') else base
        #             href = f"mem://{os.path.join(base_path, href)}"
        # elif esef_filing_root and not href.startswith('http'):
        #     res_href = re.search(esef_filing_root + r"(.*)", href)
        #     if res_href:
        #         href_local = re.sub("file://", "", res_href.group(0))
        #         if os.path.isfile(href_local):
        #             base = os.path.dirname(href_local)
        #             #resolved_href = pathlib.Path(href_local).as_uri()
        #             #return resolved_href 

        # Validate file extension
        allowed_extensions = ('xsd', 'xml', 'json')
        file_ext = href.split('.')[-1]
        if file_ext.lower() not in allowed_extensions:
            logger.warning(f"Skipping reference: Invalid file extension {file_ext}")
            return        


        # Handle alternative locations
        # Artificially replace the reference - only done for very specific purposes.
        if self.alt_locations and href in self.alt_locations:
            original_href = href
            href = self.alt_locations[href]
            logger.debug(f"Replaced href \n{original_href} \nwith alternative location \n{href}")            
            
        # Resolve URL # Generate unique key that includes the base path to prevent loops
        #resolved_href = href
        if not href.startswith(('http://', 'https://', "mem://")):
            if esef_filing_root:
                if esef_filing_root.startswith('mem://'):
                    # Handle memory filesystem paths
                    resolved_href = href  if not resolved_href else resolved_href
                else:                
                    # Try to resolve relative to esef_filing_root first                    
                    #href_filename = href.split("/")[-1] if len(href.split("/"))>0 else ""
                    res_href = re.search(esef_filing_root + r"(.*)", href)
                    if res_href:
                        href_local = re.sub("file://", "", res_href.group(0))
                        if os.path.isfile(href_local):
                            resolved_href = pathlib.Path(href_local).as_uri() 
                    else:
                        # Fall back to base path resolution
                        resolved_href = self._resolve_url(href, base, esef_filing_root)

                    # potential_path = self.get_esef_local_path(ep, esef_filing_root) # <- this is terribly wrong
                    # if os.path.exists(potential_path):
                    #     resolved_href = pathlib.Path(potential_path).as_uri()


            # Create a unique key that includes both href and base to prevent loops
            key = f'{self.current_taxonomy_hash}_{resolved_href}_{base}'
            
            if key in self.discovered:
                return
                
            self.discovered[key] = False

        try:
            if resolved_href.endswith(".xsd"):
                
                if resolved_href in self.schemas: # **CHECK IF ALREADY LOADED!**
                    logger.debug(f"Schema already loaded: {resolved_href}. Skipping.")
                    return  # Already loaded!                
                # sh = self.add_schema(resolved_href, esef_filing_root)
                # self.current_taxonomy.attach_schema(resolved_href, sh)                
                #logger.debug(f"Loading schema: \n{resolved_href}")
                if resolved_href.startswith("mem://"):
                    schema_path = resolved_href
                elif resolved_href.startswith("file://"):
                    schema_path = re.sub("file://", "", resolved_href) # Remove file:// for schema.Schema
                else:
                    schema_path = resolved_href # Use the URL directly
                logger.debug(f"schema_path: \n{schema_path}")
                #from openesef.taxonomy import taxonomy, schema, tpack, linkbase; from openesef.base import fbase, const, element, util
                #self=data_pool
                #self=data_pool; this_schema = schema.Schema(location="",container_pool=self); self = this_schema
                #self=data_pool; this_schema = schema.Schema(location=schema_path,container_pool=self); self = this_schema
                sh = self.schemas.get(
                    schema_path, 
                    schema.Schema(location=schema_path, 
                                  container_pool=self, 
                                  esef_filing_root=esef_filing_root, 
                                  memfs=self.memfs)) #<- Endless loop
                #if self.current_taxonomy:
                try:
                    self.current_taxonomy.attach_schema(schema_path, sh)
                except Exception as e:
                    logger.error(f"Failed to attach schema: location={schema_path}, esef_filing_root={esef_filing_root} \n{str(e)}")
                    traceback.print_exc(limit=10)
            else:
                if resolved_href in self.linkbases: # **CHECK IF ALREADY LOADED!**
                    logger.debug(f"Linkbase already loaded: {resolved_href}. Skipping.")
                    return # Already loaded!
                                
                logger.debug(f"Loading linkbase by pool.add_reference(...): {resolved_href}")
                # Remove file:// prefix if present
                if resolved_href.startswith("mem://"):
                    linkbase_path = re.sub("mem://", "", resolved_href)
                elif resolved_href.startswith("file://"):
                    linkbase_path = re.sub("file://", "", resolved_href)
                else:
                    linkbase_path = resolved_href
                #from openesef.taxonomy import linkbase
                #this_lb = linkbase.Linkbase(location=None, container_pool=self, esef_filing_root=esef_filing_root) #self = this_lb
                try:
                    this_lb = linkbase.Linkbase(location=linkbase_path, container_pool=self, esef_filing_root=esef_filing_root, memfs=self.memfs) #<- got error
                    lb = self.linkbases.get(resolved_href, this_lb) # <- got the error
                    #if self.current_taxonomy:
                    self.current_taxonomy.attach_linkbase(resolved_href, lb) # Use resolved_href
                except Exception as e:
                    logger.error(f"Failed to load linkbase: locatioon={resolved_href}, esef_filing_root={esef_filing_root} \n{str(e)}")
                    traceback.print_exc(limit=10)
                #data_pool = Pool(cache_folder=CACHE_DIR, max_error=1); #self = data_pool
                #this_lb = linkbase.Linkbase(location=None, container_pool=data_pool, esef_filing_root=esef_filing_root) #self = this_lb

        except OSError as e:
            self.count_exceptions += 1
            self.check_count_exceptions()

            logger.error(f"OSError Failed to load resource \n{href} \n{str(e)}")
            # Log the error but don't raise it to allow continued processing
            traceback.print_exc(limit=10)

        except Exception as e:
            self.count_exceptions += 1
            self.check_count_exceptions()

            logger.error(f"Failed to load resource \n{href} \n{str(e)}")
            traceback.print_exc(limit=10)

    @staticmethod
    def check_create_path(existing_path, part):
        new_path = os.path.join(existing_path, part)
        if not os.path.exists(new_path):
            os.mkdir(new_path)
        return new_path

    def save_output(self, content, filename):
        """
        Saves content to output directory
        Args:
            content (str): Content to save
            filename (str): Target filename
        Returns: None        
        """
        if os.path.sep in filename:
            functools.reduce(self.check_create_path, filename.split(os.path.sep)[:-1], self.output_folder)
        location = os.path.join(self.output_folder, filename)
        with open(location, 'wt', encoding="utf-8") as f:
            f.write(content)


    def _resolve_url(self, href: str, base: Optional[str], esef_filing_root: Optional[str] = None) -> str:
        """
        Resolves URLs, correctly handling relative paths and file URLs.
        Returns a file URL for local files and an absolute URL for remote resources.
        
        Calling _resolve_url(...): href: srt-types-2020-01-31.xsd, base: http://xbrl.fasb.org/srt/2020/elts, esef_filing_root: mem://
        Resolved URL (mem base):  http://xbrl.fasb.org/srt/2020/srt-types-2020-01-31.xsd

        """
        logger.debug(f"==  Calling _resolve_url(...): href: {href}, base: {base}, esef_filing_root: {esef_filing_root}")

        if href.startswith(('http://', 'https://', 'mem://', 'file://')):
            logger.debug(f"Resolved HTTP URL: \n{href}")
            return href
        elif base.startswith(('http://', 'https://', 'mem://', 'file://')):
            #print(f"20250215a:{base}{href}")
            #return f"{base}/{href}"
            if not base.endswith("/"):
                base += "/"
            resolved_path = urllib.parse.urljoin(base, href)
            logger.debug(f"Resolved URL (mem base): \n{resolved_path}")
            return resolved_path            
        # Try to find the file in ESEF structure first
        if esef_filing_root :
            if not "mem://" in esef_filing_root:
                # First, try to find in www.company.com subdirectory
                for root, _, files in os.walk(esef_filing_root):
                    if os.path.basename(href) in files:
                        resolved_path = os.path.join(root, os.path.basename(href))                    
                        resolved = pathlib.Path(resolved_path).as_uri()
                        #logger.debug(f"Resolved URL (esef_filing_root): \n{resolved}")
                        return resolved

                esef_filing_root_parent = os.path.dirname(esef_filing_root)
                _i_walk = 0 
                for root, _, files in os.walk(esef_filing_root_parent):
                    _i_walk += 1
                    if _i_walk > 16:
                        break
                    if os.path.basename(href) in files:
                        resolved_path = os.path.join(root, os.path.basename(href))
                        
                        resolved = pathlib.Path(resolved_path).as_uri()
                        #logger.debug(f"Resolved URL (esef_filing_root): \n{resolved}")
                        return resolved
            else:
                logger.debug(f"Resolved URL (mem esef_filing_root): \n{esef_filing_root}")
                for root, _, files in self.memfs.walk("."):
                    if os.path.basename(href) in files:
                        resolved_path = os.path.join("mem://", root, os.path.basename(href))
                        resolved = pathlib.Path(resolved_path).as_uri()
                        #logger.debug(f"Resolved URL (esef_filing_root): \n{resolved}")
                        return resolved
            # If not found in www subdirectory, try base directory
        if base:
            if base.startswith(('http://', 'https://', 'mem://', 'file://')):
                resolved_path = f"{base}/{href}"
            else:
                resolved_path = os.path.abspath(os.path.join(os.path.dirname(base), href)) #<- this is wrong? #20250215
            #print(f"href: \n{href} -> resolved_path: \n{resolved_path}")
            #print(f"base: \n{base}")
            if os.path.isfile(resolved_path):
                resolved = pathlib.Path(resolved_path).as_uri()
                #logger.debug(f"Resolved URL (ESEF base): \n{resolved}")
                return resolved

        if base is None or not base.strip():
            if os.path.isfile(href):
                resolve_result = pathlib.Path(os.path.abspath(href)).as_uri()
                #logger.debug(f"Resolved URL: \n{href} to \n{resolve_result}")
                return resolve_result # Ensure absolute path
            else:  
                #logger.debug(f"Resolved URL: \n{href}")
                ##return f"https://{href}" # Assume it's a remote URL and prepend https://
                return href # Don't assume https, could be a relative local path
        if base.startswith(('http://', 'https://', 'mem://', 'file://')):
            resolved = urllib.parse.urljoin(base, href)
        elif base.startswith('file://') or base.startswith("/"):
            try:  # Use try-except to handle potential parsing errors
                base_path = urllib.parse.urlparse(base).path
                resolved_path = os.path.abspath(os.path.join(os.path.dirname(base_path), href))
                resolved = pathlib.Path(resolved_path).as_uri()
            except ValueError: # Log the error and return the original href
                self.count_exceptions += 1
                self.check_count_exceptions()
                logger.error(f"Invalid base URL: {base}")
                return href # Or handle the error differently, e.g., raise an exception
        else:  # base is a local path
            resolved_path = os.path.abspath(os.path.join(os.path.dirname(base), href))
            resolved = pathlib.Path(resolved_path).as_uri()

        logger.debug(f"Resolved URL: \n{resolved}")
        return resolved

    def resolve_schema_ref(self, href, instance_path):
        """
        Resolves schema reference URL.  Returns a local file path or an absolute URL.
        """
        logger.debug(f"Resolving schema reference: \n{href}")

        if href.startswith(('http://', 'https://', 'file://')):
            return href  # Already an absolute URL

        # Resolve relative to the instance_path
        #resolved_path= os.path.abspath(os.path.join(os.path.dirname(instance_path), href))
        #resolved_path = os.path.abspath(os.path.join(os.path.dirname(instance_path), href)) # Ensure absolute path
        #logger.debug(f"Resolved path: \n{resolved_path}")
        # Construct the full URL if href is relative
        base_url = os.path.dirname(instance_path)  # Get the base URL from the instance path
        resolved_path = os.path.abspath(os.path.join(base_url, href))  # Resolve relative path
        logger.debug(f"Resolved path: \n{resolved_path}")

        return resolved_path # Return the absolute path; don't prepend https://

    def add_schema(self, location, esef_filing_root=None, memfs=None):
        """
        Adds a schema to the pool and returns the Schema object
        
        Args:
            location (str): Location/URL of the schema
            esef_filing_root (str, optional): Root directory of ESEF filing
            
        Returns:
            Schema: The loaded schema object or None if already loaded
        """
        logger.debug(f"Adding schema by add_schema() from location: {location}")
        
        # If schema is already loaded, return existing instance
        if location in self.schemas:
            logger.debug(f"Schema already loaded: {location}")
            return self.schemas[location]
            
        try:
            # Create new schema instance
            schema_obj = schema.Schema(
                location=location,
                container_pool=self,
                esef_filing_root=esef_filing_root,
                memfs=memfs
            )
            
            # Store in schemas dictionary
            self.schemas[location] = schema_obj
            
            logger.debug(f"Successfully loaded schema: {location}")
            return schema_obj
            
        except Exception as e:
            logger.error(f"Failed to load schema {location}: {str(e)}")
            logger.error(f"traceback: \n{traceback.format_exc()}")
            self.count_exceptions += 1
            self.check_count_exceptions()
            return None

    def add_reference_from_string(self, content, location, base=''):
        """
        Loads referenced schema or linkbase from a string content
        
        Args:
            content (str): The XML content as a string
            location (str): Virtual location/URL for the content
            base (str): Base URL for relative references
        Returns: None
        """
        if location is None:
            return

        # Skip basic schema objects
        if any(domain in location for domain in ['http://xbrl.org', 'http://www.xbrl.org']):
            return
        elif re.search("xbrl.org", location):
            return

        # Create a unique key that includes taxonomy context
        key = f'{self.current_taxonomy_hash}_{location}'
        
        # Check if already processed or processing
        if key in self.discovered:
            return
            
        # Mark as being processed
        self.discovered[key] = True

        try:
            # Cache the content first
            cached_path = self.cache_from_string(StringIO(content), location)
            if location.endswith(".xsd"):
                logger.debug(f"Loading schema from string: {location}")
                
                sh = self.schemas.get(
                    location,
                    schema.Schema(
                        location=cached_path,
                        container_pool=self,
                        esef_filing_root=self.esef_filing_root
                    )
                )
                self.current_taxonomy.attach_schema(location, sh)
            else:
                logger.debug(f"Loading linkbase from string: {location}")
                
                lb = self.linkbases.get(
                    location,
                    linkbase.Linkbase(
                        location=cached_path,
                        container_pool=self,
                        esef_filing_root=self.esef_filing_root
                    )
                )
                self.current_taxonomy.attach_linkbase(location, lb)

        except Exception as e:
            self.count_exceptions += 1
            self.check_count_exceptions()
            logger.error(f"Failed to load resource from string {location}: {str(e)}")
            traceback.print_exc(limit=10)    

    def add_schema_from_string(self, content, location, esef_filing_root=None, memfs=None):
        """
        Adds a schema to the pool from a string content and returns the Schema object
        
        Args:
            content (str): The schema XML content as a string
            location (str): Virtual location/URL for the schema
            esef_filing_root (str, optional): Root directory of ESEF filing
        Returns:
            Schema: The loaded schema object or None if already loaded
        """
        logger.debug(f"Adding schema from string content with virtual location: {location}")
        
        # If schema is already loaded, return existing instance
        if location in self.schemas:
            logger.debug(f"Schema already loaded: {location}")
            return self.schemas[location]
            
        try:
            # First cache the content
            cached_path = self.cache_from_string(StringIO(content), location)
            
            # Create new schema instance using the cached file
            schema_obj = schema.Schema(
                location=cached_path,  # Use cached file path for actual content
                container_pool=self,
                esef_filing_root=esef_filing_root,
                memfs=memfs,
                virtual_location=location  # Pass original location for reference tracking
            )
            
            # Store in schemas dictionary using the virtual location
            self.schemas[location] = schema_obj
            
            logger.debug(f"Successfully loaded schema from string: {location}")
            return schema_obj
            
        except Exception as e:
            logger.error(f"Failed to load schema from string {location}: {str(e)}")
            self.count_exceptions += 1
            self.check_count_exceptions()
            return None

# to test Apple
if __name__ == "__main__" and False:
    #from openesef.base.pool import *
    CACHE_DIR = os.path.expanduser("~/.xbrl_cache")
    os.makedirs(CACHE_DIR, exist_ok=True)
    # Initialize pool with cache
    data_pool = Pool(cache_folder=CACHE_DIR, max_error=1); #self = data_pool
    this_tax = data_pool.add_taxonomy(entry_points=["http://xbrl.fasb.org/srt/2020/elts/srt-eedm1-def-2020-01-31.xml"], esef_filing_root=os.getcwd())

if __name__ == "__main__":
    import requests
    # Apple's 10-K iXBRL and XBRL URLs
    # https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/0000320193-20-000096-index.htm
    #location_ixbrl = 'https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019320000096/aapl-20200926.htm'
    location_xbrl = 'https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_htm.xml'
    location_taxonomy = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926.xsd"
    location_linkbase_cal = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_cal.xml"
    location_linkbase_def = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_def.xml"
    location_linkbase_lab = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_lab.xml"
    location_linkbase_pre = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/aapl-20200926_pre.xml"


    # Process both inline XBRL and native XBRL formats
    # Parse inline document (iXBRL)
    CACHE_DIR = os.path.expanduser("~/.xbrl_cache")
    data_pool = Pool(cache_folder=CACHE_DIR, max_error=10); #self = data_pool
    files = []
    for location in [location_xbrl, location_taxonomy, location_linkbase_cal, location_linkbase_def, location_linkbase_lab, location_linkbase_pre]:
        files.append(location.split('/')[-1])
        if not os.path.exists(location.split('/')[-1]):
            response = requests.get(location, headers={'User-Agent': 'Your Name <your.email@example.com>'})
            # Save the response content to a file
            with open(location.split('/')[-1], 'wb') as file:
                file.write(response.content)

    this_tax = data_pool.add_taxonomy(files, esef_filing_root=os.getcwd())
    #location = "https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-all-2024.xsd"
    #taxonomy = data_pool.add_taxonomy(files, esef_filing_root=os.getcwd())
    print("\nTaxonomy statistics:")
    print(f"Schemas: {len(this_tax.schemas)}")
    print(f"Linkbases: {len(this_tax.linkbases)}")
    print(f"Concepts: {len(this_tax.concepts)}")

# to test ESEF
if __name__ == "__main__" and False:
    """
    We run in first openesef folder. 
    Starting to parse for observation: gvkey=352123; 
    full_instance_path=/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/352123/2023/marley_spoon_2024-05-10_esef_xmls/222100A4X237BRODWF67-2023-12-31-en/marleyspoongroup/reports/222100A4X237BRODWF67-2023-12-31-en.xhtml
2025-02-12 20:20:01,955 - main.parse_concepts - PID:13347 - INFO - concept_to_df: 
    """
    #import importlib; import openesef.base.pool; from openesef.base.pool import *
    #import importlib; import openesef.openesef.base.pool; importlib.reload(openesef.openesef.base.pool); from openesef.openesef.base.pool import *
    #from openesef.base.pool import *
    #esef_filing_root="/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/"
    #filename="reports/sap-2022-12-31-DE.xhtml"
    esef_filing_root = "/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/352123/2023/marley_spoon_2024-05-10_esef_xmls/222100A4X237BRODWF67-2023-12-31-en/marleyspoongroup/"
    filename = "reports/222100A4X237BRODWF67-2023-12-31-en.xhtml"    
    data_pool = Pool(cache_folder="../../data/xbrl_cache", esef_filing_root=esef_filing_root); 
    #data_pool = Pool(cache_folder="../data/xbrl_cache", esef_filing_root=esef_filing_root, max_error=1024); 
    #self = data_pool; attach_taxonomy=True
    data_pool.add_instance_location(esef_filing_root=esef_filing_root, filename=filename, attach_taxonomy=True)
    #esef_filing_root = taxonomy_folder
    entry_point = None
    presentation_file = None
    for root, dirs, files in os.walk(esef_filing_root):
        for file in files:
            if file.endswith('.xsd'):
                entry_point = os.path.join(root, file)
            elif file.endswith('_pre.xml'):
                presentation_file = os.path.join(root, file)    
    tax = data_pool.add_taxonomy(entry_points = [entry_point, presentation_file], esef_filing_root=esef_filing_root)
```

## resolver.py
```py
import os
import shutil
import tempfile
import urllib.request
import logging 
import requests
import traceback
from io import StringIO, BytesIO
import sys

from openesef.base import const, util

from openesef.util.util_mylogger import setup_logger #util_mylogger

import logging 

if __name__=="__main__":
    logger = setup_logger("main", logging.INFO, log_dir="/tmp/log/")
else:
    logger = logging.getLogger("main.openesf.base.resolver") 


import fs

# Create an in-memory filesystem
memfs = fs.open_fs('mem://')


class Resolver:
    """
    Resolver is responsible for downloading files from the internet and caching them.
    """
    def __init__(self, cache_folder=None, output_folder=None, max_error=1024):
        self.cache_folder = cache_folder
        self.output_folder = output_folder
        self.max_error = max_error
        if self.cache_folder is None:
            temp_dir = tempfile.gettempdir()
            xbrl_dir = os.path.join(temp_dir, 'xbrl')
            if not os.path.exists(xbrl_dir):
                os.mkdir(xbrl_dir)
            if self.output_folder is None:
                self.output_folder = os.path.join(xbrl_dir, 'output')
                if not os.path.exists(self.output_folder):
                    os.mkdir(self.output_folder)
            cache_dir = os.path.join(xbrl_dir, 'cache')
            if not os.path.exists(cache_dir):
                os.mkdir(cache_dir)
            self.cache_folder = cache_dir
        self.taxonomies_folder = os.path.join(self.cache_folder, 'taxonomies')
        if not os.path.exists(self.taxonomies_folder):
            os.mkdir(self.taxonomies_folder)
    #
    def download_file(self, url, cached_file):
        """
        Download a file with proper headers and error handling
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        #        
        try:
            #logger.info(f"Downloading {url} to {cached_file}")
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            #
            # Determine if the content is text or binary based on content-type  
            content_type = response.headers.get('content-type', '').lower()
            is_text = 'text' in content_type or 'xml' in content_type
            #
            # Get total size for logging
            total_size = int(response.headers.get('content-length', 0))
            
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(cached_file), exist_ok=True)
            #
            # Download with progress tracking
            downloaded = 0
            mode = 'w' if is_text else 'wb'
            encoding = 'utf-8' if is_text else None
            #
            with open(cached_file, mode, encoding=encoding) as f:
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=is_text):
                    if chunk:
                        if is_text:
                            if type(chunk) == bytes:
                                chunk = chunk.decode(encoding='utf-8')
                                f.write(chunk)
                            elif type(chunk) == str:
                                f.write(chunk)
                        else:
                            f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress = (downloaded / total_size) * 100
                            logger.debug(f"Download progress: {progress:.2f}%")
            #
            logger.info(f"Successfully downloaded {url}")
            return True
        #
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            if os.path.exists(cached_file):
                os.remove(cached_file)  # Clean up partial download
            traceback.print_exc()
            raise Exception(f"Failed to download {url}: {str(e)}")
    #
    def cache(self, location, content_io=None):
        """
        Enhanced cache method that can handle both URLs and StringIO/BytesIO objects
        """
        #
        # If content_io is provided, use it directly
        if content_io is not None:
            return self.cache_from_string(content_io, location)
        #
        if location is None:
            return None
        #
        parts = location.replace(os.path.sep, "/").split('/')
        new_parts = util.reduce_url_parts(parts)
        protocol = new_parts[0].replace(':', '')
        #
        if protocol not in const.KNOWN_PROTOCOLS:
            return location
        #
        #
        cached_file = self.cache_folder
        new_location = '/'.join(new_parts)
        # Starts from the second part, because the first one is the protocol and the second one is empty.
        # The last part of this list is the file name, so it is handled separately
        for part in new_parts[2:-1]:
            cached_file = os.path.join(cached_file, part)
            if not os.path.exists(cached_file):
                os.makedirs(cached_file)
        fn = new_parts[-1]
        cached_file = os.path.join(cached_file, fn)
        #
        # If file doesn't exist or is empty, download it
        if not os.path.exists(cached_file) or os.path.getsize(cached_file) == 0:
            try:
                self.download_file(url=location, cached_file=cached_file)
            except Exception as e:
                logger.error(f"Error caching {location}: {str(e)}")
                if os.path.exists(cached_file):
                    os.remove(cached_file)  # Clean up any partial download
        #
        # if not os.path.exists(cached_file):
        #     user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        #     headers = {'User-Agent': user_agent}
        #     req = urllib.request.Request(new_location, headers=headers)
        #     with urllib.request.urlopen(req) as response:
        #         html = response.read()
        #         with open(cached_file, 'w', encoding='utf-8') as f:
        #             try:
        #                 s = html.decode(encoding='utf-8')
        #                 f.write(s)
        #             except Exception as ex:
        #                 print(ex)
        #     # temp_file, headers = urllib.request.urlretrieve(new_location)
        #     # shutil.move(temp_file, cached_file)
        #   
        return cached_file
    #
    def cache_from_string(self, content, location="filename.xml", memfs=memfs):
        """
        Cache content from a StringIO/BytesIO object
        """
        if location is None:
            return None
        if type(content) == StringIO:
            content = content.getvalue()
        with  memfs.open(location.replace("mem://", ""), 'w') as f:
            f.write(content)
            
        if not "mem://" in location:
            href = "mem://" + location     
        else:
            href=location       
        logger.debug(f"Successfully cached {location} to memory with href={href}")    
        return href
    #
    def download_to_memory(self, url):
        """
        Download a file into memory instead of saving to disk
        Returns either StringIO or BytesIO depending on content type
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        #
        try:
            logger.info(f"Downloading {url} to memory")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            #
            # Determine if the content is text or binary based on content-type
            content_type = response.headers.get('content-type', '').lower()
            is_text = 'text' in content_type or 'xml' in content_type
            #
            if is_text:
                content = StringIO(response.text)
            else:
                content = BytesIO(response.content)
            #   
            logger.info(f"Successfully downloaded {url} to memory")
            return content
        #
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            traceback.print_exc()
            raise Exception(f"Failed to download {url}: {str(e)}")
        
if __name__ == "__main__":
    data_pool = Resolver()
    location = "http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd"
    location = "http://xbrl.fasb.org/srt/2020/srt-roles-2020-01-31.xsd"
    content = data_pool.cache(location=location, content_io=None)
    location = "/"
    #self = data_pool; attach_taxonomy=True
    print(content)
```

## tax_to_pd.py
```py
import openesef.base.pool as pool
import os 
import pandas as pd
from collections import defaultdict


def export_taxonomy_to_dataframe(tax):
    # Create lists to store concept information
    data = []
    
    # Iterate through all concepts in the tax
    for concept_id, concept in tax.concepts.items():
        #concept_id, concept = list(tax.concepts.items())[4492]
        # Get basic concept information
        concept_info = {
            'concept_name': concept.name,
            'concept_qname': concept.qname,
            'namespace': concept.namespace,
            'data_type': concept.data_type,
            'period_type': concept.period_type,
            'balance': concept.balance,
            'abstract': concept.abstract,
            'nillable': concept.nillable
        }
        
        # Get labels in different languages and roles
        labels = defaultdict(dict)
        if hasattr(concept, 'resources') and 'label' in concept.resources:
            for lang, role_labels in concept.resources['label'].items():
                for label in role_labels:
                    labels[lang][label.xlink.role] = label.text
        concept_info['labels'] = labels
        
        # Get references
        references = []
        if hasattr(concept, 'references') and concept.references:
            for ref_list in concept.references.values():
                for ref in ref_list:
                    references.append(str(ref))
        concept_info['references'] = references
        
        # Get presentation relationships
        presentation_parents = []
        presentation_children = []
        if hasattr(concept, 'chain_up'):
            presentation_parents = [p for p in concept.chain_up.values()]
        if hasattr(concept, 'chain_dn'):
            presentation_children = [c for c in concept.chain_dn.values()]
        
        try:
            concept_info['presentation_parents'] = [p.Concept for parents in presentation_parents for p in parents]
        except Exception as e:
            concept_info['presentation_parents'] = []  # Default to empty list on error
            # Optionally log the error: print(f"Error processing presentation_parents: {e}")
        try:
            concept_info['presentation_children'] = [c.Concept for children in presentation_children for c in children]
        except Exception as e:
            concept_info['presentation_children'] = []  # Default to empty list on error
            # Optionally log the error: print(f"Error processing presentation_children: {e}")
        
        # Add to data list
        data.append(concept_info)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    
    # Normalize the labels column (optional)
    labels_df = pd.json_normalize(df['labels'].apply(lambda x: {f"{lang.split('/')[-1]}": text 
                                                            for lang, roles in x.items() 
                                                            for role, text in roles.items()}))
    # Update column names to remove redundant parts
    #labels_df.columns = [col.split('|')[0] + '_' + col.split('/')[-1] for col in labels_df.columns]
        
    # Drop the original labels column and concatenate with normalized labels
    df = df.drop('labels', axis=1)
    df = pd.concat([df, labels_df], axis=1)
    #df.loc[df.concept_name.str.contains("Revenue")].to_dict()
    #df.loc[df.concept_name=="UnrecognizedTaxBenefits"].to_dict()
    #df.loc[df.concept_name.str.contains("TaxBenefit")].to_dict()
    return df

if __name__ == "__main__":
    CACHE_DIR = os.path.expanduser("~/.xbrl_cache")
    #data_pool = Pool(cache_folder=CACHE_DIR, max_error=10)
    data_pool = pool.Pool(cache_folder=CACHE_DIR, max_error=10); #self = data_pool
    location = "https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-all-2024.xsd"
    tax = data_pool.add_taxonomy([location], esef_filing_root=os.getcwd())

    df = export_taxonomy_to_dataframe(tax)
    df.iloc[4492]
    df.to_excel("us-gaap-all-2024.xlsx", index=False)
```

## try_virtualfs.py
```py
"""
To work around the issue of loading files from a virtual folder in memory, you can use the io module to create a virtual file system using BytesIO for binary data or StringIO for text data. However, since the lxml library requires a file-like object that behaves like a file on disk, you can use the pyfilesystem2 library, which provides a more complete virtual file system interface.
Here's how you can implement this using pyfilesystem2 to create a virtual folder and load your files from there:
"""

#   pip install pyfilesystem2
from fs.memory import MemoryFileSystem

# ... existing code ...

# Create a virtual file system
mem_fs = MemoryFileSystem()

if filing.xbrl_files.get("xml"):
    xml_filename = filing.xbrl_files.get("xml")
    instance_str = filing.documents[xml_filename].doc_text.data
    instance_str = clean_doc(instance_str)
    
    # Write the instance document to the virtual file system
    mem_fs.writexml(xml_filename, instance_str)

    # Load the instance document from the virtual file system
    with mem_fs.open(xml_filename) as instance_io:
        instance_tree = lxml_etree.parse(instance_io)
        root = instance_tree.getroot()
        xid = data_pool.add_instance_element(root, key=f"virtual://{xml_filename}", attach_taxonomy=False)

    for linkbase_type in ["cal", "def", "lab", "pre"]:
        linkbase_filename = filing.xbrl_files.get(linkbase_type)
        if linkbase_filename:
            linkbase_str = filing.documents[linkbase_filename].doc_text.data
            linkbase_str = clean_doc(linkbase_str)
            # Write the linkbase document to the virtual file system
            mem_fs.writexml(linkbase_filename, linkbase_str)
            # Load the linkbase document from the virtual file system
            with mem_fs.open(linkbase_filename) as linkbase_io:
                data_pool.add_reference_from_string(linkbase_io.read(), location=f"virtual://{linkbase_filename}")

    if filing.xbrl_files.get("sch"):
        schema_filename = filing.xbrl_files.get("sch")
        schema_str = filing.documents[schema_filename].doc_text.data
        schema_str = clean_doc(schema_str)
        # Write the schema document to the virtual file system
        mem_fs.writexml(schema_filename, schema_str)
        # Load the schema document from the virtual file system
        with mem_fs.open(schema_filename) as schema_io:
            data_pool.add_schema_from_string(schema_io.read(), location=f"virtual://{schema_filename}")
```

## util.py
```py
import os, itertools, hashlib, datetime, string, re
from functools import reduce
from openesef.base import const
from lxml import etree as lxml
from lxml import html as lhtml


def parse_xml_string(s):
    p = lxml.XMLParser(huge_tree=True)
    try:
        root = lxml.XML(bytes(s, encoding='utf-8'), parser=p)
    except:
        return None
    return root


def parse_html_string(s):
    try:
        root = lhtml.fromstring(s.encode('ascii'))
    except:
        return None
    return root


def u_dct_list(dct, key, val):
    """ Updates a dictionary, where key is a string and value is a list with a specific value. """
    lst = dct.get(key, None)
    if lst is None:
        lst = []
        dct[key] = lst
    lst.append(val)


def get_lang(resources):
    res = resources.get('label', {})
    li = [v.lang for l in res.values() for v in l]
    return li[0] if li else None


def get_label(lst, lang='en', role='/label'):
    li = [lbl.text for lbl in get_resource_nlr(lst, 'label', lang, role)]
    if not li:
        li = [lbl.text for lbl in get_resource_nlr(lst, 'label', None, role) if lbl and lbl.text]
    # If there are more than 1 label with given role, - get the shortest one
    return sorted(li, key=lambda x: len(x) if x else 0)[0] if li else ''


def get_rc_label(lst):
    return '' if lst is None else ','.join(
        ['' if lbl.text is None else lbl.text for lbl in get_resource_nlr(lst, 'label', 'en', const.ROLE_LABEL_RC)])


def get_db_label(lst):
    return '' if lst is None else ','.join(
        ['' if lbl.text is None else lbl.text for lbl in get_resource_nlr(lst, 'label', 'en', const.ROLE_LABEL_DB)])


def get_reference(resources, lang='en', role='/label'):
    return get_resource_nlr(resources, 'reference', lang, role)


def get_resource_nlr(resources, name, lang, role):
    # resources is a dictionary where the key is lang + role and value is a list of corresponding resources
    res = resources.get(name, {})
    return res.get(f'{lang}|{role}', get_resource_nlr_partial(res, lang, role))


def get_resource_nlr_partial(resources, lang, role):
    lst = [v for k, v in resources.items() if
           (lang is None or k.startswith(lang)) and (role is None or k.endswith(role))]
    result = list(itertools.chain(*lst))
    return [] if result is None else result


def escape_xml(s):
    if not (isinstance(s, str) or isinstance(s, float) or isinstance(s, int)):
        return ''
    if isinstance(s, int) or isinstance(s, float):
        s = f'{s}'
    return '' if not s else s \
        .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') \
        .replace("'", '&apos;').replace('"', '&quot;')


def normalize(s):
    is_ws = False
    o = []
    for c in s.strip():
        if not c.isspace() or not is_ws:
            o.append(c)
        is_ws = c.isspace()
    return ''.join(o)


def remove_chars(s, disallowed, replacement=''):
    return reduce(lambda x, y: x.replace(y, replacement), [s] + disallowed)


def strip_inside_brackets(s, opening, closing):
    if s is None:
        return ''
    rexp = '\\'+opening+'[^()]*\\'+closing
    return normalize(re.sub(rexp, '', s))


def get_local_name(tag):
    return tag[tag.find('}') + 1:] if '}' in tag else tag


def get_namespace(tag):
    return tag[1:tag.find('}')] if '}' in tag else None


def reduce_url_parts(parts):
    if not parts:
        return None
    new_parts = []
    for p in [p for p in parts if p != '.']:
        if p == '..' and new_parts:
            new_parts.pop()
        else:
            new_parts.append(p)
    return new_parts


def reduce_url(url):
    return '/'.join(reduce_url_parts(url.replace(os.path.sep, "/").split('/'))) if url else None


def shorten(s, maxlen=100):
    """ Shortens a string and add ... at the end """
    return (s[:maxlen] + ' ...') if len(s) > maxlen else s


def get_hash(s, digest_size=12):
    return hashlib.shake_256(s.encode()).hexdigest(digest_size)


def get_hash40(s):
    return get_hash(s, digest_size=20)


def get_sha1(s):
    return hashlib.sha1(s.encode()).hexdigest()


def get_id():
    return get_hash(str(datetime.datetime.now()))


def is_numeric_type(s):
    kind = const.xsd_types.get(s, None)
    return False if kind is None or kind != 'n' else True


def is_date_type(s):
    kind = const.xsd_types.get(s, None)
    return False if kind is None or kind != 'd' else True


def is_string_type(s):
    kind = const.xsd_types.get(s, None)
    return False if kind is None or kind != 's' else True


def is_boolean_type(s):
    kind = const.xsd_types.get(s, None)
    return False if kind is None or kind != 'b' else True


def is_binary_type(s):
    kind = const.xsd_types.get(s, None)
    return False if kind is None or kind != 'x' else True


def strip_chars(s, allowed):
    o = []
    for c in s.strip():
        if c.isnumeric() or c in allowed:
            o.append(c)
    return ''.join(o)


def get_key_lower(s):
    if not s:
        return s
    return s.translate(str.maketrans('', '', string.punctuation)).lower()


def create_key_index(dct):
    result = {}
    for k, v in dct.items():
        result[get_key_lower(k)] = v
    return result


def is_float(s):
    if not s:
        return False
    return False if re.fullmatch('^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$', s) is None else True


def split_camel(s):
    return ''.join([' ' + c.lower() if c.isupper() else c for c in s]).strip().split(' ')
```
