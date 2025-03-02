from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
import re
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from .dtd import DTD


# According to the EDGAR SGML specs, DOCUMENT.TEXT has the following children
# https://www.sec.gov/info/edgar/specifications/pds-dissemination-spec030314.pdf
attrs = ['pdf', 'xml', 'xbrl', 'table', 'caption', 'stub', 'column', 'footnotes_section']


def clean_doc(text):
    if type(text) == dict:
        text =  list(text.values())[0]
    text = re.sub(r'^<XBRL>', '', text)
    text = re.sub(r'</XBRL>$', '', text)
    text = re.sub(r"\n", '', text)
    return text


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
        

        # use data to set attributes
        for attr in attrs:
            tag = getattr(self.dtd, attr).tag

            if type(data) is dict and tag in data:
                value = data[tag]
                value = re.sub(r"\n", '', value)
                value = re.sub(r'^<XBRL>', '', value)
                value = re.sub(r'</XBRL>$', '', value)
                data[tag] = value

                if attr == 'xml':
                    # for everything else, we take the text as is
                    #value = clean_doc(value)

                    value = BeautifulSoup(value, 'html.parser')

                setattr(self, attr, value)
            elif type(data) is str:
                data = re.sub(r"\n", '', data)
                data = re.sub(r'^<XBRL>', '', data)
                data = re.sub(r'</XBRL>$', '', data)
        self.data = data        


    def __str__(self):
        return self.data
    def __repr__(self):
        return  f"DocumentText(data={self.__str__()[:100]})"
