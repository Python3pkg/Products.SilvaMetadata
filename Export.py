"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from cgi import escape
from types import IntType, FloatType, ListType

from Interfaces import IMetadataSetExporter

from Element import MetadataElement
from utils import StringBuffer, make_lookup


class MetadataSetExporter:
    """
    for exporting a metadata set definition
    """
    __implements__ = IMetadataSetExporter

    def __init__(self, set):
        self.set = set

    def __call__(self, out=None):

        ext_out = 1
        if out is None:
            ext_out = 0
            out = StringBuffer()

        print >> out, '<?xml version="1.0" encoding="iso-8859-1"?>\n\n'
        print >> out, '<metadata_set id="%s" ns_uri="%s" ns_prefix="%s">'%(
            self.set.getId(),
            self.set.metadata_uri,
            self.set.metadata_prefix
            )

        for e in self.set.getElements():
            
            print >> out, '  <metadata_element id="%s">'%e.getId()
            print >> out, '   <index_type>%s</index_type>'%e.index_type
            print >> out, '   <index_p>%s</index_p>'%e.index_p
            print >> out, '   <field_type>%s</field_type>'%e.field_type

            g = e.read_guard
            print >> out, '   <read_guard>'
            print >> out, '     <roles>%s</roles>'%g.getRolesText()
            print >> out, '     <permissions>%s</permissions>'%g.getPermissionsText()
            print >> out, '     <expr>%s</expr>'%g.getExprText()
            print >> out, '   </read_guard>'

            g = e.write_guard
            print >> out, '   <write_guard>'
            print >> out, '     <roles>%s</roles>'%g.getRolesText()
            print >> out, '     <permissions>%s</permissions>'%g.getPermissionsText()
            print >> out, '     <expr>%s</expr>'%g.getExprText()            
            print >> out, '   </write_guard>'            

            f = e.field

            print >> out, '   <field_values>'
            
            for k, v in f.values.items():
                if v is None:
                    continue
                if isinstance(v, IntType):
                    print >> out,    '        <value key="%s" type="%s" value="%d" />'%(
                        k, 'int', v )
                elif isinstance(v, FloatType):
                    print >> out,    '        <value key="%s" type="%s" value="%d" />'%(
                        k, 'float', v )
                elif isinstance(v, ListType):
                    print >> out,    '        <value key="%s" type="%s" value="%s" />'%(
                        k, 'list', escape(str(v)) )
                else:
                    print >> out,    '        <value key="%s" type="str" value="%s" />'%(
                        k, escape(str(v)) )

            print >> out, '   </field_values>'            

            print >> out, '   <field_tales>'
            for k,v in f.tales.items():
                if v is None:
                    continue
                print >> out, '     <value key="%s">%s</value>'%(k, escape(str(v)))
            print >> out, '   </field_tales>'

            print >> out, '   <field_messages>'
            for message_key in f.get_error_names():
                print >> out, '     <message name="%s">%s</message>'%(
                    escape(message_key),
                    escape(f.get_error_message(message_key))
                    )
            print >> out, '   </field_messages>'

            print >> out, '  </metadata_element>'
            
        print >> out, '</metadata_set>'
        
        if ext_out:
            return out

        return out.getvalue()

class ObjectMetadataExporter:
    """
    for exporting the metadata of an object, returns
    an xml fragement.

    XXX encoding issues
    XXX file/image binary metadata issues
    """

    def __init__(self, binding, sets):
        self.binding = binding
        self.sets = sets

    def __call__(self, out=None):

        if out is None:
            out = StringBuffer()

        print >> out, '<metadata '
        
        for set in self.sets:
            print >> out, '    xmlns:%s="%s"'%(set.getId(), set.metadata_uri)
        print >> out, '      >'

        for set in self.sets:
            sid = set.getId()
            check = make_lookup( set.objectIds(MetadataElement.meta_type) )
            data = self.binding._getData(sid)

            for k,v in data.items():
                # with updates its possible that certain annotation data
                # is no longer part of the metadata set, so we filter it out.
                if not check(k):
                    continue
                print >> out, '      <%s:%s>%s</%s:%s>'%(sid, k, escape(v), sid, k)

        print >> out, '</metadata>'

        return out.getvalue()
