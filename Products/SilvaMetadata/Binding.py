"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
# Python
from UserDict import UserDict

# Zope
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from ZODB.PersistentMapping import PersistentMapping
from OFS.interfaces import IZopeObject

from five import grok
from zope.annotation.interfaces import IAnnotations
from zope.event import notify

# Formulator
from Products.Formulator.Errors import ValidationError

from Products.SilvaMetadata.Exceptions import NotFound, ReadOnlyError
from Products.SilvaMetadata.Export import ObjectMetadataExporter
from Products.SilvaMetadata.interfaces import MetadataModifiedEvent
from Products.SilvaMetadata.interfaces import IMetadataBindingFactory

from silva.core.services.interfaces import ICataloging


#################################
### Acquired Metadata Prefix Encoding
MetadataAqPrefix = 'metadataAq'
MetadataAqVarPrefix = '_VarName_'

_marker = []


class DefaultMetadataBindingFactory(grok.Adapter):
    grok.context(IZopeObject)
    grok.implements(IMetadataBindingFactory)
    grok.provides(IMetadataBindingFactory)
    read_only = False

    def get_content(self):
        return self.context

    def __call__(self, service):
        content = self.get_content()
        if content is None:
            return None

        sets = []
        mapping = service.getTypeMapping()
        for set_name in mapping.iterChainFor(content.meta_type):
            try:
                sets.append(service.getMetadataSet(set_name))
            except AttributeError:
                pass
        if not sets:
            return None

        binding = MetadataBindAdapter(service, content, sets, self.read_only)
        binding.__parent__ = content
        return binding


class Data(UserDict):
    """
    We use this as to escape some vagaries with the zope security policy
    when using the __getitem__ interface of the binding
    """
    __roles__ = None
    __allow_access_to_unprotected_subobjects__ = 1


