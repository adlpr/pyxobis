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
        if availability_information:
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
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
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
    def __init__(self):
        ...
    def serialize_xml(self):
        # # Returns an Element.
        # holdings_e = E('holdings', **nons)
        # # variant elements
        # holding_elements = [holding.serialize_xml() for holding in self.holdings]
        # holdings_e.extend(holding_elements)
        # # resource elements
        # resource_elements = [resource.serialize_xml() for resource in self.resources]
        # holdings_e.extend(resource_elements)
        # return holdings_e
        ...


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
    def __init__(self):
        ...
    def serialize_xml(self):
        # # Returns an Element.
        # holdings_e = E('holdings', **nons)
        # # variant elements
        # holding_elements = [holding.serialize_xml() for holding in self.holdings]
        # holdings_e.extend(holding_elements)
        # # resource elements
        # resource_elements = [resource.serialize_xml() for resource in self.resources]
        # holdings_e.extend(resource_elements)
        # return holdings_e
        ...


class SummaryPolicy(Component):
    """
    element summaryPolicy {
        form,
        element availability {
          availableFor,
          ( element text { xs:string } | xs:any )
        }+,
        reservationPolicy?,
        element feeInformation { feeInformationType }
    }
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # # Returns an Element.
        # holdings_e = E('holdings', **nons)
        # # variant elements
        # holding_elements = [holding.serialize_xml() for holding in self.holdings]
        # holdings_e.extend(holding_elements)
        # # resource elements
        # resource_elements = [resource.serialize_xml() for resource in self.resources]
        # holdings_e.extend(resource_elements)
        # return holdings_e
        ...


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
    def serialize_xml(self):
        # # Returns an Element.
        # holdings_e = E('holdings', **nons)
        # # variant elements
        # holding_elements = [holding.serialize_xml() for holding in self.holdings]
        # holdings_e.extend(holding_elements)
        # # resource elements
        # resource_elements = [resource.serialize_xml() for resource in self.resources]
        # holdings_e.extend(resource_elements)
        # return holdings_e
        ...


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
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns an Element and a dict of parent attributes.

        # holdings_e = E('holdings', **nons)
        ...


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
        self.is_pointer = isinstance(type_or_source, XLinkAnyURI)
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
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns a list of 0 or more Elements.

        # holdings_e = E('holdings', **nons)
        ...


class StatusType(Component):
    """
    statusType =
      element availableCount { xs:nonNegativeInteger }?,
      availableFor?,
      element earliestDispatchDate { xs:dateTime }?,
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns a list of 0 to 3 Elements.

        # holdings_e = E('holdings', **nons)
        ...


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
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns an Element.

        # holdings_e = E('holdings', **nons)
        ...


class Form(Component):
    """
    form =
      element form { codeOrIdentifier }
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns an Element.

        # holdings_e = E('holdings', **nons)
        ...


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
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns an Element and a dict of parent attributes.

        # holdings_e = E('holdings', **nons)
        ...


class ShelfLocator(Component):
    """
    shelfLocator =
      element shelfLocator { xs:string }
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns an Element.

        # holdings_e = E('holdings', **nons)
        ...


class Sublocation(Component):
    """
    sublocation =
      element sublocation { xs:string }
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns an Element.

        # holdings_e = E('holdings', **nons)
        ...


class MonetaryValuationType(Component):
    """
    monetaryValuationType =
      attribute currencyCode { xs:string }?,
      xs:decimal
    """
    def __init__(self):
        ...
    def serialize_xml(self):
        # Returns a text string and a dict of parent attributes.

        # holdings_e = E('holdings', **nons)
        ...


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
    def __init__(self):
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
