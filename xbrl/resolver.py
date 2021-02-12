import urllib.request
import os
import shutil
from xbrl import const


class Resolver:
    def __init__(self, cache_folder=None):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        if cache_folder is None:
            self.cache_folder = os.path.join(dirname, 'cache')
        else:
            self.cache_folder = cache_folder
        if not os.path.exists(self.cache_folder):
            os.mkdir(self.cache_folder)

    def cache(self, location):
        if location is None:
            return None
        parts = location.replace(os.path.pathsep, "/").split('/')
        new_parts = self.reduce(parts)
        protocol = new_parts[0].replace(':','')
        if protocol not in const.KNOWN_PROTOCOLS:
            return location
        cached_file = self.cache_folder
        new_location = '/'.join(new_parts)
        # Starts from the second part, because the first one is the protocol and the second one is empty.
        # The last part of this list is the file name, so it is handled separately
        for part in new_parts[2:-1]:
            cached_file = os.path.join(cached_file, part)
            if not os.path.exists(cached_file):
                os.makedirs(cached_file)
        fn = new_parts[-1]
        cached_file = os.path.join(cached_file, fn)
        if not os.path.exists(cached_file):
            temp_file, headers = urllib.request.urlretrieve(new_location)
            shutil.move(temp_file, cached_file)
        return cached_file

    def reduce(self, parts):
        new_parts = []
        for p in parts:
            if p == '..':
                new_parts.pop()
            else:
                new_parts.append(p)
        return new_parts

    def reduce_url(self, url):
        parts = self.reduce(url.replace(os.path.pathsep, "/").split('/'))
        return "/".join(parts)