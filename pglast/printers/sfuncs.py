# -*- coding: utf-8 -*-
# :Project:   pglast -- Special functions
# :Created:   mer 22 nov 2017 08:34:34 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017, 2018, 2021 Lele Gaifax
#

from . import special_function


def _print_trim(where, node, output):
    output.write('trim({}'.format(where))
    if len(node.args) > 1:
        output.write(' ')
        output.print_node(node.args[1])
    output.write(' FROM ')
    output.print_node(node.args[0])
    output.write(')')


@special_function('pg_catalog.btrim')
def btrim(node, output):
    """
    Emit function ``pg_catalog.btrim('  abc  ')`` as ``trim(BOTH FROM '  abc  ')``
    and ``pg_catalog.btrim('xxabcxx', 'x')`` as ``trim(BOTH 'x' FROM 'xxabcxx')``
    """
    _print_trim('BOTH', node, output)


@special_function('pg_catalog.date_part')
def date_part(node, output):
    """
    Emit function ``pg_catalog.date_part(field, timestamp)`` as
    ``EXTRACT(field FROM timestamp)``.
    """
    output.write('EXTRACT(')
    output.write(node.args[0].val.val.value.upper())
    output.write(' FROM ')
    output.print_node(node.args[1])
    output.write(')')


@special_function('pg_catalog.ltrim')
def ltrim(node, output):
    """
    Emit function ``pg_catalog.ltrim('  abc  ')`` as ``trim(LEADING FROM '  abc  ')``
    and ``pg_catalog.ltrim('xxabcxx', 'x')`` as ``trim(LEADING 'x' FROM 'xxabcxx')``
    """
    _print_trim('LEADING', node, output)


@special_function('pg_catalog.overlaps')
def overlaps(node, output):
    "Emit function ``pg_catalog.overlaps(a, b, c, d)`` as ``(a, b) OVERLAPS (c, d)``."
    output.write('(')
    output.print_list((node.args[0], node.args[1]), standalone_items=False)
    output.write(') OVERLAPS (')
    output.print_list((node.args[2], node.args[3]), standalone_items=False)
    output.write(')')


@special_function('pg_catalog.overlay')
def overlay(node, output):
    """
    Emit function ``pg_catalog.overlay('Txxxxas','hom', 2, 4)`` as
    ``overlay('Txxxxas' PLACING 'hom' FROM 2 FOR 4)``."
    """
    output.write('overlay(')
    output.print_node(node.args[0])
    output.write(' PLACING ')
    output.print_node(node.args[1])
    output.write(' FROM ')
    output.print_node(node.args[2])
    output.write(' FOR ')
    output.print_node(node.args[3])
    output.write(')')


@special_function('pg_catalog.position')
def position(node, output):
    "Emit function ``pg_catalog.position('abcd', 'a')`` as ``position('a' IN 'abcd')``."
    output.write('position(')
    output.print_node(node.args[1])
    output.write(' IN ')
    output.print_node(node.args[0])
    output.write(')')


@special_function('pg_catalog.rtrim')
def rtrim(node, output):
    """
    Emit function ``pg_catalog.rtrim('  abc  ')`` as ``trim(TRAILING FROM '  abc  ')``
    and ``pg_catalog.rtrim('xxabcxx', 'x')`` as ``trim(TRAILING 'x' FROM 'xxabcxx')``
    """
    _print_trim('TRAILING', node, output)


@special_function('pg_catalog.substring')
def substring(node, output):
    """
    Emit function ``pg_catalog.substring('Txxxxas', 2, 4)`` as ``substring('Txxxxas' FROM 2 FOR 4)``.
    and ``pg_catalog.substring('blabla', 2)`` as ``substring('blabla' FROM 2)``.
    """
    output.write('substring(')
    output.print_node(node.args[0])
    output.write(' FROM ')
    output.print_node(node.args[1])
    if len(node.args) > 2:
        output.write(' FOR ')
        output.print_node(node.args[2])
    output.write(')')


@special_function('pg_catalog.timezone')
def timezone(node, output):
    """
    Emit function ``pg_catalog.timezone(tz, timestamp)`` as ``timestamp AT TIME ZONE tz``.
    """
    output.print_node(node.args[1])
    output.write(' AT TIME ZONE ')
    output.print_node(node.args[0])
