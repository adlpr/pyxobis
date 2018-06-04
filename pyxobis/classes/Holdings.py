#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *

from lxml.builder import ElementMaker
from lxml.etree import _Element
NSMAP = {'xsi':"http://www.w3.org/2001/XMLSchema-instance",
         'xobis':"http://www.xobis.info/ns/2.0/",
         'xlink':"https://www.w3.org/1999/xlink"}
E = ElementMaker(namespace="",
                 nsmap=NSMAP)

nons = {"{}noNameSpaceSchemaLocation".format('{'+NSMAP['xsi']+'}') :
        "https://www.loc.gov/standards/iso20775/ISOholdings_V1.0.xsd"}


class HoldingsE(Component):
    """
    element holdings {
        element holding { ... }+,
        element resource { ... }*
    }
    """
    def __init__(self, holdings, resources=[]):
        assert holdings and all(isinstance(holding, Holding) for holding in holdings)
        self.holdings = holdings
        assert all(isinstance(resource, Resource) for resource in resources)
        self.resources = resources
    def serialize_xml(self):
        # Returns an Element.
        holdings_e = E('holdings', **nons)
        # variant elements
        holding_elements = [holding.serialize_xml() for holding in self.holdings]
        holdings_e.extend(holding_elements)
        # resource elements
        resource_elements = [resource.serialize_xml() for resource in self.resources]
        holdings_e.extend(resource_elements)
        return holdings_e


class Holding(Component):
    """
    element holding {
      element institutionIdentifier { codeOrIdentifier },
      element physicalLocation { text }*,
      element physicalAddress {(
        element text { xs:string }
        | xs:any
      )}*,
      element electronicAddress {(
        element text { xs:string }
        | xs:any
      )}*,
      ( element holdingSimple { ... }
        | element holdingStructured { ... } ),
      element summaryPolicy { ... }*,
      element summaryHistory { ... }?
    }
    """
    def __init__(self, institution_identifier, holding,  \
                       physical_locations=[], physical_addresses=[],  \
                       electronic_addresses=[], summary_policies=[],  \
                       summary_history=None):
        assert isinstance(institution_identifier, CodeOrIdentifier)
        self.institution_identifier = institution_identifier
        assert all(isinstance(physical_location, str) for physical_location in physical_locations)
        self.physical_locations = physical_locations
        assert all(isinstance(physical_address, str) or isinstance(physical_address, Component) \
                   for physical_address in physical_addresses)
        self.physical_addresses = physical_addresses
        assert all(isinstance(electronic_address, str) or isinstance(electronic_address, Component) \
                   for electronic_address in electronic_addresses)
        self.electronic_addresses = electronic_addresses
        assert isinstance(holding, HoldingSimple) or isinstance(holding, HoldingStructured)
        self.holding = holding
        assert all(isinstance(summary_policy, SummaryPolicy) for summary_policy in summary_policies)
        self.summary_policies = summary_policies
        if summary_history:
            assert isinstance(summary_history, SummaryHistory)
        self.summary_history = summary_history
    def serialize_xml(self):
        # Returns an Element.
        holding_e = E('holding')
        # institutionIdentifier
        institution_identifier_e = E('institutionIdentifier')
        institution_identifier_code_or_identifier = self.institution_identifier.serialize_xml()
        institution_identifier_e.extend(institution_identifier_code_or_identifier)
        holding_e.append(institution_identifier_e)
        # physicalLocation*
        for physical_location in self.physical_locations:
            physical_location_e = E('physicalLocation')
            physical_location_e.text = physical_location
            holding_e.append(physical_location_e)
        # physicalAddress*
        for physical_address in self.physical_addresses:
            physical_address_e = E('physicalAddress')
            if isinstance(physical_address, str):
                physical_address_text_e = E('text')
                physical_address_text_e.text = physical_address
                physical_address_e.append(physical_address_text_e)
            else:
                physical_address_content_e = physical_address.serialize_xml()
                assert isinstance(physical_address_content_e, _Element)
                physical_address_e.append(physical_address_content_e)
            holding_e.append(physical_address_e)
        # electronicAddress*
        for electronic_address in self.electronic_addresses:
            electronic_address_e = E('electronicAddress')
            if isinstance(electronic_address, str):
                electronic_address_text_e = E('text')
                electronic_address_text_e.text = electronic_address
                electronic_address_e.append(electronic_address_text_e)
            else:
                electronic_address_content_e = electronic_address.serialize_xml()
                assert isinstance(electronic_address_content_e, _Element)
                electronic_address_e.append(electronic_address_content_e)
            holding_e.append(electronic_address_e)
        # holdingSimple / holdingStructured
        holding_simple_or_structured_e = self.holding.serialize_xml()
        holding_e.append(holding_simple_or_structured_e)
        # summaryPolicy*
        summary_policy_elements = [summary_policy.serialize_xml() for summary_policy in self.summary_policies]
        holding_e.extend(summary_policy_elements)
        # summaryHistory?
        if self.summary_history:
            summary_history_e = self.summary_history.serialize_xml()
            holding_e.append(summary_history_e)
        return holding_e


