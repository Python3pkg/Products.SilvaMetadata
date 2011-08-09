"""
Marker Interfaces
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from silva.core.interfaces.service import ISilvaService
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.interface import Interface, implements, Attribute


class IMetadataModifiedEvent(IObjectEvent):
    """Event to describe the fact that metadata changed.
    """
    changes = Attribute(u"dict describing the changed metadata")


class MetadataModifiedEvent(ObjectEvent):
    implements(IMetadataModifiedEvent)

    def __init__(self, object, changes):
        super(MetadataModifiedEvent, self).__init__(object)
        self.changes = changes



class IMetadataService(ISilvaService):
    """Metadata Service.
    """


class IMetadataBindingFactory(Interface):
    """Adapter on a content used to create a metadata binding for it.
    """
    read_only = Attribute(u"Boolean indicating the state of the accessor.")

    def get_content():
        """Return the content that the metadata binding should use.
        """

    def __call__(service):
        """Return a metadata binding.
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


class IMetadataSet(IOrderedContainer):
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
