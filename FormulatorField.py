"""
provides access to formulator field registry

author: kapil thangavelu <k_vertigo@objectrealms.net>
$Id: FormulatorField.py,v 1.1 2003/04/22 14:45:30 hazmat Exp $
"""
from Acquisition import aq_inner, aq_parent
from Interfaces import IMetadataElement

from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.Field import Field

def getFieldFactory(fieldname):
    return FieldRegistry.get_field_class(fieldname)

def listFields():
    mapping = FieldRegistry.get_field_classes()
    field_types = mapping.keys()
    field_types.sort()
    return field_types

def render_sub_field(self, id, value=None, REQUEST=None):
    pass

def render_sub_field_from_request(self, id, REQUEST):
    pass

def validate_sub_field(self, id, REQUEST):
    pass

def isElemental(ob):
    return IMetadataElement.isImplementedBy(aq_parent(aq_inner(ob)))
    

