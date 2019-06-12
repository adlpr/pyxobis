#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})

class Component:
    """
    An object representable by some group of "pieces" of XML representable in RelaxNG.
    Returns a one or more lxml Elements and/or a dict of attributes to pass to the parent.
    """
    def __init__(self):
        pass
    def serialize(self, format="xml"):
        if format == "xml":
            return self.serialize_xml()
        else:
            raise ValueError(f"unknown serialize format: {format}")
    def serialize_xml(self):
        # Returns None.
        return None


class PrincipalElement(Component):
    """
    Superclass for the ten principals defined in other files.
    """
    pass


class RefElement(Component):
    """
    Superclass for the reference forms of the ten principals defined in other files.
    """
    pass


class PreQualifierRefElement(RefElement):
    """
    Superclass for the reference forms of principals allowed for use as a prequalifier.
    """
    pass


class VariantEntry(Component):
    """
    Superclass for variants of principal element entries.
    """
    pass


class GenericName(Component):
    """
    genericName |=
        element xobis:name {
            nameContent
            | element xobis:part { nameContent }+
        }
    """
    def __init__(self, name_content):
        assert name_content, "GenericName must have name content"
        self.is_parts = not isinstance(name_content, NameContent)
        if self.is_parts:
            assert all(isinstance(content, NameContent) for content in name_content)
        self.name_content = name_content
    def serialize_xml(self):
        # Returns an Element.
        if self.is_parts:
            name_e = E('name')
            for content in self.name_content:
                name_content_text, name_content_attrs = content.serialize_xml()
                part_e = E('part', **name_content_attrs)
                part_e.text = name_content_text
                name_e.append(part_e)
        else:
            name_content_text, name_content_attrs = self.name_content.serialize_xml()
            name_e = E('name', **name_content_attrs)
            name_e.text = name_content_text
        return name_e


class GenericContent(Component):
    """
    genericContent |=
        attribute lang { text }?,
        text
    """
    def __init__(self, text, lang=None):
        self.lang = lang
        self.text = text
    def serialize_xml(self):
        # Returns a text string and a dict of parent attributes.
        attrs = {}
        if self.lang:
            attrs['lang'] = self.lang
        return self.text, attrs


class NameContent(Component):
    """
    nameContent |=
        attribute lang { text }?,
        attribute script { text }?,
        attribute nonfiling { xsd:positiveInteger }?,
        text
    """
    def __init__(self, text, lang=None, script=None, nonfiling=0):
        self.text = text
        self.lang = lang
        self.script = script
        assert is_non_negative_int(nonfiling)
        self.nonfiling = str(nonfiling)
    def serialize_xml(self):
        # Returns a text string and a dict of parent attributes.
        attrs = {}
        if self.lang:
            attrs['lang'] = self.lang
        if self.script:
            attrs['script'] = self.script
        attrs['nonfiling'] = self.nonfiling
        return self.text, attrs


class OptScheme(Component):
    """
    optScheme |= attribute scheme { text }?
    """
    def __init__(self, scheme=None):
        self.scheme = scheme
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        attrs = {}
        if self.scheme:
            attrs['scheme'] = self.scheme
        return attrs


class Value(Component):
    """
    value_ |= element xobis:value { content_ }
    """
    def __init__(self, content):
        assert isinstance(content, Content)
        self.content = content
    def serialize_xml(self):
        # Returns an Element.
        content_text, content_attrs = self.content.serialize_xml()
        value_e = E('value', **content_attrs)
        value_e.text = content_text
        elements.append(value_e)
        return value_e


class OptClass(Component):
    """
    optClass |= attribute class { string "individual" | string "collective" | string "referential" }?
    """
    CLASSES = ["individual", "collective", "referential", None]
    def __init__(self, class_=None):
        assert class_ in OptClass.CLASSES
        self.class_ = class_
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        attrs = {}
        if self.class_:
            attrs['class'] = self.class_
        return attrs


class RoleAttributes(Component):
    """
    roleAttributes |=
        attribute role { string "instance" | string "authority" | string "authority instance" }
    """
    ROLES = ["instance", "authority", "authority instance"]
    def __init__(self, role):
        assert role in RoleAttributes.ROLES
        self.role = role
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        return {'role' : self.role}


