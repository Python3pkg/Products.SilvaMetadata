"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from ZopeImports import *
from Interfaces import IMetadataCollection
from Set import MetadataSet

class MetadataCollection(Folder):

    meta_type = 'Metadata Collection'

    __implements__ = IMetadataCollection

    all_meta_types = (
        {'name':MetadataSet.meta_type,
         'action':'addMetadataSetForm'},
        )

    addMetadataSetForm = DTMLFile('ui/MetadataSetAddForm', globals())

    security = ClassSecurityInfo()

    def addMetadataSet(self, id, namespace_prefix, namespace_uri, RESPONSE=None):
        " "
        
        set = MetadataSet(id, namespace_prefix, namespace_uri)
        self._setObject(id, set)

        if RESPONSE is not None:
            return self.manage_main(update_menu=1)
        
    def getContentMetadata(self, object, namespace_key=None):
        
        annotations = getToolByName(self, 'portal_annotations')
        
        metadata_collection = annotations.getAnnotations(
            object,
            MetadataNamespace
            )

        if namespace_key:
            return metadata_collection[namespace_key]

        return metadata_collection

    def getMetadataSets(self):
        return self.objectValues('Metadata Set')
            

InitializeClass(MetadataCollection)
