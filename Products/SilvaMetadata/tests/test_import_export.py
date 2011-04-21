
import unittest
from cStringIO import StringIO

from zope.component import getUtility

from Products.Formulator import StandardFields
from Products.Formulator.TALESField import TALESMethod
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaMetadata.tests import SET_ID, setUp
from Products.Silva.testing import FunctionalLayer


def setupExtendedMetadataSet(context):
    # add some additional metadata fields
    pm = getUtility(IMetadataService)
    collection = pm.getCollection()
    set = collection.getMetadataSet(SET_ID)
    set.addMetadataElement('ModificationDate',
                           StandardFields.DateTimeField.meta_type,
                           'DateIndex',
                           1)
    element = set.getElement('ModificationDate')
    element.field._edit_tales({'default':
                        TALESMethod('content/bobobase_modification_time')})
    element.field._edit({'required':0})
    set.addMetadataElement('Languages',
                           StandardFields.LinesField.meta_type,
                           'KeywordIndex',)
    element = set.getElement('Languages')
    element.field._edit({'required':0})
    ######
    set.initialize()


class TestSetImportExport(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        setUp(self.root)

    def testImportExport(self):
        pm = getUtility(IMetadataService)
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        xml = set.exportXML().encode('ascii')
        xmlio = StringIO(xml)
        collection.manage_delObjects([SET_ID])
        collection.importSet(xmlio)
        set = collection.getMetadataSet(SET_ID)
        xml2 = set.exportXML()
        assert xml == xml2, "Import/Export disjoint"



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetImportExport))
    return suite


