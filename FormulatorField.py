"""
provides access to formulator field registry

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from Acquisition import aq_inner, aq_parent
from Interfaces import IMetadataElement

from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.Field import Field
from Products.Formulator.Widget import MultiItemsWidget

def getFieldFactory(fieldname):
    return FieldRegistry.get_field_class(fieldname)

def listFields():
    mapping = FieldRegistry.get_field_classes()
    field_types = mapping.keys()
    field_types.sort()
    return field_types


