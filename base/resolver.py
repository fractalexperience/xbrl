import os
import shutil
import tempfile
import urllib.request
from xbrl.base import const, util
import logging 
import requests
import traceback
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def download_file(self, url, cached_file):
        """
        Download a file with proper headers and error handling
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        try:
            logger.info(f"Downloading {url} to {cached_file}")
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()

            # Determine if the content is text or binary based on content-type
            content_type = response.headers.get('content-type', '').lower()
            is_text = 'text' in content_type or 'xml' in content_type

            # Get total size for logging
            total_size = int(response.headers.get('content-length', 0))
            
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(cached_file), exist_ok=True)

            # Download with progress tracking
            downloaded = 0
            mode = 'w' if is_text else 'wb'
            encoding = 'utf-8' if is_text else None

            with open(cached_file, mode, encoding=encoding) as f:
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=is_text):
                    if chunk:
                        if is_text:
                            f.write(chunk)
                        else:
                            f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress = (downloaded / total_size) * 100
                            logger.debug(f"Download progress: {progress:.2f}%")

            logger.info(f"Successfully downloaded {url}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            if os.path.exists(cached_file):
                os.remove(cached_file)  # Clean up partial download
            traceback.print_exc()
            raise Exception(f"Failed to download {url}: {str(e)}")

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

        # If file doesn't exist or is empty, download it
        if not os.path.exists(cached_file) or os.path.getsize(cached_file) == 0:
            try:
                self.download_file(new_location, cached_file)
            except Exception as e:
                logger.error(f"Error caching {location}: {str(e)}")
                if os.path.exists(cached_file):
                    os.remove(cached_file)  # Clean up any partial download
                

        # if not os.path.exists(cached_file):
        #     user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        #     headers = {'User-Agent': user_agent}
        #     req = urllib.request.Request(new_location, headers=headers)
        #     with urllib.request.urlopen(req) as response:
        #         html = response.read()
        #         with open(cached_file, 'w', encoding='utf-8') as f:
        #             try:
        #                 s = html.decode(encoding='utf-8')
        #                 f.write(s)
        #             except Exception as ex:
        #                 print(ex)
        #     # temp_file, headers = urllib.request.urlretrieve(new_location)
        #     # shutil.move(temp_file, cached_file)

        return cached_file
