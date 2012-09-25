# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
"""
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
import sys

# Zope
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager, Permissions
from Acquisition import aq_inner, aq_parent
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from OFS.Folder import Folder

from Products.PluginIndexes.interfaces import IPluggableIndex

from zope.interface import implements
from zope.component import getUtility

# SilvaMetadata
from Products.SilvaMetadata.Element import MetadataElement
from Products.SilvaMetadata.Exceptions import (
    NamespaceConflict, ConfigurationError, NotFound)
from Products.SilvaMetadata.Export import MetadataSetExporter
from Products.SilvaMetadata.FormulatorField import listFields
from Products.SilvaMetadata.Index import createIndexes
from Products.SilvaMetadata.interfaces import IMetadataSet, IOrderedContainer

from silva.core.services.interfaces import ICatalogService

DefaultPrefix = 'example'
DefaultNamespace = "http://www.example.com/unknown_namespace"


class OrderedContainer(Folder):
    implements(IOrderedContainer)
    security = ClassSecurityInfo()

    security.declareProtected(
        Permissions.copy_or_move, 'moveObject')
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

    security.declareProtected(
        Permissions.copy_or_move, 'getObjectPosition')
    def getObjectPosition(self, id):

        objs = list(self._objects)
        om = [objs.index(om) for om in objs if om['id']==id ]

        if om: # only 1 in list if any
            return om[0]

        raise NotFound('Object %s was not found' % str(id))

    security.declareProtected(
        Permissions.copy_or_move, 'moveObjectUp')
    def moveObjectUp(self, id, steps=1, RESPONSE=None):
        """ Move an object up """
        self.moveObject(
            id,
            self.getObjectPosition(id) - int(steps)
            )
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(
        Permissions.copy_or_move, 'moveObjectDown')
    def moveObjectDown(self, id, steps=1, RESPONSE=None):
        """ move an object down """
        self.moveObject(
            id,
            self.getObjectPosition(id) + int(steps)
            )
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(
        Permissions.copy_or_move, 'moveObjectTop')
    def moveObjectTop(self, id, RESPONSE=None):
        """ move an object to the top """
        self.moveObject(id, 0)
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(
        Permissions.copy_or_move, 'moveObjectBottom')
    def moveObjectBottom(self, id, RESPONSE=None):
        """ move an object to the bottom """
        self.moveObject(id, sys.maxint)
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(
        Permissions.view_management_screens, 'manage_renameObject')
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
    implements(IMetadataSet)

    security = ClassSecurityInfo()

    all_meta_types = (
        {'name': MetadataElement.meta_type,
         'action':'addElementForm'},
        )

    manage_options = (
        {'label':'Elements',
         'action':'manage_main'},
        {'label':'Settings',
         'action':'manage_settings'},
        )

    security.declareProtected(
        Permissions.view_management_screens, 'manage_settings')
    manage_settings = DTMLFile('ui/SetSettingsForm', globals())

    security.declareProtected(
        Permissions.view_management_screens, 'addElementForm')
    addElementForm  = DTMLFile('ui/ElementAddForm', globals())

    manage_main = DTMLFile('ui/SetContainerView', globals())

    initialized = None
    use_action_p = None
    action = None
    title = ''
    description = ''

    # for backwards compatibility...
    _category = ''
    _minimal_role = ''

    def __init__(self, id, title='', description='', i18n_domain='',
                 metadata_prefix=DefaultPrefix, metadata_uri=DefaultNamespace):

        self.id = id
        self.initialized = None
        self.use_action_p = None
        self.title = title
        self.description = description
        self.i18n_domain = i18n_domain
        self._minimal_role = ''
        self._category = ''

        # we can't do any verification till after we have a ctx
        self.metadata_uri = metadata_uri
        self.metadata_prefix = metadata_prefix


    def getTitle(self):
        return self.title

    def getDescription(self):
        return self.description

    def getMinimalRole(self):
        return self._minimal_role

    security.declareProtected(
        Permissions.view_management_screens, 'setMinimalRole')
    def setMinimalRole(self, role):
        self._minimal_role = role

    def getCategory(self):
        return self._category

    security.declareProtected(
        Permissions.view_management_screens, 'setCategory')
    def setCategory(self, cat):
        self._category = cat

    security.declareProtected(
        Permissions.view_management_screens, 'addMetadataElement')
    def addMetadataElement(self,
                           id,
                           field_type,
                           index_type,
                           index_p=None,
                           acquire_p=None,
                           read_only_p=None,
                           metadata_in_catalog_p=None,
                           automatic_p=None,
                           RESPONSE=None):
        """ """
        element = MetadataElement(id)
        self._setObject(id, element)
        element = self._getOb(id)

        element.editElementPolicy(field_type = field_type,
                                  index_type = index_type,
                                  index_p = index_p,
                                  read_only_p = read_only_p,
                                  metadata_in_catalog_p = metadata_in_catalog_p,
                                  acquire_p = acquire_p,
                                  automatic_p = automatic_p)

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_main')

    security.declareProtected(
        Permissions.view_management_screens, 'editSettings')
    def editSettings(
        self, title, description, i18n_domain, ns_uri, ns_prefix,
        minimal_role='', category=''):
        """ Edit Set Settings """

        if self.isInitialized():
            raise ConfigurationError (" Set Already Initialized ")

        self.title = title
        self.description = description
        self.i18n_domain = i18n_domain

        self.setNamespace(ns_uri, ns_prefix)
        self.setMinimalRole(minimal_role)
        self.setCategory(category)

        request = getattr(self, 'REQUEST', None)
        if request is not None:
            request.RESPONSE.redirect('manage_workspace')

    def exportXML(self, RESPONSE=None):
        """ export an xml serialized version of the policy """

        exporter = MetadataSetExporter(self)

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-Type', 'text/xml')
            RESPONSE.setHeader('Content-Disposition',
                               'attachment; filename=%s.xml' % self.getId())
        return exporter()

    def setNamespace(self, ns_uri, ns_prefix):
        verifyNamespace(self, ns_uri, ns_prefix)
        self.metadata_prefix = ns_prefix
        self.metadata_uri = ns_uri

    def isInitialized(self):
        return self.initialized

    security.declareProtected(
        Permissions.view_management_screens, 'setInitialized')
    def setInitialized(self, initialization_flag, RESPONSE=None):
        """ """
        flag = not not initialization_flag

        if flag != self.initialized:
            if self.initialized:
                self.initialized = 0
            else:
                self.initialize()

        if RESPONSE:
            return RESPONSE.redirect('manage_settings')

    security.declareProtected(
        Permissions.view_management_screens, 'initialize')
    def initialize(self, RESPONSE=None):
        """ initialize the metadata set """
        if self.isInitialized():
            return None

        # install indexes
        indexables = [e for e in self.getElements() if e.index_p]
        createIndexes(getUtility(ICatalogService), indexables)

        self.initialized = 1

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_settings')


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

        elements = []
        for e in self.getElements():
            if mode == 'edit' and (e.read_only_p or e.automatic_p):
                continue
            if mode == 'write' and (e.read_only_p and not e.automatic_p):
                continue
            if getattr(e, guard).check(sm, e, object):
                elements.append(e)
        return elements

    def getMetadataSet(self):
        return self

    def getDefaults(self, content):
        res = {}
        for e in self.getElements():
            res[e.getId()] = e.getDefault(content)
        return res

    def listFieldTypes(self):
        return listFields()

    def listIndexTypes(self):
        catalog = getUtility(ICatalogService)
        return [i['name'] for i in catalog.all_meta_types(
                interfaces=(IPluggableIndex,))]

    def get_i18n_domain(self):
        """Get i18n domain, if any.
        """
        return getattr(self, 'i18n_domain', '')

InitializeClass(MetadataSet)


def metadataset_added(metadataset, event):
    # verify our namespace
    metadataset.setNamespace(
        metadataset.metadata_uri, metadataset.metadata_prefix)


def verifyNamespace(ctx, uri, prefix):
    sid = ctx.getId()
    container = aq_parent(aq_inner(ctx))

    for s in container.getMetadataSets():
        if s.getId() == sid:
            continue
        if s.metadata_uri == uri:
            raise NamespaceConflict("%s uri is already in use" % uri)
        elif s.metadata_prefix == prefix:
            raise NamespaceConflict("%s prefix is already in use" % prefix)
