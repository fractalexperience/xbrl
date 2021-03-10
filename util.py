import os


def u_dct_list(dct, key, val):
    """ Updates a dictionary, where key is a string and value is a list with a specific value. """
    lst = dct.get(key, None)
    if lst is None:
        lst = []
        dct[key] = lst
    lst.append(val)


def escape_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
        .replace("'", '&apos;').replace('"', '&quot;')


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
    return '/'.join(reduce_url_parts(url.replace(os.path.pathsep, "/").split('/'))) if url else None
