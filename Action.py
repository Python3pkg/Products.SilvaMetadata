"""
CMF/Silva (In)Compatibility for Actions
author: kapil thangavelu <k_vertigo@objectrealms.net>
$Id: Action.py,v 1.1 2003/04/22 14:45:29 hazmat Exp $
"""

try:
    from Products.CMFCore.ActionInformation import ActionInformation
except ImportError:
    ActionInformation = None

def actionFactory(**kw):
    if ActionInformation is None:
        return None
    return ActionInformation(**kw)
    


