from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from .dtd import DTD


# According to the EDGAR SGML specs, DOCUMENT.TEXT has the following children
# https://www.sec.gov/info/edgar/specifications/pds-dissemination-spec030314.pdf
attrs = ['pdf', 'xml', 'xbrl', 'table', 'caption', 'stub', 'column', 'footnotes_section']

class DocumentText:
    '''
    Used to model a DOCUMENT.TEXT element within an EDGAR SGML
    '''
    dtd = DTD()

    def __init__(self, data):
        '''
        Constructor

        :param data: a dictionary of parsed SGML DOCUMENT.TEXT;
            keys are tags and values are data as strings
        '''
        self.data = data

        # use data to set attributes
        for attr in attrs:
            tag = getattr(self.dtd, attr).tag

            if type(data) is dict and tag in data:
                value = data[tag]

                if attr == 'xml':
                    # for everything else, we take the text as is
                    value = BeautifulSoup(value, 'html.parser')

                setattr(self, attr, value)

    def __str__(self):
        return self.data
    def __repr__(self):
        return  f"DocumentText(data={self.__str__()[:100]})"
