"""
Marker Interfaces
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from Interface import Interface
from Compatibility import IPortalMetadata

#################################
# Metadata Tool/Service Interface
#################################
class IMetadataTool(IPortalMetadata):
    pass

#################################
# Base Building Blocks
#################################

class IMetadataCollection(Interface):
    pass

class IOrderedContainer(Interface):

    def moveObject(self, id, position):
        pass

    def moveObjectUp(self, id, steps=1):
        pass

    def moveObjectDown(self, id, steps=1):
        pass

    def getObjectPosition(self, id):
        pass
    
class IMetadataSet(Interface):
    pass

class IMetadataElement(Interface):
    pass

#################################
# Adapter Provided Functionality
#################################
# all of these operate on a set basis.

class IMetadataSetExporter(Interface):
    pass

class IMetadataForm(Interface):
    pass

class IMetadataValidation(Interface):
    pass

class IMetadataStorage(Interface):
    pass
