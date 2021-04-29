import collections


""" Enumeration refers to a base set composed of definition arcs with domain-member arcrole.
    Key: Base Set Role | Domain | Head Usable 
    Concepts: List of concepts having the same enumeration key.
    Members: List of concepts, which are members of the enumeration. """
Enumeration = collections.namedtuple('Enumeration', 'Key,Concepts,Members')

""" A simple named tuple, which refers to a concept inside a certain base set. 
    Concept: Reference to the concept object. 
    Level: An integer representing the level of nesting inside the base set. """
ConceptWrapper = collections.namedtuple('ConceptWrapper', 'Concept,Level')
