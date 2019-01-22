# Transform classes

## Transformer
```python
transform ( record )
```

------------------------------------------------------

## Indexer
```python
# Given a pymarc field interpreted as a particular XOBIS element type, look up its associated control number.
lookup ( field, element_type )

# Given just a single string of text, assume it is the value of the primary subfield of an identity, and look up its associated control number.
simple_lookup ( text, element_type=None )

# Given a control number, return identity subfield list of the main entry of the associated record, or None if not found.
reverse_lookup ( ctrlno )

# Given a relationship name string, return a list of its relationship types. For use with the RelationshipBuilder set_type method.
lookup_rel_types ( rel_name )

# If there is a match to a field identity in only one element type, return that element type.
element_type_from_value ( field )

# If there is a match to a primary-field-string (simplified) identity in only one element type, return that element type.
simple_element_type_from_value ( text )

# Returns a dict by element type listing identities with conflicts in the main index.
list_conflicts ( )
```

------------------------------------------------------

## DateTimeParser
```python
```

------------------------------------------------------

## NameParser
```python
```

------------------------------------------------------

## LaneMARCRecord
```python
```
