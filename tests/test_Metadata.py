from unittest import TestCase, TestSuite, makeSuite, main
import Zope

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

class PortalMetadataTests( SecurityTest ):

    def setUp( self ):
        SecurityTest.setUp(self)

        self.root._setObject('portal_types', TypesTool())
        self.root._setObject('portal_annotations', AnnotationTool())
        self.root._setObject('portal_metadata', MetadataTool())
        self.root._setObject('portal_catalog', CatalogTool())
        
        types_tool = self.root.portal_types
        
        types_tool._setObject( 'Folder'
                             , FTI( id='Folder'
                                  , title='Folder or Directory'
                                  , meta_type=PortalFolder.meta_type
                                  , product='CMFCore'
                                  , factory='manage_addPortalFolder'
                                  , filter_content_types=0
                                  )
                             )
        types_tool._setObject( 'Dummy Content', DummyFTI )


    def testAddEditMetadataSet(self):
        # collection test
        pm = self.root.portal_metadata
        pm.collection.addMetadataSet('test_md',
                                     'tmd',
                                     'http://www.example.com/xml/test_md')

        ms = pm.getMetadataSet('test_md')
        assert ms.namespace_prefix == 'tmd'
        assert ms.namespace_uri == 'http://www.example.com/xml/test_md'

        
    def testEditMetadataSet(self):
        pass
        
