import os
import itertools
from xbrl.base import const


def u_dct_list(dct, key, val):
    """ Updates a dictionary, where key is a string and value is a list with a specific value. """
    lst = dct.get(key, None)
    if lst is None:
        lst = []
        dct[key] = lst
    lst.append(val)


def get_label(lst, lang='en', role='/label'):
    return ','.join([lbl.text for lbl in get_resource_nlr(lst, 'label', lang, role)]) if lst else ''


def get_rc_label(lst):
    return ','.join([lbl.text for lbl in get_resource_nlr(lst, 'label', 'en', const.ROLE_LABEL_RC)]) if lst else ''


def get_db_label(lst):
    return ','.join([lbl.text for lbl in get_resource_nlr(lst, 'label', 'en', const.ROLE_LABEL_DB)]) if lst else ''


def get_reference(res_list, lang='en', role='/label'):
    return get_resource_nlr(res_list, 'reference', lang, role)


def get_resource_nlr(res_list, name, lang, role):
    # res is a dictionary where the key is lang + role and value is a list of corresponding resources
    res = res_list.get(name, None)
    if res is None:
        return []
    return res.get(f'{lang}|{role}', get_resource_nlr_partial(res, lang, role))


def get_resource_nlr_partial(res, lang, role):
    l = [v for k, v in res.items() if (lang is None or k.startswith(lang)) and (role is None or k.endswith(role))]
    result = list(itertools.chain(*l))
    return [] if result is None else result


def escape_xml(s):
    return '' if not s else s\
        .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
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
    for p in parts:
        if p == '..' and new_parts:
            new_parts.pop()
        else:
            new_parts.append(p)
    return new_parts


def reduce_url(url):
    return '/'.join(reduce_url_parts(url.replace(os.path.sep, "/").split('/'))) if url else None
