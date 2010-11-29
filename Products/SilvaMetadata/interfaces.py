"""
Marker Interfaces
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from silva.core.interfaces.service import ISilvaService
from zope.interface import Interface


class IMetadataService(ISilvaService):
    """Metadata Service.
    """


class IMetadataCollection(Interface):
    pass


class IOrderedContainer(Interface):

    def moveObject(id, position):
        """
        move an object with the given an id to the specified
        position.
        """
    def moveObjectUp(id, steps=1):
        """
        move an object with the given id up the ordered list
        the given number of steps
        """

    def moveObjectDown(id, steps=1):
        """
        move an object with the given id down the ordered list
        the given number of steps
        """

    def getObjectPosition(id):
        """
        given an object id return its position in the ordered list
        """


class IMetadataSet(Interface):
    pass


class IMetadataElement(Interface):
    pass


# Adapter Provided Functionality


class IMetadataSetExporter(Interface):
    pass


class IMetadataForm(Interface):
    pass


class IMetadataValidation(Interface):
    pass


class IMetadataStorage(Interface):
    pass
