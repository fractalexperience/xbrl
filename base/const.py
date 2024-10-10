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
    XDT_DOMAIN_MEMBER_ARCROLE,
    # XDT_ALL_ARCROLE,
    # XDT_NOTALL_ARCROLE,
    # XDT_DIMENSION_DOMAIN_ARCROLE,
    # XDT_DIMENSION_DEFAULT_ARCROLE,
    # XDT_HYPERCUBE_DIMENSION_ARCROLE
)
