# Recurring Attributes

* **role** — Used on "substantive" Principal Elements (Place/Being/Object/Work) to indicate the _role(s) served by the record_: `authority`, `instance`, or `authority instance`.
* **type** — Indicates membership as one of a _limited group of prescribed choices_ for various elements.
  - Record: ***generic type***
  - Principal Elements
    - Being: `human`, `nonhuman`, `special`
      - Being entry: ***generic type*** (legal name, pseudonym, etc.)
        - Being entry name parts: `given`, `surname`, `paternal surname`, `maternal surname`, `expansion`
    - Concept: `abstract`, `collective`, `control`, `specific`
      - Concept subtype: `general`, `form`, `topical`, `unspecified`
    - Event: `natural`, `meeting`, `journey`, `occurrence`, `miscellaneous`
    - Language: _no type_
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
  - Language: `individual`, `collective`, `referential`
  - Object
    - Object authority: `individual`, `collective`, `referential`
    - Object instance or authority-instance: `individual`, `collective`
  - Organization: `individual`, `collective`, `referential`
  - Place: `individual`, `collective`, `referential`
  - String: `word`, `phrase`
  - Time: `individual`, `collective`, `referential`
  - Work: `individual`, `serial`, `collective`, `referential`
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

# Builders

## RecordBuilder
```
# Organization owning/managing the record.
set_id_org_ref ( id_org_ref )  # OrganizationRef

# Record ID.
set_id_value ( id_value )  # str

# Other record IDs (LCCN, etc.).
add_id_alternate ( id_org_ref,
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
# Required: ROLE and at least one NAME

set_role ( new_role )      # str

set_type ( new_type )      # str

set_class ( new_class )    # str

set_scheme ( new_scheme )  # str

# Most main entries don't have a generic type, but Being records may
# be for real names or pseudonyms (unlike other principal elements).
set_entry_type ( link_title,       # str
                 set_URI,         # str (URI)
                 href_URI = None ) # str (URI)

# Since Being entries have a generic type, this is separated out because it is referencing the time/duration of the entry TYPE.
set_time_or_duration_ref ( time_or_duration_ref )

add_name ( name_text,         # str
           type_  = "generic", # str ("generic" -or- <part>s with "given", "surname", "patronym", etc.)
           lang   = None,      # str (ISO 639-2/B?)
           script = None,   # str (ISO 15924?)
           nonfiling = 0 )     # int (>=0)

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )    # BeingVariantEntry

add_note ( content_text,        # str
           content_lang = None, # str (ISO 639-2/B?)
           class_ = None,       # str
           link_title = None,   # str
           href_URI = None,     # str (URI)
           set_URI = None )    # str (URI)
```

### BeingVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### ConceptVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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
set_type ( new_type )

set_class ( new_class )

set_scheme ( new_scheme )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### EventVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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
set_class ( new_class )

set_usage ( new_usage )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### LanguageVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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
set_role ( new_role )

set_class ( new_class )

set_type ( new_type )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

set_organization ( link_title,
                   link_href = None,
                   id_content = None,
                   id_content_lang = None )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )

set_holdings ( versions_holdings_opt )
```

### ObjectVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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
set_type ( new_type )

set_class ( new_class )

set_scheme ( new_scheme )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### OrganizationVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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
set_role ( new_role )

set_type ( new_type )

set_class ( new_class )

set_usage ( new_usage )

set_scheme ( new_scheme )

add_name ( name_text,
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### PlaceVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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
set_type ( new_type )  # "textual", "numeric", "mixed"

set_class ( new_class )  # "word", "phrase"

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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### StringVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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

### TimeContentBuilder
```
set_type ( link_title,
           set_URI,    # Time Type
           href_URI = None )

set_certainty ( certainty )  # ["exact", "implied", "estimated", "approximate", None]

set_quality ( quality )  # ["before", "after", "early", "mid", "late", None] (+)

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

set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_time_content ( time_content )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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

set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_calendar1 ( link_title,
                set_URI,
                href_URI = None )

set_calendar2 ( link_title,
                set_URI,
                href_URI = None )

set_time_entry1 ( time_content1,
                  time_content2 = None)

set_time_entry2 ( time_content1,
                  time_content2 = None)

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )
```

### TimeVariantBuilder
```
set_type ( link_title,
           set_URI,
           href_URI = None )

set_scheme ( new_scheme )

set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_time_content ( time_content )
```


### DurationVariantBuilder
```
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

set_time_entry1 ( time_content1,
                  time_content2 = None )

set_time_entry1_link ( link_title,
                       href_URI = None )

set_time_entry2 ( time_content1,
                  time_content2 = None )

set_time_entry2_link ( link_title,
                       href_URI = None )
```

### TimeRefBuilder
```
set_calendar ( link_title,
               set_URI,
               href_URI = None )

set_link ( link_title,
           href_URI = None )

set_time_entry ( time_content1,
                 time_content2 = None )
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

set_time_entry1 ( time_content1,
                  time_content2 = None )

set_time_entry1_link ( link_title,
                       href_URI = None )

set_time_entry2 ( time_content1,
                  time_content2 = None )

set_time_entry2_link ( link_title,
                       href_URI = None )
```

## Work

### WorkBuilder
```
set_type ( new_type )

set_role ( new_role )

set_class ( new_class )

add_name ( name_text,
           type_  = "generic",
           lang   = None,
           script = None,
           nonfiling = 0 )

add_qualifier ( qualifier )  # RefElement

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
           link_title = None,
           href_URI = None,
           set_URI = None )

set_holdings ( versions_holdings_opt )
```

### WorkVariantBuilder
```
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
           class_ = None,  # ["transcription", "annotation", "documentation", "description", None]
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
