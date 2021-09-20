import os
import itertools
import hashlib
from xbrl.base import const



def u_dct_list(dct, key, val):
    """ Updates a dictionary, where key is a string and value is a list with a specific value. """
    lst = dct.get(key, None)
    if lst is None:
        lst = []
        dct[key] = lst
    lst.append(val)


def get_label(lst, lang='en', role='/label'):
    li = [lbl.text for lbl in get_resource_nlr(lst, 'label', lang, role)]
    if not li:
        li = [lbl.text for lbl in get_resource_nlr(lst, 'label', None, role)]
    return li[0] if li else ''


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


def get_hash(s, digest_size=12):
    return hashlib.shake_256(s.encode()).hexdigest(digest_size)
