from zipfile import ZipFile, ZIP_DEFLATED
from xbrl.base import util
import lxml.html as lhtml
import zlib
import os
import json


class Archiver:
    """ Basic class for storing content in ZIP archives """

    def __init__(self, zip_folder, length=3):
        self.zip_folder = zip_folder
        if not os.path.exists(self.zip_folder):
            os.mkdir(self.zip_folder)
        """ Length of archive ZIP files Because we have 16 possible characters for file name, the total number of 
        ZIP files is 16^length. For example 2 corresponds to 256 files, 3 corresponds to 4096 files etc. """
        self.archive_file_length = min(max(1, length), 4)
        """ All open archives."""
        self.zip_cache = {}
        """ All written file names."""
        self.written_hashes = set()
        """ Key is the original reference (inside HTML), value is the resolved content based hash. """
        self.map_id_hash = {}
        """ Temporary cache for HTMl files. """
        self.html_cache = {}

    def create_archive(self, file_hash):
        zfn = f'{os.path.join(self.zip_folder, file_hash)}.zip'
        if os.path.exists(zfn):
            os.remove(zfn)
        return ZipFile(zfn, 'w', compression=zlib.DEFLATED)

    def get_archive(self, filename, zip_prefix=None):
        if zip_prefix is None:
            zip_prefix = self.get_zip_prefix(filename)
        zip_path = os.path.join(self.zip_folder, f'{zip_prefix}.zip')
        archive = self.zip_cache.get(zip_prefix)
        if archive is not None:
            return archive
        if os.path.exists(zip_path):
            archive = ZipFile(zip_path, mode='a', compression=ZIP_DEFLATED, compresslevel=7)
        else:
            archive = self.create_archive(zip_prefix)
        self.zip_cache[zip_prefix] = archive
        return archive

    def get_zip_prefix(self, filename):
        hsh = util.get_sha1(filename)
        pref = hsh[:self.archive_file_length]
        return pref

    def store_content(self, filename, content, zip_prefix=None):
        archive = self.get_archive(filename, zip_prefix)
        if filename in self.written_hashes:
            return
        try:
            archive.writestr(filename, content)
            self.written_hashes.add(filename)
        except ValueError:
            print('Archive is closed')
        except Exception as ex:
            print(ex)

    def store_html(self, filename, content):
        s = content if isinstance(content, str) else (
            content.decode() if isinstance(content, bytes) else ''.join(content))
        self.html_cache[filename] = s

    def flush_html(self):
        # Index content hash map
        print('Index content hash map', len(self.html_cache), 'items')
        map_id_dom = {}
        for filename, s in self.html_cache.items():
            ext = '' if '.' not in filename else filename.split('.')[-1]
            content_hash = util.get_sha1(filename)
            if not s.startswith('<?xml'):
                try:
                    dom = lhtml.fromstring(s)
                    # Calculate a hash code based on content. IMPORTANT: We remove href attributes before calculating hash.
                    content_no_hrefs = lhtml.tostring(lhtml.rewrite_links(dom, lambda l: None))
                    content_hash = util.get_sha1(content_no_hrefs.decode())
                    map_id_dom[filename] = dom
                except:
                    continue
            self.map_id_hash[filename] = f'{content_hash}.{ext}'

        # Replace references inside HTML reports with content based hashes and save to ZIP archives
        print('Replace references inside HTML reports', len(self.html_cache), 'items')
        for filename, s in self.html_cache.items():
            content_reduced_hrefs = s
            dom = map_id_dom.get(filename)
            content_hash = self.map_id_hash.get(filename)
            if dom is not None:
                content_reduced_hrefs = lhtml.tostring(lhtml.rewrite_links(
                    dom, lambda l: self.map_id_hash.get(l, l) if '=' not in l else
                    l.split('=')[0] + '=' +
                    self.map_id_hash.get(l.split('=')[1] + '.html',
                                         self.map_id_hash.get(l.split('=')[1] + '.xml', '')).split('.')[0]))

            ext = '' if '.' not in filename else filename.split('.')[-1]
            new_filename = f'{content_hash}'
            # Store resolved HTML content
            self.store_content(new_filename, content_reduced_hrefs, new_filename[:self.archive_file_length])

    def close(self):
        # Store collected HTML files in the cache
        self.flush_html()
        # Flush content of ZIP archives
        for zip_id, archive in self.zip_cache.items():
            archive.close()
        self.zip_cache = {}
        # Clear HTMl cache
        self.html_cache = {}

        # with open(os.path.join(self.zip_folder, 'map.json'), "w") as f:
        #     json.dump(self.map_id_hash, f)
        print('closed - written hashes: ', len(self.written_hashes))

    def open(self):
        files = [it.path for it in os.scandir(self.zip_folder) if it.path.endswith('zip')]
        # print(len(files), 'ZIP archives found')
        for file in files:
            archive = ZipFile(file, mode='r')
            pref = file.split(os.sep)[-1].split('.')[0]
            # self.zip_cache[pref] = archive
            self.written_hashes.update(set([f.filename for f in archive.filelist]))
            archive.close()
        print('opened - written hashes: ', len(self.written_hashes))

    def reset_database(self):
        exts = ['zip']
        files = [i.path for i in os.scandir(self.zip_folder) if i.path.split('.')[-1] in exts]
        # Conversion to list is needed in order to execute the loop
        list(map(lambda z: os.remove(z), files))
        # print(len(files), f'files deleted from {self.zip_folder} folder')

    def read_content(self, filename):
        archive = self.get_archive(filename)
        try:
            with archive.open(filename, 'r') as f:
                return f.read().decode()
        except KeyError:
            return self.read_content_hash(filename)
        except Exception as ex:
            print(ex)
        return None

    def read_content_hash(self, filename):
        # Now try to find a hashed file name
        filename_resolved = self.map_id_hash.get(filename)
        if filename_resolved is None:
            return None
        archive = self.get_archive(filename_resolved)
        with archive.open(filename, 'r') as f:
            return f.read().decode()