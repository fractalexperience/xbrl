"""
XBRL Pool Module Documentation

The Pool class serves as a central repository for managing XBRL taxonomies, instances, and related resources.
It inherits from Resolver class and provides functionality for loading, caching, and managing XBRL documents.

Key Features:
1. Taxonomy Management
   - Loading and caching taxonomies
   - Managing taxonomy packages
   - Handling multiple entry points

2. Instance Document Management
   - Loading instance documents from files, archives, or XML elements
   - Managing relationships between instances and taxonomies

3. Resource Management
   - Caching and resolving schemas and linkbases
   - Managing taxonomy packages
   - Handling alternative locations for resources

Class Attributes:
    taxonomies (dict): Stores loaded taxonomies
    current_taxonomy (Taxonomy): Reference to the currently active taxonomy
    current_taxonomy_hash (str): Hash identifier for the current taxonomy
    discovered (dict): Tracks discovered resources to prevent circular references
    schemas (dict): Stores loaded schema documents
    linkbases (dict): Stores loaded linkbase documents
    instances (dict): Stores loaded instance documents
    alt_locations (dict): Maps URLs to alternative locations
    packaged_entrypoints (dict): Maps entry points to package locations
    packaged_locations (dict): Maps locations to package contents
    active_packages (dict): Currently opened taxonomy packages
    active_file_archive (ZipFile): Currently opened archive file
"""

import os, zipfile, functools
from lxml import etree as lxml
from xbrl.base import resolver, util
from xbrl.taxonomy import taxonomy, schema, tpack, linkbase
from xbrl.instance import instance
import gzip
from xbrl.base import const, util
import os

import zipfile
import functools
import logging
import time
from typing import Optional, Dict, List, Union, Tuple
import traceback
import pathlib

import re 
import urllib.parse
from xbrl.base import util

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
#console_handler = logging.StreamHandler()

# Create formatters and add it to handlers
#log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#console_formatter = logging.Formatter(log_format)
#console_handler.setFormatter(console_formatter)


# Add handlers to the logger
#logger.addHandler(console_handler)


#file_handler = logging.FileHandler('xbrl_pool.log')
#file_formatter = logging.Formatter(log_format)
#file_handler.setFormatter(file_formatter)
#logger.addHandler(file_handler)


