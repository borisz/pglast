# -*- coding: utf-8 -*-
# :Project:   pg_query -- Test the node.py module
# :Created:   ven 04 ago 2017 09:31:57 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

import pytest

from pg_query import Missing, Node
from pg_query.node import List, Scalar


def test_basic():
    ptree = [{'Foo': {'bar': {'Bar': {'a': 1, 'b': 'b'}}}},
             {'Foo': {'bar': {'Bar': {'a': 0, 'c': [
                 {'C': {'x': 0, 'y': 0}},
                 {'C': {'x': 0, 'y': 0}}
             ]}}}}]

    root = Node(ptree)
    assert root.parent_node is None
    assert root.attribute_name is None
    assert isinstance(root, List)
    assert len(root) == 2
    assert repr(root) == '[<Foo>]'
    assert str(root) == 'None=[<Foo>]'
    with pytest.raises(AttributeError):
        root.not_there

    foo1 = root[0]
    assert foo1 != root
    assert foo1.node_tag == 'Foo'
    assert foo1.parse_tree == {'bar': {'Bar': {'a': 1, 'b': 'b'}}}
    assert foo1.parent_node is None
    assert foo1.attribute_name == (None, 0)
    assert repr(foo1) == '<Foo>'
    assert str(foo1) == 'None[0]=<Foo>'
    assert foo1.attribute_names == {'bar'}
    assert foo1.not_there is Missing
    assert not foo1.not_there
    assert repr(foo1.not_there) == 'MISSING'
    with pytest.raises(ValueError):
        foo1[1.0]

    bar1 = foo1.bar
    assert bar1 != foo1
    assert bar1.node_tag == 'Bar'
    assert bar1.parent_node is foo1
    assert bar1.attribute_name == 'bar'
    assert bar1.attribute_names == {'a', 'b'}
    assert foo1[bar1.attribute_name] == bar1
    assert str(bar1) == 'bar=<Bar>'
    assert str(bar1.a) == 'a=1'
    assert str(bar1.b) == "b='b'"

    foo2 = root[1]
    assert foo2 != foo1

    bar2 = foo2['bar']
    assert bar2 != bar1
    assert bar2.attribute_name == 'bar'
    assert bar2.attribute_names == {'a', 'c'}

    c = bar2.c
    assert isinstance(c, List)
    assert repr(c) == '[<C>]'
    assert len(c) == 2

    c1 = c[0]
    c2 = c[1]
    assert c1.attribute_name == ('c', 0)
    assert c2.attribute_name == ('c', 1)
    assert c1 != c2
    assert c1.parent_node[c1.attribute_name] == c1
    assert str(c1) == 'c[0]=<C>'
    assert str(c2) == 'c[1]=<C>'

    x1 = c1['x']
    x2 = c2['x']
    assert isinstance(x1, Scalar)
    assert x1 != x2
    assert x1.value == x2.value


def test_traverse():
    ptree = [{'Foo': {'bar': {'Bar': {'a': 1, 'b': 'b'}}}}]
    root = Node(ptree)
    assert tuple(root.traverse()) == (
        root[0],
        root[0].bar,
        root[0].bar['a'],
        root[0].bar.b,
    )

    ptree = [{'Foo': {'bar': {'Bar': {'a': 1, 'b': 'b'}}}},
             {'Foo': {'bar': {'Bar': {'a': 0, 'c': [
                 {'C': {'x': 0, 'y': 0}},
                 {'C': {'x': 0, 'y': 0}}
             ]}}}}]

    root = Node(ptree)
    assert tuple(root.traverse()) == (
        root[0],
        root[0].bar,
        root[0].bar['a'],
        root[0].bar.b,
        root[1],
        root[1].bar,
        root[1].bar['a'],
        root[1].bar.c[0],
        root[1].bar.c[0].x,
        root[1].bar.c[0].y,
        root[1].bar.c[1],
        root[1].bar.c[1].x,
        root[1].bar.c[1].y,
    )
