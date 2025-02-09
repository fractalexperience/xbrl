from openesef.base import const, element, util


class SimpleType(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        unique_id = f'{self.namespace}:{self.name}'
        self.schema.simple_types[unique_id] = self
