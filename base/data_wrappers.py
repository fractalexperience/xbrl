from collections import namedtuple
import enum

""" Data wrapper of the entryPoint element inside a taxonomy package. 
    Name: Official name, or code of the entry point.
    Urls: List of URLs for the Web resources needed for that entry point.
    Description: Some human readable explanation. """
EntryPoint = namedtuple('EntryPoint', 'Name,Urls,Description,Hash')

""" Enumeration refers to a base set composed of definition arcs with domain-member arcrole.
    Key: Base Set Role | Domain | Head Usable 
    Concepts: List of concepts having the same enumeration key.
    Members: List of concepts, which are members of the enumeration. """
Enumeration = namedtuple('Enumeration', 'Key,Concepts,Members')

""" Represents a node in a base set. 
    Concept: Reference to the concept object.
    Arc: Reference to the arc objects, which points to that concept. If the node is in the chain_dn collection, 
         then the arc's 'to' attribute points to the concept. If it is in the chain_up collection, then 
         the arc's 'from' attribute points to the concept. """
BaseSetNode = namedtuple('BaseSetNode', 'Concept,Level,Arc')


""" Represents a constraint in a table cell.
    Dimension: The QName of the constraint dimension, or unit, period, entityIdentifier or entityScheme. 
    Member: The value of the member, which is a QName for explicit custom dimensions. 
    Axis: x,y or z depending on the axis where the constraint comes from. """
Constraint = namedtuple('Constraint', 'Dimension,Member,Axis')


""" Represents a restriction in a xsd:simpleType or xsd:complexType with simple content."""
XsdRestriction = namedtuple('Restriction', 'Name,Value')

""" Represents a DPM Map. DPM stands for DAta Point Model.
    Id: The identifier of the map. Normally this is the table id. 
    Dimensions: Set of all custom dimensions included in the map. Note that not all cells will include all dimensions.
    Mappings: A Dictionary of dictionaries where outer key is the address of the data point. 
              The value is a dictionary of constraints for the cell where key is the dimension (aspect) and the value
              is the value of the member. If the dimension is open, the member value is an asterisk (*). """
DpmMap = namedtuple('DpmMap', 'Id,Dimensions,Mappings,OpenAxes')

""" Represents a fact according OIM (Open Information Model) - the fact value + all associated aspects.  """
OimFact = namedtuple('OimFact', 'Signature,Value')

DpmMapMandatoryDimensions = ['Label', 'Metrics', 'Data Type', 'Period Type']
Axis = enum.Enum('Axis', 'X Y Z')