class HoldingSimple(Component):
    """
    element holdingSimple {
      element copiesSummary {
        element copiesCount {
          [ a:defaultValue = "1" ]
          xs:positiveInteger
        },
        element status { statusType }*,
        element reservationQueueLength { xs:nonNegativeInteger }?,
        element onOrderCount { xs:nonNegativeInteger }?,
      },
      element copyInformation {
        pieceIdentifier+,
        resourceIdentifier?,
        form?,
        element monetaryValuation { monetaryValuationType }?,
        sublocation*,
        shelfLocator*,
        element electronicLocator { electronicLocatorType }*,
        element note { xs:string }*,
        element enumerationAndChronology { enumChron }*,
        element availabilityInformation { availabilityInformationType }?
      }
    }
    """
    def __init__(self, piece_identifiers, copies_count=1, statuses=[],  \
                       reservation_queue_length=None, on_order_count=None,  \
                       resource_identifier=None, form=None, monetary_valuation=None,  \
                       sublocations=[], shelf_locators=[], electronic_locators=[],  \
                       notes=[], enum_chrons=[], availability_information=None):
        # <copiesSummary>
        assert (isinstance(copies_count, int) or copies_count.isdigit()) and int(copies_count) > 0
        self.copies_count = str(int(copies_count))
        assert all(isinstance(status, StatusType) for status in statuses)
        self.statuses = statuses
        if reservation_queue_length is not None:
            assert ( isinstance(reservation_queue_length, int) or reservation_queue_length.isdigit() )  \
                   and int(reservation_queue_length) >= 0
            reservation_queue_length = str(int(reservation_queue_length))
        self.reservation_queue_length = reservation_queue_length
        if on_order_count is not None:
            assert (isinstance(on_order_count, int) or on_order_count.isdigit()) \
                   and int(on_order_count) >= 0
            on_order_count = str(int(on_order_count))
        self.on_order_count = on_order_count
        # <copyInformation>
        assert piece_identifiers and all(isinstance(piece_identifier, PieceIdentifier) for piece_identifier in piece_identifiers)
        self.piece_identifiers = piece_identifiers
        if resource_identifier is not None:
            assert isinstance(resource_identifier, ResourceIdentifier)
        self.resource_identifier = resource_identifier
        if form is not None:
            assert isinstance(form, Form)
        self.form = form
        if monetary_valuation is not None:
            assert isinstance(monetary_valuation, MonetaryValuationType)
        self.monetary_valuation = monetary_valuation
        assert all(isinstance(sublocation, Sublocation) for sublocation in sublocations)
        self.sublocations = sublocations
        assert all(isinstance(shelf_locator, ShelfLocator) for shelf_locator in shelf_locators)
        self.shelf_locators = shelf_locators
        assert all(isinstance(electronic_locator, ElectronicLocatorType) for electronic_locator in electronic_locators)
        self.electronic_locators = electronic_locators
        assert all(isinstance(note, str) for note in notes)
        self.notes = notes
        assert all(isinstance(enum_chron, EnumChron) for enum_chron in enum_chrons)
        self.enum_chrons = enum_chrons
        if availability_information is not None:
            assert isinstance(availability_information, AvailabilityInformationType)
        self.availability_information = availability_information
    def serialize_xml(self):
        # Returns an Element.
        holding_simple_e = E('holdingSimple')
        # <copiesSummary>
        copies_summary_e = E('copiesSummary')
        # -- <copiesCount>
        copies_count_e = E('copiesCount')
        copies_count_e.text = self.copies_count
        copies_summary_e.append(copies_count_e)
        # -- <status> *
        for status in self.statuses:
            status_elements = status.serialize_xml()
            if status_elements:
                status_e = E('status')
                status_e.extend(status_elements)
                copies_summary_e.append(status_e)
        # -- <reservationQueueLength> ?
        if self.reservation_queue_length is not None:
            reservation_queue_length_e = E('reservationQueueLength')
            reservation_queue_length_e.text = self.reservation_queue_length
            copies_summary_e.append(reservation_queue_length_e)
        # -- <onOrderCount> ?
        if self.on_order_count is not None:
            on_order_count_e = E('onOrderCount')
            on_order_count_e.text = self.on_order_count
            copies_summary_e.append(on_order_count_e)
        holding_simple_e.append(copies_summary_e)
        # <copyInformation>
        copy_information_e = E('copyInformation')
        # -- <pieceIdentifier> +
        piece_identifier_elements = [piece_identifier.serialize_xml() for piece_identifier in self.piece_identifiers]
        copy_information_e.extend(piece_identifier_elements)
        # -- <resourceIdentifier> ?
        if self.resource_identifier is not None:
            resource_identifier_e = self.resource_identifier.serialize_xml()
            copy_information_e.append(resource_identifier_e)
        # -- <form> ?
        if self.form is not None:
            form_e = self.form.serialize_xml()
            copy_information_e.append(form_e)
        # -- <monetaryValuation> ?
        if self.monetary_valuation is not None:
            monetary_valuation_text, monetary_valuation_attrs = self.monetary_valuation.serialize_xml()
            monetary_valuation_e = E('monetaryValuation', **monetary_valuation_attrs)
            monetary_valuation_e.text = monetary_valuation_amount
            copy_information_e.append(monetary_valuation_e)
        # -- <sublocation> *
        sublocation_elements = [sublocation.serialize_xml() for sublocation in self.sublocations]
        copy_information_e.extend(sublocation_elements)
        # -- <shelfLocator> *
        shelf_locator_elements = [shelf_locator.serialize_xml() for shelf_locator in self.shelf_locators]
        copy_information_e.extend(shelf_locator_elements)
        # -- <electronicLocator> *
        for electronic_locator in self.electronic_locators:
            electronic_locator_content_e, electronic_locator_attrs = electronic_locator.serialize_xml()
            electronic_locator_e = E('electronicLocator', **electronic_locator_attrs)
            electronic_locator_e.append(electronic_locator_content_e)
            copy_information_e.append(electronic_locator_e)
        # -- <note> *
        for note in self.notes:
            note_e = E('note')
            note_e.text = note
            copy_information_e.append(note_e)
        # -- <enumerationAndChronology> *
        for enum_chron in self.enum_chrons:
            enum_chron_content_e, enum_chron_attrs = enum_chron.serialize_xml()
            enum_chron_e = E('enumerationAndChronology', **enum_chron_attrs)
            enum_chron_e.append(enum_chron_content_e)
            copy_information_e.append(enum_chron_e)
        # -- <availabilityInformation> ?
        if self.availability_information is not None:
            availability_information_elements = self.availability_information.serialize_xml()
            copy_information_e.extend(availability_information_elements)
        holding_simple_e.append(copy_information_e)
        return holding_simple_e


