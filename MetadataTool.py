"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
# Zope
from zope.interface import implements
from Acquisition import aq_base
from AccessControl import getSecurityManager
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.interfaces import IObjectWillBeRemovedEvent

from zope.app.container.interfaces import IObjectAddedEvent
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

# Formulator
from Products.Formulator import Form

# Silva
from Products.Silva.SilvaPermissions import ChangeSilvaContent
from Products.Silva.helpers import add_and_edit, \
    register_service, unregister_service

from silva.core.services.base import SilvaService
from silva.core.views.interfaces import IPreviewLayer
from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

# SilvaMetadata
from Access import invokeAccessHandler, getAccessHandler
from Namespace import BindingRunTime
from Binding import ObjectDelegate, encodeElement
from Exceptions import BindingError
from interfaces import IMetadataService, ICatalogService
from Compatibility import getContentTypeNames


class MetadataTool(Folder, SilvaService):

    id = 'service_metadata'
    meta_type = 'Advanced Metadata Tool'
    title =  meta_type

    manage_options = (
        {'label':'Overview',
         'action':'manage_overview'},

        {'label':'Metadata Sets',
         'action':'collection/manage_workspace'},

        {'label':'Type Mapping',
         'action':'manage_mapping'},
        )

    implements(IMetadataService)
    silvaconf.icon('metadata.png')
    silvaconf.factory('manage_addMetadataTool')

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
        """
        return a metadata binding adapter for a particular content
        object. a bind adapter encapsulates both metadata definitions,
        data, and policy behavior into an api for manipulating and
        introspecting metadata
        """
        ct = content.meta_type

        if not ct in getContentTypeNames(self):
            return None
        return invokeAccessHandler(self, content)

    def getMetadataValue(self, content, set_id, element_id, acquire=1):
        """Get a metadata value right away. This can avoid
        building up the binding over and over while indexing.

        This really goes to the low-level to speed this up to the maximum.
        It's only going to work for Silva, not CMF.
        Also, optionally turn off acquiring, in case you want to
        get this objects metadata _only_"""

        # We explicitly test for registered handlers.
        default_handler = getAccessHandler(None)
        handler = getAccessHandler(content.meta_type)
        if handler is not default_handler:
            version = None
            # Hum, I don't like the content.REQUEST
            if IPreviewLayer.providedBy(content.REQUEST):
                sm = getSecurityManager()
                if sm.checkPermission(ChangeSilvaContent, content):
                    version = content.get_editable()

            if version is None:
                version = content.get_viewable()
                if version is None:
                    return None

            binding = self.getMetadata(version)
            if binding is None:
                return None
            return binding.get(set_id, element_id)

        # XXX how does this interact with security issues?
        set = self.collection.getMetadataSet(set_id)
        element = set.getElement(element_id)
        annotations = IAnnotations(aq_base(content))

        bind_data = None
        if annotations is not None:
            bind_data = annotations.get(BindingRunTime)
        if bind_data is not None:
            delegate = bind_data.get(ObjectDelegate)
            if delegate is not None:
                content = getattr(content, delegate)()
                annotations = IAnnotations(aq_base(content))

        try:
            saved_data = annotations.get(set.metadata_uri)
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
                #print 'attr error on', repr(aqelname)
                pass
        # if not acquired, fall back on default
        return element.getDefault(content=content)

    def getMetadataForm(self, context, set_id):
        """Get a complete Formulator form for a metadata set. This helps
        validating user input.
        """
        set = self.collection.getMetadataSet(set_id)
        fields = [element.field for element in set.getElements()]
        form = Form.BasicForm().__of__(context)
        form.add_fields(fields)
        return form

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

    silvaconf.name('manage_overview')


class MetadataTypeMapping(silvaviews.ZMIView):

    silvaconf.name('manage_mapping')

    def update(self):
        if 'save_mapping' in self.request.form:
            self.context.ct_mapping.editMappings(
                self.request.form['default_chain'],
                self.request.form['type_chains'])


def manage_addMetadataTool(self, id, title=None, REQUEST=None):
    """Add a metadatatool.
    """

    service = MetadataTool(id)
    if title is not None:
        service.title = title
    register_service(self, id, service, IMetadataService)
    add_and_edit(self, id, REQUEST)
    return ''


@silvaconf.subscribe(
    IMetadataService, IObjectWillBeRemovedEvent)
def unregisterMetadataTool(service, event):
    unregister_service(service, IMetadataService)


@silvaconf.subscribe(
    IMetadataService, IObjectAddedEvent)
def configureMetadataTool(tool, event):

    from Collection import MetadataCollection
    from TypeMapping import TypeMappingContainer

    # if we are being imported as a zexp, the collection will already
    # be there. If we detect this, the setup has actually already been
    # completed (this is being imported). We should not add the new
    # collection object as it would fail with a duplicate id. We
    # should be able to bail out right away.
    if hasattr(tool.aq_explicit, 'collection'):
        return

    collection = MetadataCollection('collection')
    collection.id = 'collection'
    tool._setObject('collection', collection)

    mapping = TypeMappingContainer('ct_mapping')
    mapping.id = 'ct_mapping'
    tool._setObject('ct_mapping', mapping)