class GenericType(Component):
    """
    genericType |=
        element xobis:type {
            linkAttributes,
            attribute set { xsd:anyURI },
            empty
        }
    """
    def __init__(self, link_attributes, set_ref):
        assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(set_ref, XSDAnyURI), f"invalid set ref: {set_ref}"
        self.set_ref = set_ref
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        link_attributes = self.link_attributes.serialize_xml()
        attrs.update(link_attributes)
        set_ref_text = self.set_ref.serialize_xml()
        attrs.update( { 'set' : set_ref_text } )
        type_e = E('type', **attrs)
        return type_e



class LinkAttributes(Component):
    """
    linkAttributes |=
        attribute href { xsd:anyURI }?,
        attribute title { text }
    """
    def __init__(self, title, href=None):
        if href:
            assert isinstance(href, XSDAnyURI)
        self.href = href
        self.title = title
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        attrs = {}
        if self.href:
            href_text = self.href.serialize_xml()
            attrs['href'] = href_text
        attrs['title'] = self.title
        return attrs



class OptSubstituteAttribute(Component):
    """
    optSubstituteAttribute |=
        attribute substitute { xsd:boolean }?
    """
    TYPES = [True, False, None]
    def __init__(self, type_=None):
        assert type_ in OptSubstituteAttribute.TYPES
        self.type = type_
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        attrs = {}
        if self.type is not None:
            attrs['type'] = str(self.type).lower()
        return attrs


class OptSubdivisions(Component):
    """
    optSubdivisions |=
        element xobis:subdivision { subdivisonContent }*
    """
    def __init__(self, subdiv_contents=[]):
        assert all(isinstance(subdiv_content, SubdivisionContent)  \
                   for subdiv_content in subdiv_contents)
        self.subdiv_contents = subdiv_contents
    def serialize_xml(self):
        # Returns a list of zero or more Elements.
        subdivision_elements = []
        for subdiv_content in self.subdiv_contents:
            subdiv_content_text, subdiv_content_attrs = subdiv_content.serialize_xml()
            subdivision_e = E('subdivison', **subdiv_content_attrs)
            subdivision_e.text = subdiv_content_text
            subdivision_elements.append(subdivision_e)
        return subdivision_elements


class SubdivisionContent(Component):
    """
    subdivisonContent |=
        ( linkAttributes,
          optSubstituteAttribute )?,
        genericContent
    """
    def __init__(self, content, link_attributes=None, opt_substitute_attribute=OptSubstituteAttribute()):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
            assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
            self.opt_substitute_attribute = opt_substitute_attribute
        else:
            self.opt_substitute_attribute = OptSubstituteAttribute()
        self.link_attributes = link_attributes
        assert isinstance(content, GenericContent)
        self.content = content
    def serialize_xml(self):
        # Returns a text string and a dict of parent attributes.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        opt_substitute_attribute_attrs = self.opt_substitute_attribute.serialize_xml()
        attrs.update(opt_substitute_attribute_attrs)
        content_text, content_attrs = self.content.serialize_xml()
        attrs.update(content_attrs)
        return content_text, attrs


class OptNoteList(Component):
    """
    optNoteList |=
        ( note
          | element xobis:noteList { note+ } )?
    """
    def __init__(self, notes=[]):
        assert all(isinstance(note, Note) for note in notes)
        self.notes = notes
    def serialize_xml(self):
        # Returns either an Element or None.
        if not self.notes:
            return None
        if len(self.notes) == 1:
            return self.notes[0].serialize_xml()
        note_list_e = E('noteList')
        for note in self.notes:
            note_e = note.serialize_xml()
            note_list_e.append(note_e)
        return note_list_e


