"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from ZopeImports import *
from Interfaces import IMetadataCollection
from Import import read_set, make_set
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

    def addMetadataSet(self,
                       id,
                       namespace_prefix,
                       namespace_uri,
                       RESPONSE=None):
        " "

        set = MetadataSet(id, namespace_prefix, namespace_uri)
        self._setObject(id, set)

        if RESPONSE is not None:
            return self.manage_main(update_menu=1)
        
    def getMetadataSets(self):
        return self.objectValues('Metadata Set')

    def importSet(self, xml_file, RESPONSE=None):
        """ import an xml definition of a metadata set"""
            
        set_node = read_set(xml_file)
        make_set(self, set_node)

        if RESPONSE is not None:
            return self.manage_main(update_menu=1)
            

InitializeClass(MetadataCollection)
