# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from xml.sax import make_parser, ContentHandler
from UserDict import UserDict

_marker = []

class DefinitionNode(UserDict):
    reserved = ('data',)

    def __getattr__(self, name):

        v = self.__dict__.get(name, _marker)
        if v is _marker:
            return self.data[name]
        return v

    def __setattr__(self, name, value):
        if name in DefinitionNode.reserved:
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
        if self.prefix:
            name = '%s%s' % (self.prefix, name.capitalize())
        else:
            name = name.capitalize()

        method = getattr(self, 'start%s' % name, None)
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
        if self.prefix:
            name = '%s%s' % (self.prefix, name.capitalize())
        else:
            name = name.capitalize()

        method = getattr(self, 'end%s' % name, None)
        if method:
            apply(method, (chars,))

    def characters(self, chars):
        self.buf.append(chars)


class MetadataSetReader(MetaReader):

    def getSet(self):
        return self.set

    def endTitle(self, chars):
        self.set.title = chars

    def endDescription(self, chars):
        self.set.description = chars

    def endI18n_domain(self, chars):
        self.set.i18n_domain = chars

    def endMinimalrole(self, chars):
        self.set.minimalrole = chars

    def endCategory(self, chars):
        self.set.category = chars

    def startMetadata_set(self, attrs):
        self.set = s = DefinitionNode(attrs)
        s.setdefault('elements', [])

    def startMetadata_element(self, attrs):
        element = DefinitionNode(attrs)
        self.set.elements.append(element)

    def getElement(self):
        return self.set.elements[-1]

    def endIndex_type(self, chars):
        self.getElement().index_type = chars

    def endIndex_p(self, chars):
        self.getElement().index_p = chars

    def endMetadata_in_catalog_p(self, chars):
        self.getElement().metadata_in_catalog_p = chars

    def endRead_only_p(self, chars):
        self.getElement().read_only_p = int(chars)

    def endAutomatic_p(self, chars):
        self.getElement().automatic_p = int(chars)

    def endAcquire_p(self, chars):
        self.getElement().acquire_p = int(chars)

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

    def endFieldMField_messages(self, chars):
        self.prefix = ''

    def startFieldMMessage(self, attrs):
        fm = DefinitionNode(attrs)
        self.getElement().field_messages.append(fm)

    def endFieldMMessage(self, chars):
        self.getElement().field_messages[-1].text = chars

    def startIndex_args(self, attrs):
        self.prefix = 'IndexArg'
        self.getElement().index_args = []

    def endIndexArgIndex_args(self, chars):
        self.prefix = ''

    def startIndexArgValue(self, attrs):
        iav = DefinitionNode(attrs)
        self.getElement().index_args.append(iav)

    def endIndexArgValue(self, chars):
        self.getElement().index_args[-1].value = chars


def read_set(xml):
    parser = make_parser()
    reader = MetadataSetReader()
    parser.setContentHandler(reader)
    parser.parse(xml)
    return reader.getSet()


def make_set(collection, set_node):
    from Products.Formulator.TALESField import TALESMethod

    # compatiblity.. ick
    if not set_node.has_key('title'):
        set_node['title'] = ''
    if not set_node.has_key('description'):
        set_node['description'] = ''
    if not set_node.has_key('i18n_domain'):
        set_node['i18n_domain'] = ''

    collection.addMetadataSet(
        set_node.id, set_node.ns_prefix, set_node.ns_uri, set_node.title,
        set_node.description, set_node.i18n_domain)

    set = collection._getOb(set_node.id)
    set.setCategory(set_node.get('category', ''))
    set.setMinimalRole(set_node.get('minimalrole', ''))

    for e_node in set_node.elements:

        # compatiblity.. ick
        if not e_node.has_key('acquire_p'):
            e_node['acquire_p'] = 0
        if not e_node.has_key('read_only_p'):
            e_node['read_only_p'] = 0
        if not e_node.has_key('automatic_p'):
            e_node['automatic_p'] = 0
        if not e_node.has_key('index_p'):
            e_node['index_p'] = 0
        if not e_node.has_key('metadata_in_catalog_p'):
            e_node['metadata_in_catalog_p'] = 0

        # type possible is string, convert to 'boolean'
        for p in ['index_p', 'acquire_p', 'read_only_p', 'automatic_p',
                  'metadata_in_catalog_p']:
            try:
                e_node[p] = not not int(e_node[p])
            except ValueError:
                e_node[p] = 0

        set.addMetadataElement(
            e_node.id, e_node.field_type, e_node.index_type, e_node.index_p,
            e_node.acquire_p, e_node.read_only_p, e_node.metadata_in_catalog_p,
            e_node.automatic_p)

        element = set.getElement(e_node.id)

        field = element.field
        for fv in e_node.field_values:
            k = fv.key
            v = fv.value
            t = fv.type
            if t == 'int':
                v = int(v)
            elif t == 'float':
                v = float(v)
            elif t == 'list':
                # XXX this is incomplete support for lists
                # the originial version of formulator xml support
                # did an eval here, which is not an option
                # XXX we'll make use of this option anyway
                # metadata sets are edited on the filesystem after all
                v = eval(v, {})

            field.values[k]=v

        # some sort of formulator hack
        if e_node.field_type == 'DateTimeField':
            field.on_value_input_style_changed(field.get_value('input_style'))

        for ft in e_node.field_tales:
            if ft.expr:
                field.tales[ft.key] = TALESMethod(ft.expr)

        for fm in e_node.field_messages:
            field.message_values[fm.name]=fm.text

        constructor_args = {}
        for iav in e_node.index_args:
            constructor_args[iav['key']]=iav['value']
        element.index_constructor_args = constructor_args


if __name__ == '__main__':
    # visual check
    import sys
    set_node = read_set(sys.argv[1])

    for k,v in set_node.items():
        print k

        if isinstance(v, DefinitionNode):
            for k,v in v.items():
                print "  "*5, k, v
        else:
            print v
