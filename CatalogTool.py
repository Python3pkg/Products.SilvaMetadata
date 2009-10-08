# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from zope.app.container.interfaces import IObjectAddedEvent

from OFS.interfaces import IObjectWillBeRemovedEvent
from Products.ZCatalog.ZCatalog import ZCatalog

from Products.ProxyIndex.ProxyIndex import RecordStyle
from Products.Silva.helpers import add_and_edit, \
    register_service, unregister_service

from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf

from Products.SilvaMetadata.interfaces import ICatalogService


class CatalogService(ZCatalog, SilvaService):
    """The Service catalog.
    """

    meta_type = "Silva Service Catalog"

    implements(ICatalogService)

    silvaconf.factory('manage_addCatalogService')


def manage_addCatalogService(self, id, title=None, REQUEST=None):
    """Add a catalog service.
    """

    service = CatalogService(id, title)
    register_service(self, id, service, ICatalogService)
    add_and_edit(self, id, REQUEST)
    return ''


@silvaconf.subscribe(
    ICatalogService, IObjectWillBeRemovedEvent)
def unregisterCatalogTool(service, event):
    unregister_service(service, ICatalogService)


class El:
    """Helper class to initialize the catalog lexicon
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)


@silvaconf.subscribe(
    ICatalogService, IObjectAddedEvent)
def configureCatalogService(catalog, event):

    lexicon_id = 'silva_lexicon'
    # Add lexicon with right splitter (Silva.UnicodeSplitter.Splitter
    # registers under "Unicode Whitespace splitter")
    if not lexicon_id in catalog.objectIds():
        # XXX ugh, hardcoded dependency on names in ZCTextIndex
        catalog.manage_addProduct['ZCTextIndex'].manage_addLexicon(
            lexicon_id,
            elements=[
                El(group='Case Normalizer', name='Case Normalizer'),
                El(group='Stop Words', name=" Don't remove stop words"),
                El(group='Word Splitter', name="Unicode Whitespace splitter"),
                ]
            )

    existing_columns = catalog.schema()
    columns = [
        'id',
        'meta_type',
        'silva_object_url',
        ]

    for column_name in columns:
        if column_name in existing_columns:
            continue
        catalog.addColumn(column_name)

    existing_indexes = catalog.indexes()
    indexes = [
        ('id', 'FieldIndex'),
        ('meta_type', 'FieldIndex'),
        ('path', 'PathIndex'),
        ('fulltext', 'ZCTextIndex'),
        ('version_status', 'FieldIndex'),
        ('haunted_path', 'FieldIndex'),
        ]

    for field_name, field_type in indexes:
        if field_name in existing_indexes:
            continue

        # special handling for argument passing to zctextindex ranking
        # algorithm used is best for larger text body / query size
        # ratios
        if field_type == 'ZCTextIndex':
            extra = RecordStyle(
                {'doc_attr':field_name,
                 'lexicon_id':'silva_lexicon',
                 'index_type':'Okapi BM25 Rank'}
                )
            catalog.addIndex(field_name, field_type, extra)
            continue

        catalog.addIndex(field_name, field_type)
