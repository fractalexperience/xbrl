import urllib.request
import os, tempfile
import shutil
from xbrl.base import const, util


class Resolver:
    def __init__(self, cache_folder=None, output_folder=None):
        self.cache_folder = cache_folder
        self.output_folder = output_folder
        if self.cache_folder is None:
            temp_dir = tempfile.gettempdir()
            xbrl_dir = os.path.join(temp_dir, 'xbrl')
            if not os.path.exists(xbrl_dir):
                os.mkdir(xbrl_dir)
            if self.output_folder is None:
                self.output_folder = os.path.join(xbrl_dir, 'output')
                if not os.path.exists(self.output_folder):
                    os.mkdir(self.output_folder)
            cache_dir = os.path.join(xbrl_dir, 'cache')
            if not os.path.exists(cache_dir):
                os.mkdir(cache_dir)
            self.cache_folder = cache_dir
        self.taxonomies_folder = os.path.join(self.cache_folder, 'taxonomies')
        if not os.path.exists(self.taxonomies_folder):
            os.mkdir(self.taxonomies_folder)

    def cache(self, location):
        if location is None:
            return None
        parts = location.replace(os.path.pathsep, "/").split('/')
        new_parts = util.reduce_url_parts(parts)
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
