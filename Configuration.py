"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
$Id: Configuration.py,v 1.2 2003/04/22 17:58:48 hazmat Exp $
"""

#################################
### Silva / CMF Compatiblity Flag
# if using Silva set to 0
UsingCMF = 0

#################################
# this module gets populated with
# permissions for these by the compatiblity
# module.
pMetadataView = None
pMetadataEdit = None
pMetadataManage = None

#################################
### internal names
MetadataCollection = 'collection'
TypeMapping = 'ct_mapping'
