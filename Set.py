"""
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from __future__ import nested_scopes

from ZopeImports import *
from AccessControl import getSecurityManager
from Compatibility import actionFactory
from Element import MetadataElement, ElementFactory
from Exceptions import NamespaceConflict, ConfigurationError
from Export import MetadataSetExporter
from FormulatorField import listFields
from Index import createIndexes
from Interfaces import IMetadataSet, IOrderedContainer
from Namespace import MetadataNamespace, DefaultNamespace, DefaultPrefix

from Products.ProxyIndex.ProxyIndex import getIndexTypes

class OrderedContainer(Folder):

    __implements__ = IOrderedContainer

    security = ClassSecurityInfo()

    #security.declareProtected('moveObject')
    def moveObject(self, id, position):
        obj_idx  = self.getObjectPosition(id)
        if obj_idx == position:
            return None
        elif position < 0:
            position = 0

        metadata = list(self._objects)
        obj_meta = metadata.pop(obj_idx)
        metadata.insert(position, obj_meta)
        self._objects = tuple(metadata)

    #security.declareProtected('getObjectPosition')
    def getObjectPosition(self, id):
        # range was faster last i checked.. (v. xrange)
        objs = list(self._objects)
        om = [objs.index(om) for om in objs if om['id']==id ]

        if om: # only 1 in list if any
            return om[0]

        raise NotFound('Object %s was not found'%str(id))

    #security.declareProtected('moveObjectUp')
    def moveObjectUp(self, id, steps=1):
        self.moveObject(
            self.getObjectPosition(id) - int(steps)
            )

    #security.declareProtected('moveObjectDown')
    def moveObjectDown(self, id, steps=1):
        self.moveObject(
            self.getObjectPosition(id) + int(steps)
            )

    def manage_renameObject(self, id, new_id, REQUEST=None):
        " "
        objidx = self.getObjectPosition(id)
        method = OrderedContainer.inheritedAttribute('manage_renameObject')
        result = method(self, id, new_id, REQUEST)
        self.moveObject(new_id, objidx)

        return result
        
InitializeClass(OrderedContainer)  

class MetadataSet(OrderedContainer):
    """
    Set of Elements constituting a metadata dialect
    """
    
    meta_type = 'Metadata Set'
    __implements__ = IMetadataSet

    security = ClassSecurityInfo()

    all_meta_types = (
        {'name':MetadataElement.meta_type,
         'action':'addElementForm'},
        )

    manage_options = (
        {'label':'Elements',
         'action':'manage_main'},        
        {'label':'Settings',
         'action':'setSettingsForm'},        
        {'label':'Action',
         'action':'setActionForm'},
        )

    setSettingsForm = DTMLFile('ui/SetSettingsForm', globals())
    setActionForm   = DTMLFile('ui/SetActionForm', globals())
    addElementForm  = DTMLFile('ui/ElementAddForm', globals())
    
    initialized = None
    use_action_p = None
    action = None
    
    def __init__(self,
                 id,
                 metadata_prefix=DefaultPrefix,
                 metadata_uri=DefaultNamespace
                 ):
        
        self.id = id
        self.initialized = None
        self.use_action_p = None
        self.metadata_uri = metadata_uri
        self.metadata_prefix = metadata_prefix

    def getTitle(self):
        return self.id

    def addMetadataElement(self,
                           id,
                           field_type,
                           index_type,
                           index_p=None,
                           RESPONSE=None):
        """ """
        element = ElementFactory(id)
        self._setObject(id, element)
        element = self._getOb(id)
        element.editElementPolicy(field_type, index_type, index_p)
        
        if RESPONSE is not None:
            return RESPONSE.redirect('manage_main')

    def editAction(self,
                   use_action_p,
                   id,
                   permission,
                   action,
                   condition,
                   category,
                   visible,
                   RESPONSE=None):
        """ CMF Action Provider Support """

        self.use_action_p = not not use_action_p

        self.action = actionFactory(id=id,
                                    title=title,
                                    permission=permission,
                                    category=category,
                                    action=action,
                                    condition=condition,
                                    visible=visible)

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def editSettings(self, ns_uri, ns_prefix, RESPONSE):
        """ Edit Set Settings """

        if self.isInitialized():
            raise ConfigurationError (" Set Already Initialized ")

        verifyNamespace(self, ns_uri, ns_prefix)
        self.setNamespace(ns_uri, ns_prefix)

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def exportXML(self, RESPONSE=None):
        """ export an xml serialized version of the policy """
        
        exporter = MetadataSetExporter(self)
        RESPONSE.setHeader('Content-Type', 'text/xml')
        return exporter()
        
    def setNamespace(self, ns_prefix, ns_uri):
        self.metadata_prefix = ns_prefix
        self.metadata_uri = ns_uri

    def isInitialized(self):
        return self.initialized

    def initialize(self, RESPONSE=None):
        """ initialize the metadata set """
        if self.isInitialized():
            return None
        
        # install indexes        
        indexables = [e for e in self.getElements() if e.index_p]
        catalog = getToolByName(self, 'portal_catalog')
        createIndexes(catalog, indexables)
        
        self.initialized = 1

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def getNamespace(self):
        return (self.metadata_prefix, self.metadata_uri)

    def getElements(self):
        return self.objectValues(spec='Metadata Element')

    def getElement(self, element_id):
        return self._getOb(element_id)

    def getElementsFor(self, object, mode='view'):

        if mode == 'view':
            guard = 'read_guard'
        else:
            guard = 'write_guard'

        sm = getSecurityManager()
        
        res = []
        for e in self.getElements():
            if getattr(e, guard).check(sm, e, object):
                res.append(e)
            if mode == 'edit' and e.read_only_p:
                continue
        return res

    def getMetadataSet(self):
        return self

    def getDefaults(self):
        res = {}
        for e in self.getElements():
            d = e.field.get_value('default')
            if d:
                res[e.getId()]=d
        return res

    def listFieldTypes(self):
        return listFields()

    def listIndexTypes(self):
        return getIndexTypes( getToolByName(self, 'portal_catalog') )
    
InitializeClass(MetadataSet)

def verifyNamespace(ctx, uri, prefix):

    sid = ctx.getId()
    container = aq_parent(aq_inner(ctx))
    
    for s in container.getMetadataSets():
        if s.getId() == sid:
            continue
        if s.metadata_uri == uri:
            raise NamespaceConflict("%s uri is already in use"%uri)
        elif s.metadata_prefix == prefix:
            raise NamespaceConflict("%s prefix is already in use"%prefix)
