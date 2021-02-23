def u_dct_list(dct, key, val):
    """ Updates a dictionary, where key is a string and value is a list with a specific value. """
    lst = dct.get(key, None)
    if lst is None:
        lst = []
        dct[key] = lst
    lst.append(val)


def escape_xml(s):
    return s\
        .Replace("&", "&amp;")\
        .Replace("<", "&lt;")\
        .Replace(">", "&gt;")\
        .Replace("\"", "&quot;")


def get_local_name(tag):
    return tag[tag.find('}') + 1:] if '}' in tag else tag


def get_namespace(tag):
    return tag[1:tag.find('}')] if '}' in tag else None