class HoldingStructured(Component):
    """
    element holdingStructured {
      element set { ... }+
    }
    """
    def __init__(self, sets):
        assert all(isinstance(set_, HoldingStructuredSet) for set_ in sets)
        self.sets = sets
    def serialize_xml(self):
        # Returns an Element.
        holding_structured_e = E('holdingStructured')
        # set elements
        set_elements = [set_.serialize_xml() for set_ in self.sets]
        holding_structured_e.extend(set_elements)
        return holding_structured_e


class HoldingStructuredSet(Component):
    """
      element set {
        element label { xs:string }?,
        form?,
        sublocation?,
        element shelfLocator { xs:string }*,
        element electronicLocator { electronicLocatorType }*,
        element completeness {(
          string "0"      # info not available
          | string "1"    # complete
          | string "2"    # incomplete
          | string "3"    # very incomplete or scattered
        )}?,
        element enumerationAndChronology { ... }*,
        element retention {(
          string "0"      # unknown
          | string "2"    # replaced by updates
          | string "3"    # sample issue retained
          | string "4"    # replaced by preservation format
          | string "5"    # replaced by cumulation
          | string "6"    # limited retention
          | string "7"    # no retention
          | string "8"    # permanent retention
          | string ""     # ?
        )}?,
        resourceIdentifier?,
        element component { ... }*
      }
    """
    def __init__(self, label=None, form=None, sublocation=None, shelf_locators=[],
                       electronic_locators=[], completeness=None, enum_chrons=[],
                       retention=None, resource_identifier=None, components=[]):
        if label:
            assert isinstance(label, str)
        self.label = label
        if form is not None:
            assert isinstance(form, Form)
        self.form = form
        if sublocation is not None:
            assert isinstance(sublocation, Sublocation)
        self.sublocation = sublocation
        assert all(isinstance(shelf_locator, str) for shelf_locator in shelf_locators)
        self.shelf_locators = shelf_locators
        assert all(isinstance(electronic_locator, ElectronicLocatorType) for electronic_locator in electronic_locators)
        self.electronic_locators = electronic_locators
        if completeness is not None:
            assert (isinstance(completeness, int) or completeness.isdigit()) and 0 <= int(completeness) <= 3
            completeness = str(int(completeness))
        self.completeness = completeness
        assert all(isinstance(enum_chron, HoldingStructuredSetEnumerationAndChronology) \
                   for enum_chron in enum_chrons)
        self.enum_chrons = enum_chrons
        if retention not in [None, ""]:
            assert isinstance(retention, int) or retention.isdigit()
            retention = str(int(retention))
            assert len(retention) == 1 and retention in "02345678"
        self.retention = retention
        if resource_identifier is not None:
            assert isinstance(resource_identifier, ResourceIdentifier)
        self.resource_identifier = resource_identifier
        assert all(isinstance(component, HoldingStructuredSetComponent) \
                   for component in components)
        self.components = components
    def serialize_xml(self):
        # Returns an Element.
        set_e = E('set')
        # <label> ?
        if self.label:
            label_e = E('label')
            label_e.text = self.label
            set_e.append(label_e)
        # <form> ?
        if self.form is not None:
            form_e = self.form.serialize_xml()
            set_e.append(form_e)
        # <sublocation> ?
        if self.sublocation is not None:
            sublocation_e = self.sublocation.serialize_xml()
            set_e.append(sublocation_e)
        # <shelfLocator> *
        for shelf_locator in self.shelf_locators:
            shelf_locator_e = E('shelfLocator')
            shelf_locator_e.text = self.shelf_locator
            set_e.append(shelf_locator_e)
        # <electronicLocator> *
        for electronic_locator in self.electronic_locators:
            electronic_locator_content_e, electronic_locator_attrs = electronic_locator.serialize_xml()
            electronic_locator_e = E('electronicLocator', **electronic_locator_attrs)
            electronic_locator_e.append(electronic_locator_content_e)
            set_e.append(electronic_locator_e)
        # <completeness> ?
        if self.completeness is not None:
            completeness_e = E('completeness')
            completeness_e.text = self.completeness
            set_e.append(completeness_e)
        # <enumerationAndChronology> *
        enum_chron_elements = [enum_chron.serialize_xml() for enum_chron in self.enum_chrons]
        set_e.extend(enum_chron_elements)
        # <retention> ?
        if self.retention is not None:
            retention_e = E('retention')
            retention_e.text = self.retention
            set_e.append(retention_e)
        # <resourceIdentifier> ?
        if self.resource_identifier is not None:
            resource_identifier_e = self.resource_identifier.serialize_xml()
            set_e.append(resource_identifier_e)
        # <component> *
        component_elements = [component.serialize_xml() for component in self.components]
        set_e.extend(component_elements)
        return set_e


