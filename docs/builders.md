# Builders

<!--
## Builder
```
add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )
```

## PrincipalElementBuilder
```
add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )

set_type ( new_type )

set_role ( new_role )

set_scheme ( new_scheme )

set_class ( new_class )

set_usage ( new_usage )
```

## PrincipalElementVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

set_scheme ( new_scheme )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

## PrincipalElementRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_subdivision_link ( content_text,
                       content_lang = None,
                       link_title = None,
                       href_URI = None,
                       substitute = None )
```

VersionsHoldingsBuilder
...
-->

## RecordBuilder
```
# Organization owning/managing the record.
set_id_org_ref ( id_org_ref )  # OrganizationRef

# Record ID.
set_id_value( id_value )  # str

# Type of record (e.g. original, derivative, suppressed)
add_type ( xlink_title = None,  # str
           xlink_href = None,   # URI
           xlink_role = None )  # URI

set_principal_element ( principal_element )  # PrincipalElement

add_action ( time_or_duration_ref,  # TimeRef or DurationRef
             xlink_title = None,    # str
             xlink_href = None,     # URI
             xlink_role = None )    # URI

add_relationship ( relationship )   # Relationship
```

## Being

### BeingBuilder
```
set_role ( new_role )  # ["instance", "authority", "authority instance"]

set_type ( new_type )  # ["human", "nonhuman", "special", None]

set_class ( new_class )  # ["individual", "familial", "collective", "undifferentiated", "referential", None]

set_scheme ( new_scheme )  # str

set_entry_type ( link_title,
                 role_URI,
                 href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

add_name ( name_text,
           type_ = "generic",
           lang  = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### BeingVariantBuilder
```
set_type ( new_type )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

set_scheme ( new_scheme )

add_name ( name_text,
           type_ = "generic",
           lang  = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### BeingRefBuilder
```
add_name ( name_text,
           type_ = "generic",
           lang  = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

set_link ( link_title,
           href_URI = None )
```

## Event

### EventBuilder
```
set_type ( new_type )

set_class ( new_class )

set_scheme ( new_scheme )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### EventVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

set_scheme ( new_scheme )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### EventRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )
```

## String

### StringBuilder
```
set_type ( new_type )

set_class ( new_class )

set_grammar ( new_grammar )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### StringVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### StringRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )
```

## Time

### TimeEntryContentBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_certainty ( text,
                lang = None,
                set_ = None )

add_name ( name_text,
           lang = None,
           translit = None,
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

set_calendar ( new_calendar )

set_time_entry_content ( new_time_entry_content )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### DurationBuilder
```
set_class ( new_class )

set_usage ( new_usage )

set_scheme ( scheme1,
             scheme2 = "" )

set_calendar ( calendar1,
               calendar2 = "" )

set_time_entry1 ( time_entry_content1,
                  time_entry_content2 = None)

set_time_entry2 ( time_entry_content1,
                  time_entry_content2 = None)

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### TimeVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_scheme ( new_scheme )

set_calendar ( new_calendar )

set_time_entry_content ( new_time_entry_content )
```


### DurationVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_scheme ( scheme1,
             scheme2 = "" )

set_calendar ( calendar1,
               calendar2 = "" )

set_time_entry1 ( time_entry_content1,
                  time_entry_content2 = None)

set_time_entry2 ( time_entry_content1,
                  time_entry_content2 = None)
```

### TimeRefBuilder
```
set_calendar ( new_calendar )

set_link ( link_title,
           href_URI = None )

set_time_entry_content ( new_time_entry_content )
```

### DurationRefBuilder
```
set_calendar ( new_calendar )

set_link ( link_title,
           href_URI = None )

set_time_entry1 ( time_entry_content1,
                  time_entry_content2 = None)

set_time_entry2 ( time_entry_content1,
                  time_entry_content2 = None)
```

## Object

### ObjectBuilder
```
set_role ( new_role )

set_class ( new_class )

set_type ( new_type )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

set_organization ( link_title,
                   link_href = None,
                   id_content = None,
                   id_content_lang = None )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )

set_holdings ( versions_holdings_opt )
```

### ObjectVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

set_scheme ( new_scheme )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### ObjectRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )
```

## Work

### WorkBuilder
```
set_type ( new_type )

set_role ( new_role )

set_class ( new_class )

add_name ( name_text,
           type_ = "generic",
           lang  = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )

set_holdings ( versions_holdings_opt )
```

### WorkVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

set_scheme ( new_scheme )

add_name ( name_text,
           type_ = "generic",
           lang  = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### WorkRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           type_ = "generic",
           lang  = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )
```

## Language

### LanguageBuilder
```
set_class ( new_class )

set_usage ( new_usage )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### LanguageVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### LanguageRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_subdivision_link ( content_text,
                       content_lang = None,
                       link_title = None,
                       href_URI = None,
                       substitute = None )
```

## Concept

### ConceptBuilder
```
set_type ( new_type )

set_usage ( new_usage )

set_subtype ( new_subtype )

set_scheme ( new_scheme )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### ConceptVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

set_scheme ( new_scheme )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### ConceptRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_subdivision_link ( content_text,
                       content_lang = None,
                       link_title = None,
                       href_URI = None,
                       substitute = None )
```

## Organization

### OrganizationBuilder
```
set_type ( new_type )

set_class ( new_class )

set_scheme ( new_scheme )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### OrganizationVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

set_scheme ( new_scheme )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### OrganizationRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_prequalifier ( prequalifier )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

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
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_variant ( variant )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### PlaceVariantBuilder
```
set_type ( link_title,
           role_URI,
           href_URI = None )

set_time_or_duration_ref ( time_or_duration_ref )

set_substitute_attribute_type ( substitute_attribute_type )

set_scheme ( new_scheme )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )

add_note ( content_text,
           content_lang = None,
           class_ = None,
           link_title = None,
           href_URI = None,
           role_URI = None )
```

### PlaceRefBuilder
```
set_link ( link_title,
           href_URI = None )

add_name ( name_text,
           lang = None,
           translit = None,
           nonfiling = 0 )

add_qualifier ( qualifier )
```

## RelationshipBuilder
```
set_type ( new_type )  # in

set_degree ( new_degree )

set_name ( name_text,
           name_lang = None )

set_modifier ( modifier_text,
              modifier_lang = None,
              modifier_nonfiling = 0 )

set_time_or_duration_ref ( time_or_duration_ref )

set_element_ref ( element_ref )
```

## Holdings

**TODO** -- implements (subset of?) [ISO 20775](https://www.loc.gov/standards/iso20775/)
