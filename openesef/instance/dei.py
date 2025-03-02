"""


Summary of Changes and Steps:

Adapted the code from https://github.com/ifanchu/pyXBRL/blob/master/xbrl.py

Rename dei.Context to DEI_ContextType in dei.py.

Modify m_xbrl.py (or instance.py if more appropriate) to:

Add self.dei = {} to XbrlModel.__init__.

Create a _parse_dei method in XbrlModel and call it from __init__.

Move the DEI extraction logic from XBRLDocument._determine_dei and _find_contexts into XbrlModel._parse_dei, adapting it to work within the existing XbrlModel fact parsing loop.

Remove the _find_contexts method if context handling is already sufficient in context.py.

Remove the XBRLDocument class from dei.py.

Update instance.py to access DEI from self.xbrl.dei instead of creating XBRLDocument.

By following these steps, you'll integrate DEI parsing more efficiently into your existing openesef project, avoid redundancy, and resolve the naming conflict. Let me know if you have any more questions or need further clarification on any of these steps!
"""


# instance/dei.py
from lxml import etree
from datetime import date
#from .. import fbase  # Assuming fbase.py is in the parent directory

class DEI_ContextType(object):
    """A simulated Enum class to represent 2 different contexts: Instant and Duration
    Renamed from `Context` to `DEI_ContextType` to avoid conflict with the library name
    """
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
DEI.DocumentAnnualReport = DEI('DocumentAnnualReport')
DEI.DocumentTransitionReport = DEI('DocumentTransitionReport')
DEI.EntityFileNumber = DEI('EntityFileNumber')
DEI.EntityIncorporationStateCountryCode = DEI('EntityIncorporationStateCountryCode')
DEI.EntityTaxIdentificationNumber = DEI('EntityTaxIdentificationNumber')
DEI.EntityAddressAddressLine1 = DEI('EntityAddressAddressLine1')
DEI.EntityAddressCityOrTown = DEI('EntityAddressCityOrTown')
DEI.EntityAddressStateOrProvince = DEI('EntityAddressStateOrProvince')
DEI.EntityAddressPostalZipCode = DEI('EntityAddressPostalZipCode')
DEI.CityAreaCode = DEI('CityAreaCode')
DEI.LocalPhoneNumber = DEI('LocalPhoneNumber')

DEI.EntityInteractiveDataCurrent = DEI('EntityInteractiveDataCurrent')
DEI.EntitySmallBusiness = DEI('EntitySmallBusiness')
DEI.EntityEmergingGrowthCompany = DEI('EntityEmergingGrowthCompany')
DEI.IcfrAuditorAttestationFlag = DEI('IcfrAuditorAttestationFlag')
DEI.EntityShellCompany = DEI('EntityShellCompany')  

## XBRLDocument class removed - DEI parsing integrated into XbrlModel

# class XBRLDocument(fbase.XmlFileBase):  # Inherit from fbase.XmlFileBase
#     """
#     This class represents an XBRL XML file from SEC EDGAR.
#     """

#     def __init__(self, url):
#         """
#         This url can be a local file path or a http url points to the xml file
#         """
#         super().__init__(url)  # Initialize the base class
#         self.url = url
#         try:
#             # self.doc_root = etree.parse(url).getroot() # Handled by XmlFileBase
#             self.doc_root = self.xml_root  # Use the parsed XML from XmlFileBase
#         except IOError as err:
#             raise err
#         self.nsmap = {}
#         for key in self.doc_root.nsmap.keys():
#             if key:
#                 self.nsmap[key] = self.doc_root.nsmap[key]
#         self.nsmap['xbrli'] = 'http://www.xbrl.org/2003/instance'
#         self.nsmap['xlmns'] = 'http://www.xbrl.org/2003/instance'

#         self.fiscal_year = 0
#         self.fiscal_period_end_date = None
#         self.dei = {}
#         self._determine_dei()

#         self.context_instant = ''
#         self.context_duration = ''
#         self._find_contexts()

