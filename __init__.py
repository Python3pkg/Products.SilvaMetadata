"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import Configuration
import Compatibility

import Collection
import Set
import Element
import Binding
import MetadataTool

from Globals import ImageFile
from Products.Annotations.helpers import setupIcon

# Allow Errors to be imported TTW
from Products.PythonScripts.Utility import allow_module
allow_module('Products.SilvaMetadata.Exceptions')

misc_ = {
    'up'     : ImageFile('www/up.gif', globals()),
    'down'   : ImageFile('www/down.gif', globals()),
    'top'    : ImageFile('www/top.gif', globals()),
    'bottom' : ImageFile('www/bottom.gif', globals()),
    # XXX ugh! misc_ here overrides whatever is done in setupIcon apparently,
    # so let's set up metadata icon here again..
    'silva_metadata.png': ImageFile('www/silva_metadata.png', globals()),
    }

setupIcon(MetadataTool.MetadataTool,
          'www/silva_metadata.png', 'SilvaMetadata', globals())
