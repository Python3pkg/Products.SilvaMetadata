from __future__ import nested_scopes

from unittest import TestCase, TestSuite, makeSuite, main
import Zope
Zope.startup()

from DateTime import DateTime

from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyFTI
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.tests.base.testcase import newSecurityManager
from Products.CMFCore.tests.base.utils import has_path
from Products.CMFCore.tests.base.security import OmnipotentUser

from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.CatalogTool import CatalogTool
from Products.PortalAnnotations.AnnotationTool import AnnotationTool
from Products.SilvaMetadata.MetadataTool import MetadataTool

from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName

SET_ID = 'ut_md'

def setupTools(root):
    root._setObject('portal_types', TypesTool())
    root._setObject('portal_annotations', AnnotationTool())
    root._setObject('portal_metadata', MetadataTool())
    root._setObject('portal_catalog', CatalogTool())    

def setupContentTypes(context):
    types_tool = getToolByName(context, 'portal_types')

    types_tool._setObject( 'Folder'
                           , FTI( id='Folder'
                                  , title='Folder or Directory'
                                  , meta_type=PortalFolder.meta_type
                                  , product='CMFCore'
                                  , factory='manage_addPortalFolder'
                                  , filter_content_types=0
                                  )
                             )

def setupContentTree(container):
    ttool = getToolByName(container, 'portal_types')
    ttool.constructContent('Folder', container, 'zoo')

    zoo = container._getOb('zoo')

    ttool.constructContent('Folder', zoo, 'mammals')
    ttool.constructContent('Folder', zoo, 'reptiles')

    mammals = zoo._getOb('mammals')
    reptiles = zoo._getOb('reptiles')

    return zoo

def setupCatalog(context):
    catalog = getToolByName(context, 'portal_catalog')
    pass
    
def setupMetadataSet(context):
    from Products.Formulator import StandardFields
    
    mtool = getToolByName(context, 'portal_metadata')
    collection = mtool.getCollection()
    collection.addMetadataSet(SET_ID,
                              'tmd',
                              'http://www.example.com/xml/test_md')

    set = collection.getMetadataSet(SET_ID)


    set.addMetadataElement('Title',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1
                           )


    set.addMetadataElement('Description',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1
                           )

    element = set.getElement('Description')
    element.field._edit({'required':0})
    element.editElementPolicy(acquire_p = 1)
    
    return set

def setupMetadataMapping(context):

    mtool = getToolByName(context, 'portal_metadata')
    mapping = mtool.getTypeMapping()
    mapping.setDefaultChain('ut_md')

class MetadataTests( SecurityTest ): 

    def setUp( self ):
        SecurityTest.setUp(self)
        
        setupTools(self.root)
        setupCatalog(self.root)        
        setupContentTypes(self.root)
        setupMetadataSet(self.root)
        setupMetadataMapping(self.root)
        setupContentTree(self.root)
                           
class TestSetImportExport( MetadataTests ):

    def testImportExport(self):

        from cStringIO import StringIO
        
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        xml = set.exportXML()
        xmlio = StringIO(xml)
        
        collection.manage_delObjects([SET_ID])
        collection.importSet(xmlio)

        set = collection.getMetadataSet(SET_ID)
        xml2 = set.exportXML()

        assert xml == xml2, "Import/Export disjoint"

