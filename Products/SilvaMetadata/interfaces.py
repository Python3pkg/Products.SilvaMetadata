# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""
Marker Interfaces
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.interface import Interface, implements, Attribute

# Exposed for the API.
from Products.SilvaMetadata.Exceptions import ReadOnlyError
from silva.core.services.interfaces import IMetadataService


class IMetadataModifiedEvent(IObjectEvent):
    """Event to describe the fact that metadata changed.
    """
    changes = Attribute(u"dict describing the changed metadata")


class MetadataModifiedEvent(ObjectEvent):
    implements(IMetadataModifiedEvent)

    def __init__(self, object, changes):
        super(MetadataModifiedEvent, self).__init__(object)
        self.changes = changes




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


class ITypeMapping(Interface):
    """Map content type to a metadata set.
    """

    def getMetadataChain():
        """Return the metadata set chain names associated to this content.
        """

    def setMetadataChain(chain):
        """Set (and validate) the metadata set chain names associated to
        this content.
        """

    def iterChain():
        """Iter through each metadata set names associated to this content.
        """


# Adapter Provided Functionality


class IMetadataSetExporter(Interface):
    pass


class IMetadataForm(Interface):
    pass


class IMetadataValidation(Interface):
    pass


class IMetadataStorage(Interface):
    pass
