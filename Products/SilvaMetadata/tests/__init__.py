# only to make this a package

from zope.component import getUtility

from Products.Formulator import StandardFields
from Products.SilvaMetadata.interfaces import IMetadataService


SET_ID = 'ut_md'

def setUp(context):
    mtool = getUtility(IMetadataService)
    collection = mtool.getCollection()
    collection.addMetadataSet(SET_ID,
                              'tmd',
                              'http://www.example.com/xml/test_md')
    set = collection.getMetadataSet(SET_ID)
    set.addMetadataElement('Title',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1)
    set.addMetadataElement('Description',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1)
    element = set.getElement('Description')
    element.field._edit({'required':0})
    element.editElementPolicy(acquire_p = 1)

    mapping = mtool.getTypeMapping()
    mapping.setDefaultChain('ut_md')
    mtool.addTypesMapping(('Silva Folder', ), ('ut_md', 'silva-extra'))

    factory = context.manage_addProduct['Silva']
    factory.manage_addFolder('zoo', "Zoo Folder")
    factory = context.zoo.manage_addProduct['Silva']
    factory.manage_addFolder('mammals', "Zoo Mammals")
    factory.manage_addFolder('reptiles', "Zoo Reptiles")
