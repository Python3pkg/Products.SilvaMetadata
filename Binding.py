"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import types, copy

from Acquisition import Implicit, aq_base
from zExceptions import Unauthorized
from Exceptinos import NotFound
import Initialize as BindingInitialize
from Namespace import MetadataNamespace, BindingRunTime
import View 
from ZopeImports import Interface, ClassSecurityInfo, InitializeClass
from utils import make_lookup

#################################
### runtime bind data keys
AcquireRuntime = 'acquire_runtime'
ObjectDelegate = 'object_delegate'
MutationTrigger = 'mutation_trigger'

#################################
### Acquired Metadata Prefix Encoding 
MetadataAqPrefix = 'metadataAq'
MetadataAqVarPrefix = '_VarName_'

_marker = []

class MetadataBindAdapter(Implicit):

    security = ClassSecurityInfo()

    def __init__(self, content, collection):
        self.content = content

        if isinstance(collection, types.ListType):
            d = {}
            for s in collection:
                d[s.getId()]=s
            collection = d
            
        assert isinstance(collection, types.DictType)
        
        self.collection = collection
        self.cached_values = {}

    #################################
    ### Views
    def renderForm(self, set_id=None, namespace_key=None, REQUEST=None, messages=None):
        """
        return a rendered form.

        if set_id or namespace_key is specified the form will be returned
        only for the specified metadata set. otherwise the returned form
        will be for all metadata defined on the content object.

        if request is specified it will be used for the values of the
        metadata in the form. this is to allow for 'sticky' forms.

        messages unimplemented.. error messages on fields

        acquired metadata is not displayed in forms.. the fields for
        acquired metadata will be presented empty.
        """
        
        set = self._getSet(set_id, namespace_key)

        if not set is None:
            return View.getForm(self, set, REQUEST=REQUEST)

        res = []

        for set in self.collection.values():
            res.append(View.getForm(self, set, REQUEST=REQUEST))
            
        return '<br />\n<br />\n'.join(res)

    def renderView(self, set_id=None, namespace_key=None):
        """
        render a view of a given metadata set corresponding
        to set_id or namespace_key.
        """
        set = self._getSet(set_id, namespace_key)

        if not set is None:
            return View.getView(self, set)

        res = []

        for set in self.collection.values():
            res.append(View.getView(self, set))

        return '<br />\n<br />\n'.join(res)

    def renderXML(self, set_id=None, namespace_key=None):
        """
        return an xml serialization of the object's metadata
        """

        if set_id or namespace_key:
            sets = [self._getSet(set_id, namespace_key)]
        else:
            sets = self.collection.values()

        exporter = ObjectMetadataExporter(self, sets)
        return exporter()
            

    #################################
    ### Validation

    def validate(self, data, errors=None, set_id=None, namespace_key=None):
        """
        validate the data. implicit transforms may be preformed.
        """
        if set_id:
            return validateData(self, data, self.collection[set_id])
        if namespace_key:
            return validateData(self, data, self._getSetByKey(namespace_key))

        res = []
        for set in self.collection.values():
            res.append( validateData(self, data, set, errors) )
        return res

    def validateFromRequest(self, REQUEST, errors=None, set_id=None, namespace_key=None):
        """
        validate from request
        """
        assert set_id or namespace_key
        if set_id:
            data = REQUEST.form.get(set_id)
        elif namespace_key:
            data = REQUEST.form.get(
                self._getSetByKey(namespace_key).getId()
                )

        if data is None:
            raise NotFound("Metadata for %s/%s not found"%(
                str(set_id),
                str(namespace_key)
                )
                )
        return self.validate(data, errors, set_id, namespace_key)

    #################################
    ### Storage (invokes validation)

    def setValues(self, data, set_id=None, namespace_key=None):
        """
        returns a dictionary of errors if any, or none otherwise
        """
        
        errors = {}
        data = self.validate(data, errors, set_id, namespace_key)
        
        if errors:
            return errors

        set = self._getSet(set_id, namespace_key)
        self._setData(data, set_id=set_id)
    
    def setValuesFromRequest(self, REQUEST, set_id=None, namespace_key=None): 
        """
        returns a dictionary of errors if any, or none otherwise
        """

        set = self._getSet(set_id, namespace_key)
        # some issues with classifying the errors by namespace
        data = REQUEST.form.get(set.getId())
        return self.setValues(data, set_id=set.getId())

    #################################
    ### Discovery Introspection
    def getSetNames(self):
        """
        return the ids of the metadata sets available for this content
        type.
        """
        names = self.collection.keys()
        names.sort()
        return names

    keys = getSetNames

    def getElementNames(self, set_id=None, namespace_key=None):
        """
        given a set identifier return the ids of the elements
        within the set.
        """
        # XXX
        # this returns all elements of a set.
        # not all elements visible here will be viewable
        # for editing or viewing.
        set = self._getSet(set_id, namespace_key)
        return [e.getId() for e in set.getElements()]

    #################################
    ### Accessor Interface
    def __getitem__(self, key):
        if key in self.collection.keys():
            return self._getData(key)
        raise KeyError(str(key))

    #################################
    ### RunTime Binding Methods

    def setAcquire(self, set_id, element_id, flag):
        """
        set a flag for runtime acquisition of metadata
        for all objects *below* this one, such that
        if they don't define their own values for the
        metadata element, it will be acquired from
        the nearest container which has this flag
        set on the element. IE this method is called
        on containers when you want contained content
        to acquire metadata.
        """

        set = self._getSet(set_id)
        flag = not not flag
        token = (set_id, element_id)        
        attr_name = encodeElement(set_id, element_id)
        bind_data = self._getBindData()
        acquire_runtime = bind_data.get(AcquireRuntime)
        
        if acquire_runtime is None:
            acquire_runtime = []
        
        if flag:
            # add a cache lookup value.. see encode el doc string
            data = self._getData(set_id)
            setattr(self.content, attr_name, data[element_id])
            if not token in acquire_runtime:
                acquire_runtime.append(token)
            bind_data[AcquireRuntime] = acquire_runtime
            
        else:
            # get rid of the acq lookup value
            if hasattr(aq_base(self.content), attr_name):
                delattr(self.content, attr_name)

            # get rid of it from the bind data
            if token in acquire_runtime:
                acquire_runtime.remove(token)
        
    def listAcquired(self):
        """
        compute and return a list of (set_id, element_id)
        values for all metadata which this binding/content
        acquires from the containment hiearchy.
        """
        res = []
        for s in self.collection.values():
            sid = s.getId()
            data = self._getData(set_id = sid)
            for e in set.getElements():
                eid = e.getId()
                if data.has_key(eid) and data[eid]:
                    continue
                name = encodeElement(sid, e.getId())
                try:
                    value = getattr(self.content, name)
                except:
                    continue
                res.append( (sid, eid) )
                
        return res

    def setObjectDelegator(self, method_name):
        """
        we get and set all metadata on a delegated object,
        method should be a callable method on the object
        (acquiring the method is ok) that should take zero
        args, and return an object. if it doesn't return
        an object, we return the default metadata values
        associated (not a good idea).
        """
        assert getattr(self.content, method_name), "invalid object delegate %s"%method_name
        
        bind_data = self._getBindData()
        bind_data[ObjectDelegate]=method_name

    def getObjectDelegator(self):
        return self._getBindData()[ObjectDelegate]

    def setMutationTrigger(self, set_id, element_id, method_name):
        """
        support for simple events, based on path expression
        invocation. major use case.. cache invalidation on
        metadata setting.
        """
        assert getattr(self.content, method_name), "invalid mutation trigger %s"%method_name        

        bind_data = self._getBindData()
        bind_data[MutationTrigger].set_default(set_id, {})[element_id]=method_name

    #################################
    ### Private

    def _getSet(self, set_id=None, namespace_key=None):
        if set_id:
            return self.collection[set_id]
        elif namespace_key:
            return self.getSetByKey(namespace_key)
        else:
            raise NotFound("metadata set not found %s %s"%(set_id, namespace_key)

    def _getBindData(self):
        annotations = getToolByName(self.content, 'portal_annotations')
        metadata    = annotations.getAnnotations(self.content, MetadataNamespace)
        bind_data   = metadata.get(BindingRunTime)

        if bind_data is None:
            init_handler = BindingInitialize.getHandler(content)
            bind_data = metadata.setdefault(BindingRunTime, PersistentMapping())
            if init_handler is not None:
                init_handler(bind_data)

        return bind_data

    def _getMutationTriggers(self, set_id):
        bind_data = self._getBindData()
        return bind_data.get(MutationTrigger, {})
    
    def _getAnnotatableObject(self):
        # check for object delegation
        bind_data = self._getBindData()        
        object_delegate = bind_data.get(ObjectDelegate)
        
        if object_delegate is not None:
            od = getattr(self.content, object_delegate)
            ob = od()
        else:
            ob = self.content        

    def _getData(self, set_id=None, namespace_key=None, acquire=1):
        """
        find the metadata for the given content object,
        performs runtime binding work as well.
        """
        set = self._getSet(set_id, namespace_key)
        
        # cache lookup
        data = self.cached_values.get(set.getId())
        if data is not None:
            return data

        ob = self._getAnnotatableObject()

        # get the annotation data
        annotations = getToolByName(ob, 'portal_annotations')
        metadata = annotations.getAnnotations(ob, MetadataNamespace)
        data = metadata.get(set.metadata_uri)

        if data is None:
            data = set.getDefaults()
        else:
            # make a copy so we can modify with acq metadata
            data = copy.deepcopy(data)
            
        self.cached_values[set_id]=data

        if not acquire:
            return data

        # get the acquired metadata
        sid = set.getId()        
        hk = data.has_key
        for e in set.getElements():
            eid = e.getId()
            if hk(eid):
                continue
            aqelname = encodeElement(sid, eid)
            try:
                val = getattr(self.content, aqelname)
            except AttributeError:
                continue
            data[eid]=val

        return data

    def _setData(self, data, set_id=None, namespace_key=None):
        # no checking of acquired values, a save operation
        # saves all values passed in.
        set = self._getSet(set_id, namespace_key)

        # check for delegates
        ob = self._getAnnotatableObject()

        # filter based on write guard and wheter field is readonly
        eids = [e.getId() for e in set.getElementsFor(ob, mode='edit')]
        
        #todo, convert this to a hash lookup maybe..
        #valid_key = make_lookup(eids)
        keys = data.keys()
        for k in keys:
            if k not in eids:
                raise Unauthorized('Not Allowed to Edit %s in this context'%k)
            
        triggers = self._getMutationTriggers(set.getId())
        for k in keys:
            if triggers.has_key(k):
                try:
                    getattr(triggers[k])()
                except: # gulp
                    pass
                
        annotations = getToolByName(ob, 'portal_annotations')
        metadata = annotations.getAnnotations(ob, MetadataNamespace)
        metadata[set.metadata_uri].update(data)
    
    def _getSetByKey(self, namespace_key):
        for s in self.collection:
            if s.metadata_uri == namespace_key:
                return s
        raise NotFound(str(namespace_key))

InitializeClass(MetadataBindAdapter)

def validateData(binding, set, data, errors_dict=None):
    # XXX formulator specific
    from Products.Formulator.Errors import ValidationError
    for e in set.getElements():
        try:
            data[e.getId()] = e.validate(data)
        except ValidationError, exception:
            if errors_dict:
                errors_dict[e.getId()]=exception.error_text
            else:
                raise
    return data

def encodeVariable(set, element):
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
    return MetadataAqPrefix+set.getId() + MetadataAqVarPrefix + element.getId()

def decodeVariable(name):
    """ decode an encode variable name... not used """
    assert name.startswith(MetadataAqPrefix)

    set_id = name[len(MetadataAqPrefix):name.find(MetadataAqVarPrefix)]
    e_id = name[name.find(MetadataAqVarPrefix)+len(MetadataAqVarPrefix):]

    return set_id, e_id
    
    
