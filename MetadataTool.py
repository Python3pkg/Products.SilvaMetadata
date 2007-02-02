"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
# Zope
from zope.interface import implements
from Acquisition import aq_base
from AccessControl import getSecurityManager
# Annotations
from Products.Annotations.AnnotationTool import Annotations
# Formulator
from Products.Formulator import Form
# Silva
from Products.Silva.interfaces import IGhostFolder
from Products.Silva.SilvaPermissions import ChangeSilvaContent
# SilvaMetadata
from Access import invokeAccessHandler, getAccessHandler
import Configuration
from ZopeImports import *
from Namespace import MetadataNamespace, BindingRunTime
from Binding import ObjectDelegate, encodeElement
from Exceptions import BindingError
from interfaces import IPortalMetadata
from Compatibility import ActionProviderBase
from Compatibility import getContentType, getContentTypeNames

class MetadataTool(UniqueObject, Folder, ActionProviderBase):

    id = 'portal_metadata'
    meta_type = 'Advanced Metadata Tool'
    title =  meta_type

    manage_options = (
        {'label':'Overview',
         'action':'manage_main'},

        {'label':'Metadata Sets',
         'action':'%s/manage_workspace' % Configuration.MetadataCollection},

        {'label':'Type Mapping',
         'action':'%s/manage_workspace' % Configuration.TypeMapping},
        )

    implements(IPortalMetadata)

    _actions = []

    security = ClassSecurityInfo()
    #security.declareProtected('metadata_overview', Configuration.pMetadataManage)
    #metadata_overview = DTMLFile('ui/MetadataToolOverview', globals())
    manage_main = DTMLFile('ui/MetadataToolOverview', globals())

    def __init__(self):
        pass

    #################################
    # Action Provider Interface
    def listActions(self, info=None):
        actions = []
        for set in self.getCollection().getMetadataSets():
            if set.use_action_p is not None and set.action is not None:
                actions.append(set.action)
        return self._actions

    #################################
    # Metadata interface

    ## site wide queries

    # this is the wrong tool to be asking.
    #def getFullName(self, userid):
    #    return userid

    # this is just lame, assumes global publisher for a site
    #def getPublisher(self):
    #    pass

    ## dublin core hardcodes :-(
    # we don't have vocabulary implementation yet.

    def listAllowedSubjects(self, content=None):
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor('Subject')

    def listAllowedFormats(self, content=None):
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor('Format')

    def listAllowedLanguages(self, content=None):
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.uniqueValuesFor('Language')

    def listAllowedRights(self, content=None):
        catalog = getToolByName(self, 'portal_catalog')
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
        collections = self._getOb(Configuration.MetadataCollection)
        return [coll for coll in collections if coll.getCategory() == category]
    
    def getCollection(self):
        """return a container containing all known metadata sets
        """
        return self._getOb(Configuration.MetadataCollection)

    def getTypeMapping(self):
        """ return the mapping of content types to metadata sets """
        return self._getOb(Configuration.TypeMapping)

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
        ct = getContentType(content)

        if not ct in getContentTypeNames(self):
            raise BindingError(
                "invalid content type %s for metadata system" % ct
                )
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
        handler = getAccessHandler(getContentType(content))
        if handler is not default_handler:
            metadataservice = content.aq_inner.service_metadata
            # XXX nasty hack to get the editable metadata in case of preview
            url = content.REQUEST['URL'].split('/')
            binding = None
            if 'preview_html' in url or 'tab_preview' in url:
                sm = getSecurityManager()
                if sm.checkPermission(ChangeSilvaContent, content):
                    content = content.get_editable()
            if content is None:
                return None
            else:
                binding = metadataservice.getMetadata(content)
            if binding is None:
                return None
            return binding.get(set_id, element_id)
        # XXX how does this interact with security issues?
        set = self.collection.getMetadataSet(set_id)
        element = set.getElement(element_id)
        annotations = getattr(aq_base(content), '_portal_annotations_', None)

        bind_data = None
        if annotations is not None:
            bind_data = annotations[MetadataNamespace].get(BindingRunTime)
        if bind_data is not None:
            delegate = bind_data.get(ObjectDelegate)
            if delegate is not None:
                content = getattr(content,delegate)()
                annotations = getattr(aq_base(content), '_portal_annotations_', None)

        try:
            saved_data = annotations[MetadataNamespace].get(set.metadata_uri)
        except (TypeError, KeyError):
            saved_data = None
            
        #print 'found it for:', repr((saved_data, content))
            
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

def tool_added(tool, event):
    initializeTool(tool)
        
def initializeTool(tool):

    from Collection import MetadataCollection
    from TypeMapping import TypeMappingContainer

    collection = MetadataCollection(Configuration.MetadataCollection)
    collection.id = Configuration.MetadataCollection
    tool._setObject(Configuration.MetadataCollection, collection)

    mapping = TypeMappingContainer(Configuration.TypeMapping)
    mapping.id = Configuration.TypeMapping
    tool._setObject(Configuration.TypeMapping, mapping)

