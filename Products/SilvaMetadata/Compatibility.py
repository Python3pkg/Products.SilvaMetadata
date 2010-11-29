"""
Provides for code compatiblity between silva and the cmf.

Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

_allowed_content_types = []

def registerTypeForMetadata(type_name):
    if type_name not in _allowed_content_types:
        _allowed_content_types.append(type_name)

def getContentTypeNames(ctx):
    return tuple(_allowed_content_types)
#return ctx.get_silva_addables_all()

