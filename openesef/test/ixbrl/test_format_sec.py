import sys
sys.path.insert(0, r'../../../')
from xbrl.ixbrl.m_format import Formatter


def test_numwordsen():
    formatter = Formatter()
    formatted = formatter.apply_format('one', 'numwordsen')
    assert formatted == 1