class Note(Component):
    """
    note |=
        element xobis:note {
            attribute role { "transcription" | "annotation" | "documentation" | "description" }?,
            ( linkAttributes,
              attribute set { xsd:anyURI } )?,
            genericType?,
            genericContent,
            noteSource*
        }

    noteSource |=
        element xobis:source {
          ( orgRef | workRef | element xobis:description { text } )+
        }
    """
    ROLES = ["transcription", "annotation", "documentation", "description", None]
    def __init__(self, content, role=None, link_attributes=None, set_ref=None, generic_type=None, source=[]):
        assert role in Note.ROLES
        self.role = role
        assert not (bool(link_attributes) ^ bool(set_ref)), "Need both or neither: link / set"
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
            assert isinstance(set_ref, XSDAnyURI)
        self.link_attributes = link_attributes
        self.set_ref = set_ref
        if generic_type is not None:
            assert isinstance(generic_type, GenericType)
        self.generic_type = generic_type
        assert isinstance(content, GenericContent)
        self.content = content
        # cannot be asserted here... assert at builder level for now?
        # for source_part in source:
        #     assert any(isinstance(source_part, valid_type) for valid_type in (OrganizationRef, WorkRef, str))
        self.source = source
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.role:
            attrs['role'] = self.role
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
            set_ref_text = self.set_ref.serialize_xml()
            attrs['set'] = set_ref_text
        content_text, content_attrs = self.content.serialize_xml()
        attrs.update(content_attrs)
        note_e = E('note', **attrs)
        if self.generic_type is not None:
            type_e = self.generic_type.serialize_xml()
            note_e.append(type_e)
        note_e.text = content_text
        if self.source:
            source_e = E('source')
            for source_part in self.source:
                if isinstance(source_part, str):
                    source_part_e = E('description')
                    source_part_e.text = source_part
                else:
                    source_part_e = source_part.serialize_xml()
                source_e.append(source_part_e)
        return note_e


class PreQualifiersOpt(Component):
    """
    preQualifiersOpt |= element xobis:qualifiers { (eventRef | orgRef | placeRef)+ }?
    """
    def __init__(self, qualifiers=None):
        if qualifiers:
            assert all(isinstance(qualifier, PreQualifierRefElement) for qualifier in qualifiers), \
                "Prequalifier must be an Event, Organization, or Place"
        self.qualifiers = qualifiers
    def serialize_xml(self):
        # Returns either an Element or None.
        if not self.qualifiers:
            return None
        qualifiers_e = E('qualifiers')
        for qualifier in self.qualifiers:
            qualifier_e = qualifier.serialize_xml()
            qualifiers_e.append(qualifier_e)
        return qualifiers_e


class QualifiersOpt(Component):
    """
    qualifiersOpt |=
        element xobis:qualifiers {
            (conceptRef
             | eventRef
             | stringRef
             | languageRef
             | (timeRef | durationRef)
             | beingRef
             | placeRef
             | orgRef
             | objectRef
             | workRef)+
        }?
    """
    def __init__(self, qualifiers=[]):
        if qualifiers:
            assert all(isinstance(qualifier, RefElement) for qualifier in qualifiers)
        self.qualifiers = qualifiers
    def serialize_xml(self):
        # Returns either an Element or None.
        if not self.qualifiers:
            return None
        qualifiers_e = E('qualifiers')
        for qualifier in self.qualifiers:
            qualifier_e = qualifier.serialize_xml()
            qualifiers_e.append(qualifier_e)
        return qualifiers_e



class OptVariantAttributes(Component):
    """
    optVariantAttributes |=
        attribute includes { string "broader" | string "narrower" | string "related" }?
    """
    INCLUDES = ["broader", "narrower", "related", None]
    def __init__(self, includes=None):
        assert includes in OptVariantAttributes.INCLUDES
        self.includes = includes
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        attrs = {}
        if self.includes is not None:
            attrs['includes'] = self.includes
        return attrs


class OptEntryGroupAttributes(Component):
    """
    optEntryAttributes |=
        attribute id { text }?,
        attribute group { text }?,
        attribute preferred { xsd:boolean }?
    """
    PREFERRED = [True, False, None]
    def __init__(self, id=None, group=None, preferred=None):
        self.id = id
        self.group = group
        assert preferred in OptEntryGroupAttributes.PREFERRED
        self.preferred = preferred
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        attrs = {}
        if self.id is not None:
            attrs['id'] = str(self.id)
        if self.group is not None:
            attrs['group'] = str(self.group)
        if self.preferred is not None:
            attrs['preferred'] = str(self.preferred).lower()
        return attrs


