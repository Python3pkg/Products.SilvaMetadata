from Interface import Interface
try:
    from Products.CMFCore.interfaces.portal_metadata \
         import portal_metadata as IPortalMetadata
except ImportError:
    class IPortalMetadata(Interface): pass

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
