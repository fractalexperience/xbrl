I was trying to modify the code from `xbrl` package to make it work for ESEF. 
Please show me the modified code in `pool.py` and `taxonomy.py` to resolve the endless loop.

The issue is, unlike xbrl, ESEF files have a folder structure and the schema references are relative to the instance file, not the taxonomy folder. 

Example: 
```
pwd                    
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls
(base) mbp16@Reeyarns-MBP sap_Jahres-_2023-04-05_esef_xmls % ls -R sap-2022-12-31-DE
META-INF	reports		www.sap.com

sap-2022-12-31-DE/META-INF:
catalog.xml		taxonomyPackage.xml

sap-2022-12-31-DE/reports:
sap-2022-12-31-DE.xhtml

sap-2022-12-31-DE/www.sap.com:
sap-2022-12-31.xsd		sap-2022-12-31_cal.xml		sap-2022-12-31_def.xml		sap-2022-12-31_lab-de.xml	sap-2022-12-31_lab-en.xml	sap-2022-12-31_pre.xml
```


Question: Does the current code run into an endless loop? 

The issue is add_taxonomy() calls add_reference() throughh `taxonomy.Taxonomy(ep_list, self)`,
but the same file is being added again and again and again. 
It seems that the first time it got the resolved URL correct, but later it was resolved wrong and into endless loop.

It still keeps calling. 
Log: ```
Calling add_reference(...): 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com/sap-2022-12-31.xsd 

...
Calling add_reference(...): 
sap-2022-12-31.xsd 
...
DEBUG:xbrl.base.pool:Resolving URL - href: 
sap-2022-12-31.xsd, 
base: 
/Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/www.sap.com
DEBUG:xbrl.base.pool:Resolved URL: 
file:///Users/mbp16/Dropbox/data/proj/bmcg/bundesanzeiger/public/103487/2022/sap_Jahres-_2023-04-05_esef_xmls/sap-2022-12-31-DE/sap-2022-12-31.xsd
...
Calling add_reference(...): 
sap-2022-12-31.xsd 

```



