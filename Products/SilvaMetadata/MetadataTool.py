"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

# Zope
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder

from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from five import grok

# Silva
from silva.core import conf as silvaconf
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ICatalogService
from silva.core.views import views as silvaviews

# SilvaMetadata
from Products.SilvaMetadata.Binding import encodeElement
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaMetadata.interfaces import IMetadataBindingFactory


def configure_metadata(service):
    from Collection import MetadataCollection
    from TypeMapping import TypeMappingContainer

    collection = MetadataCollection('collection')
    collection.id = 'collection'
    service._setObject('collection', collection)

    mapping = TypeMappingContainer('ct_mapping')
    mapping.id = 'ct_mapping'
    service._setObject('ct_mapping', mapping)


class MetadataTool(SilvaService, Folder):
    meta_type = 'Advanced Metadata Tool'

    manage_options = (
        {'label':'Overview', 'action':'manage_overview'},
        {'label':'Metadata Sets', 'action':'collection/manage_workspace'},
        {'label':'Type Mapping', 'action':'manage_mapping'},
        )

    grok.implements(IMetadataService)
    grok.name('service_metadata')
    silvaconf.default_service(setup=configure_metadata)
    silvaconf.icon('metadata.png')

    security = ClassSecurityInfo()

    #################################
    # Metadata interface

    def listAllowedSubjects(self, content=None):
        catalog = getUtility(ICatalogService)
        return catalog.uniqueValuesFor('Subject')

    def listAllowedFormats(self, content=None):
        catalog = getUtility(ICatalogService)
        return catalog.uniqueValuesFor('Format')

    def listAllowedLanguages(self, content=None):
        catalog = getUtility(ICatalogService)
        return catalog.uniqueValuesFor('Language')

    def listAllowedRights(self, content=None):
        catalog = getUtility(ICatalogService)
        return catalog.uniqueValuesFor('Rights')

    #################################
    ## validation hooks
    def setInitialMetadata(self, content):
        binding = self.getMetadata(content)
        sets = binding.getSetNames()
        # getting the set metadata will cause its
        # initialization if nots already initialized
        for s in sets:
            binding[s]

    def validateMetadata(self, content):
        binding = self.getMetadata(content)
        sets = binding.getSetNames()
        for s in sets:
            data = binding[s]
            binding.validate(data, set_id=s)

    #################################
    ## new interface

    def getCollectionForCategory(self, category=''):
        """return a container containing all known metadata sets
        """
        collections = self._getOb('collection')
        return [coll for coll in collections if coll.getCategory() == category]

    def getCollection(self):
        """return a container containing all known metadata sets
        """
        return self._getOb('collection')

    def getTypeMapping(self):
        """ return the mapping of content types to metadata sets """
        return self._getOb('ct_mapping')

    def getMetadataSet(self, set_id):
        """ get a particular metadata set """
        return self.getCollection().getMetadataSet(set_id)

    def getMetadataSetFor(self, metadata_namespace):
        """ get a particular metadata set by its namespace """
        return self.getCollection().getSetByNamespace(metadata_namespace)

    def getMetadata(self, content):
        return IMetadataBindingFactory(content)(self)

    def getMetadataValue(self, content, set_id, element_id, acquire=1):
        content = IMetadataBindingFactory(content).get_content()
        if content is None:
            return None

        try:
            mset = self.collection.getMetadataSet(set_id)
            element = mset.getElement(element_id)
        except AttributeError:
            return None
        annotations = IAnnotations(aq_base(content))

        try:
            saved_data = annotations.get(mset.metadata_uri)
        except (TypeError, KeyError):
            saved_data = None

        # if it's saved, we're done
        if saved_data:
            if saved_data.get(element_id, None):
                return saved_data[element_id]

        # if not, check whether we acquire it, if so, we're done
        if acquire and element.isAcquireable():
            aqelname = encodeElement(set_id, element_id)
            try:
                return getattr(content, aqelname)
            except AttributeError:
                pass
        # if not acquired, fall back on default
        return element.getDefault(content=content)

    # Convenience methods
    def initializeMetadata(self):
        # initialize the sets if not already initialized
        collection = self.getCollection()
        for set in collection.getMetadataSets():
            if not set.isInitialized():
                set.initialize()

    def addTypesMapping(self, types, setids, default=''):
        for type in types:
            self.addTypeMapping(type, setids, default)

    def addTypeMapping(self, type, setids, default=''):
        mapping = self.getTypeMapping()
        chain = mapping.getChainFor(type)
        if chain == 'Default':
            chain = ''
        chain = [c.strip() for c in chain.split(',') if c]
        for setid in setids:
            if setid in chain:
                continue
            chain.append(setid)
        tm = {'type': type, 'chain': ','.join(chain)}
        mapping.editMappings(default, (tm, ))

    def removeTypesMapping(self, types, setids):
        for type in types:
            self.removeTypeMapping(type, setids)

    def removeTypeMapping(self, type, setids):
        mapping = self.getTypeMapping()
        chain = mapping.getChainFor(type)
        if chain == 'Default' or chain == '':
            return
        chain = [c.strip() for c in chain.split(',') if c]
        for setid in setids:
            if setid in chain:
                chain.remove(setid)
        tm = {'type': type, 'chain': ','.join(chain)}
        default = mapping.getDefaultChain()
        mapping.editMappings(default, (tm, ))

    #################################
    # misc

    def update(self, RESPONSE):
        """ """
        RESPONSE.redirect('manage_workspace')


class MetadataToolOverview(silvaviews.ZMIView):
    grok.name('manage_overview')


class MetadataTypeMapping(silvaviews.ZMIView):
    grok.name('manage_mapping')

    def update(self):
        if 'save_mapping' in self.request.form:
            self.context.ct_mapping.editMappings(
                self.request.form['default_chain'],
                self.request.form['type_chains'])

