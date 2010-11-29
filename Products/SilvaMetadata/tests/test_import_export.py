from unittest import TestSuite, makeSuite
from cStringIO import StringIO

from zope.component import getUtility

from Products.Formulator import StandardFields
from Products.Formulator.TALESField import TALESMethod
from Products.SilvaMetadata.interfaces import IMetadataService

from test_metadata import MetadataTestCase


SET_ID = 'ut_md'


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


class TestSetImportExport(MetadataTestCase):

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


class TestObjectImportExport(MetadataTestCase):

    def testImportExport(self):
        from Products.ParsedXML.ParsedXML import createDOMDocument
        from Products.SilvaMetadata.Import import import_metadata

        pm = getUtility(IMetadataService)
        setupExtendedMetadataSet(self.root)
        zoo = self.root.zoo
        mammals = zoo.mammals
        binding = pm.getMetadata(zoo)
        values = binding.get(SET_ID)
        lines = """
        english
        hebrew
        swahili
        urdu
        """
        values.update(
            {'Title':'hello world',
             'Description':'cruel place',
             'Languages':lines }
            )
        binding.setValues(SET_ID, values)
        xml = "<folder>%s</folder>" % binding.renderXML(SET_ID)
        dom = createDOMDocument(xml)
        import_metadata(mammals, dom.childNodes[0])
        mammals_binding = pm.getMetadata(mammals)
        mammal_values = binding.get(SET_ID)
        for k in values.keys():
            self.assertEqual(values[k], mammal_values[k],
                             "Object Import/Export disjoint")

        xml2 = "<folder>%s</folder>" % mammals_binding.renderXML(SET_ID)
        xml_list = xml.splitlines()
        xml2_list = xml2.splitlines()
        for x in xml2_list:
            self.assert_(x in xml_list, "Object Import Export disjoin")
        for x in xml_list:
            self.assert_(x in xml2_list, "Object Import Export disjoin")


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetImportExport))
    suite.addTest(makeSuite(TestObjectImportExport))
    return suite