class Pool(resolver.Resolver):
    def __init__(self, cache_folder=None, output_folder=None, alt_locations=None):
        """
        Initializes a new Pool instance
        Args:
            cache_folder (str): Path to cache directory
            output_folder (str): Path to output directory
            alt_locations (dict): Alternative URL mappings        
        """
        logger.info(f"\n\nInitializing Pool with cache_folder={cache_folder}, output_folder={output_folder}")

        super().__init__(cache_folder, output_folder)
        self.taxonomies = {}
        self.current_taxonomy = None
        self.current_taxonomy_hash = None
        self.discovered = {}
        self.schemas = {}
        self.linkbases = {}
        self.instances = {}
        """ Alternative locations. If set, this is used to resolve Qeb references to alternative (existing) URLs. """
        self.alt_locations = alt_locations
        """ Index of all packages in the cache/taxonomy_packages folder by entrypoint """
        self.packaged_entrypoints = {}
        self.packaged_locations = None
        """ Currently opened taxonomy packages """
        self.active_packages = {}
        """ Currently opened archive, where files can be read from - optional."""
        self.active_file_archive = None

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        return '\n'.join([
            f'Taxonomies: {len(self.taxonomies)}',
            f'Instance documents: {len(self.instances)}',
            f'Taxonomy schemas: {len(self.schemas)}',
            f'Taxonomy linkbases: {len(self.linkbases)}'])

    def index_packages(self):
        """ Index the content of taxonomy packages found in cache/taxonomies/ """
        package_files = [os.path.join(r, file) for r, d, f in
                         os.walk(self.taxonomies_folder) for file in f if file.endswith('.zip')]
        for pf in package_files:
            self.index_package(tpack.TaxonomyPackage(pf))

    def index_package(self, package):
        """ Index the content of a taxonomy package """
        for ep in package.entrypoints:
            eps = ep.Urls
            for path in eps:
                self.packaged_entrypoints[path] = package.location

    def add_instance_location(self, location, key=None, attach_taxonomy=True):
        """
        Loads an instance document from a file location
        Args:
            location (str): File path or URL
            key (str): Optional identifier
            attach_taxonomy (bool): Whether to load associated taxonomy
        Returns:
            Instance: The loaded instance document"""        

        logger.info(f"\n\nAdding instance from location: {location}")
        location = os.path.abspath(location) # Ensure location is absolute
        if key is None:
            key = re.sub("file://", "", location)
            logger.debug(f"Using location as key: {key}")

        #base_dir = os.path.dirname(location)
        
        # Parse the XML document using the existing methods
        parser = lxml.XMLParser(huge_tree=True)
        logger.debug("Attempting to parse XML document")
        try:
            doc = lxml.parse(location, parser=parser)
            root = doc.getroot()
            
            # Find schema references
            nsmap = {'link': const.NS_LINK}
            schema_refs = root.findall(".//link:schemaRef", namespaces=nsmap)
            logger.info(f"Found {len(schema_refs)} schema references")
            
            for schema_ref in schema_refs:
                href = schema_ref.get(f'{{{const.NS_XLINK}}}href')
            if href:
                logger.debug(f"Processing schema reference: {href}")

                # Resolve the href first
                resolved_href = self.resolve_schema_ref(href, location)

                # THEN convert to file URL if it's a local path
                if resolved_href:
                    # 1. Ensure resolved_href is absolute BEFORE any modifications
                    if not resolved_href.startswith(('http://', 'https://', 'file://')):
                        resolved_href = os.path.abspath(resolved_href)

                    # 2. Convert to file URI if it's a local path, AFTER making it absolute
                    if not resolved_href.startswith(('http://', 'https://')):
                        resolved_href_removeprefix = resolved_href.replace('file://', '')
                        try:
                            #resolved_href = 'file://' + pathlib.Path(resolved_href_removeprefix).as_uri()
                            resolved_href = pathlib.Path(resolved_href_removeprefix).as_uri()
                        except Exception as e:
                            logger.error(f"Error adding {resolved_href} as uri: {str(e)}")
                            traceback.print_exc(limit=10)

                    # 3. Set the href in the XML element
                    schema_ref.set(f'{{{const.NS_XLINK}}}href', resolved_href)          

                else:
                    logger.warning(f"Could not resolve schema reference: {href}") # Log a warning

                schema_ref.set(f'{{{const.NS_XLINK}}}href', resolved_href)
                logger.debug(f"Resolved schema reference: \n{resolved_href}")            
            # Write back the modified XML
            doc.write(location)
            logger.debug("Successfully wrote back modified XML")

            # Continue with the original implementation
            location_removeprefix = re.sub("file://", "", location)
            xid = instance.Instance(location=location_removeprefix, container_pool=self)
            try:
                self.add_instance(xid, key, attach_taxonomy) # <= it raised an error here? 
                logger.info(f"Successfully added instance from {location_removeprefix}")
            except Exception as e:
                traceback.print_exc(limit=10)
                logger.error(f"Error adding instance from {location_removeprefix}: {str(e)}")
                logger.error(f"key: {key}")
                logger.error(f"location: {location}")
                logger.error(f"location_removeprefix: {location_removeprefix}")

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            traceback.print_exc(limit=10)
            return None
            
        return xid

    def add_instance_archive(self, archive_location, filename, key=None, attach_taxonomy=False):
        """
        Adds an XBRL instance from an archive file (supports both .zip and .gzip formats)
        
        Args:
            archive_location (str): Path to the archive file (.zip or .gzip)
            filename (str): Name of the file within the archive (for zip) or the original filename (for gzip)
            key (str, optional): Key to identify the instance. Defaults to None.
            attach_taxonomy (bool, optional): Whether to attach taxonomy. Defaults to False.
        
        Returns:
            Instance: The loaded XBRL instance or None if loading fails
        
        Raises:
            FileNotFoundError: If archive_location doesn't exist
            ValueError: If archive format is not supported
        """
        if not os.path.exists(archive_location):
            raise FileNotFoundError(f"Archive not found: {archive_location}")

        # Handle GZIP files
        if archive_location.endswith('.gzip'):
            try:
                with gzip.open(archive_location, 'rb') as gf:
                    content = gf.read()
                    root = lxml.XML(content)
                    return self.add_instance_element(
                        root,
                        filename if key is None else key,
                        attach_taxonomy
                    )
            except Exception as e:
                raise ValueError(f"Error processing gzip file: {str(e)}")

        # Handle ZIP files
        elif archive_location.endswith('.zip'):
            try:
                archive = zipfile.ZipFile(archive_location)
                zil = archive.infolist()
                xid_file = [f for f in zil if f.filename.endswith(filename)]
                
                if not xid_file:
                    raise ValueError(f"File {filename} not found in archive")
                    
                xid_file = xid_file[0]
                
                with archive.open(xid_file) as xf:
                    root = lxml.XML(xf.read())
                    return self.add_instance_element(
                        root,
                        xid_file if key is None else key,
                        attach_taxonomy
                    )
            except Exception as e:
                raise ValueError(f"Error processing zip file: {str(e)}")

        else:
            raise ValueError("Unsupported archive format. Use .zip or .gzip")
    
    def add_instance_element(self, e, key=None, attach_taxonomy=False):
        """
        Adds an instance document from an XML element
        Args:
            e (Element): XML element
            key (str): Optional identifier
            attach_taxonomy (bool): Whether to load associated taxonomy
        """
        xid = instance.Instance(container_pool=self, root=e)
        if key is None:
            key = e.tag
        self.add_instance(xid, key, attach_taxonomy)
        return xid

    def add_instance(self, xid, key=None, attach_taxonomy=False):
        """
        Adds an instance document to the pool
        Args:
            xid (Instance): The instance document to add
            key (str): Optional identifier
            attach_taxonomy (bool): Whether to load associated taxonomy
        """
        if key is None:
            key = xid.location_ixbrl
        self.instances[key] = xid

        if attach_taxonomy and xid.xbrl is not None:
            entry_points = [ref if ref.startswith('http') else self.resolve_schema_ref(ref, xid.location) # Use xid.location
                            for ref in xid.xbrl.schema_refs]

            #entry_points = [pathlib.Path(ep).as_uri() if not ep.startswith(('http://', 'https://')) else ep
            #                for ep in entry_points]
            # Convert to file URIs ONLY if it's a local file
            entry_points = [pathlib.Path(ep).as_uri() if os.path.isfile(ep) else ep  # Check if it's a file
                            for ep in entry_points]
            
            tax = self.add_taxonomy(entry_points)
            xid.taxonomy = tax

    def add_taxonomy(self, entry_points):
        """
        Adds a taxonomy from a list of entry points
        Args:
            entry_points (list): List of entry points
        Returns:
            Taxonomy: The loaded taxonomy object
        """
        logger.info("\n\nAdding taxonomy")
        ep_list = entry_points if isinstance(entry_points, list) else [entry_points]
        logger.info(f"Processing {len(ep_list)} entry points")

        # self.packaged_locations = {}
        for ep in ep_list:
            # if self.active_file_archive and ep in self.active_file_archive.namelist():
            #     self.packaged_locations[ep] = (self.active_file_archive, ep)
            # else:
            logger.debug(f"Processing entry point: {ep}")
            self.add_packaged_entrypoints(ep)
            logger.debug(f"Added packaged entry points for {ep}")
        key = ','.join(entry_points)
        logger.debug(f"Generated taxonomy key: {key}")
        if key in self.taxonomies:
            logger.debug(f"Taxonomy already loaded: {key}")
            return self.taxonomies[key]  # Previously loaded
        logger.debug(f"Loading new taxonomy")
        taxonomy.Taxonomy(ep_list, self)  # Sets the new taxonomy as current
        self.taxonomies[key] = self.current_taxonomy
        self.packaged_locations = None
        return self.current_taxonomy

    def add_packaged_entrypoints(self, ep):
        """
        Adds packaged entry points
        Args:
            ep (str): Entry point
        Returns: None
        """
        pf = self.packaged_entrypoints.get(ep)
        if not pf:
            return  # Not found
        pck = self.active_packages.get(pf, None)
        if pck is None:
            pck = tpack.TaxonomyPackage(pf)
            pck.compile()
        self.index_package_files(pck)

    def index_package_files(self, pck):
        """
        Indexes files in a taxonomy package
        Args:
            pck (TaxonomyPackage): The taxonomy package object
        Returns: None
        """
        if self.packaged_locations is None:
            self.packaged_locations = {}
        for pf in pck.files.items():
            self.packaged_locations[pf[0]] = (pck, pf[1])  # A tuple

    def cache_package(self, location):
        """ 
        Stores a taxonomy package from a Web location to local taxonomy package repository 
        Args:
            location (str): Location of taxonomy package
        Returns:
            TaxonomyPackage: The loaded taxonomy package object
        """
        package = tpack.TaxonomyPackage(location, self.taxonomies_folder)
        self.index_packages()
        return package
    
    def add_package(self, location):
        """
        Adds a taxonomy package provided in the location parameter, creates a taxonomy 
        using all entrypoints in the package and returns the taxonomy object.
        Args:
            location (str): Location of taxonomy package
        Returns:
            Taxonomy: The loaded taxonomy object
        """
        package = self.cache_package(location)
        self.active_packages[location] = package
        entry_points = [f for ep in package.entrypoints for f in ep.Urls]
        tax = self.add_taxonomy(entry_points)
        return tax

    def add_reference(self, href, base):
        """

        Loads referenced schema or linkbase
        Args:
            href (str): Reference URL
            base (str): Base URL for relative references
        Returns: None

        Loads schema or linkbase depending on file type. TO IMPROVE!!! -- original comment
        """
        logger.debug(f"\n\nAdding reference: \n{href} \nfrom base: \n{base}")
        if href is None:
            logger.debug("Reference URL is None")
            return

        # Validate file extension
        allowed_extensions = ('xsd', 'xml', 'json')
        file_ext = href.split('.')[-1]
        if file_ext not in allowed_extensions:
            logger.warning(f"Skipping reference: Invalid file extension {file_ext}")
            return        

        # Skip basic schema objects
        if any(domain in href for domain in ['http://xbrl.org', 'http://www.xbrl.org']):
            logger.debug("Skipping basic schema object")
            return

        # Handle alternative locations
        # Artificially replace the reference - only done for very specific purposes.
        if self.alt_locations and href in self.alt_locations:
            original_href = href
            href = self.alt_locations[href]
            logger.debug(f"Replaced href \n{original_href} \nwith alternative location \n{href}")            
            

        # Resolve URL
        if not href.startswith('http'):
            resolved_href = self._resolve_url(href, base)  # Use _resolve_url for consistent resolution
            logger.debug(f"Resolved URL to: {resolved_href}")

            # Check if already discovered using resolved_href
            key = f'{self.current_taxonomy_hash}_{resolved_href}'
            if key in self.discovered:
                logger.debug(f"Resource already discovered: {resolved_href}")
                return
            logger.debug(f"Resource not discovered: {resolved_href}")
            self.discovered[key] = False

        try:
            if resolved_href.endswith(".xsd"):
                logger.debug(f"Loading schema: \n{resolved_href}")

                if resolved_href.startswith("file://"):
                    schema_path = re.sub("file://", "", resolved_href) # Remove file:// for schema.Schema
                else:
                    schema_path = resolved_href # Use the URL directly

                logger.debug(f"schema_path: \n{schema_path}")

                sh = self.schemas.get(schema_path, schema.Schema(schema_path, self))
                self.current_taxonomy.attach_schema(schema_path, sh)
            else:
                logger.debug(f"Loading linkbase: \n{resolved_href}")
                # Remove file:// prefix if present
                if resolved_href.startswith("file://"):
                    resolved_href = re.sub("file://", "", resolved_href)

                lb = self.linkbases.get(resolved_href, linkbase.Linkbase(resolved_href, self)) # Use resolved_href
                self.current_taxonomy.attach_linkbase(resolved_href, lb) # Use resolved_href

        except OSError as e:
            logger.error(f"OSError Failed to load resource \n{href} \n{str(e)}")
            # Log the error but don't raise it to allow continued processing
            traceback.print_exc(limit=10)

        except Exception as e:
            logger.error(f"Failed to load resource \n{href} \n{str(e)}")
            traceback.print_exc(limit=10)

    @staticmethod
    def check_create_path(existing_path, part):
        new_path = os.path.join(existing_path, part)
        if not os.path.exists(new_path):
            os.mkdir(new_path)
        return new_path

    def save_output(self, content, filename):
        """
        Saves content to output directory
        Args:
            content (str): Content to save
            filename (str): Target filename
        Returns: None        
        """
        if os.path.sep in filename:
            functools.reduce(self.check_create_path, filename.split(os.path.sep)[:-1], self.output_folder)
        location = os.path.join(self.output_folder, filename)
        with open(location, 'wt', encoding="utf-8") as f:
            f.write(content)


    def _resolve_url(self, href: str, base: Optional[str]) -> str:
        """
        Resolves URLs, correctly handling relative paths and file URLs.
        Returns a file URL for local files and an absolute URL for remote resources.
        """
        logger.debug(f"Resolving URL - href: \n{href}, \nbase: \n{base}")

        if href.startswith(('http://', 'https://')):
            return href
        elif href.startswith('file://'):
            return href

        if base is None or bool(base.strip()) == False:
            if os.path.isfile(href):
                return pathlib.Path(os.path.abspath(href)).as_uri() # Ensure absolute path
            else:  # Assume it's a remote URL and prepend https://
                return f"https://{href}"

        if base.startswith(('http://', 'https://')):
            resolved = urllib.parse.urljoin(base, href)
        elif base.startswith('file://'):
            try:  # Use try-except to handle potential parsing errors
                base_path = urllib.parse.urlparse(base).path
                resolved_path = os.path.abspath(os.path.join(os.path.dirname(base_path), href))
                resolved = pathlib.Path(resolved_path).as_uri()
            except ValueError: # Log the error and return the original href
                logger.error(f"Invalid base URL: {base}")
                return href # Or handle the error differently, e.g., raise an exception
        else:  # base is a local path
            resolved_path = os.path.abspath(os.path.join(os.path.dirname(base), href))
            resolved = pathlib.Path(resolved_path).as_uri()
        # else:
        #     resolved_path = os.path.abspath(os.path.join(os.path.dirname(base), href))
        #     if os.path.isfile(resolved_path):
        #         return pathlib.Path(resolved_path).as_uri() # Already absolute
        #         #resolved = pathlib.Path(resolved_path).as_uri()
        #     else:
        #         # Assume it's a remote URL and prepend https://
        #         resolved = f"https://{resolved_path}"

        logger.debug(f"Resolved URL: \n{resolved}")
        return resolved

    def resolve_schema_ref(self, href, instance_path):
        """
        Resolves schema reference URL.  Returns a local file path or an absolute URL.
        """
        logger.debug(f"Resolving schema reference: \n{href}")

        if href.startswith(('http://', 'https://', 'file://')):
            return href  # Already an absolute URL

        # Resolve relative to the instance_path
        #resolved_path= os.path.abspath(os.path.join(os.path.dirname(instance_path), href))
        resolved_path = os.path.abspath(os.path.join(os.path.dirname(instance_path), href)) # Ensure absolute path
        logger.debug(f"Resolved path: \n{resolved_path}")

        return resolved_path # Return the absolute path; don't prepend https://

        # if os.path.isfile(resolved_path):
        #     return resolved_path
        # else:
        #     # Assume it's a remote URL
        #     return f"https://{resolved_path}" # or raise an exception if you prefer

    
# to test     
if __name__ == "__main__":
    location_path="/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/"
    filename="reports/sap-2022-12-31-DE.xhtml"
    data_pool = Pool(cache_folder="../data/xbrl_cache")
    data_pool.add_instance_location(location=os.path.join(location_path, filename), attach_taxonomy=True)     