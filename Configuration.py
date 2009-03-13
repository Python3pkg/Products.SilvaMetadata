"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

# Permissions

from Products.Silva.SilvaPermissions import View as pMetadataView
from Products.Silva.SilvaPermissions import ChangeSilvaContent as pMetadataEdit
from Products.Silva.SilvaPermissions import ViewManagementScreens as pMetadataManage


#################################
### internal names
MetadataCollection = 'collection'
TypeMapping = 'ct_mapping'
