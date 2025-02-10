# taxonomy/formula Contents
## taxonomy/formula/__init__.py
```py
from . import existence_assertion
from . import assertion
from . import consistency_assertion
from . import filter
from . import assertion_set
from . import parameter
from . import value_assertion
```

## taxonomy/formula/assertion.py
```py
from ...taxonomy import resource


class Assertion(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.severity = 'ERROR'
        super().__init__(e, container_xlink)
        self.implicit_filtering = e.attrib.get('implicitFiltering')
        self.aspect_model = e.attrib.get('aspectModel')
```

## taxonomy/formula/assertion_set.py
```py
from ...taxonomy import resource


class AssertionSet(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.assertions = {}
        self.tables = {}
        super().__init__(e, container_xlink)
        container_xlink.linkbase.pool.current_taxonomy.assertion_sets[container_xlink.linkbase.location] = self
```

## taxonomy/formula/consistency_assertion.py
```py
from ...taxonomy.formula import assertion


class ConsistencyAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        self.strict = e.attrib.get('strict')
        self.abs_radius = e.attrib.get('absoluteAcceptanceRadius')
        self.prop_radius = e.attrib.get('proportionalAcceptanceRadius')
        container_xlink.linkbase.pool.current_taxonomy.consistency_assertions[self.xlabel] = self
```

## taxonomy/formula/existence_assertion.py
```py
from ...taxonomy.formula import assertion


class ExistenceAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        self.test = e.attrib.get('test')
        container_xlink.linkbase.pool.current_taxonomy.existence_assertions[self.xlabel] = self
```

## taxonomy/formula/filter.py
```py
from ...taxonomy import resource


class Filter(resource.Resource):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
```

## taxonomy/formula/parameter.py
```py
from ...taxonomy import resource


class Parameter(resource.Resource):
    def __init__(self, e, container_xlink=None):
        self.xlink = container_xlink
        super().__init__(e)
        self.name = e.attrib.get('name')
        self.select = e.attrib.get('select')
        self.data_type = e.attrib.get('as')
        container_xlink.linkbase.pool.current_taxonomy.parameters[self.xlabel] = self
```

## taxonomy/formula/value_assertion.py
```py
from ...taxonomy.formula import assertion


class ValueAssertion(assertion.Assertion):
    def __init__(self, e, container_xlink=None):
        super().__init__(e, container_xlink)
        self.test = e.attrib.get('test')
        container_xlink.linkbase.pool.current_taxonomy.value_assertions[self.xlabel] = self
```
