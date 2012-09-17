"""
Metadata Elements
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from AccessControl import ClassSecurityInfo, Permissions
from AccessControl import getSecurityManager
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from OFS.SimpleItem import SimpleItem

from zope.interface import implements

from Products.SilvaMetadata.Exceptions import ConfigurationError
from Products.SilvaMetadata.FormulatorField import getFieldFactory
from Products.SilvaMetadata.Guard import Guard
from Products.SilvaMetadata.interfaces import IMetadataElement
from Products.SilvaMetadata.utils import normalize_kv_pairs

_marker = []

encoding = 'UTF-8'


class MetadataElement(SimpleItem):
    """
    Property Bag For Element Policies, this implementation is
    formulator specific
    """

    meta_type = 'Metadata Element'

    implements(IMetadataElement)

    #################################
    # default element policy properties
    #################################

    read_only_p = False
    index_p = False
    metadata_in_catalog_p = False
    acquire_p = False
    automatic_p = False
    index_type = None
    field_type = None
    field = None

    manage_options = (
        {'label':'Settings',
         'action':'manage_settings'},

        {'label':'Guards',
         'action':'manage_guard_form'},

        {'label':'Field',
         'action':'field/manage_main'},
        )

    security = ClassSecurityInfo()

    security.declareProtected(
        Permissions.view_management_screens, 'manage_settings')
    manage_settings = DTMLFile('ui/ElementPolicyForm', globals())

    security.declareProtected(
        Permissions.view_management_screens, 'manage_guard_form')
    manage_guard_form = DTMLFile('ui/ElementGuardForm', globals())


    def __init__(self, id, **kw):
        self.id = id
        self.read_guard = Guard()
        self.write_guard = Guard()
        self.index_constructor_args = {}

        self.editElementPolicy(**kw)

    security.declareProtected(
        Permissions.view_management_screens, 'editElementGuards')
    def editElementGuards(self, read_guard, write_guard, RESPONSE=None):
        """save element guards"""
        self.read_guard.changeFromProperties(read_guard)
        self.write_guard.changeFromProperties(write_guard)

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(
        Permissions.view_management_screens, 'editElementPolicy')
    def editElementPolicy(self,
                          field_type = None,
                          index_type = None,
                          index_p = None,
                          metadata_in_catalog_p = None,
                          read_only_p = None,
                          extra = None,
                          acquire_p = None,
                          automatic_p = None,
                          RESPONSE = None
                          ):
        """
        edit an element's policy
        """
        if index_type is not None:
            ms = self.getMetadataSet()
            if ms.isInitialized():
                raise ConfigurationError("Not Allowed Set Already initialized")

        if field_type is not None:
            ms = self.getMetadataSet()
            if ms.isInitialized():
                raise ConfigurationError("Not Allowed Set Already initialized")

        f = self.field
        if acquire_p is not None and f is not None:
            required_p = f.has_value('required') and f.get_value('required')
            if required_p and acquire_p:
                raise ConfigurationError("Required Values may not be Acquired")

        field_type = field_type or self.field_type
        index_type = index_type or self.index_type

        if index_p is None:
            index_p = self.index_p

        if read_only_p is None:
            read_only_p = self.read_only_p

        if acquire_p is None:
            acquire_p = self.acquire_p

        if field_type != self.field_type:
            try:
                factory = getFieldFactory(field_type)
            except KeyError:
                raise ConfigurationError("invalid field type %s" % field_type)
            self.field = factory(self.getId())
            self.field.field_record = self.getMetadataSet().getId()
            self.field_type = field_type
            self.field.values['unicode']=1

        if index_type is not None:
            if index_type in self.getMetadataSet().listIndexTypes():
                self.index_type = index_type
            else:
                raise ConfigurationError("invalid index type %s" % index_type)

        # need to cascacde this so we can create indexes at the set level
        self.index_p = not not index_p
        self.metadata_in_catalog_p = not not metadata_in_catalog_p
        self.automatic_p = not not automatic_p
        self.read_only_p = not not read_only_p
        self.acquire_p = not not acquire_p

        # normalize the key value pairs into a mapping[k]->v
        if extra:
            constructor_args = normalize_kv_pairs(extra)
            self.index_constructor_args.update(constructor_args)

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_workspace')

    def Title(self):
        return self.field.get_value('title')

    def Description(self):
        return self.field.get_value('description')

    def isViewable(self, content):
        """
        is this element viewable for the content object
        """
        return self.read_guard.check(getSecurityManager(), self, content)

    def isEditable(self, content):
        """
        is this element editable for the content object
        """
        if not self.read_only_p and not self.automatic_p:
            return self.write_guard.check(getSecurityManager(), self, content)
        return False

    def isAcquireable(self):
        """
        is this field acquireable to objects lower in the container
        """
        return self.acquire_p

    def extract(self, content, request):
        field = self.field.__of__(content)
        return field.validate(request)

    def validate(self, content, data):
        field = self.field.__of__(content)
        return field.validator.check(field, data)

    def renderView(self, content, value=None):
        """
        render the element given a particular element value
        """
        field = self.field.__of__(content)
        return field.render_view(value)

    def renderEdit(self, content, value=None):
        """
        render the element as a form field given a particular value
        """
        field = self.field.__of__(content)
        return field.render(value)

    def isRequired(self):
        """
        is the element required to have a value
        """
        return self.field.is_required()

    def getDefault(self, content):
        """
        return the default value for this element
        """
        return self.field.get_value('default', content=content)

    def getVocabulary(self, content):
        """
        return the set of allowed of words
        """
        raise NotImplemented

    ## little hack to get formulator fields to do unicode
    def get_form_encoding(self):
        return encoding

    # fields are not in unicode mode, unfortunately
    def get_unicode_mode(self):
        return 0

    ## formulator sends on change messages when internal field
    ## values are changed, we catch the required message in
    ## order to maintain our invariant that an element can not
    ## be both required and acquired.
    def on_value_required_changed(self, required_value):
        if required_value and self.acquire_p:
            raise ConfigurationError("Acquired values may not be Required")

InitializeClass(MetadataElement)

