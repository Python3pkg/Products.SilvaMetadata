"""
author: kapil thangavelu <k_vertigo@objectrealms.net>
$Id: Set.py,v 1.2 2003/04/22 17:58:48 hazmat Exp $
"""
from __future__ import nested_scopes

from ZopeImports import *
from AccessControl import getSecurityManager
from Compatiblity import actionFactory
from Element import MetadataElement, ElementFactory
from Export import MetadataSetExporter
from FormulatorField import listFields
from Index import createIndexes
from Interfaces import IMetadataSet
from Namespace import MetadataNamespace, DefaultNamespace, DefaultPrefix

from Products.ProxyIndex.ProxyIndex import getIndexTypes

class MetadataSet(Folder):
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
        {'label':'Settings',
         'action':'setSettingsForm'},        
        {'label':'Elements',
         'action':'manage_main'},
        {'label':'Action',
         'action':'setActionForm'},
        )

    setSettingsForm = DTMLFile('ui/SetSettingsForm', globals())
    setActionForm   = DTMLFile('ui/SetActionForm', globals())
    addElementForm  = DTMLFile('ui/ElementAddForm', globals())
    
    # XXX remove me
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
            raise Exception (" Set Already Initialized ")
        
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

##     def getView(self, object, mode='view'):

##         if mode == 'edit': raise NotImplemented, "no view code yet"
        
##         elements = self.getElementsFor(object, 'write')

##         annotations = getToolByName(self, 'portal_annotations')
##         data = annotations.getAnnotations(object, self.namespace_uri)

##         for e in elements:
##             e.render( data.get(e.getId()) )

        
    def getNamespace(self):
        return (self.metadata_prefix, self.metadata_uri)

    def getElements(self):
        return self.objectValues(spec='Metadata Element')

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

