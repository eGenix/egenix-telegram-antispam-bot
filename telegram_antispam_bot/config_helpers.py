#!/usr/bin/env python3

""" Python config module helpers.

    Written by Marc-Andre Lemburg.
    Copyright (c) 2022-2025, eGenix.com Software GmbH; mailto:info@egenix.com
    License: MIT
"""
import os

### Custom config types

class IntFrozenSet(set):

    """ Frozen set with int values
    """
    pass

class FloatFrozenSet(set):

    """ Frozen set with float values
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
        - bool
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
            if isinstance(value, bool):
                new_value = True if new_value.lower() in (
                    '1', 'yes', 'true') else False
                new_value = bool(new_value)
            elif isinstance(value, int):
                new_value = int(new_value)
            elif isinstance(value, float):
                new_value = float(new_value)
            elif isinstance(value, IntFrozenSet):
                new_value = comma_separated_to_frozenset(new_value, int)
            elif isinstance(value, StrFrozenSet):
                new_value = comma_separated_to_frozenset(new_value, str)
            elif isinstance(value, FloatFrozenSet):
                new_value = comma_separated_to_frozenset(new_value, float)
            elif isinstance(value, frozenset):
                new_value = comma_separated_to_frozenset(new_value)
            vars[name] = new_value

### Tests

def _tests():

    vars = dict(
        INT = 10,
        FLOAT = 2.34,
        BOOL_10 = False,
        BOOL_YES = False,
        BOOL_TRUE = False,
    )
    os.environ.update(dict(
        INT = '1',
        FLOAT = '1.23',
        BOOL_10 = '1',
        BOOL_YES = 'Yes',
        BOOL_TRUE = 'True',
    ))
    test_vars = vars.copy()
    os_env_override(test_vars)
    assert test_vars['INT'] == 1
    assert test_vars['FLOAT'] == 1.23
    assert test_vars['BOOL_10'] is True
    assert test_vars['BOOL_YES'] is True
    assert test_vars['BOOL_TRUE'] is True

    assert comma_separated_to_frozenset('1,2,3') == set(('1','2','3'))
    assert comma_separated_to_frozenset('1,2,3', int) == set((1,2,3))
    assert comma_separated_to_frozenset('1,2,3', int) == IntFrozenSet((1,2,3))
    assert comma_separated_to_frozenset('1.3, 2.4, 3.5', float) == set((1.3, 2.4, 3.5))
    assert (comma_separated_to_frozenset('1.3, 2.4, 3.5', float) == 
            FloatFrozenSet((1.3, 2.4, 3.5)))

if __name__ == '__main__':
    _tests()
