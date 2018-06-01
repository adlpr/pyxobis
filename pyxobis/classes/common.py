#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from lxml.builder import ElementMaker
nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
       'xlink':"https://www.w3.org/1999/xlink"}
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap=nsmap)

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
            raise ValueError("unknown serialize format: {}".format())
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


class GenericName(Component):
    """
    genericName |=
        element xobis:name {
            nameContent_
            | element xobis:part { nameContent_ }+
        }
    """
    def __init__(self, name_content=None):
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


class Content(Component):
    """
    content_ |=
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
    nameContent_ |=
        (attribute lang { text },
         attribute translit { text }?)?,
        attribute nonfiling { xsd:positiveInteger }?,
        text
    """
    def __init__(self, text, lang=None, translit=None, nonfiling=0):
        self.text = text
        self.lang = lang
        if translit: assert lang
        self.translit = translit
        assert is_positive_integer(nonfiling)
        self.nonfiling = str(nonfiling)
    def serialize_xml(self):
        # Returns a text string and a dict of parent attributes.
        attrs = {}
        if self.lang:
            attrs['lang'] = self.lang
            if self.translit:
                attrs['translit'] = self.translit
        attrs['nonfiling'] = self.nonfiling
        return self.text, attrs


class OptScheme(Component):
    """
    optScheme_ |= attribute scheme { text }?
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
    optClass_ |= attribute class { string "individual" | string "collective" | string "referential" }?
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


class OptSubdivision(Component):
    """
    optSubdivision_ |= element xobis:subdivision { linkContent_ }*
    """
    def __init__(self, link_contents=[]):
        assert all(isinstance(link_content, LinkContent) for link_content in link_contents)
        self.link_contents = link_contents
    def serialize_xml(self):
        # Returns a list of zero or more Elements.
        subdivision_elements = []
        for link_content in self.link_contents:
            link_content_text, link_content_attrs = link_content.serialize_xml()
            subdivision_e = E('subdivison', **link_content_attrs)
            subdivision_e.text = link_content_text
            subdivision_elements.append(subdivision_e)
        return subdivision_elements


class RoleAttributes(Component):
    """
    roleAttributes_ |=
        attribute role { string "instance" | string "authority" | string "authority instance" }
    """
    ROLES = ["instance", "authority", "authority instance"]
    def __init__(self, role):
        assert role in RoleAttributes.ROLES
        self.role = role
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        return {'role' : self.role}


class Type(Component):
    """
    type_ |=
        element xobis:type {
            linkAttributes_,
            attribute xlink:role { xsd:anyURI },
            empty
        }?
    """
    def __init__(self, link_attributes=None, xlink_role=None):
        assert not (bool(link_attributes) ^ bool(xlink_role)), "Need both or neither: link / role"
        self.no_attrs = link_attributes is None
        if not self.no_attrs:
            assert isinstance(link_attributes, LinkAttributes)
            assert isinstance(xlink_role, XLinkAnyURI)
        self.link_attributes = link_attributes
        self.xlink_role = xlink_role
    def serialize_xml(self):
        # Returns either an Element or None.
        if self.no_attrs:
            return None
        link_attributes = self.link_attributes.serialize_xml()
        type_e = E('type', **link_attributes)
        xlink_role_text = self.xlink_role.serialize_xml()
        type_e.attrib['{%s}role' % nsmap['xlink']] = xlink_role_text
        return type_e



class LinkAttributes(Component):
    """
    linkAttributes_ =
        attribute xlink:href { xsd:anyURI }?,
        attribute xlink:title { text }
    """
    def __init__(self, xlink_title, xlink_href=None):
        if xlink_href:
            assert isinstance(xlink_href, XLinkAnyURI)
        self.xlink_href = xlink_href
        self.xlink_title = xlink_title
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        attrs = {}
        if self.xlink_href:
            xlink_href_text = self.xlink_href.serialize_xml()
            attrs['{%s}href' % nsmap['xlink']] = xlink_href_text
        attrs['{%s}title' % nsmap['xlink']] = self.xlink_title
        return attrs



class LinkContent(Component):
    """
    linkContent_ =
        (linkAttributes_,
         attribute substitute {
             string "abbrev" | string "citation" | string "code" | string "singular"
         }?)?,
        content_
    """
    SUBSTITUTES = ["abbrev", "citation", "code", "singular"]
    def __init__(self, content, link_attributes=None, substitute=None):
        if link_attributes: assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        if substitute:
            assert link_attributes
            assert substitute in LinkContent.SUBSTITUTES
        self.substitute = substitute
        assert isinstance(content, Content)
        self.content = content
    def serialize_xml(self):
        # Returns a text string and a dict of parent attributes.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.substitute:
            attrs['substitute'] = self.substitute
        content_text, content_attrs = self.content.serialize_xml()
        attrs.update(content_attrs)
        return content_text, attrs


class SubstituteAttribute(Component):
    """
    substituteAttribute |=
        attribute type { string "abbrev" | string "citation" | string "code" | string "singular" }?
    """
    TYPES = ["abbrev", "citation", "code", "singular", None]
    def __init__(self, type_=None):
        assert type_ in SubstituteAttribute.TYPES
        self.type = type_
    def serialize_xml(self):
        # Returns a dict of parent attributes.
        attrs = {}
        if self.type:
            attrs['type'] = self.type
        return attrs


class OptNoteList(Component):
    """
    optNoteList_ |=
         (element xobis:noteList { note_+ }
          | note_)?
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
    note_ |=
       element xobis:note {
           attribute class { "transcription" | "annotation" | "documentation" | "description" }?,
           (linkAttributes_,
            attribute xlink:role { xsd:anyURI })?,
           content_
       }
    """
    NOTECLASSES = ["transcription", "annotation", "documentation", "description", None]
    def __init__(self, content, class_=None, link_attributes=None, xlink_role=None):
        assert class_ in Note.NOTECLASSES
        self.class_ = class_
        assert not (bool(link_attributes) ^ bool(xlink_role)), "Need both or neither: link / role"
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
            assert isinstance(xlink_role, XLinkAnyURI)
        self.link_attributes = link_attributes
        self.xlink_role = xlink_role
        assert isinstance(content, Content)
        self.content = content
    def serialize_xml(self):
        # Returns an Element.
        note_e = E('note')
        if self.class_:
            note_e.attrib['class'] = self.class_
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            for k,v in link_attributes_attrs.items():
                note_e.attrib[k] = v
            if self.xlink_role:
                xlink_role_text = self.xlink_role.serialize_xml()
                note_e.attrib['{%s}role' % nsmap['xlink']] = xlink_role_text
        content_text, content_attrs = self.content.serialize_xml()
        for k,v in content_attrs.items():
            note_e.attrib[k] = v
        note_e.text = content_text
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




class VersionsHoldingsOpt(Component):
    """
    versionsHoldingsOpt |=
        (element xobis:versions {
             element xobis:version {
                 element xobis:entry {
                     element xobis:name { nameContent_ },
                     qualifiersOpt
                 },
                 optNoteList_,
                 _holdings
             }+
         }
         | _holdings)?
    """
    def __init__(self, versions=None):
        self.is_none = not bool(versions)
        self.is_holdings = isinstance(versions, Holdings)
        if not (self.is_holdings or self.is_none):
            assert len(versions) > 0
            assert all(isinstance(v, Version) for v in versions)
        self.versions = versions
    def serialize_xml(self):
        # Returns an Element or None.
        if self.is_none:
            return None
        if self.is_holdings:
            return self.versions.serialize_xml()
        # List of versions
        versions_e = E('versions')
        versions_e.extend([v.serialize_xml() for v in self.versions])
        return versions_e


class Version(Component):
    """
    element xobis:version {
         element xobis:entry {
             element xobis:name { nameContent_ },
             qualifiersOpt
         },
         optNoteList_,
         _holdings
    }
    """
    def __init__(self, name_content, holdings, qualifiers_opt=QualifiersOpt(), opt_note_list=OptNoteList()):
        assert isinstance(name_content, NameContent)
        self.name_content = name_content
        assert isinstance(holdings, Holdings)
        self.holdings = holdings
        assert isinstance(qualifiers_opt, QualifiersOpt)
        self.qualifiers_opt = qualifiers_opt
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        version_e = E('version')
        entry_e = E('entry')
        name_content_text, name_content_attrs = self.name_content.serialize_xml()
        name_e = E('name', **name_content_attrs)
        name_e.text = name_content_text
        entry_e.append(name_e)
        qualifiers_e = self.qualifiers_opt.serialize_xml()
        if qualifiers_e is not None:
            entry_e.append(qualifiers_e)
        version_e.append(entry_e)
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            version_e.append(opt_note_list_e)
        holdings_e = self.holdings.serialize_xml()
        if holdings_e is not None:
            version_e.append(holdings_e)
        return version_e


class Holdings(Component):
    """
    ### PLACEHOLDER FOR A BETTER SCHEMA FOR HOLDINGS ###
    _holdings |= element xobis:holdings { content_ }
    """
    def __init__(self, content):
        assert isinstance(content, Content)
        self.content = content
    def serialize_xml(self):
        # Returns an Element.
        content_text, content_attrs = self.content.serialize_xml()
        holdings_e = E('holdings', **content_attrs)
        holdings_e.text = content_text
        return holdings_e


# other namespaces

class XLinkAnyURI(Component):
    def __init__(self, anyURI):
        # validate??????
        self.anyURI = anyURI
    def serialize_xml(self):
        # Returns a text string.
        return self.anyURI

# functions

def is_positive_integer(s):
    return (isinstance(s, int) or s.isdigit()) and int(s) >= 0
