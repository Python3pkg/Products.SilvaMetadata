==============
Silva Metadata
==============

Implemented Use Cases
=====================

- Define Metadata

- Map Metadata to a Content Type

- Import Metadata Definition

- Export Metadata Definition

- Export Metadata for a Content Object

- Import Metadata for a Content Object

- Display a Form for Metadata

- Validate Values for Metadata

- Restrict Displayable/Editable Metadata based on
  permissions, roles, or state.

- Containment Based Metadata Acquisition

- Invoke Triggers upon Metadata Changes

- Index/Search Metadata


Design
======

Storage/Annotations
-------------------

Metadata storage is based on annotating content objects. Metadata
storage itself is partioned by set namespaces, and also includes a
partition for metadata configuration on a per object basis.

Definitions
-----------

Definitions of the metadata are conducted with the metadata tool zmi
interface. These definitions are managed as sets composed of elements,
with guards and fields attached to elements. These definitions can
be exported and imported to xml and are used for validation and display
of the metadata. These definitions are then mapped onto content types
that they will be available for.

Tool API
--------

The metadata tool api is fairly simple, the core of it is simply
one method. ``getMetadata`` which returns a binding object, below.

The additional methods are present to conform to the metadata tool
api defined by the cmf interfaces.

Binding/Adapter
---------------

Bindings functions as an adapter between the content object,
the metadata definition, and the stored metdata values. It offers
a unified api to the programmer to operate on an object's metadata,
and unlike a service or tool, allows for security checks to be
automatically performed in the context of the content object.

Additionally the binding adapter makes use of the metadata storage
to store configuration options that can be set per object, that
affect the runtime behavior of the binding. this capability is used
to implement some of the advanced features of the metadata system
such as metadata acquisition and mutation triggers, and can be
extended as need arises.

Hook Points
-----------

To allow for flexibility and customization based on a
requirements the metadata system offers two major hook points
exposed at by its python api.

Access
  The Access hook is used by the metadata tool to construct
  a binding for a content object. access hooks can be registered
  on a per content type basis or as a default hook.

Runtime Data Initializer
  When a metadata binding is constructed for an object with no
  metadata annotation data, a runtime data initializer is
  invoked to construct the binding's runtime data. initializers
  can be defined on a per content type basis or as a default
  initializer.

