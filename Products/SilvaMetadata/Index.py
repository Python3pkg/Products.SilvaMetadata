
from five import grok
from silva.core.services.catalog import RecordStyle
from silva.core.services.interfaces import ICatalogingAttributes
from zope import component
from zope.interface import Interface

from Products.SilvaMetadata.interfaces import IMetadataService


class MetadataCatalogingAttributes(grok.Adapter):
    """Access to attributes to catalog objects which have metadata.
    """
    grok.context(Interface)
    grok.provides(ICatalogingAttributes)
    grok.implements(ICatalogingAttributes)

    def __init__(self, context):
        super(MetadataCatalogingAttributes, self).__init__(context)
        self._content = context
        self._metadata = component.getUtility(IMetadataService)

    def __getattr__(self, name):
        # We first look in SilvaMetadata if we have a match for this
        # item. This code is not optimal, but we can't do better with
        # SilvaMetadata.
        for mid, mset in self._metadata.collection.objectItems():
            if name.startswith(mset.metadata_prefix):
                for eid in mset.objectIds():
                    if name == ''.join((mset.metadata_prefix, eid,)):
                        # We have a match !
                        try:
                            return self._metadata.getMetadataValue(
                                self._content, mid, eid)
                        except KeyError:
                            pass
        return getattr(self._content, name)


def createIndexes(catalog, elements):
    for element in elements:
        index_id = createIndexId(element)
        extra = createIndexArguements(element)

        if index_id not in catalog.indexes():
            catalog.addIndex(index_id, element.index_type, extra)

        if element.metadata_in_catalog_p:
            if index_id not in catalog.schema():
                catalog.addColumn(index_id)


def getIndexNamesFor(elements):
    res = []
    for e in elements:
        res.append(createIndexId(e))
    return res


def createIndexId(element):
    ms = element.getMetadataSet()
    return "%s%s" % (ms.metadata_prefix, element.getId())


def createIndexArguements(element):
    # try to get the element's index construction key/value pair
    if element.index_constructor_args is not None:
        return RecordStyle(**element.index_constructor_args)
    return RecordStyle()


