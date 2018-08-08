# Recurring Attributes

* **role** — Used on "substantive" Principal Elements (Place/Being/Object/Work) to indicate the _role(s) served by the record_: `authority`, `instance`, or `authority instance`.
* **type** — Indicates membership as one of a _limited group of prescribed choices_ for various elements.
  - Record: ***generic type***
  - Principal Elements
    - Being: `human`, `nonhuman`, `special`
      - Being entry: ***generic type*** (legal name, pseudonym, etc.)
        - Being entry name parts: `given`, (`surname` | `paternal surname`, `maternal surname`), `patronym`, `matronym`, `teknonym`, `expansion`
    - Concept: `abstract`, `collective`, `control`, `specific`
      - Concept subtype: `general`, `form`, `topical`, `unspecified`
    - Event: `natural`, `meeting`, `journey`, `occurrence`, `miscellaneous`
    - Language: `natural`, `constructed`, `script`
    - Object: `natural`, `crafted`, `manufactured`
    - Organization: `business`, `government`, `nonprofit`, `other`
    - Place: `natural`, `constructed`, `jurisdictional`
    - String: `textual`, `numeric`, `mixed`
    - Time: ***generic type***
    - Work: `intellectual`, `artistic`
      - Work Parts: `subtitle`, `section`, `generic`
  - Relationship: `subordinate`, `superordinate`, `preordinate`, `postordinate`, `associative`, `dissociative`
* **class** — Represents a _broad category_ of Entry, often `individual`, `collective`, or `referential`, but varies by Principal Element.
  - Being: `individual`, `familial`, `collective`, `undifferentiated`, `referential`
  - Concept: _none_
  - Event: `individual`, `collective`, `referential`
    - _"While events are typically collective, individual is offered in reference to solo performances and for single natural occurrences. The referential value serves informational records with indirect associations to actual events"_
  - Language: `individual`, `collective`, `referential`
  - Object
    - Object authority: `individual`, `collective`, `referential`
    - Object instance or authority-instance: `individual`, `collective`
      - _"collective: Diamonds, Uncut; Minerals of Oklahoma; Collection of Teapots; Tea Service (Frost, V. : undated)"_
  - Organization: `individual`, `collective`, `referential`
    - _""_
  - Place: `individual`, `collective`, `referential`
  - String: `word`, `phrase`
  - Time: `individual`, `collective`, `referential`
    - _""_
  - Work: `individual`, `serial`, `collective`, `referential`
    - _"collective: Collections; Databases; Loose-leaf Services; Websites"_
    - _"Assembled collections are collective, as are "integrative" works."_
* **type** of **note**
  - `transcription`: Designates transcribed information and may contain supplied data in brackets; could be quoted in display
  - `annotation`: Data supplied by the cataloger for public display
  - `documentation`: Data supplied by the cataloger typically not for public display
  - `description`: A transitional value when description cannot be parsed for association with the proper Principal Element or Relationship
  - `unspecified`
* **degree** — Used on a Relationship to indicate its _relative strength_, usually `primary` or `secondary`, but for conceptual ones, also `broad` and `tertiary`.
* **scheme** — Indicates the _authoritative work_ containing the term used. Code (an entry substitute) for the Entry of a Work is used to control the value of another Entry or Variant, typically a Concept. e.g. `LCSH`, `MeSH`, ...
* **substitute** — <del>Indicates _which Substitute Entry_ (`abbrev`/`citation`/`code`/`singular`) is used as a part of the Qualifiers element of another Entry or in a Relationship. Its absence means the Entry is used. The 'scheme' attribute uses `code` by default.</del> A boolean attribute indicating:
  - whether the text of a particular variant may be used as a substitute for the text of the main entry in a reference, or
  - whether a reference to an entry is using such a substitute value.
* **set** — Used within a link to designate the category of records expected to be used in this sort of link. E.g. as a main or variant entry type: link href --> "Pseudonym"; set --> "Variant Type".
* **included** — Used to denote subsumed (`narrow`)/supersumed (`broader`)/circumsumed (`related`) variants.

# Builders

