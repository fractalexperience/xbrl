from xbrl.base import const, element, util


class TupleType(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        unique_id = f'{self.namespace}:{self.name}'
        self.schema.tuple_types[unique_id] = self