class MetadataBindAdapter(object):
    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, service, content, sets, read_only=False):
        self.service = service
        self.content = content
        self.collection = {}
        self.setnames = []
        self.category_to_setnames = {}
        self.cached_values = {}
        self.read_only = read_only

        for set in sets:
            set_id = set.getId()
            self.setnames.append(set_id)
            self.collection[set_id] = set
            category = set.getCategory()
            setnames = self.category_to_setnames.setdefault(category, [])
            setnames.append(set_id)

    #################################
    ### Views
    security.declarePublic('renderXML')
    def renderXML(self, set_id=None):
        """
        return an xml serialization of the object's metadata
        """

        if set_id:
            sets = [self.getSet(set_id)]
        else:
            sets = self.collection.values()

        exporter = ObjectMetadataExporter(self, sets)
        return exporter()

    security.declarePublic('renderElementView')
    def renderElementView(self, set_id, element_id):
        element = self.getElement(set_id, element_id)
        data = self._getData(set_id)
        value = data.get(element_id, None)
        return element.renderView(value)

    security.declarePublic('renderElementEdit')
    def renderElementEdit(self, set_id, element_id, REQUEST=None):
        element = self.getElement(set_id, element_id)
        if REQUEST:
            #here we want to render the value from the request
            #(i.e. a save didn't pass validation and the form
            #needs to be preloaded with the previously supplied values)
            #so the value for this element comes from the REQUEST
            value = REQUEST.get(set_id).get(element_id)
        else:
            #if request is false, then we want to render the default/saved
            # value
            value = self._getData(set_id, acquire=0).get(element_id,None)
        return element.renderEdit(value)

    #################################
    ### Storage (invokes validation)

    security.declarePublic('setValues')
    def setValues(self, set_id, data, reindex=0):
        """Data should be a mutable dictionary.

        Return True if modifications are made, false otherwise.
        """
        if self.read_only:
            raise ReadOnlyError()

        set = self.getSet(set_id)
        errors = {}
        values = []
        for element in set.getElementsFor(self.content, mode='write'):
            element_id = element.getId()
            if element_id not in data:
                continue
            try:
                value = element.validate(data[element_id])
            except ValidationError as error:
                errors[element_id] = error.error_text
            else:
                values.append((element_id, element, value))
        if errors:
            return errors

        self._store(values, set, set_id, reindex=reindex)
        return {}

    security.declarePublic('setValuesFromRequest')
    def setValuesFromRequest(self, request, reindex=0):
        """Returns a dictionary of errors if any
        """
        if self.read_only:
            raise ReadOnlyError()

        all_errors = {}
        for set_id in self.getSetNames():
            if set_id not in request.form:
                continue
            data = request.form[set_id]
            set = self.getSet(set_id)
            errors = {}
            values = []
            for element in set.getElementsFor(self.content, mode='edit'):
                element_id = element.getId()
                if element_id not in data:
                    continue
                try:
                    value = element.extract(data)
                except ValidationError as error:
                    errors[element_id] = error.error_text
                else:
                    values.append((element_id, element, value))
            if errors:
                all_errors[set_id] = errors
            else:
                self._store(values, set, set_id, reindex=reindex)
        return all_errors

    def _store(self, values, set, set_id, reindex=0):
        if not values:
            return False

        # Update acquirable values
        for element_id, element, value in values:
            if element.isAcquireable():
                attr_name = encodeElement(set_id, element_id)
                if not (value == '' or value is None):
                    setattr(self.content, attr_name, value)
                else:
                    # Try and get rid of encoded attribute on the
                    # annotatable object; this will get acquisition
                    # of the value working again.
                    try:
                        delattr(self.content, attr_name)
                    except (KeyError, AttributeError):
                        pass

        # Save values in Annotations
        annotations = IAnnotations(aq_base(self.content))
        if set.metadata_uri not in annotations:
            annotations[set.metadata_uri] = PersistentMapping({})
        storage = annotations[set.metadata_uri]

        data = {}
        for element_id, element, value in values:
            if not (value == '' or value is None):
                storage[element_id] = value
            elif element_id in storage:
                del storage[element_id]
            # For the event
            data[element_id] = value

        # invalidate the cache version of the set if any
        # we do a check for cached acquired/non-acquired
        if self.cached_values.has_key((0, set_id)):
            del self.cached_values[(0, set_id)]
        if self.cached_values.has_key((1, set_id)):
            del self.cached_values[(1, set_id)]

        # mark both the content and the annotatable object as changed so
        # on txn commit bindings in other objectspaces get invalidated as well
        self.content._p_changed = 1

        # reindex object
        if reindex and not getattr(self.content, '__initialization__', False):
            ICataloging(self.content).reindex()
        notify(MetadataModifiedEvent(self.content, data))
        return True


    #################################
    ### Discovery Introspection // Definition Accessor Interface

    security.declarePublic('getSetNames')
    def getSetNames(self, category=None):
        """Return the ids of the metadata sets available for this
        content type.
        """
        if category is None:
            return tuple(self.setnames)
        setnames = self.category_to_setnames.get(category, [])
        return tuple(setnames)

    security.declarePublic('keys')
    keys = getSetNames

    security.declarePublic('getElementNames')
    def getElementNames(self, set_id, mode=None):
        """Given a set identifier return the ids of the elements
        within the set.
        """
        set = self.getSet(set_id)
        if mode is not None:
            elements = set.getElementsFor(self.content, mode=mode)
        else:
            elements = set.getElements()

        return [e.getId() for e in elements]

    security.declarePublic('getSetNameByURI')
    def getSetNameByURI(self, uri):
        for set in self.collection.values():
            if set.metadata_uri == uri:
                return set.getId()
        raise NotFound(uri)

    security.declarePublic('getSet')
    def getSet(self, set_id):
        """To invoke methods on the set requires permissions on
        the set not the content, whereas binding methods
        merely require permissions on the content.
        """
        try:
            return self.collection[set_id]
        except KeyError:
            raise NotFound("Metadata set not found %s" % set_id)


    security.declarePublic('getElement')
    def getElement(self, set_id, element_id):
        return self.getSet(set_id).getElement(element_id)

    security.declarePublic('isViewable')
    def isViewable(self, set_id, element_id):
        """
        is the element viewable for the content object
        """
        element = self.getSet(set_id).getElement(element_id)
        return element.isViewable(self.content)

    security.declarePublic('isEditable')
    def isEditable(self, set_id, element_id):
        """
        is the element editable for the content object
        """
        if self.read_only:
            return False
        element = self.getSet(set_id).getElement(element_id)
        return element.isEditable(self.content)

    security.declarePublic('listAcquired')
    def listAcquired(self):
        """
        compute and return a list of (set_id, element_id)
        values for all metadata which this binding/content
        acquires from above in the containment hiearchy.
        """
        res = []

        for set in self.collection.values():
            set_id = set.getId()
            data = self._getData(set_id=set_id, acquire=0)
            for e in [e for e in set.getElements() if e.isAcquireable()]:
                eid = e.getId()
                if data.has_key(eid) and data[eid]:
                    continue
                name = encodeElement(set_id, e.getId())
                try:
                    getattr(self.content, name)
                except AttributeError:
                    continue
                # filter out any empty metadata fields
                # defined on ourselves to acquire
                if not hasattr(aq_base(self.content), name):
                    res.append((set_id, eid))

        return res

    #################################
    ### Data Accessor Interface

    security.declarePublic('get')
    def get(self, set_id, element_id=None, acquire=1, no_defaults=0):
        """
        if element_id is specified, only the value of that element is
        returned, otherwise a Data object is returned. Data objects
        implement a mapping interface.

        the acquire flag determines whether or not metadata acquisition
        will be used in retrieving values, acquired values will override
        default values but not values stored on the object.

        the no_defaults flag specifies whether an element's default values
        should be used. default values are only used when there is no
        value stored on the object.

        the use case for no_defaults is whe using tales defaults to defer
        an element's value to another element within the same set. also when
        no_defaults is used not all elements of the set will nesc. be
        in the data object returned only those which were findable.
        """
        data = self._getData(set_id=set_id,
                             acquire=acquire,
                             no_defaults=no_defaults)
        if element_id is not None:
            return data.get(element_id)
        return data

    def __getitem__(self, key):
        if self.collection.has_key(key):
            return self._getData(key)
        raise KeyError(str(key))

    #################################
    ### Private

    def _getData(self, set_id, acquire=1, no_defaults=0):
        """
        find the metadata for the given content object,
        performs runtime binding work as well.

        """
        set = self.getSet(set_id)

        # cache lookup
        data = self.cached_values.get((acquire, set_id))
        if data is not None:
            return data

        using_defaults = []

        # get the annotation data
        metadata = IAnnotations(aq_base(self.content))

        saved_data = metadata.get(set.metadata_uri)
        data = Data()

        element_ids = self.getElementNames(set_id)

        if saved_data is None and no_defaults:
            pass
        elif saved_data is None:
            # use the sets defaults
            defaultvalues = set.getDefaults(content=self.content)
            data.update(defaultvalues)
            # record which elements we used default values for
            using_defaults = element_ids
        else:
            # make a copy so we can modify with acq metadata
            data.update(saved_data)

            if not no_defaults:
                # update individual elements with default values
                # if they don't have a saved value.
                for element_id in element_ids:
                    if data.has_key(element_id):
                        continue
                    defaultvalue = set.getElement(
                        element_id).getDefault(content=self.content)
                    data[element_id] = defaultvalue
                    using_defaults.append(element_id)

        # cache metadata
        self.cached_values[(acquire, set_id)] = data

        if not acquire:
            return data

        # get the acquired metadata
        hk = data.has_key
        for e in [e for e in set.getElements() if e.isAcquireable()]:
            eid = e.getId()
            if hk(eid) and data[eid] and not eid in using_defaults:
                continue
            aqelname = encodeElement(set_id, eid)
            try:
                val = getattr(self.content, aqelname)
            except AttributeError:
                continue
            data[eid]=val

        return data


InitializeClass(MetadataBindAdapter)


def encodeElement(set_id, element_id):
    """
    after experimenting with various mechanisms for doing
    containment based metadata acquisition, using extension class
    acquisition was found to be the quickest way to do the containment
    lookup. as attributes are stored as opaque objects, the current
    implementation decorates the object heirarchy with encoded variables
    corresponding to the metadata specified as acquired. the encoding
    is used to minimize namespace pollution. acquired metadata is only
    specified in this manner on the source object.
    """
    return MetadataAqPrefix + set_id + MetadataAqVarPrefix + element_id

def decodeVariable(name):
    """ decode an encoded variable name... not used """
    assert name.startswith(MetadataAqPrefix)

    set_id = name[len(MetadataAqPrefix):name.find(MetadataAqVarPrefix)]
    e_id = name[name.find(MetadataAqVarPrefix)+len(MetadataAqVarPrefix):]

    return set_id, e_id

