"""
Maps Metadata Sets onto Content Types

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import operator

# Zope
from OFS.Folder import Folder
from Acquisition import aq_base

from zope.interface import implements

# SilvaMetadata
from Products.SilvaMetadata.interfaces import ITypeMapping
from Products.SilvaMetadata.Exceptions import ConfigurationError
from Products.Silva.ExtensionRegistry import extensionRegistry

DEFAULT_MAPPING_NAME = 'Default'


def verifyChain(ctxt, chain):
    for part in filter(None, [c.strip() for c in chain.split(',')]):
        try:
            ctxt.getMetadataSet(part)
        except AttributeError:
            return False
    return True


def chainIterator(chain):
    return filter(None, [c.strip() for c in chain.split(',')])


class TypeMappingContainer(Folder):
    meta_type = 'Type Mapping Container'

    def __init__(self, id):
        super(TypeMappingContainer, self).__init__(id)
        self.default_chain = ''

    def setDefaultChain(self, chain, RESPONSE=None):
        if not verifyChain(self, chain):
            raise ConfigurationError("invalid metadata set")

        self.default_chain = chain

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_workspace')

    def getDefaultChain(self):
        return self.default_chain

    def getChainFor(self, content_type):
        if content_type not in self.getContentTypes():
            return ''
        try:
            ctm = self._getOb(content_type)
        except AttributeError:
            return self.getDefaultChain()
        return ctm.getMetadataChain()

    def iterChainFor(self, content_type):
        return chainIterator(self.getChainFor(content_type))

    def getTypeMappings(self):
        return self.objectValues(TypeMapping.meta_type)

    def getTypeMappingFor(self, content_type):
        try:
            ctm = self._getOb(content_type)
        except AttributeError:
            return None
        return ctm

    def editMappings(self, default_chain, type_chains):
        self.setDefaultChain(default_chain)

        for tcr in type_chains:
            t = tcr['type']
            tc = tcr['chain']
            tc = tc.strip()
            if tc == DEFAULT_MAPPING_NAME:
                if self.getChainFor(t) != DEFAULT_MAPPING_NAME:
                    self._delObject(t)
            elif tc == self.getChainFor(t):
                continue
            else:
                tm = self.getTypeMappingFor(t)
                if tm is None:
                    self._setObject(t, TypeMapping(t))
                    ctm = self._getOb(t)
                    ctm.setMetadataChain(tc)
                else:
                    tm.setMetadataChain(tc)

    def getContentTypes(self):
        if not hasattr(aq_base(self), '_v_content_types'):
            self._v_content_types = map(
                operator.itemgetter('name'), extensionRegistry.get_contents())
        return self._v_content_types


class TypeMapping(Folder):
    meta_type = 'Metadata Type Mapping'
    implements(ITypeMapping)

    def __init__(self, id):
        super(TypeMapping, self).__init__(id)
        self.chain = None

    def getMetadataChain(self):
        return self.chain

    def setMetadataChain(self, chain):
        if not verifyChain(self, chain):
            raise ConfigurationError("invalid metadata set")
        self.chain = chain

    def iterChain(self):
        return chainIterator(self.chain)


