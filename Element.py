"""
Metadata Elements
Author: kapil thangavelu <k_vertigo@objectrealms.net>
$Id: Element.py,v 1.2 2003/04/22 17:58:48 hazmat Exp $
"""

from ZopeImports import *
from Interfaces import IMetadataElement
from FormulatorField import getFieldFactory
from Guard import Guard

_marker = []

class NoContext(Exception):
    pass

class ConfigurationError(Exception):
    pass

class MetadataElement(SimpleItem):
    """
    Property Bag For Element Policies
    """
    
    meta_type = 'Metadata Element'

    __implements__ = IMetadataElement

    #################################
    # element policy properties
    #################################
    
    read_only_p = False
    index_p = False
    index_type = None
    field_type = None

    ## defer to formulator for now
    use_default_p = True
    #required_p = False    
    #default = None
    
    ## out of scope for initial impl
    #export_p = True
    #enforce_vocabulary_p = True
    
    manage_options = (
        {'label':'Settings',
         'action':'elementSettingsForm'},
        {'label':'Guards',
         'action':'elementGuardForm'},
        {'label':'Field',
         'action':'field/manage_main'},        
        )

    elementSettingsForm = DTMLFile('ui/ElementPolicyForm', globals())
    elementGuardForm   = DTMLFile('ui/ElementGuardForm', globals())

    security = ClassSecurityInfo()
    
    def __init__(self, id, **kw):
        self.id = id
        self.read_guard = Guard()
        self.write_guard = Guard()

    def editElementGuards(self, read_guard, write_guard, RESPONSE=None):

        self.read_guard.changeFromProperties(read_guard)
        self.write_guard.changeFromProperties(write_guard)
        
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def editElementPolicy(self,
                          field_type = None,
                          index_type = None,
                          index_p = None,
                          read_only_p = None,
                          use_default_p = None,
                          RESPONSE = None
                          ):
        """
        edit an element's policy
        """

        if index_type is not None:
            ms = self.getMetadataSet()
            if ms.isInitialized():
                raise ConfigurationError("Not Allowed Set Already initialized")

        if field_type is not None:
            ms = self.getMetadataSet()
            if ms.isInitialized():
                raise ConfigurationError("Not Allowed Set Already initialized")

        field_type = field_type or self.field_type
        index_type = index_type or self.index_type
        
        if index_p is None:
            index_p = self.index_p


        if use_default_p is None:
            use_default_p = self.use_default_p

        if read_only_p is None:
            read_only_p = self.read_only_p
        
        if field_type != self.field_type:
            try:
                factory = getFieldFactory(field_type)
            except KeyError:
                raise ConfigurationError("invalid field type %s"%field_type)
            self.field = factory( self.getId() )
            self.field_type = field_type
        
        if index_type is not None:
            if index_type in self.getMetadataSet().listIndexTypes():
                self.index_type = index_type
            else:
                raise ConfigurationError("invalid index type %s"%index_type)

        # need to cascacde this so we can create indexes at the set level
        self.index_p = not not index_p
        self.read_only_p = not not read_only_p
        self.use_default_p = not not use_default_p

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_workspace')
    
##     def getValidator(self, object=None):
##         if object is None and self.validator_context_dependent:
##             raise NoContext(self.getId())
##         return getValidator(self.validator_type, object)
        
##     def getWidget(self, object=None):
##         if object is None and self.widget_context_dependent:
##             raise NoContext(self.getId())
##         return getWidget(self.widget_type, object)

##     def getVocabulary(self, object=None):
##         if self.validator_vocabulary:
##             return self.getValidator(object).getVocabulary()
##         return self.vocabulary_values

InitializeClass(MetadataElement)


def ElementFactory(id, **kw):

    return MetadataElement(id, **kw)
    

        
