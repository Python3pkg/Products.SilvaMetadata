"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""


from Access import invokeAccessHandler
import Configuration
from ZopeImports import *
from Binding import MetadataBindAdapter
from Exceptions import BindingError
from Namespace import DublinCore
from Compatibility import IActionProvider, IPortalMetadata, ActionProviderBase
from Compatibility import getContentType, getContentTypeNames

class MetadataTool(UniqueObject, Folder, ActionProviderBase):

    id = 'portal_metadata'
    meta_type = 'Advanced Metadata Tool'
    title =  meta_type

    manage_options = (
        {'label':'Overview',
         'action':'manage_main'},
        
        {'label':'Metadata Sets',
         'action':'%s/manage_workspace'%Configuration.MetadataCollection},
        
        {'label':'Type Mapping',
         'action':'%s/manage_workspace'%Configuration.TypeMapping},
        )
    
    __implements__ = (IActionProvider, IPortalMetadata)

    _actions = []

    security = ClassSecurityInfo()
    #security.declareProtected('metadata_overview', Configuration.pMetadataManage)
    #metadata_overview = DTMLFile('ui/MetadataToolOverview', globals())
    manage_main = DTMLFile('ui/MetadataToolOverview', globals())
    
    def __init__(self):
        pass
    
    #################################
    # Action Provider Interface
    def listActions(self, info=None):
        actions = []
        for set in self.getCollection().getMetadataSets():
            if set.use_action_p is not None and set.action is not None:
                actions.append(set.action)
        return self._actions

    #################################
    # Metadata interface

    ## site wide queries
    
    # this is the wrong tool to be asking.
    #def getFullName(self, userid):
    #    return userid 

    # this is just lame, assumes global publisher for a site
    #def getPublisher(self):
    #    pass
    
    ## dublin core hardcodes :-(
    # we don't have vocabulary implementation yet.


    def listAllowedSubjects( self, content=None):
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor()

    def listAllowedFormats(self, content=None):
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor()
    
    def listAllowedLanguages(self, content=None):
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor()

    def listAllowedRights(self, content=None):
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor()

    #################################
    ## validation hooks
    def setInitialMetadata(self, content):
        binding = self.getMetadata(content)
        sets = binding.getSetNames()
        # getting the set metadata will cause its
        # initialization if nots already initialized
        for s in sets:
            binding[s]

    def validateMetadata(self, content):
        binding = self.getMetadata(content)
        sets = binding.getSetNames()
        for s in sets:
            data = binding[s]
            binding.validate(data, set_id=s)
            
    #################################
    ## new interface 

    def getCollection(self):
        """ return a container containing all known metadata sets """
        return self._getOb(Configuration.MetadataCollection)
    
    def getTypeMapping(self):
        """ return the mapping of content types to metadata sets """
        return self._getOb(Configuration.TypeMapping)
    
    def getMetadataSet(self, set_id):
        """ get a particular metadata set """
        return self.getCollection().getMetadataSet(set_id)

    def getMetadataSetFor(self, metadata_namespace):
        """ get a particular metadata set by its namespace """
        return self.getCollection().getSetByNamespace(metadata_namespace)

    def getMetadata(self, content):
        """
        return a metadata binding adapter for a particular content
        object. a bind adapter encapsulates both metadata definitions,
        data, and policy behavior into an api for manipulating and
        introspecting metadata
        """
        ct = getContentType(content)
        
        if not ct in getContentTypeNames(self):
            raise BindingError(
                "invalid content type %s for metadata system"%ct
                )
        return invokeAccessHandler(self, content)

    #################################
    # misc

    def manage_afterAdd(self, item, container):
        initializeTool(self)

    def update(self, RESPONSE):
        """ """
        RESPONSE.redirect('manage_workspace')

def initializeTool(tool):

    from Collection import MetadataCollection
    from TypeMapping import TypeMappingContainer
    
    collection = MetadataCollection(Configuration.MetadataCollection)
    collection.id = Configuration.MetadataCollection
    tool._setObject(Configuration.MetadataCollection, collection)

    mapping = TypeMappingContainer(Configuration.TypeMapping)
    mapping.id = Configuration.TypeMapping
    tool._setObject(Configuration.TypeMapping, mapping)    

    
    
