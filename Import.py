"""
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from xml.sax import make_parser, ContentHandler
from UserDict import UserDict

_marker = []

class DefinitionNode(UserDict):
    reserved = ('data',)

    def __getattr__(self, name):

        v = self.__dict__.get(name, marker)
        if v is marker:
            return self.data[name]
        return v
    
    def __setattr__(self, name, value):
        if name in PolicyNode.reserved:
            self.__dict__[name]=value
        else:
            self.data[name]=value
            
class MetaReader(ContentHandler):

    def __init__(self):

        self.buf = []
        self.prefix = ''
        self.stack = []
        
    def startElement(self, element_name, attrs):
        name = element_name.lower()
        if self.prefix: name = '%s%s'%(self.prefix, name.capitalize())
        else: name = name.capitalize()
        method = getattr(self, 'start%s'%name, None)

        # get rid of unicode...
        d = {}
        for k, v in attrs.items():
            d[str(k)]= str(v)
        
        if method: 
            apply(method, (d,))

    def endElement(self, element_name):
        chars = str(''.join(self.buf)).strip()
        self.buf = []

        name = element_name.lower()
        
        if self.prefix: name = '%s%s'%(self.prefix, name.capitalize())            
        method = getattr(self, 'end%s'%name.capitalize(), None)
        
        if method: 
            apply(method, (chars,))
         
    def characters(self, chars):
        self.buf.append(chars)
        
class MetadataSetReader(MetaReader):
    
    def getSet(self):
        return self.set

    def startMetadata_set(self, attrs):
        self.set = s = DefinitionNode(attrs)
        s.setdefault('elements', [])
        
    def startElement(self, attrs):
        element = DefinitionNode(attrs)
        self.set.elements.append(element)

    def getElement(self):
        return self.set.elements[-1]
    
    def endIndextype(self, chars):
        self.getElement().index_type = chars

    def endIndex_p(self, chars):
        self.getElement().index_p = chars

    def endField_type(self, chars):
        self.getElement().field_type = chars

    def startRead_guard(self, attrs):
        self.prefix = 'Read'
        self.getElement().read_guard = DefinitionNode()
        
    def endReadRead_guard(self, chars):
        self.prefix = ''

    def endReadRoles(self, chars):
        self.getElement().read_guard.roles = chars

    def endReadPermissions(self, chars):
        self.getElement().read_guard.permissions = chars

    def endReadExpr(self, chars):
        self.getElement().read_guard.expr = chars

    def startWrite_guard(self, attrs):
        self.getElement().write_guard = DefinitionNode()
        self.prefix = 'Write'

    def endWriteWrite_guard(self, chars):
        self.prefix = ''

    def endWriteRoles(self, chars):
        self.getElement().read_guard.roles = chars

    def endWritePermissions(self, chars):
        self.getElement().read_guard.permissions = chars

    def endWriteExpr(self, chars):
        self.getElement().read_guard.expr = chars
    
    def startField_values(self, attrs):
        self.getElement().field_values = []
        self.prefix = 'FieldV'

    def endFieldVField_values(self, chars):
        self.prefix = ''

    def startFieldVValue(self, attrs):
        fv = DefinitionNode(attrs)
        self.getElement().field_values.append(fv)

    def startField_tales(self, attrs):
        self.getElement().field_tales = []
        self.prefix = 'FieldT'

    def endFieldTField_tales(self, chars):
        self.prefix = ''
    
    def startFieldTValue(self, attrs):
        ft = DefinitionNode(attrs)
        self.getElement().field_tales.append(ft)

    def endFieldTValue(self, chars):
        self.getElement().field_tales[-1].expr = chars
        
    def startField_messages(self, attrs):
        self.getElement().field_messages = []
        self.prefix='FieldM'

    def endFieldMField_message(self, chars):
        self.prefix = ''

    def startFieldMmessage(self, attrs):
        fm = DefinitionNode(attrs)
        self.getElement().field_messages.append(fm)

    def endFieldMmessage(self, chars):
        self.getElement().field_messages[-1].text = chars

        
def read_set( xml ):
    parser = make_parser()
    reader = MetadataSetReader()
    parser.setContentHandler(reader)
    parser.parse( xml )
    return reader.getSet()

def make_set( container, set_node ):

    import Configuration
    from Compatiblity import getToolByName
    from Products.Formulator.TALESField import TALESMethod
    
    pm = getToolByName(container, 'portal_metadata')
    
    collection = getattr(pm, Configuration.MetadataCollection)
    collection.addMetadataSet( set_node.id,
                               set_node.ns_prefix,
                               set_node.ns_uri )
    
    set = pm.getMetadataSet(set_node.id)
    
    for e_node in set_node.elements:
        set.addMetadataElement( e_node.id,
                                e_node.field_type,
                                e_node.index_type,
                                e_node.index_p )

        element = set.getElement(e_node.id)

        # XXX formulator specific..
        field = element.field
        for fv in e_node.field_values:
            k = fv.key
            v = fv.value
            t = fv.type
            if t == 'int':
                v = int(v)
            elif t == 'float':
                v = float(v)
            field.values[k]=v

        # some sort of formulator hack
        if e_node.field_type == 'DateTimeField':
            field.on_value_input_style_changed(field.get_value('input_style'))
            
        for ft in e_node.field_tales:
            field.field_tales[ft.key] = TALESMethod(ft.expr)

        for fm in e_node.field_messages:
            field.message_values[fm.name]=fm.text
                
        
if __name__ == '__main__':
    # visual check
    import sys, pprint
    set_node = read_set(sys.argv[1])

    for k,v in set_node.items():
        print k

        for k,v in v.items():
            print "  "*5, k, v