#     def _determine_dei(self):
#         """For all DEI, fetch the value from XBRL xml and put it in self.dei"""
#         for dei in DEI.all():
#             fact_name = dei.fact_name
#             nodes = self.doc_root.xpath('//{0}'.format(fact_name), namespaces=self.nsmap)
#             value = nodes[0].text if nodes and len(nodes) > 0 else ''
#             if not value:
#                 value = ''
#             self.dei[dei] = value

#         if not self.dei[DEI.TradingSymbol] or self.dei[DEI.TradingSymbol] == '':
#             self.dei[DEI.TradingSymbol] = self.url.split('/')[-1].split('.')[0].split('-')[0].upper()

#         tokens = self.dei[DEI.DocumentPeriodEndDate].split('-')
#         tokens = tuple(int(x) for x in tokens)
#         self.fiscal_period_end_date = date(tokens[0], tokens[1], tokens[2])

#         if not self.dei[DEI.DocumentFiscalYearFocus]:
#             self.dei[DEI.DocumentFiscalYearFocus] = self.fiscal_period_end_date.year

#         self.fiscal_year = int(self.dei[DEI.DocumentFiscalYearFocus])

#     def _find_contexts(self):
#         """Find instant and duration contextRef"""
#         context_instant = ''
#         context_duration = ''
#         END_DATE = str(self.fiscal_period_end_date)
#         document_type = self.dei[DEI.DocumentType]

#         for node in self.doc_root.xpath("//*[local-name() = 'context']"):
#             entity_node = None
#             period_node = None

#             for child in node.getchildren():
#                 tag = child.tag[child.tag.find('}') + 1:]
#                 if tag == 'entity':
#                     entity_node = child
#                 elif tag == 'period':
#                     period_node = child

#             if len(entity_node.getchildren()) != 1:
#                 continue

#             if not 'identifier' in entity_node.getchildren()[0].tag:
#                 continue

#             if len(period_node.getchildren()) == 1:
#                 instant_node = period_node.getchildren()[0]
#                 if instant_node.text != END_DATE:
#                     continue
#                 context_instant = node.get('id')

#             elif len(period_node.getchildren()) == 2:
#                 start_date_node = period_node.getchildren()[0]
#                 end_date_node = period_node.getchildren()[1]
#                 if end_date_node.text != END_DATE:
#                     continue

#                 if 'Q' in document_type:
#                     year, month = self.fiscal_period_end_date.year, self.fiscal_period_end_date.month
#                     start_month = 12 if (month - 2) % 12 == 0 else (month - 2) % 12
#                     start_year = year - 1 if month <= 2 else year
#                     filter_text1 = '{0}-{1:02d}'.format(start_year, start_month)

#                     start_month = 12 if (month - 3) % 12 == 0 else (month - 3) % 12
#                     start_year = year - 1 if month <= 3 else year
#                     filter_text2 = '{0}-{1:02d}'.format(start_year, start_month)

#                     if filter_text1 not in start_date_node.text and filter_text2 not in start_date_node.text:
#                         continue

#                 context_duration = node.get('id')

#         self.context_instant = context_instant
#         self.context_duration = context_duration

#     def _get_elementlist(self, fact_name, context_type=Context.Duration):
#         """
#         In an XBRL xml document, there will be multiple context defined, but only 1 instant context and 1 duration context for current year.
#         """
#         ret = []
#         if context_type == Context.Duration:
#             main, secondary = self.context_duration, self.context_instant
#         elif context_type == Context.Instant:
#             main, secondary = self.context_instant, self.context_duration

#         ret.extend(self.doc_root.xpath("//{0}[@contextRef='{1}']".format(fact_name, main), namespaces=self.nsmap))

#         if len(ret) == 0:
#             ret.extend(self.doc_root.xpath("//{0}[@contextRef='{1}']".format(fact_name, secondary), namespaces=self.nsmap))

#         return tuple(ret)

#     def get_fact_value(self, fact_name):
#         """Given fact_name, return the text for that fact. If not found, return empty string"""
#         ret = self._get_elementlist(fact_name)
#         return ret[0].text if ret else ''

#     def get_dei_value(self, dei_item):
#         """A convenience method to get the DEI value from self.dei"""
#         if not isinstance(dei_item, DEI):
#             raise ValueError('Given dei_item is not of type DEI')
#         if dei_item not in self.dei:
#             return ''
#         return self.dei[dei_item]