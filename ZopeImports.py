from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from Globals import DTMLFile, InitializeClass
from Interface import Base as Interface
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, UniqueObject
from ZODB.PersistentMapping import PersistentMapping

# py2.2.2 forward decl
try:
    True, False
except:
    True = 1
    False = 0
    