class TestMetadataElement( MetadataTests ):

    def testGetDefault(self):
        from Products.Formulator.TALESField import TALESMethod
        
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)

        element = set.getElement('Title')
        element.field._edit_tales( {'default':
                                    TALESMethod('content/getPhysicalPath') } )

        zoo = self.root.zoo
        
        binding = pm.getMetadata(zoo)
        defaults = set.getDefaults(content = zoo)

        self.assertEqual( defaults['Title'],
                          zoo.getPhysicalPath(),
                          "Tales Context Passing Failed" )

    def testAcquisitionInvariant(self):
        from Products.SilvaMetadata.Exceptions import ConfigurationError

        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)        
        element = set.getElement('Description')
        
        try:
            element.field._edit( {'required':1} )
            element.editElementPolicy(acquire_p = 1)
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition / Required Element Invariant Failed")

        try:
            element.field._edit( {'required':0})
            element.editElementPolicy(acquire_p = 1)
            #import pdb; pdb.set_trace()
            element.field._edit( {'required':1})
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition / Required Element Invariant Failed 2")
        
        
class TestAdvancedMetadata( MetadataTests ):
    """ tests for runtime binding methods """
    
    def setupAcquiredMetadata(self):
        zoo = self.root.zoo
        binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)
        set_id = SET_ID
        binding.setValues(
            set_id,
            {'Title':'hello world',
             'Description':'cruel place'}
            )
        
    def testContainmentAcquisitionValue(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mammals = zoo.mammals

        z_binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)
        m_binding = getToolByName(mammals, 'portal_metadata').getMetadata(mammals)
        
        set_id = SET_ID

        assert m_binding[set_id]['Description'] == z_binding[set_id]['Description']
        assert m_binding.get(set_id, 'Description', acquire=0) != \
               z_binding[set_id]['Description']

        
    def testContainmentAcquisitionList(self):
        self.setupAcquiredMetadata()

        zoo = self.root.zoo
        mammals = zoo.mammals

        m_binding = getToolByName(mammals, 'portal_metadata').getMetadata(mammals)
        z_binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)

        set_id = SET_ID

        acquired = m_binding.listAcquired()

        # test the contained's list acquired
        self.assertEqual(len(acquired), 1)
        self.assertEqual(acquired[0][1], 'Description')

        # test the container's listacquired
        acquired = z_binding.listAcquired()
        self.assertEqual( len(acquired), 0)

        # special case for 
        z_binding.setValues(set_id, {'Title':'', 'Description':''} )
        acquired = z_binding.listAcquired()
        self.assertEqual( len(acquired), 0)
        
        
        
    def testObjectDelegation(self):

        from Acquisition import Implicit
        
        class Delegator(Implicit):

            def __init__(self, name):
                self.name = name

            def __call__(self):
                ob = self.aq_inner.aq_parent
                return getattr(ob, self.name)

        zoo = self.root.zoo
        delegate = Delegator('reptiles')
        zoo.delegate = delegate

        mammals = zoo.mammals
        reptiles = zoo.reptiles

        r_binding = getToolByName(reptiles, 'portal_metadata').getMetadata(reptiles)
        m_binding = getToolByName(mammals, 'portal_metadata').getMetadata(mammals)

        r_binding.setValues(SET_ID,
                            {'Title':'snake food', 'Description':'yummy n the tummy'}
                            )
        
        m_binding.setObjectDelegator('delegate')
        
        self.assertEqual(
            m_binding[SET_ID]['Title'],
            r_binding[SET_ID]['Title']
            )

        m_binding.clearObjectDelegator()
        assert m_binding[SET_ID]['Title'] != r_binding[SET_ID]['Title']
        

    def testMutationTriggerDelegation(self):


        class MutationTrigger:

            def __init__(self):
                self.called = 0

            def __call__(self):
                self.called += 1

        zoo = self.root.zoo
        mammals = zoo.mammals

        m_binding = getToolByName(mammals, 'portal_metadata').getMetadata(mammals)

        trigger = MutationTrigger()
        zoo.trigger = trigger

        m_binding.setMutationTrigger(SET_ID, 'Title', 'trigger')

        m_binding.setValues(SET_ID, {'Title':'surfin betty',
                                     'Description':'morning pizza'} )
        
        self.assertEqual(trigger.called, 1)

        m_binding.setValues(SET_ID, {'Description':'midnight raid'} )
        self.assertEqual(trigger.called, 1)

        m_binding.clearMutationTrigger(SET_ID)

        # props to tennyson
        m_binding.setValues(SET_ID,
                            {'Title':'To strive, to seek, to find, and not to yield'}
                            )
        self.assertEqual(trigger.called, 1)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TestAdvancedMetadata ) )
    suite.addTest( unittest.makeSuite( TestSetImportExport ) )    
    



if __name__ == '__main__':
    main()
    