Exisitng code:
`pool.py`:
```
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
        # Alternative locations. If set, this is used to resolve Qeb references to alternative (existing) URLs. 
        self.alt_locations = alt_locations
        # Index of all packages in the cache/taxonomy_packages folder by entrypoint 
        self.packaged_entrypoints = {}
        self.packaged_locations = None
        # Currently opened taxonomy packages 
        self.active_packages = {}
        # Currently opened archive, where files can be read from - optional.
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

    def add_instance_location(self, location_path, filename, key=None, attach_taxonomy=True):
        """Loads an instance document from a file location within an ESEF structure."""

        instance_location = os.path.join(location_path, filename)
        instance_location = os.path.abspath(instance_location)

        if key is None:
            key = instance_location

        try:
            parser = lxml.XMLParser(huge_tree=True)
            doc = lxml.parse(instance_location, parser=parser)
            root = doc.getroot()

            # Resolve schemaRefs relative to the *location_path*, not the instance file
            self.resolve_and_update_schema_refs(root, location_path)

            # Write back the modified XML
            doc.write(instance_location)

            xid = instance.Instance(location=instance_location, container_pool=self)
            #self.add_instance(xid, key, attach_taxonomy)
            self.add_instance(xid, key, attach_taxonomy, location_path) # Pass location_path

            return xid

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return None

    def resolve_and_update_schema_refs(self, root, location_path):
        """Resolves and updates schemaRef elements within an ESEF context."""
        nsmap = {'link': const.NS_LINK}
        schema_refs = root.findall(".//link:schemaRef", namespaces=nsmap)

        for schema_ref in schema_refs:
            href = schema_ref.get(f'{{{const.NS_XLINK}}}href')
            if href:
                resolved_href = self.resolve_esef_schema_ref(href, location_path)
                if resolved_href:
                    schema_ref.set(f'{{{const.NS_XLINK}}}href', resolved_href)
                else:
                    logger.warning(f"Could not resolve schema reference: {href}")

    def resolve_esef_schema_ref(self, href, location_path):
        """Resolves schema references within an ESEF structure."""

        resolved_path = os.path.abspath(os.path.join(location_path, href))
        if os.path.isfile(resolved_path):
            return pathlib.Path(resolved_path).as_uri()
        else:
            logger.warning(f"Schema file not found: {resolved_path}")
            return None

    def add_instance_location_depreciated (self, location_path, filename, key=None, attach_taxonomy=True):
        """Loads an instance document from a file location.

        Args:
            location_path (str): Directory path to the instance file.
            filename (str): The name of the instance file.
            key (str, optional): Optional identifier. Defaults to None.
            attach_taxonomy (bool, optional): Whether to load associated taxonomy. Defaults to True.

        Returns:
            Instance: The loaded instance document, or None if an error occurs.
        """

        location = os.path.join(location_path, filename)  # Combine path and filename
        location = os.path.abspath(location)
        logger.info(f"\n\nAdding instance from location: {location}")

        if key is None:
            key = location  # Or another suitable default

        try:
            parser = lxml.XMLParser(huge_tree=True)
            doc = lxml.parse(location, parser=parser)
            root = doc.getroot()

            nsmap = {'link': const.NS_LINK}
            schema_refs = root.findall(".//link:schemaRef", namespaces=nsmap)
            logger.info(f"Found {len(schema_refs)} schema references")

            for schema_ref in schema_refs:
                href = schema_ref.get(f'{{{const.NS_XLINK}}}href')
                if href:
                    resolved_href = self.resolve_schema_ref(href, location)
                    if resolved_href:
                        if not resolved_href.startswith(('http://', 'https://', 'file://')):
                            resolved_href = os.path.abspath(resolved_href)
                        if not resolved_href.startswith(('http://', 'https://')):
                            resolved_href_removeprefix = resolved_href.replace('file://', '')
                            resolved_href = pathlib.Path(resolved_href_removeprefix).as_uri()
                        schema_ref.set(f'{{{const.NS_XLINK}}}href', resolved_href)
                        logger.debug(f"Resolved schema reference: \n{resolved_href}")
                    else:
                        logger.warning(f"Could not resolve schema reference: {href}")

            # Write back the modified XML if any schema references were updated
            if schema_refs:  # Only write if changes were made
                doc.write(location)
                logger.debug("Successfully wrote back modified XML")

            xid = instance.Instance(location=location, container_pool=self)
            self.add_instance(xid, key, attach_taxonomy)
            logger.info(f"Successfully added instance from {location}")
            return xid

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            traceback.print_exc(limit=10)
            return None

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

    #def add_instance(self, xid, key=None, attach_taxonomy=False):
    def add_instance(self, xid, key=None, attach_taxonomy=False, location_path=None): # Add location_path    
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
            # entry_points = [ref if ref.startswith('http') else self.resolve_schema_ref(ref, xid.location) # Use xid.location
            #                 for ref in xid.xbrl.schema_refs]

            # entry_points = [pathlib.Path(ep).as_uri() if os.path.isfile(ep) else ep  # Check if it's a file
            #                 for ep in entry_points]
            entry_points = [ref if ref.startswith('http') else self.resolve_schema_ref(ref, xid.location)
                            for ref in xid.xbrl.schema_refs]
            entry_points = [pathlib.Path(ep).as_uri() if os.path.isfile(ep) else ep for ep in entry_points]

            #tax = self.add_taxonomy(entry_points)
            tax = self.add_taxonomy(entry_points, location_path) # Pass location_path
            xid.taxonomy = tax

    def add_taxonomy(self, entry_points, location_path=None): # Add location_path
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
            self.add_packaged_entrypoints(ep, location_path) # Pass location_path
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

    def add_reference(self, href, base, location_path=None): # Add location_path
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
        
        if location_path:
            # Dynamically determine subfolders within the location_path
            subfolders = [d for d in os.listdir(location_path) if os.path.isdir(os.path.join(location_path, d))]

            for subfolder in subfolders:
                potential_base = os.path.join(location_path, subfolder)
                resolved_href = self._resolve_url(href, potential_base)

                if os.path.exists(resolved_href.replace("file://", "")): # Check if resolved path exists
                    base = potential_base # Use this base path
                    break # Stop searching after finding a valid base

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
        resolved_href = href
        if not href.startswith('http'):
            resolved_href = self._resolve_url(href, base)  # Use _resolve_url for consistent resolution
            logger.debug(f"Resolved URL to: {resolved_href}")

            key = f'{self.current_taxonomy_hash}_{resolved_href}_{base}'  # Include base in the key
            logger.debug(f"key: {key}")
            if key in self.discovered:
                logger.debug(f"key: {key}")
                logger.debug(f"Resource already discovered: {resolved_href} from base {base}")
                return
            else:
                logger.debug(f"key: {key}")
                logger.debug(f"Resource not discovered: {resolved_href} from base {base}")
                self.discovered[key] = False  # Mark as discovered
                
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

        if base is None or not base.strip():
            if os.path.isfile(href):
                return pathlib.Path(os.path.abspath(href)).as_uri() # Ensure absolute path
            else:  
                ##return f"https://{href}" # Assume it's a remote URL and prepend https://
                return href # Don't assume https, could be a relative local path
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
    #data_pool.add_instance_location(location=os.path.join(location_path, filename), attach_taxonomy=True)     
    data_pool.add_instance_location(location_path=location_path, filename=filename, attach_taxonomy=True)

```

