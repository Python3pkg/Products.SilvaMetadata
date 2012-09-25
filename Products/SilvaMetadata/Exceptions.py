# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
"""
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

class MetadataError(Exception):
    pass


class ReadOnlyError(MetadataError):
    pass

class NoContext(MetadataError):
    pass

class NamespaceConflict(MetadataError):
    pass

class ConfigurationError(MetadataError):
    pass

class NotFound(MetadataError, AttributeError):
    pass

class ImportError(MetadataError):
    pass

class ValidationError(MetadataError):
    pass

class BindingError(MetadataError):
    pass

class XMLMarshallError(MetadataError):
    pass

# For use in python scripts
from Products.PythonScripts.Utility import allow_class
allow_class(BindingError)
