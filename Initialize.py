"""
Type Specific Initialization of Metadata Binding Runtime Data
not really meant for public api exposure (certainly not ttw)

Handler Signature is as follows

def metadata_initialization()

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from Compatibility import getContentType

_typeHandlers = {}

def registerHandler(content_type, handler):
    assert iscallable(handler)
    global _typeHandlers
    _typeHandlers[content_type]=handler

def getHandler(content):
    ct = getContentType(content)
    return _typeHandlers.get(ct)


