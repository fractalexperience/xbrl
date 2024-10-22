import os, itertools, hashlib, datetime, string, re
from functools import reduce
from xbrl.base import const
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