class HoldingStructuredSetEnumerationAndChronology(Component):
    """
    element enumerationAndChronology {
      [ a:defaultValue = "1" ]
      attribute unitType {(
        string "1"      # basic
        | string "2"    # supplement
        | string "3"    # index
      )}?,
      [ a:defaultValue = "0" ]
      attribute altNumbering { xs:boolean }?,
      attribute note { xs:string }?,
      element startingEnumAndChronology {(
        element text { text }
        |
        element structured {
          element enumeration { enumerationType }*,
          element chronology { chronologyType }*
        }
      )},
      element endingEnumAndChronology {(
        element text { text }
        |
        element structured {
          element enumeration { enumerationType }*,
          element chronology { chronologyType }*
        }
      )}?
    }
    """
    def __init__(self, starting, ending=None, unit_type=1, alt_numbering=0, note=None):
        if unit_type is not None:
            assert (isinstance(unit_type, int) or unit_type.isdigit()) and 1 <= int(unit_type) <= 3
            unit_type = str(int(unit_type))
        self.unit_type = unit_type
        if alt_numbering is not None:
            assert ((isinstance(alt_numbering, int) or alt_numbering.isdigit()) and int(alt_numbering) in [0,1]) \
                   or isinstance(alt_numbering, bool)
           # if bool, auto converts to binary bool (0/1)
            alt_numbering = str(int(alt_numbering))
        self.alt_numbering = alt_numbering
        if note is not None:
            assert isinstance(note, str)
        self.note = note
        # starting and ending should be either a string,
        # or a tuple ([EnumerationType, ...], [ChronologyType, ...])
        self.starting_is_str = isinstance(starting, str)
        assert self.starting_is_str or (len(starting) == 2 \
                                        and all(isinstance(e, EnumerationType) for e in starting[0]) \
                                        and all(isinstance(c, ChronologyType) for c in starting[1]))
        self.starting = starting
        self.ending_is_str = isinstance(ending, str)
        assert self.ending_is_str or (len(ending) == 2 \
                                      and all(isinstance(e, EnumerationType) for e in ending[0]) \
                                      and all(isinstance(c, ChronologyType) for c in ending[1]))
        self.ending = ending
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        enum_chron_attrs = {}
        if self.unit_type is not None:
            enum_chron_attrs['unitType'] = self.unit_type
        if self.alt_numbering is not None:
            enum_chron_attrs['altNumbering'] = self.alt_numbering
        if self.note is not None:
            enum_chron_attrs['note'] = self.note
        enum_chron_e = E('enumerationAndChronology', **enum_chron_attrs)
        # <startingEnumAndChronology>
        starting_e = E('startingEnumAndChronology')
        if self.starting_is_str:
            text_e = E('text')
            text_e.text = self.starting
            starting_e.append(text_e)
        else:
            structured_e = E('structured')
            starting_enums, starting_chrons = self.starting
            for starting_enum in starting_enums:
                starting_enum_contents, starting_enum_attrs = starting_enum.serialize_xml()
                starting_enum_e = E('enumeration', **starting_enum_attrs)
                starting_enum_e.extend(starting_enum_contents)
                structured_e.append(starting_enum_e)
            for starting_chron in starting_chrons:
                starting_chron_contents, starting_chron_attrs = starting_chron.serialize_xml()
                starting_chron_e = E('chronology', **starting_chron_attrs)
                starting_chron_e.extend(starting_chron_contents)
                structured_e.append(starting_chron_e)
            starting_e.append(structured_e)
        enum_chron_e.append(starting_e)
        # <endingEnumAndChronology> ?
        if self.ending is not None:
            ending_e = E('endingEnumAndChronology')
            if self.ending_is_str:
                text_e = E('text')
                text_e.text = self.starting
                ending_e.append(text_e)
            else:
                structured_e = E('structured')
                ending_enums, ending_chrons = self.starting
                for ending_enum in ending_enums:
                    ending_enum_contents, ending_enum_attrs = ending_enum.serialize_xml()
                    ending_enum_e = E('enumeration', **ending_enum_attrs)
                    ending_enum_e.extend(ending_enum_contents)
                    structured_e.append(ending_enum_e)
                for ending_chron in ending_chrons:
                    ending_chron_contents, ending_chron_attrs = ending_chron.serialize_xml()
                    ending_chron_e = E('chronology', **ending_chron_attrs)
                    ending_chron_e.extend(ending_chron_contents)
                    structured_e.append(ending_chron_e)
                ending_e.append(structured_e)
            enum_chron_e.append(ending_e)
        return enum_chron_e


