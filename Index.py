"""
functions for installing and removing indexes for
metadata elements in a zcatalog.

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from Products.ProxyIndex import ProxyIndex
from Compatiblity import index_expression_template

def createIndexes(catalog, elements):

    all_indexes = catalog.indexes()

    for e in elements:
        idx_id  = createIndexId(e)
        extra   = createIndexArguements(e)
        
        if idx_id in all_indexes:
            continue
        
        catalog.addIndex(idx_id, ProxyIndex.meta_type, extra)
        all_indexes.append(idx_id)

    return None

def removeIndexes(catalog, elements):

    all_indexes = catalog.indexes()

    for e in elements:
        idx_id = createIndexId(e)

        if not idx_id in all_indexes:
            continue

        catalog.delIndex(idx_id)
        all_indexes.remove(idx_id)

    return None

def createIndexId(element):
    ms = element.getMetadataSet()
    return "%s%s"%(ms.metadata_prefix, element.getId())

def createIndexArguements(element):

    d = {}
    class IndexArgs: pass
    
    d['index_type'] = element.index_type
    d['value_expr'] = createIndexExpression(element)

    args = IndexArgs()
    args.__dict__.update(d)

    return args

def createIndexExpression(element):
    return index_expression_template%(
        element.getMetadataSet().getId(),
        element.getId()
        )

