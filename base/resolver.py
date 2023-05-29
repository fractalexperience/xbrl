import os
import shutil
import tempfile
import urllib.request
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
        parts = location.replace(os.path.sep, "/").split('/')
        new_parts = util.reduce_url_parts(parts)
        protocol = new_parts[0].replace(':', '')
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
            user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
            headers = {'User-Agent': user_agent}
            req = urllib.request.Request(new_location, headers=headers)
            with urllib.request.urlopen(req) as response:
                html = response.read()
                with open(cached_file, 'w', encoding='utf-8') as f:
                    try:
                        s = html.decode(encoding='utf-8')
                        f.write(s)
                    except Exception as ex:
                        print(ex)
            # temp_file, headers = urllib.request.urlretrieve(new_location)
            # shutil.move(temp_file, cached_file)

        return cached_file
