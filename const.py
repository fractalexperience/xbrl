# Namespaces
# Basic XML
NS_XML = 'http://www.w3.org/XML/1998/namespace'
NS_XS = 'http://www.w3.org/2001/XMLSchema'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
# XHTML
NS_XHTML = 'http://www.w3.org/1999/xhtml'
# XLINK
NS_XLINK = 'http://www.w3.org/1999/xlink'
# Basic XBRL
NS_XBRLI = 'http://www.xbrl.org/2003/instance'
NS_LINK = 'http://www.xbrl.org/2003/linkbase'
NS_ISO4217 = 'http://www.xbrl.org/2003/iso4217'
# XBRL XDT
NS_XBRLDI = 'http://xbrl.org/2006/xbrldi'
NS_XBRLDT = 'http://xbrl.org/2005/xbrldt'
# EBA
NS_FIND = 'http://www.eurofiling.info/xbrl/ext/filing-indicators'
# Generic links
NS_GEN = 'http://xbrl.org/2008/generic'
# OTHER
KNOWN_PROTOCOLS = ['http', 'https', 'ftp']
SUBSTITUTION_GROUPS = ['item', 'tuple']
# Standard roles
ROLE_LABEL = 'http://www.xbrl.org/2003/role/label'
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
# LabelResource
CONEPT_LABEL_ARCROLE  = 'http://www.xbrl.org/2003/arcrole/concept-label'
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
# Assertions
ASSERTION_SET_ARCROLE = 'http://xbrl.org/arcrole/2008/assertion-set'
ASSERTION_UNSATISFIED_SEVERITY_ARCROLE = 'http://xbrl.org/arcrole/2016/assertion-unsatisfied-severity'
