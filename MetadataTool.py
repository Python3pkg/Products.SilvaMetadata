"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import Configuration
from ZopeImports import *
from Binding import MetadataBindAdapter
from Namespace import DublinCore

from Compatiblity import IActionProvider, IPortalMetadata
from Compatiblity import ActionProviderBase

class MetadataTool(UniqueObject, Folder, ActionProviderBase):

    id = 'portal_amt'
    meta_type = 'Advanced Metadata Tool'
    titlte =  meta_type

    __implements__ = (IActionProvider, IPortalMetadata)

    _actions = []

    security = ClassSecurityInfo()

    def __init__(self):
        pass
    
    #################################
    # Action Provider Interface
    def listActions(self, info=None):
        actions = []
        for set in self.collection.getMetadataSets():
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
        catalog =getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor()
    
    def listAllowedLanguages(self, content=None):
        catalog =getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor()

    def listAllowedRights(self, content=None):
        catalog =getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor()

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
    # new interface 

    def getMetadataSet(self, set_id):
        return self.collection._getOb(set_id)

    def getMetadataSetFor(self, metadata_namespace):
        for set in self.collection.getMetadataSets():
            if set.metadata_uri == metadata_namespace:
                return set
            
        raise NotFound("No Metadata Set Matching %s"%str(metadata_namespace))

    def getMetadata(self, content):
        ctm = self._getOb(Configuration.TypeMapping)
        metadata_sets = ctm.getMetadataSetsFor(content.getPortalTypeName())
        return MetadataBindAdapter(content, metadata_sets)

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
    
    cid = 'collection'
    collection = MetadataCollection(cid)
    collection.id = cid

    tool._setObject(cid, collection)

    tid = 'ct_mapping'
    mapping = TypeMappingContainer(tid)
    mapping.id = tid
    
    self._setObject(tid, mapping)    

    
    
