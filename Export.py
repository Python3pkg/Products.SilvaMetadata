from Interfaces import IMetadataSetExporter
from cgi import escape
from types import IntType

class StringBuffer:

    def __init__(self):
        self.buf =[]
    def write(self, data):
        self.buf.append(data)
    def getvalue(self):
        return ''.join(self.buf)

class MetadataSetExporter:

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
            
            print >> out, '  <element id="%s">'%e.getId()
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
                else:
                    print >> out,    '        <value key="%s" value="%s" />'%(
                        k, escape(str(v)) )
                        

            print >> out, '   </field_values>'            

            print >> out, '   <field_tales>'
            for k,v in f.tales.items():
                if v is None:
                    continue                
            print >> out, '   </field_tales>'

            print >> out, '  </element>'
            print >> out, '</metadata_set>'
        if ext_out:
            return out

        return out.getvalue()