# class VersionsHoldingsOpt(Component):
#     """
#     versionsHoldingsOpt |=
#         (element xobis:versions {
#              element xobis:version {
#                  element xobis:entry {
#                      element xobis:name { nameContent },
#                      qualifiersOpt
#                  },
#                  optNoteList,
#                  holdings
#              }+
#          }
#          | holdings)?
#     """
#     def __init__(self, versions=None):
#         self.is_none = not bool(versions)
#         self.is_holdings = isinstance(versions, Holdings)
#         if not (self.is_holdings or self.is_none):
#             assert len(versions) > 0
#             assert all(isinstance(v, Version) for v in versions)
#         self.versions = versions
#     def serialize_xml(self):
#         # Returns an Element or None.
#         if self.is_none:
#             return None
#         if self.is_holdings:
#             return self.versions.serialize_xml()
#         # List of versions
#         versions_e = E('versions')
#         versions_e.extend([v.serialize_xml() for v in self.versions])
#         return versions_e
#
# 
# class Version(Component):
#     """
#     element xobis:version {
#         element xobis:entry {
#             element xobis:name { nameContent },
#             qualifiersOpt
#         },
#         optNoteList,
#         holdings
#     }
#     """
#     def __init__(self, name_content, holdings, qualifiers_opt=QualifiersOpt(), opt_note_list=OptNoteList()):
#         assert isinstance(name_content, NameContent)
#         self.name_content = name_content
#         assert isinstance(holdings, Holdings)
#         self.holdings = holdings
#         assert isinstance(qualifiers_opt, QualifiersOpt)
#         self.qualifiers_opt = qualifiers_opt
#         assert isinstance(opt_note_list, OptNoteList)
#         self.opt_note_list = opt_note_list
#     def serialize_xml(self):
#         # Returns an Element.
#         version_e = E('version')
#         entry_e = E('entry')
#         name_content_text, name_content_attrs = self.name_content.serialize_xml()
#         name_e = E('name', **name_content_attrs)
#         name_e.text = name_content_text
#         entry_e.append(name_e)
#         qualifiers_e = self.qualifiers_opt.serialize_xml()
#         if qualifiers_e is not None:
#             entry_e.append(qualifiers_e)
#         version_e.append(entry_e)
#         opt_note_list_e = self.opt_note_list.serialize_xml()
#         if opt_note_list_e is not None:
#             version_e.append(opt_note_list_e)
#         holdings_e = self.holdings.serialize_xml()
#         if holdings_e is not None:
#             version_e.append(holdings_e)
#         return version_e
#
#
# class Holdings(Component):
#     """
#     ### PLACEHOLDER FOR A BETTER SCHEMA FOR HOLDINGS ###
#     holdings |= element xobis:holdings { genericContent }
#     """
#     def __init__(self, content):
#         assert isinstance(content, GenericContent)
#         self.content = content
#     def serialize_xml(self):
#         # Returns an Element.
#         content_text, content_attrs = self.content.serialize_xml()
#         holdings_e = E('holdings', **content_attrs)
#         holdings_e.text = content_text
#         return holdings_e


# representations of XS datatypes

class XSDAnyURI(Component):
    def __init__(self, anyURI):
        # validate??????
        self.anyURI = anyURI
    def serialize_xml(self):
        # Returns a text string.
        return self.anyURI

# class XSDDateTime(Component):
#     def __init__(self, date_time):
#         # verify match to ISO 8601 extended format
#         assert re.match(r"-?\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(Z|[+-]\d\d:\d\d])?$", date_time), \
#             f"Datetime ({date_time}) must match ISO 8601 extended format"
#         self.date_time = date_time
#     def serialize_xml(self):
#         # Returns a text string.
#         return self.date_time

# functions

def is_non_negative_int(s):
    return (isinstance(s, int) or s.isdigit()) and int(s) >= 0
