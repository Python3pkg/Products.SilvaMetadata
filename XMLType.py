"""
Simple Type System for (De)Serializing python values to XML

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import types
from cgi import escape

from DateTime import DateTime
from Exceptions import XMLMarshallError

def serialize( value):

    if isinstance(value, types.IntType):
        return '<element type="integer">%s</element>'%unicode(value)
    
    elif isinstance(value, types.FloatType):
        return '<element type="float">%s</element>' % unicode(value)
    
    elif isinstance(value, types.StringType):
        return '<element type="string">%s</element>'%unicode( escape(value, 1) )

    elif isinstance(value, DateTime):
        return '<element type="date">%s</element>'%unicode(value)
    
    elif isinstance(value, types.UnicodeType):
        return '<element type="string">%s</element>'%escape(value, 1)
    
    elif isinstance(value, types.ListType):
        return '<element_list type="list">%s</element_list>'%(''.join(map(serialize, value)))

    elif isinstance(value, types.NoneType):
        return '<element type="none">%s</element>'%unicode(str(value))

def deserialize( node ):
    
    if not node.nodeName in ('element', 'element_list'):
        raise XMLMarshallError("invalid xml node type %s"%node.nodeName)

    node_type = node.getAttribute('type')

    try:
        if node_type == 'integer':
            return int(node.childNodes[0].nodeValue)

        elif node_type == 'float':
            return float(node.childNodes[0].nodeValue)

        elif node_type == 'string':
            return node.childNodes[0].nodeValue

        elif node_type == 'date':
            return DateTime(node.childNodes[0].nodeValue)

        elif node_type == 'list':
            res = []
            for cn in node.childNodes:
                res.append(
                    deserialize(cn)
                    )
            return res
            
    except Exception, e:
        raise XMLMarshallError("error on marshalling %s  %s %s %s"%(
            node.nodeName,
            node_type,
            node.getValue(),
            str(e)
            )
            )

    
        