class HoldingStructuredSetComponent(Component):
    """
    element component {
      pieceIdentifier+,
      form?,
      element monetaryValuation { monetaryValuationType }?,
      sublocation*,
      shelfLocator*,
      element electronicLocator { electronicLocatorType }*,
      element note { xs:string }*,
      element enumerationAndChronology { enumChron }+,
      element availabilityInformation { availabilityInformationType }?
    }
    """
    def __init__(self, piece_identifiers, enum_chrons, form=None, monetary_valuation=None,  \
                       sublocations=[], shelf_locators=[], electronic_locators=[],  \
                       notes=[], availability_information=None):
        assert piece_identifiers and all(isinstance(piece_identifier, PieceIdentifier) for piece_identifier in piece_identifiers)
        self.piece_identifiers = piece_identifiers
        if form is not None:
            assert isinstance(form, Form)
        self.form = form
        if monetary_valuation is not None:
            assert isinstance(monetary_valuation, MonetaryValuationType)
        self.monetary_valuation = monetary_valuation
        assert all(isinstance(sublocation, Sublocation) for sublocation in sublocations)
        self.sublocations = sublocations
        assert all(isinstance(shelf_locator, ShelfLocator) for shelf_locator in shelf_locators)
        self.shelf_locators = shelf_locators
        assert all(isinstance(electronic_locator, ElectronicLocatorType) for electronic_locator in electronic_locators)
        self.electronic_locators = electronic_locators
        assert all(isinstance(note, str) for note in notes)
        self.notes = notes
        assert enum_chron and all(isinstance(enum_chron, EnumChron) for enum_chron in enum_chrons)
        self.enum_chrons = enum_chrons
        if availability_information is not None:
            assert isinstance(availability_information, AvailabilityInformationType)
        self.availability_information = availability_information
    def serialize_xml(self):
        # Returns an Element.
        component_e = E('component')
        # <pieceIdentifier> +
        piece_identifier_elements = [piece_identifier.serialize_xml() for piece_identifier in self.piece_identifiers]
        component_e.extend(piece_identifier_elements)
        # <form> ?
        if self.form is not None:
            form_e = self.form.serialize_xml()
            component_e.append(form_e)
        # <monetaryValuation> ?
        if self.monetary_valuation is not None:
            monetary_valuation_text, monetary_valuation_attrs = self.monetary_valuation.serialize_xml()
            monetary_valuation_e = E('monetaryValuation', **monetary_valuation_attrs)
            monetary_valuation_e.text = monetary_valuation_amount
            component_e.append(monetary_valuation_e)
        # <sublocation> *
        sublocation_elements = [sublocation.serialize_xml() for sublocation in self.sublocations]
        component_e.extend(sublocation_elements)
        # <shelfLocator> *
        shelf_locator_elements = [shelf_locator.serialize_xml() for shelf_locator in self.shelf_locators]
        component_e.extend(shelf_locator_elements)
        # <electronicLocator> *
        for electronic_locator in self.electronic_locators:
            electronic_locator_content_e, electronic_locator_attrs = electronic_locator.serialize_xml()
            electronic_locator_e = E('electronicLocator', **electronic_locator_attrs)
            electronic_locator_e.append(electronic_locator_content_e)
            component_e.append(electronic_locator_e)
        # <note> *
        for note in self.notes:
            note_e = E('note')
            note_e.text = note
            component_e.append(note_e)
        # <enumerationAndChronology> +
        for enum_chron in self.enum_chrons:
            enum_chron_content_e, enum_chron_attrs = enum_chron.serialize_xml()
            enum_chron_e = E('enumerationAndChronology', **enum_chron_attrs)
            enum_chron_e.append(enum_chron_content_e)
            component_e.append(enum_chron_e)
        # <availabilityInformation> ?
        if self.availability_information is not None:
            availability_information_elements = self.availability_information.serialize_xml()
            component_e.extend(availability_information_elements)
        return component


class SummaryPolicy(Component):
    """
    element summaryPolicy {
        form,
        element availability {
          availableFor,
          ( element text { xs:string } | xs:any )
        }+,
        reservationPolicy?,
        element feeInformation { feeInformationType }?
    }
    """
    def __init__(self, form, availabilities, reservation_policy=None, fee_information=None):
        if form is not None:
            assert isinstance(form, Form)
        self.form = form
        # availabilities should be a list of tuples
        assert availabilities and all(len(availability) == 2 for availability in availabilities)
        for availability in availabilities:
            available_for, text_or_element = availability
            assert isinstance(available_for, AvailableFor)
            assert isinstance(text_or_element, str) or isinstance(text_or_element, _Element)
        self.availabilities = availabilities
        if reservation_policy is not None:
            assert isinstance(reservation_policy, ReservationPolicy)
        self.reservation_policy = reservation_policy
        if fee_information is not None:
            assert isinstance(fee_information, FeeInformationType)
        self.fee_information = fee_information
    def serialize_xml(self):
        # Returns an Element.
        summary_policy_e = E('summaryPolicy')
        # <form> ?
        if self.form is not None:
            form_e = self.form.serialize_xml()
            summary_policy_e.append(form_e)
        # <availability> +
        for availability in availabilities:
            availability_e = E('availability')
            available_for, text_or_element = availability
        # <reservationPolicy> ?
        if self.reservation_policy is not None:
            reservation_policy_e = self.reservation_policy.serialize_xml()
            summary_policy_e.append(reservation_policy_e)
        # <feeInformation> ?
        if self.fee_information is not None:
            fee_information_e = E('feeInformation')
            fee_information_content_elements = self.fee_information.serialize_xml()
            fee_information_e.extend(fee_information_content_elements)
            summary_policy_e.append(fee_information_e)
        return summary_policy_e