`taxonomy.py`:
```
from xbrl.base import const, data_wrappers, util
from xbrl.taxonomy.xdt import dr_set


class Taxonomy:
    """ entry_points is a list of entry point locations
        cache_folder is the place where to store cached Web resources """
    def __init__(self, entry_points, container_pool):
        self.entry_points = entry_points
        self.pool = container_pool
        self.pool.current_taxonomy = self
        self.pool.current_taxonomy_hash = util.get_hash(','.join(entry_points))
        """ All schemas indexed by resolved location """
        self.schemas = {}
        """ All linkbases indexed by resolved location """
        self.linkbases = {}
        """ All concepts  indexed by full id - target namespace + id """
        self.concepts = {}
        """ All concepts indexed by QName"""
        self.concepts_by_qname = {}
        """ General elements, which are not concepts """
        self.elements = {}
        self.elements_by_id = {}
        """ All base set objects indexed by base set key """
        self.base_sets = {}
        """ Dimension defaults - Key is dimension QName, value is default member concept """
        self.defaults = {}
        """ Default Members - Key is the default member QName, value is the corresponding dimension concept. """
        self.default_members = {}
        """ Dimensional Relationship Sets """
        self.dr_sets = {}
        """ Excluding Dimensional Relationship Sets """
        self.dr_sets_excluding = {}
        """ Key is primary item QName, value is the list of dimensional relationship sets, where it participates. """
        self.idx_pi_drs = {}
        """ Key is the Qname of the dimensions. Value is the set of DR keys, where this dimension participates """
        self.idx_dim_drs = {}
        """ Key is the QName of the hypercube. Value is the set of DR Keys, where this hypercube participates. """
        self.idx_hc_drs = {}
        """ Key is the QName of the member. Value is the set of DR keys, where this member participates. """
        self.idx_mem_drs = {}
        """ All table resources in taxonom """
        self.tables = {}
        """ All role types in all schemas """
        self.role_types = {}
        self.role_types_by_href = {}
        """ All arcrole types in all schemas """
        self.arcrole_types = {}
        self.arcrole_types_by_href = {}
        """ Global resources - these, which have an id attribute """
        self.resources = {}
        """ All locators """
        self.locators = {}
        """ All parameters """
        self.parameters = {}
        """ All assertions by type """
        self.value_assertions = {}
        self.existence_assertions = {}
        self.consistency_assertions = {}
        """ Assertion Sets """
        self.assertion_sets = {}
        """ Simple types """
        self.simple_types = {}
        """ Complex types with simple content. Key is the QName, value is the item type object. """
        self.item_types = {}
        """ Complex types with simple content. Key is the unique identifier, value is the item type object. """
        self.item_types_by_id = {}
        """ Complex types with complex content: Key is qname, value is the tuple type object """
        self.tuple_types = {}
        """ Complex types with complex content: Key is unique identifier, value is the tuple type object """
        self.tuple_types_by_id = {}

        self.load()
        self.compile()

    def __str__(self):
        return self.info()

    def __repr__(self):
        return self.info()

    def info(self):
        return '\n'.join([
            f'Schemas: {len(self.schemas)}',
            f'Linkbases: {len(self.linkbases)}',
            f'Role Types: {len(self.role_types)}',
            f'Arcrole Types: {len(self.arcrole_types)}',
            f'Concepts: {len(self.concepts)}',
            f'Item Types: {len(self.item_types)}',
            f'Tuple Types: {len(self.tuple_types)}',
            f'Simple Types: {len(self.simple_types)}',
            f'Labels: {sum([0 if not "label" in c.resources else len(c.resources["label"]) for c in self.concepts.values()])}',
            f'References: {sum([0 if not "reference" in c.resources else len(c.resources["reference"]) for c in self.concepts.values()])}',
            f'Hierarchies: {len(self.base_sets)}',
            f'Dimensional Relationship Sets: {len(self.base_sets)}',
            f'Dimensions: {len([c for c in self.concepts.values() if c.is_dimension])}',
            f'Hypercubes: {len([c for c in self.concepts.values() if c.is_hypercube])}',
            f'Enumerations: {len([c for c in self.concepts.values() if c.is_enumeration])}',
            f'Enumerations Sets: {len([c for c in self.concepts.values() if c.is_enumeration_set])}',
            f'Table Groups: {len([c for c in self.concepts.values() if "table" in c.resources])}',
            f'Tables: {len(self.tables)}',
            f'Parameters: {len(self.parameters)}',
            f'Assertion Sets: {len(self.assertion_sets)}',
            f'Value Assertions: {len(self.value_assertions)}',
            f'Existence Assertions: {len(self.existence_assertions)}',
            f'Consistency Assertions: {len(self.consistency_assertions)}'
        ])

    def load(self):
        for ep in self.entry_points:
            self.pool.add_reference(ep, '')

    def resolve_prefix(self, pref):
        for sh in self.schemas.values():
            ns = sh.namespaces.get(pref, None)
            if ns is not None:
                return ns
        return None

    def resolve_qname(self, qname):
        pref = qname.split(':')[0] if ':' in qname else ''
        ns = self.resolve_prefix(pref)
        nm = qname.split(':')[1] if ':' in qname else qname
        return f'{ns}:{nm}'

    def attach_schema(self, href, sh):
        if href in self.schemas:
            return
        self.schemas[href] = sh
        for key, imp in sh.imports.items():
            self.pool.add_reference(key, sh.base)
        for key, ref in sh.linkbase_refs.items():
            self.pool.add_reference(key, sh.base)

    def attach_linkbase(self, href, lb):
        if href in self.linkbases:
            return
        self.linkbases[href] = lb
        for href in lb.refs:
            self.pool.add_reference(href, lb.base)

    def get_bs_roots(self, arc_name, role, arcrole):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}')
        if not bs:
            return None
        return bs.roots

    def get_bs_members(self, arc_name, role, arcrole, start_concept=None, include_head=True):
        bs = self.base_sets.get(f'{arc_name}|{arcrole}|{role}', None)
        if not bs:
            return None
        return bs.get_members(start_concept, include_head)

    def get_enumerations(self):
        enumerations = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enumerations.get(key)
            if not e:
                members = self.get_bs_members('definitionArc', c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE, c.domain, c.head_usable)
                e = data_wrappers.Enumeration(key, [], [] if members is None else [m.Concept for m in members])
                enumerations[key] = e
            e.Concepts.append(c)
        return enumerations

    def get_enumeration_sets(self):
        enum_sets = {}
        for c in [c for k, c in self.concepts.items() if c.data_type and c.data_type.endswith('enumerationSetItemType')]:
            key = f'{c.linkrole}|{c.domain}|{c.head_usable}'
            e = enum_sets.get(key)
            if not e:
                members = self.get_bs_members('definitionArc', c.linkrole, const.XDT_DOMAIN_MEMBER_ARCROLE, c.domain, c.head_usable)
                if members is None:
                    continue
                e = data_wrappers.Enumeration(key, [], [m.Concept for m in members])
                enum_sets[key] = e
            e.Concepts.append(c)
        return enum_sets

    def compile(self):
        self.compile_schemas()
        self.compile_linkbases()
        self.compile_defaults()
        self.compile_dr_sets()

    def compile_schemas(self):
        for sh in self.schemas.values():
            for c in sh.concepts.values():
                self.concepts_by_qname[c.qname] = c
                if c.id is not None:
                    key = f'{sh.location}#{c.id}'  # Key to search from locator href
                    self.concepts[key] = c
            for key, e in sh.elements.items():
                self.elements[key] = e
            for key, e in sh.elements_by_id.items():
                self.elements_by_id[key] = e
            for key, art in sh.arcrole_types.items():
                self.arcrole_types[key] = art
                self.arcrole_types_by_href[f'{sh.location}#{art.id}'] = art
            for key, rt in sh.role_types.items():
                self.role_types[key] = rt
                self.role_types_by_href[f'{sh.location}#{rt.id}'] = rt

            for key, it in sh.item_types.items():
                self.item_types[key] = it
            for key, it in sh.item_types_by_id.items():
                self.item_types_by_id[key] = it
            for key, tt in sh.tuple_types.items():
                self.tuple_types[key] = tt
            for key, tt in sh.tuple_types_by_id.items():
                self.tuple_types_by_id[key] = tt

            for key, st in sh.simple_types.items():
                self.simple_types[key] = st

    def compile_linkbases(self):
        # Pass 1 - Index global objects
        for lb in self.linkbases.values():
            for xl in lb.links:
                for key, loc in xl.locators_by_href.items():
                    self.locators[key] = loc
                for key, l_res in xl.resources.items():
                    for res in l_res:
                        if res.id:
                            href = f'{xl.linkbase.location}#{res.id}'
                            self.resources[href] = res
        # Pass 2 - Connect resources to each other
        for lb in self.linkbases.values():
            for xl in lb.links:
                xl.compile()

    def compile_defaults(self):
        # key = f'definitionArc|{const.XDT_DIMENSION_DEFAULT_ARCROLE}|{const.ROLE_LINK}'
        frag = f'definitionArc|{const.XDT_DIMENSION_DEFAULT_ARCROLE}'
        for key, bs in self.base_sets.items():
            if frag not in key:
                continue
            bs = self.base_sets.get(key, None)
        # if bs is None:
        #     return
            for dim in bs.roots:
                chain_dn = dim.chain_dn.get(key, None)
                if chain_dn is None:
                    continue
                for def_node in chain_dn:
                    self.defaults[dim.qname] = def_node.Concept.qname
                    self.default_members[def_node.Concept.qname] = dim.qname

    def compile_dr_sets(self):
        for bs in [bs for bs in self.base_sets.values() if bs.arc_name == 'definitionArc']:
            if bs.arcrole == const.XDT_DIMENSION_DEFAULT_ARCROLE:
                self.add_default_member(bs)
                continue
            if bs.arcrole == const.XDT_ALL_ARCROLE:
                self.add_drs(bs, self.dr_sets)
                continue
            if bs.arcrole == const.XDT_NOTALL_ARCROLE:
                self.add_drs(bs, self.dr_sets_excluding)
                continue

    def add_drs(self, bs, drs_collection):
        drs = dr_set.DrSet(bs, self)
        drs.compile()
        drs_collection[bs.get_key()] = drs

    def add_default_member(self, bs):
        for d in bs.roots:
            members = bs.get_members(start_concept=d, include_head=False)
            if not members:
                continue
            for m in members:
                self.defaults[d.qname] = m
                self.default_members[m.qname] = d

    def get_prefixes(self):
        return set(c.prefix for c in self.concepts.values())

    def get_languages(self):
        return set([r.lang for k, r in self.resources.items() if r.name == 'label'])

```