## RecordBuilder
```
# Organization owning/managing the record; or text description of the ID.
set_id_org_ref_or_description ( id_org_ref_or_description )  # OrganizationRef or str

# Record ID.
set_id_value ( id_value )  # str

# Other record IDs (LCCN, etc.).
add_id_alternate ( id_org_ref_or_description,
                   id_value )

# Type of record (e.g. original, derivative, suppressed?)
add_type ( xlink_title = None,  # str
           xlink_href = None,   # URI
           set_ref = None )  # URI  [Subset(?)]

set_principal_element ( principal_element )  # PrincipalElement

add_action ( time_or_duration_ref,  # TimeRef or DurationRef
             xlink_title = None,    # str
             xlink_href = None,     # str (URI)
             set_ref = None )    # str (URI)  [*Action Type(?)]

add_relationship ( relationship )   # Relationship
```

------------------------------------------------------

## Being

### BeingBuilder
```
set_role ( new_role )

set_type ( new_type )

set_class ( new_class )

set_scheme ( new_scheme )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )

# Most main entries don't have a generic type, but Being records may
# be for real names or pseudonyms (unlike other principal elements).
set_entry_type ( link_title,
                 set_URI,
                 href_URI = None )

# Since Being entries have a generic type, this is separated out because it is referencing the time/duration of the entry TYPE.
set_time_or_duration_ref ( time_or_duration_ref )

add_name ( name_text,
           type_  = "generic", # "generic" -or- <part>s with "given", "surname", "patronym", etc.
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### BeingVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )  # variant type (pseudonym/birth name/etc)

set_time_or_duration_ref ( time_or_duration_ref )  # time/duration qualifier for the type

set_substitute_attribute ( substitute_attribute )  # optional

set_scheme ( new_scheme )

add_name ( name_text,
           type_  = "generic",
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### BeingRefBuilder
```
add_name ( name_text,
           type_  = "generic",
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

set_link ( link_title,
           href_URI = None )
```

## Concept

### ConceptBuilder
```
set_type ( new_type )  # abstract, collective, control, specific

set_usage ( new_usage )  # subdivision ?

# Only used when usage = "subdivision"; type of subdivision
set_subtype ( new_subtype )  # general, form, topical, unspecified

set_scheme ( new_scheme )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### ConceptVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute ( substitute_attribute )

set_scheme ( new_scheme )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### ConceptRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_subdivision_link ( content_text,
                       content_lang = None,
                       link_title = None,
                       href_URI = None,
                       substitute = None )
```

## Event

### EventBuilder
```
set_type ( new_type )  # natural, meeting, journey, occurrence, miscellaneous

set_class ( new_class )  # individual, collective, referential

set_scheme ( new_scheme )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### EventVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute ( substitute_attribute )

set_scheme ( new_scheme )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### EventRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement
```

## Language

### LanguageBuilder
```
set_class ( new_class )  # individual, collective, referential

set_usage ( new_usage )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### LanguageVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute ( substitute_attribute )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### LanguageRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_subdivision_link ( content_text,
                       content_lang = None,
                       link_title = None,
                       href_URI = None,
                       substitute = None )
```

## Object

### ObjectBuilder
```
set_role ( new_role )  # authority, instance, authority instance

set_class ( new_class )  # individual, collective, referential [aut only]

set_type ( new_type )  # natural, crafted, manufactured

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

set_organization ( org_ref )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )

set_holdings ( versions_holdings_opt )
```

### ObjectVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute ( substitute_attribute )

set_scheme ( new_scheme )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### ObjectRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement
```

## Organization

### OrganizationBuilder
```
set_type ( new_type )  # business, government, nonprofit, other

set_class ( new_class )  # individual, collective, referential

set_scheme ( new_scheme )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### OrganizationVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute ( substitute_attribute )

set_scheme ( new_scheme )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### OrganizationRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_subdivision_link ( content_text,
                       content_lang = None,
                       link_title = None,
                       href_URI = None,
                       substitute = None )
```

## Place

### PlaceBuilder
```
set_role ( new_role )  # authority, instance, authority instance

set_type ( new_type )  # natural, constructed, jurisdictional

set_class ( new_class )  # individual, collective, referential

set_usage ( new_usage )

set_scheme ( new_scheme )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### PlaceVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute ( substitute_attribute )

set_scheme ( new_scheme )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### PlaceRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement
```

## String