class SummaryHistory(Component):
    """
    element summaryHistory {
        element countPeriod {
          element countPeriodStart { xs:dateTime },
          element countPeriodEnd { xs:dateTime },
          element totalCirculation {
            element totalCirculationCount { xs:nonNegativeInteger },
            element totalLoansCount { xs:nonNegativeInteger }?,
            element totalDCBCount { xs:nonNegativeInteger }?,
            element totalILL {
              element totalILLCount { xs:nonNegativeInteger },
              element totalILLLent { xs:nonNegativeInteger }?,
              element totalILLBorrowed { xs:nonNegativeInteger }?,
            }?,
          }?,    # end <totalCirculation>
          element totalReservationsCount { xs:nonNegativeInteger }?,
          element totalAccessCount { xs:nonNegativeInteger }?,
          element copiesCount {
            element totalCopiesHeld { xs:positiveInteger }?,
            element totalAcquired {
              element totalAcquiredCount { xs:nonNegativeInteger },
              element collection {
                element totalCollectionCount { xs:positiveInteger },
                element collectionProfile {
                  element collectionCode { text },
                  element collectionDescription { text }
                }*
              }*
            }?,
            element totalDiscardedCount { xs:nonNegativeInteger }?
          }    # end <copiesCount>
        }*,    # end <countPeriod>
        element lastActivityInfo {
          element lastActivityDate { xs:dateTime },
          element lastActivityType { codeOrIdentifier }?
        }*
    }
    """
    def __init__(self):
        ...
        ...
        print("WARNING: SummaryHistory not yet implemented")
        ...
        ...
    def serialize_xml(self):
        # Returns an Element.
        # summary_history_e = E('summaryHistory')
        ...
        ...
        ...
        ...
        # return summary_history_e


class EnumChron(Component):
    """
    enumChron =
      [ a:defaultValue = "1" ]
      attribute unitType {(
        string "1"      # basic
        | string "2"    # supplement
        | string "3"    # index
      )}?,
      [ a:defaultValue = "0" ]
      attribute altNumbering { xs:boolean }?,
      attribute note { xs:string }?,
      (
        element text { text }
        |
        element structured {
          element enumeration { enumerationType }*,
          element chronology { chronologyType }*,
        }
      )
    """
    def __init__(self, enum_chron_contents, unit_type=1, alt_numbering=0, note=None):
        if unit_type is not None:
            assert (isinstance(unit_type, int) or unit_type.isdigit()) and 1 <= int(unit_type) <= 3
            unit_type = str(int(unit_type))
        self.unit_type = unit_type
        if alt_numbering is not None:
            assert ((isinstance(alt_numbering, int) or alt_numbering.isdigit()) and int(alt_numbering) in [0,1]) \
                   or isinstance(alt_numbering, bool)
           # if bool, auto converts to binary bool (0/1)
            alt_numbering = str(int(alt_numbering))
        self.alt_numbering = alt_numbering
        if note is not None:
            assert isinstance(note, str)
        self.note = note
        # contents should be either a string,
        # or a tuple/list ([EnumerationType, ...], [ChronologyType, ...])
        self.is_str = isinstance(enum_chron_contents, str)
        assert self.is_str or (len(enum_chron_contents) == 2 \
                               and all(isinstance(e, EnumerationType) for e in enum_chron_contents[0]) \
                               and all(isinstance(c, ChronologyType) for c in enum_chron_contents[1]))
        self.enum_chron_contents = enum_chron_contents
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        enum_chron_attrs = {}
        if self.unit_type is not None:
            enum_chron_attrs['unitType'] = self.unit_type
        if self.alt_numbering is not None:
            enum_chron_attrs['altNumbering'] = self.alt_numbering
        if self.note is not None:
            enum_chron_attrs['note'] = self.note
        enum_chron_e = E('enumerationAndChronology', **enum_chron_attrs)
        # <enum_chron_contentsEnumAndChronology>
        enum_chron_contents_e = E('enum_chron_contentsEnumAndChronology')
        if self.is_str:
            text_e = E('text')
            text_e.text = self.enum_chron_contents
            enum_chron_contents_e.append(text_e)
        else:
            structured_e = E('structured')
            enums, chrons = self.enum_chron_contents
            for enum in enums:
                enum_contents, enum_attrs = enum.serialize_xml()
                enum_e = E('enumeration', **enum_attrs)
                enum_e.extend(enum_contents)
                structured_e.append(enum_e)
            for chron in chrons:
                chron_contents, chron_attrs = chron.serialize_xml()
                chron_e = E('chronology', **chron_attrs)
                chron_e.extend(chron_contents)
                structured_e.append(chron_e)
            enum_chron_contents_e.append(structured_e)
        enum_chron_e.append(enum_chron_contents_e)
        return enum_chron_e


class CodeOrIdentifier(Component):
    """
    codeOrIdentifier =
      element value { text },
      element typeOrSource {(
        element pointer { xs:anyURI }
        | element text { text }
      )}
    """
    def __init__(self, value, type_or_source):
        assert isinstance(value, str)
        self.value = value
        self.is_pointer = isinstance(type_or_source, XSDAnyURI)
        assert self.is_pointer or isinstance(type_or_source, str)
        self.type_or_source = type_or_source
    def serialize_xml(self):
        # Returns a list of two Elements.
        value_e = E('value')
        value_e.text = self.value
        type_or_source_e = E('typeOrSource')
        if self.is_pointer:
            pointer_e = E('pointer')
            pointer_e.text = self.type_or_source.serialize_xml()
            type_or_source_e.append(pointer_e)
        else:
            text_e = E('text')
            text_e.text = self.type_or_source
            type_or_source_e.append(text_e)
        return [value_e, type_or_source_e]


