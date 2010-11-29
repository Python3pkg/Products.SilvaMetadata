"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from OFS.Folder import Folder

from zope.interface import implements

from Products.Silva import SilvaPermissions
from Products.SilvaMetadata.Exceptions import NotFound
from Products.SilvaMetadata.Import import read_set, make_set
from Products.SilvaMetadata.Set import MetadataSet
from Products.SilvaMetadata.interfaces import IMetadataCollection


class MetadataCollection(Folder):

    meta_type = 'Metadata Collection'

    implements(IMetadataCollection)

    security = ClassSecurityInfo()

    all_meta_types = (
        {'name':MetadataSet.meta_type,
         'action':'addMetadataSetForm'},
        )

    manage_options = (

        {'label':'Metadata Sets',
         'action':'manage_main'},

        {'label':'Metadata Tool',
         'action':'../manage_workspace'},
        )

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'addMetadataSetForm')
    addMetadataSetForm = DTMLFile('ui/MetadataSetAddForm', globals())

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'addMetadataSet')
    def addMetadataSet(self, id, namespace_prefix, namespace_uri,
                       title='', description='', i18n_domain='', RESPONSE=None):
        " "

        set = MetadataSet(id=id,
                          title = title,
                          description = description,
                          i18n_domain = i18n_domain,
                          metadata_prefix = namespace_prefix,
                          metadata_uri = namespace_uri,
                          )

        self._setObject(id, set)

        if RESPONSE is not None:
            return self.manage_main(update_menu=1)

    #security.declareProtected()
    def getMetadataSets(self):
        return self.objectValues('Metadata Set')

    #security.declareProtected()
    def getMetadataSet(self, set_id):
        return self._getOb(set_id)

    #security.declareProtected()
    def getSetByNamespace(self, metadata_uri):
        for set in self.getMetadataSets():
            if set.metadata_uri == metadata_uri:
                return set

        raise NotFound("No Metadata Set Matching %s" % str(metadata_uri))

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'importSet')
    def importSet(self, xml_file, RESPONSE=None):
        """ import an xml definition of a metadata set"""

        set_node = read_set(xml_file)
        make_set(self, set_node)

        if RESPONSE is not None:
            return self.manage_main(update_menu=1)


InitializeClass(MetadataCollection)
