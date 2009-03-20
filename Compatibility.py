"""
Provides for code compatiblity between silva and the cmf.

Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
import warnings
from Acquisition import aq_get

#################################
### Service Lookup

_marker = []

SilvaToolMap = {
    'portal_catalog':'service_catalog',
    'portal_annotations':'service_annotations',
    'portal_metadata':'service_metadata'
    }

def getToolByName(ctx, service_name, default=_marker):
    warnings.warn(
        'getToolByName is deprecated and will be removed in Silva 2.3',
        DeprecationWarning)
    silva_name = SilvaToolMap[service_name]

    try:
        tool = aq_get(ctx, silva_name, default, 1)
    except AttributeError:
        if default is _marker:
            raise
        return default

    if tool is _marker:
        raise AttributeError(silva_name)

    return tool

_allowed_content_types = []

def registerTypeForMetadata(type_name):
    if type_name not in _allowed_content_types:
        _allowed_content_types.append(type_name)

def getContentTypeNames(ctx):
    return tuple(_allowed_content_types)
#return ctx.get_silva_addables_all()


tem = "python: object.service_metadata.getMetadataValue(object, '%s', '%s')"
index_expression_template = tem