class AvailabilityInformationType(Component):
    """
    availabilityInformationType =
      element status {
        [ a:defaultValue = "0" ]
        element availabilityStatus {(
          string "0"      # unknown
          | string "1"    # available
          | string "2"    # not available
          | string "3"    # possibly available
        )}?,
        availableFor?,
        element dateTimeAvailable { xs:dateTime }?
      }*,
      element policy { xs:any }?,
      element feeInformation { feeInformationType }?,
      reservationPolicy?,
      element reservationQueue { xs:nonNegativeInteger }?
    """
    def __init__(self, statuses=[], policy=None, fee_information=None, reservation_policy=None, reservation_queue=None):
        # each status must have 3 parts
        statuses_normalized = []
        for status in statuses:
            assert len(status) == 3
            availability_status, available_for, date_time_available = status
            if availability_status is not None:
                assert (isinstance(availability_status, int) or availability_status.isdigit()) and 0 <= int(availability_status) <= 3
                availability_status = str(int(availability_status))
            if available_for is not None:
                assert isinstance(available_for, AvailableFor)
            if date_time_available is not None:
                assert isinstance(date_time_available, XSDDateTime)
            statuses_normalized.append((availability_status, available_for, date_time_available))
        self.statuses = statuses_normalized
        if policy is not None:
            assert isinstance(policy, _Element)
        self.policy = policy
        if fee_information is not None:
            assert isinstance(fee_information, FeeInformationType)
        self.fee_information = fee_information
        if reservation_policy is not None:
            assert isinstance(reservation_policy, ReservationPolicy)
        self.reservation_policy = reservation_policy
        if reservation_queue is not None:
            assert (isinstance(reservation_queue, int) or reservation_queue.isdigit()) and 0 <= int(reservation_queue)
            reservation_queue = str(int(reservation_queue))
        self.reservation_queue = reservation_queue
    def serialize_xml(self):
        # Returns a list of 0 or more Elements.
        elements = []
        for status in self.statuses:
            status_e = E('status')
            availability_status, available_for, date_time_available = status
            if availability_status is not None:
                availability_status_e = E('availabilityStatus')
                availability_status_e.text = availability_status
                status_e.append(availability_status_e)
            if available_for is not None:
                available_for_e = available_for.serialize_xml()
                status_e.append(available_for_e)
            if date_time_available is not None:
                date_time_available_e = E('dateTimeAvailable')
                date_time_available_e.text = date_time_available.serialize_xml()
                status_e.append(date_time_available_e)
            elements.append(status_e)
        if self.policy is not None:
            policy_e = E('policy')
            policy_e.append(self.policy)
            elements.append(policy_e)
        if self.fee_information is not None:
            fee_information_e = E('feeInformation')
            fee_information_content_elements = elf.fee_information.serialize_xml()
            fee_information_e.extend(fee_information_content_elements)
            elements.append(fee_information_e)
        if self.reservation_policy is not None:
            reservation_policy_e = self.reservation_policy.serialize_xml()
            elements.append(reservation_policy_e)
        if self.reservation_queue is not None:
            reservation_queue_e = E('reservationQueue')
            reservation_queue_e.text = self.reservation_queue
            elements.append(reservation_queue_e)
        return elements


class StatusType(Component):
    """
    statusType =
      element availableCount { xs:nonNegativeInteger }?,
      availableFor?,
      element earliestDispatchDate { xs:dateTime }?,
    """
    def __init__(self, available_count=None, available_for=None, earliest_dispatch_date=None):
        if available_count is not None:
            assert (isinstance(available_count, int) or available_count.isdigit()) \
                   and int(available_count) >= 0
            available_count = str(int(available_count))
        self.available_count = available_count
        if available_for is not None:
            assert isinstance(available_for, AvailableFor)
        self.available_for = available_for
        if earliest_dispatch_date is not None:
            assert isinstance(earliest_dispatch_date, XSDDateTime)
        self.earliest_dispatch_date = earliest_dispatch_date
    def serialize_xml(self):
        # Returns a list of 0 to 3 Elements.
        elements = []
        if self.available_count is not None:
            available_count_e = E('availableCount')
            available_count_e.text = self.available_count
            elements.append(available_count_e)
        if self.available_for is not None:
            available_for_e = available_for.serialize_xml()
            elements.append(available_for_e)
        if self.earliest_dispatch_date is not None:
            earliest_dispatch_date_e = E('earliestDispatchDate')
            earliest_dispatch_date_e.text = earliest_dispatch_date.serialize_xml()
            elements.append(earliest_dispatch_date_e)
        return elements


class PieceIdentifier(Component):
    """
    pieceIdentifier =
      element pieceIdentifier { codeOrIdentifier }
    """
    def __init__(self, code_or_identifier):
        assert isinstance(code_or_identifier, CodeOrIdentifier)
        self.code_or_identifier = code_or_identifier
    def serialize_xml(self):
        # Returns an Element.
        piece_identifier_e = E('pieceIdentifier')
        code_or_identifier_elements = self.code_or_identifier.serialize_xml()
        piece_identifier_e.extend(code_or_identifier_elements)
        return piece_identifier_e


class ResourceIdentifier(Component):
    """
    resourceIdentifier =
      element resourceIdentifier { codeOrIdentifier }
    """
    def __init__(self, code_or_identifier):
        assert isinstance(code_or_identifier, CodeOrIdentifier)
        self.code_or_identifier = code_or_identifier
    def serialize_xml(self):
        # Returns an Element.
        resource_identifier_e = E('resourceIdentifier')
        code_or_identifier_elements = self.code_or_identifier.serialize_xml()
        resource_identifier_e.extend(code_or_identifier_elements)
        return resource_identifier_e


