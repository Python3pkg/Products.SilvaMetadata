"""
Provides for code compatiblity between silva and the cmf.

Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import Configuration
from Acquisition import aq_inner, aq_base, aq_get
from OFS.ObjectManager import UNIQUE
from ExtensionClass import Base

class CompatiblityException(Exception): pass

#################################
### Interface declarations/assertions
if Configuration.UsingCMF:
    from Products.CMFCore.interfaces import portal_actions, portal_metadata
    IActionProvider = portal_actions.ActionProvider
    IPortalMetadata = portal_metadata.portal_metadata
else:
    class IActionProvider(Interface): pass
    class IPortalMetadata(Interface): pass

#################################
### Action Provider and Info 
if Configuration.UsingCMF:
    from Products.CMFCore.ActionInformation import ActionInformation
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
else:
    ActionInformation = None

    class ActionProviderBase(Base):
        pass

def actionFactory(**kw):
    if ActionInformation is None:
        return None
    return ActionInformation(**kw)

#################################
### Service Lookup

if Configuration.UsingCMF:
    from Products.CMFCore.utils import getToolByName

else:
    _marker = []
    
    SilvaToolMap = {
        'portal_catalog':'service_catalog',
        'portal_annotations':'service_annotations'
        }

    def getToolByName(ctx, service_name, default=_marker):
        try:
            silva_name = SilvaToolMap[service_name]
        except KeyError, e:
            raise CompatilbilityException(str(e))

        try:
            tool = aq_get(ctx, silva_name, default, 1)
        except AttributeError:
            if default is _marker:
                raise
            return default
        
        if tool is _marker:
            raise AttributeError(silva_name)
        
        return tool
        
#################################
### Content Type Lookup
if Configuration.UsingCMF:
    def getContentTypeNames(ctx):
        pt = getToolByName(ctx, 'portal_types')
        return pt.objectIds()
else:
    def getContentTypeNames(ctx):
        return ctx.get_silva_addables_all()
        
#################################
### Permissions
if Configuration.UsingCMF:
    from Products.CMFCore import CMFCorePermissions
    Configuration.pMetadataView = CMFCorePermissions.View
    Configuration.pMetadataEdit = CMFCorePermissions.ModifyPortalContent
    Configuration.pMetadataManage = CMFCorePermissions.ManagePortal
else:
    from Products.Silva import SilvaPermissions
    Configuration.pMetadataView = SilvaPermissions.View
    Configuration.pMetadataEdit = SilvaPermissions.ChangeSilvaContent
    Configuration.pMetadataManage = SilvaPermissions.ViewManagementScreens

#################################
### Misc    
if Configuration.UsingCMF:
    from Products.CMFCore.utils import UniqueObject
else:
    class ImmutableId(Base):

        """ Base class for objects which cannot be renamed.
        """
        def _setId(self, id):

            """ Never allow renaming!
            """
            if id != self.getId():
                raise MessageDialog(
                    title='Invalid Id',
                    message='Cannot change the id of this object',
                    action ='./manage_main',)

    class UniqueObject (ImmutableId):

        """ Base class for objects which cannot be "overridden" / shadowed.
        """
        __replaceable__ = UNIQUE
