"""
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
class NoContext(Exception): pass
class NamespaceConflict(Exception): pass
class ConfigurationError(Exception): pass
class NotFound(AttributeError): pass
class CompatibilityException(Exception): pass
class ImportError(Exception): pass
class ValidationError(Exception): pass