class Form(Component):
    """
    form =
      element form { codeOrIdentifier }
    """
    def __init__(self, code_or_identifier):
        assert isinstance(code_or_identifier, CodeOrIdentifier)
        self.code_or_identifier = code_or_identifier
    def serialize_xml(self):
        # Returns an Element.
        form_e = E('form')
        code_or_identifier_elements = self.code_or_identifier.serialize_xml()
        form_e.extend(code_or_identifier_elements)
        return form_e


class ElectronicLocatorType(Component):
    """
    electronicLocatorType =
      attribute accessRestrictions {
        string "0"      # unknown
        | string "1"    # unrestricted access
        | string "2"    # access with authorization
        | string "3"    # preview only
        | string "4"    # no online access
        | string "5"    # restrictions unspecified
        | string "6"    # access restricted URL based
        | string ""     # ?
      }?,
      (
        element pointer { xs:anyURI }
        | element text { text }
      )
    """
    def __init__(self, pointer_or_text, access_restrictions=None):
        if access_restrictions not in [None, ""]:
            assert (isinstance(access_restrictions, int) or access_restrictions.isdigit()) and 0 <= int(access_restrictions) <= 6
            access_restrictions = str(int(access_restrictions))
        self.access_restrictions = access_restrictions
        assert self.is_pointer or isinstance(pointer_or_text, str)
        self.pointer_or_text = pointer_or_text
    def serialize_xml(self):
        # Returns an Element and a dict of parent attributes.
        attrs = {}
        if self.access_restrictions is not None:
            attrs['accessRestrictions'] = self.access_restrictions
        if self.is_pointer:
            content_e = E('pointer')
            content_e.text = self.pointer_or_text.serialize_xml()
        else:
            content_e = E('text')
            content_e.text = self.pointer_or_text
        return content_e, attrs


class ShelfLocator(Component):
    """
    shelfLocator =
      element shelfLocator { xs:string }
    """
    def __init__(self, shelf_locator):
        assert isinstance(shelf_locator, str)
        self.shelf_locator = shelf_locator
    def serialize_xml(self):
        # Returns an Element.
        shelf_locator_e = E('shelfLocator')
        shelf_locator_e.text = self.shelf_locator
        return shelf_locator_e


class Sublocation(Component):
    """
    sublocation =
      element sublocation { xs:string }
    """
    def __init__(self, sublocation):
        assert isinstance(sublocation, str)
        self.sublocation = sublocation
    def serialize_xml(self):
        # Returns an Element.
        sublocation_e = E('sublocation')
        sublocation_e.text = self.sublocation
        return sublocation_e


class MonetaryValuationType(Component):
    """
    monetaryValuationType =
      attribute currencyCode { xs:string }?,
      xs:decimal
    """
    def __init__(self, valuation, currency_code=None, valuation_format_string='{:.2f}'):
        if currency_code is not None:
            assert isinstance(currency_code, str)
        self.currency_code = currency_code
        try:
            valuation = float(valuation)
        except:
            raise ValueException("valuation must be expressible as float")
        self.valuation = valuation_format_string.format(valuation)
    def serialize_xml(self):
        # Returns a text string and a dict of parent attributes.
        attrs = {}
        if self.currency_code is not None:
            attrs['currencyCode'] = self.currency_code
        return self.valuation, attrs


class FeeInformationType(Component):
    """
    feeInformationType = (
        element feeText { text }
        | element feeStructured {
          element feeReason { xs:string }?,
          element feeUnit { xs:string }?,
          element feeAmount { monetaryValuationType }
        }+
      )
    """
    def __init__(self, ):
        ...
    def serialize_xml(self):
        # Returns a list of 1 or more Elements.

        # holdings_e = E('holdings', **nons)
        ...


class EnumerationType(Component):
    """
    enumerationType =
      attribute level { xs:integer },
      element caption { text }?,
      element value { text }
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns a list of 1 or 2 Elements and a dict of parent attributes.

        # holdings_e = E('holdings', **nons)
        ...


class ChronologyType(Component):
    """
    chronologyType =
      attribute level { xs:integer }?,
      element caption { text }?,
      element value { text }
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns a list of 1 or 2 Elements and a dict of parent attributes.

        # holdings_e = E('holdings', **nons)
        ...


class AvailableFor(Component):
    """
    availableFor =
      element availableFor {(
        string "0"      # unspecified
        | string "1"    # loan:  request for a loan of a physical resource
        | string "2"    # physical copy:  request for a physical copy of a physical or digital resource to be made available for collection or delivery
        | string "3"    # digital copy:  request for a digital copy of a physical or digital resource to be made available, e.g. PDF to be made available for collection from a website or delivery to an email address
        | string "4"    # online access:  request for authorisation to access a digital resource
        | string "5"    # reference look-up:  request for consultation of a resource by a reference service, e.g. to consult the index or table of contents to determine if specific content is present
        | string "6"    # other
      )}
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns an Element.

        # holdings_e = E('holdings', **nons)
        ...


class ReservationPolicy(Component):
    """
    reservationPolicy =
      element reservationPolicy {(
        string "0"      # unknown
        | string "1"    # will accept
        | string "2"    # will not accept
        | string "3"    # will possibly accept
      )}
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns an Element.

        # holdings_e = E('holdings', **nons)
        ...
