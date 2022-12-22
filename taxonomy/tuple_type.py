from xbrl.base import const, element, util


class TupleType(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        if container_schema is not None:
            self.namespace = container_schema.target_namespace
            self.qname = f'{container_schema.target_namespace_prefix}:{self.name}'
        unique_id = f'{self.namespace}:{self.name}'
        self.schema.tuple_types[self.qname] = self
        self.schema.tuple_types_by_id[unique_id] = self
