from xbrl.base import const, element
import itertools


class Concept(element.Element):
    def __init__(self, e, container_schema):
        super().__init__(e, container_schema)
        self.period_type = e.attrib.get('periodType')
        self.balance = e.attrib.get('balance')
        self.data_type = e.attrib.get('type')
        self.domain = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}domain')
        self.linkrole = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}linkrole')
        hu = e.attrib.get(f'{{{const.NS_EXTENSIBLE_ENUMERATIONS}}}headUsable')
        self.head_usable = hu is not None and (hu.lower() == 'true' or hu == '1')
        self.resources = {}  # Related labels - first by lang and then by role
        self.references = {}  # Related reference resources
        self.chain_up = {}  # Related parent concepts. Key is the base set key, value is the list of parent concepts
        self.chain_dn = {}  # Related child concepts. Key is the base set key, value is the list of child concepts
        if self.id is not None:
            key = f'{self.schema.location}#{self.id}'  # Key to search from locator href
            self.schema.taxonomy.concepts[key] = self
            self.schema.taxonomy.concepts_by_qname[self.qname] = self

    def __str__(self):
        return self.qname

    def __repr__(self):
        return self.qname

    def get_label(self):
        return self.get_label_lr(lang='en', role=const.ROLE_LABEL)

    def get_reference(self):
        return self.get_reference_lr(lang='en', role=const.ROLE_REFERENCE)

    def get_label_lr(self, lang, role):
        lbls = self.get_labels_lr(lang, role)
        return lbls[0] if lbls else None

    def get_reference_lr(self, lang, role):
        refs = self.get_references_lr(lang, role)
        return refs[0] if refs else None

    def get_labels_lr(self, lang, role):
        return self.get_resources_lr('label', lang, role)

    def get_references_lr(self, lang, role):
        return self.get_resources_lr('reference', lang, role)

    def get_resources_lr(self, resource_name, lang, role):
        cres = self.resources.get(resource_name)
        if cres is None:
            return None
        # cres is a dictionary where the key is lang + role and value is a list of corresponding resources
        llist = [l[1] for l in cres.items()
                 if (lang is None or l[0].startswith(lang)) and (role is None or l[0].endswith(role))]
        return list(itertools.chain(*llist))

    def info(self):
        return '\n'.join([
            f'QName: {self.qname}',
            f'Data type: {self.data_type}',
            f'Abstract: {self.abstract}',
            f'Nillable: {self.nillable}',
            f'Period Type: {self.period_type}',
            f'Balance: {self.balance}'])
