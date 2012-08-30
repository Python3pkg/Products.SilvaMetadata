"""
Tests for the SilvaMetada.

$Id: test_Metadata.py,v 1.22 2005/09/14 23:10:16 clemens Exp $
"""

import unittest

from zope.component import getUtility

from Products.Formulator.TALESField import TALESMethod
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaMetadata.tests import SET_ID, setUp
from Products.Silva.testing import FunctionalLayer


class TestMetadataElement(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        setUp(self.root)

    def testGetDefault(self):
        pm = getUtility(IMetadataService)
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        element = set.getElement('Title')
        element.field._edit_tales({'default':
                                   TALESMethod('content/getPhysicalPath')})
        zoo = self.root.zoo
        binding = pm.getMetadata(zoo)
        defaults = set.getDefaults(content = zoo)
        self.assertEqual(defaults['Title'],
                         zoo.getPhysicalPath(),
                         "Tales Context Passing Failed")

    def testGetDefaultWithTalesDelegate(self):
        mtool = getUtility(IMetadataService)
        mtoolId = mtool.getId()
        collection = mtool.getCollection()
        set = collection.getMetadataSet(SET_ID)
        zoo = self.root.zoo
        test_value = 'Rabbits4Ever'
        binding = mtool.getMetadata(zoo)
        binding.setValues(SET_ID, {'Title':test_value})
        element = set.getElement('Description')
        # yikes, narly tales expression
        method = "python: content.%s.getMetadata(content).get(" \
                 "'%s', 'Title', no_defaults=1)" % (mtoolId, SET_ID)
        element.field._edit_tales({'default': TALESMethod(method)})
        value = binding.get(SET_ID, 'Description')
        self.assertEqual(value, test_value,
                         "Tales delegate for default didn't work")
        # make sure the right cached value was stored.
        value = binding.get(SET_ID, 'Description')
        self.assertEqual(value, test_value, "Wrong Data Object Cached")
        # test shortcut, too
        self.assertEqual(value,
                         mtool.getMetadataValue(zoo, SET_ID, 'Description'))

    def testAcquisitionInvariant(self):
        # invariant == can't be required and acquired
        from Products.SilvaMetadata.Exceptions import ConfigurationError
        pm = getUtility(IMetadataService)
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        element = set.getElement('Description')
        try:
            element.field._edit({'required':1})
            element.editElementPolicy(acquire_p = 1)
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition/Required Element" \
                                 " Invariant Failed")
        try:
            element.field._edit({'required':0})
            element.editElementPolicy(acquire_p = 1)
            element.field._edit({'required':1})
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition/Required Element" \
                                 " Invariant Failed 2")


class TestAdvancedMetadata(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        setUp(self.root)

    def setupAcquiredMetadata(self):
        zoo = self.root.zoo
        binding = getUtility(IMetadataService).getMetadata(zoo)
        set_id = SET_ID
        binding.setValues(set_id, {'Title':'hello world',
                                   'Description':'cruel place'})

    def testContainmentAcquisitionValue(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mams = zoo.mammals
        z_binding = getUtility(IMetadataService).getMetadata(zoo)
        m_binding = getUtility(IMetadataService).getMetadata(mams)
        set_id = SET_ID
        self.assertEqual(m_binding[set_id]['Description'],
                         z_binding[set_id]['Description'])
        # test shortcut, too
        self.assertEqual(getUtility(IMetadataService).getMetadataValue(mams,set_id,'Description'),
                         getUtility(IMetadataService).getMetadataValue(zoo,set_id,'Description'))
        self.assertNotEqual(m_binding.get(set_id, 'Description', acquire=0),
                            z_binding[set_id]['Description'])

    def testContainmentAcquisitionList(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mams = zoo.mammals
        m_binding = getUtility(IMetadataService).getMetadata(mams)
        z_binding = getUtility(IMetadataService).getMetadata(zoo)
        set_id = SET_ID
        acquired = m_binding.listAcquired()
        # test the contained's list acquired
        self.assertEqual(len(acquired), 1)
        self.assertEqual(acquired[0][1], 'Description')
        # test the container's listacquired
        acquired = z_binding.listAcquired()
        self.assertEqual(len(acquired), 0)
        # special case for
        z_binding.setValues(set_id, {'Title':'', 'Description':''})
        acquired = z_binding.listAcquired()
        self.assertEqual(len(acquired), 0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMetadataElement))
    suite.addTest(unittest.makeSuite(TestAdvancedMetadata))
    return suite


