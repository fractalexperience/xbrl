"""
To work around the issue of loading files from a virtual folder in memory, you can use the io module to create a virtual file system using BytesIO for binary data or StringIO for text data. However, since the lxml library requires a file-like object that behaves like a file on disk, you can use the pyfilesystem2 library, which provides a more complete virtual file system interface.
Here's how you can implement this using pyfilesystem2 to create a virtual folder and load your files from there:
"""

#   pip install pyfilesystem2
from fs.memory import MemoryFileSystem

# ... existing code ...

# Create a virtual file system
mem_fs = MemoryFileSystem()

if filing.xbrl_files.get("xml"):
    xml_filename = filing.xbrl_files.get("xml")
    instance_str = filing.documents[xml_filename].doc_text.data
    instance_str = clean_doc(instance_str)
    
    # Write the instance document to the virtual file system
    mem_fs.writexml(xml_filename, instance_str)

    # Load the instance document from the virtual file system
    with mem_fs.open(xml_filename) as instance_io:
        instance_tree = lxml_etree.parse(instance_io)
        root = instance_tree.getroot()
        xid = data_pool.add_instance_element(root, key=f"virtual://{xml_filename}", attach_taxonomy=False)

    for linkbase_type in ["cal", "def", "lab", "pre"]:
        linkbase_filename = filing.xbrl_files.get(linkbase_type)
        if linkbase_filename:
            linkbase_str = filing.documents[linkbase_filename].doc_text.data
            linkbase_str = clean_doc(linkbase_str)
            # Write the linkbase document to the virtual file system
            mem_fs.writexml(linkbase_filename, linkbase_str)
            # Load the linkbase document from the virtual file system
            with mem_fs.open(linkbase_filename) as linkbase_io:
                data_pool.add_reference_from_string(linkbase_io.read(), location=f"virtual://{linkbase_filename}")

    if filing.xbrl_files.get("sch"):
        schema_filename = filing.xbrl_files.get("sch")
        schema_str = filing.documents[schema_filename].doc_text.data
        schema_str = clean_doc(schema_str)
        # Write the schema document to the virtual file system
        mem_fs.writexml(schema_filename, schema_str)
        # Load the schema document from the virtual file system
        with mem_fs.open(schema_filename) as schema_io:
            data_pool.add_schema_from_string(schema_io.read(), location=f"virtual://{schema_filename}")