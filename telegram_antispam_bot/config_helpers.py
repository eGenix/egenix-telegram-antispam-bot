#!/usr/bin/env python3

""" Python config module helpers.

    Written by Marc-Andre Lemburg in 2022.
    Copyright (c) 2022, eGenix.com Software GmbH; mailto:info@egenix.com
    License: MIT
"""
import os

### Custom config types

class IntFrozenSet(set):

    """ Frozen set with int values
    """
    pass

class StrFrozenSet(set):

    """ Frozen set with str values
    """
    pass

### Parsers

def comma_separated_to_frozenset(text, value_type=str):

    """ Convert a comma separated string text into a frozenset of values
        of the given value_type.

        value_type defaults to str.

    """
    s = set()
    add = s.add
    for value in text.split(','):
        value = value.strip()
        if value:
            add(value_type(value))
    return frozenset(s)

### Processors

def os_env_override(vars, prefix=''):

    """ Override values in dict vars with parsed values from the
        os.environ of the same name (with optional added prefix).

        The type of the default values in vars is used to determine how
        to parse the os.environ values.

        Supported types are:
        - int
        - float
        - IntSet
        - set (a set of strings)

        The dict vars is manipulated in place.

    """
    for name in vars.keys():
        if name.startswith('_') or name != name.upper():
            continue
        value = vars[name]
        env_name = prefix + name
        if env_name in os.environ:
            new_value = os.environ[env_name]
            if isinstance(value, int):
                new_value = int(new_value)
            elif isinstance(value, float):
                new_value = float(new_value)
            elif isinstance(value, IntFrozenSet):
                new_value = comma_separated_to_frozenset(new_value, int)
            elif isinstance(value, StrFrozenSet):
                new_value = comma_separated_to_frozenset(new_value, str)
            elif isinstance(value, frozenset):
                new_value = comma_separated_to_frozenset(new_value)
            vars[name] = new_value

### Tests

def _tests():
    assert comma_separated_to_set('1,2,3') == set(('1','2','3'))
    assert comma_separated_to_set('1,2,3', int) == set((1,2,3))
    assert comma_separated_to_set('1,2,3', int) == IntSet((1,2,3))
    assert comma_separated_to_set('1.3, 2.4, 3.5', float) == set((1.3, 2.4, 3.5))

if __name__ == '__main__':
    _tests()