### StringBuilder
```
set_type ( new_type )  # textual, numeric, mixed

set_class ( new_class )  # word, phrase

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_pos ( pos_text,
          pos_lang = None,
          xlink_title = None,
          xlink_href = None )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### StringVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute ( substitute_attribute )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_pos ( pos_text,
          pos_lang = None,
          xlink_title = None,
          xlink_href = None )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### StringRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_pos ( pos_text,
          pos_lang = None,
          xlink_title = None,
          xlink_href = None )

add_qualifier ( qualifier )  # RefElement
```

## Time

### TimeContentSingleBuilder
```
set_type ( link_title,
           set_URI,    # Time Type
           href_URI = None )

set_certainty ( certainty )  # ["exact", "implied", "estimated", "approximate", None]

set_quality ( quality )  # ["before", "after", "early", "mid", "late", None] (0+)

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

set_time_contents ( year = None,
                    month = None,
                    day = None,
                    hour = None,
                    tz_hour = None,
                    minute = None,
                    tz_minute = None,
                    second = None,
                    milliseconds = None )
```

### TimeBuilder
```
set_class ( new_class )

set_usage ( new_usage )

set_scheme ( new_scheme )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_time_content_single ( time_content_single )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### DurationBuilder
```
set_class ( new_class )

set_usage ( new_usage )

set_scheme ( scheme1,
             scheme2 = "" )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_calendar1 ( link_title,
                set_URI,
                href_URI = None )

set_calendar2 ( link_title,
                set_URI,
                href_URI = None )

set_time_content1 ( time_content_single1,
                    time_content_single2 = None)

set_time_content2 ( time_content_single1,
                    time_content_single2 = None)

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### TimeVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_scheme ( new_scheme )

set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_time_content_single ( time_content_single )
```


### DurationVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

# empty string defaults to same as scheme1; use None for no scheme2
set_scheme ( scheme1,
             scheme2 = "" )

set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_calendar1 ( link_title,
                set_URI,
                href_URI = None )

set_calendar2 ( link_title,
                set_URI,
                href_URI = None )

set_time_content1 ( time_content_single1,
                  time_content_single2 = None )

set_time_content1_link ( link_title,
                         href_URI = None )

set_time_content2 ( time_content_single1,
                  time_content_single2 = None )

set_time_content2_link ( link_title,
                         href_URI = None )
```

### TimeRefBuilder
```
set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_link ( link_title,
           href_URI = None )

set_time_content ( time_content_single1,
                   time_content_single2 = None )
```

### DurationRefBuilder
```
set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_calendar1 ( link_title,
                set_URI,
                href_URI = None )

set_calendar2 ( link_title,
                set_URI,
                href_URI = None )

set_link ( link_title,
           href_URI = None )

set_time_content1 ( time_content_single1,
                    time_content_single2 = None )

set_time_content1_link ( link_title,
                       href_URI = None )

set_time_content2 ( time_content_single1,
                    time_content_single2 = None )

set_time_content2_link ( link_title,
                       href_URI = None )
```

## Work

### WorkBuilder
```
set_type ( new_type )  # intellectual, artistic

set_role ( new_role )  # authority, instance, or authority instance

set_class ( new_class )  # individual, serial, collective, referential

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

add_name ( name_text,
           type_  = "generic",
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )

set_holdings ( versions_holdings_opt )
```

### WorkVariantBuilder
```
set_included ( included )

set_entry_group_attributes ( id = None,
                             group = None,
                             preferred = None )  # bool

set_type ( link_title,
           set_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute ( substitute_attribute )

set_scheme ( new_scheme )

add_name ( name_text,
           type_  = "generic",
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_note ( content_text,
           content_lang = None,
           class_ = None,  # transcription, annotation, documentation, description
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### WorkRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           type_  = "generic",
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement
```

------------------------------------------------------

## RelationshipBuilder
```
set_type ( new_type )  [????? this has a type aut though: Relationship Type]

set_degree ( new_degree )

set_name ( name_text,
           name_lang = None )

set_modifier ( modifier_text,
              modifier_lang = None,
              modifier_nonfiling = 0 )

set_time_or_duration_ref ( time_or_duration_ref )

set_element_ref ( element_ref )
```

------------------------------------------------------

## Holdings

**TODO** -- implements (subset of?) [ISO 20775](https://www.loc.gov/standards/iso20775/)
