"""
Type Specific Initialization of Metadata Binding Runtime Data
not really meant for public api exposure (certainly not ttw)

Handler Signature is as follows

def metadata_initialization(content, bind_data)

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from Compatibility import getContentType

_typeInitHandlers = {}

def registerInitHandler(content_type, handler):
    assert callable(handler)
    global _typeInitHandlers
    _typeInitHandlers[content_type]=handler

def getHandler(content):
    ct = getContentType(content)
    return _typeInitHandlers.get(ct)


