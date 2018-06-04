#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class ObjectBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Object element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_scheme, set_usage
    # ADDITIONAL: set_organization, set_holdings
    def __init__(self):
        super().__init__()
        # org info
        self.organization_link_title = None
        self.organization_link_href = None
        self.organization_id_content = None
        self.organization_id_content_lang = None
        # holdings
        self.holdings = VersionsHoldingsOpt()
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("Object element does not have property 'scheme'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Object element does not have property 'usage'")
    def set_organization(self, link_title, link_href=None, id_content=None, id_content_lang=None):
        self.organization_link_title = link_title
        self.organization_link_href = link_href
        self.organization_id_content = id_content
        self.organization_id_content_lang = id_content_lang
    def set_holdings(self, versions_holdings_opt):
        # input should be a VersionsHoldingsOpt object (TEMPORARY UNTIL BETTER SCHEME).
        # use VersionsHoldingsBuilder to build.
        # assert isinstance(versions_holdings_opt, VersionsHoldingsOpt)
        self.holdings = versions_holdings_opt
    def add_variant(self, variant):
        # input should be an ObjectVariantEntry. use ObjectVariantBuilder to build.
        assert isinstance(variant, ObjectVariantEntry)
        super().add_variant(variant)
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        organization_link_attributes = LinkAttributes(
                        self.organization_link_title,
                        xlink_href = XSDAnyURI(self.organization_link_href) \
                                     if self.organization_link_href else None
            ) if self.organization_link_title else None
        organization_id_content = Content(
                self.organization_id_content,
                lang = self.organization_id_content_lang,
            ) if self.organization_id_content else None
        return Object(
                   ObjectContent(
                       ObjectEntryContent(
                           GenericName(name_content),
                           QualifiersOpt(self.qualifiers)
                       ),
                       type_ = self.type,
                       organization_link_attributes = organization_link_attributes,
                       organization_id_content = organization_id_content,
                       variants = self.variants,
                       opt_note_list = OptNoteList(self.note_list)
                   ),
                   role   = self.role,
                   class_ = self.class_,
                   opt_class = OptClass(self.class_),
                   versions_holdings_opt = self.holdings
               )


class ObjectVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a ObjectVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: -
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return ObjectVariantEntry(
                   ObjectEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   substitute_attribute = SubstituteAttribute(self.substitute_attribute_type),
                   opt_scheme = OptScheme(self.scheme),
                   opt_note_list = OptNoteList(self.note_list)
               )


class ObjectRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a ObjectRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_subdivision_link
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("Object element ref does not have subdivisions")
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return ObjectRef(
                   ObjectEntryContent(
                       GenericName(name_content),  # either NameContent or list of NameContents
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
