"""
Simple Type System for (De)Serializing python values to XML

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

import types
from cgi import escape

from DateTime import DateTime
from Exceptions import XMLMarshallError

def serialize( value, indent):

    if isinstance(value, types.IntType):
        return '<element type="integer">%s</element>'%unicode(value)
    
    elif isinstance(value, types.FloatType):
        return '<element type="float">%s</element>' % unicode(value)
    
    elif isinstance(value, types.StringType):
        return '<element type="string">%s</element>'%unicode(escape(value))
    
    elif isinstance(value, DateTime):
        return '<element type="date">%s</element>'%unicode(value)
    
    elif isinstance(value, types.UnicodeType):
        return '<element type="string">%s</element>'%escape(value)
    
    elif isinstance(value, types.ListType):
        return '<element_list type="list">%s</element_list>'%(''.join(map(serialize, value)))

def deserialize( node ):
    
    if not node.nodeName in ('element', 'element_list'):
        raise XMLMarshallError("invalid xml node type %s"%node.nodeName)

    node_type = node.getAttribute('type')

    try:
        if node_type == 'integer':
            return int(node.nodeValue)

        elif node_type == 'float':
            return float(node.nodeValue)

        elif node_type == 'string':
            return node.nodeValue

        elif node_type == 'date':
            return DateTime(node.nodeValue)

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

    
        

