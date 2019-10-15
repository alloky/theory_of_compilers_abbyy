#!/usr/bin/env python3

import unittest

import os
import sys
import inspect

currentdir = os.path.dirname(
    os.path.abspath(
        inspect.getfile(
            inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

sys.path.insert(0, parentdir)


from dotlib import Graph


class TestGraph(unittest.TestCase):

    def test_simple(self):
        g = Graph()
        a = g.nodes.add('a')
        b = g.nodes.add('b')
        c = g.nodes.add('c')
        ab = a.add_edge_to(b, 'ab')
        bc = g.edges.add(b, c, 'bc')
        self.assertCountEqual(g.nodes, [a, b, c])
        self.assertCountEqual(g.edges, [ab, bc])
        self.assertCountEqual(a.neighbors, [b])
        self.assertCountEqual(b.neighbors, [a, c])
        self.assertCountEqual(c.neighbors, [b])
        self.assertCountEqual(a.edges, [ab])
        self.assertCountEqual(b.edges, [ab, bc])
        self.assertCountEqual(c.edges, [bc])
        self.assertCountEqual(ab.nodes, [a, b])
        self.assertCountEqual(bc.nodes, [b, c])
        self.assertTrue(a in g)
        self.assertTrue(b in g)
        self.assertTrue(c in g)
        self.assertTrue(ab in g)
        self.assertTrue(bc in g)

    def test_delete_node(self):
        g = Graph()
        a = g.nodes.add('a')
        b = g.nodes.add('b')
        c = g.nodes.add('c')
        ab = a.add_edge_to(b, 'ab')
        bc = g.edges.add(b, c, 'bc')
        b.delete()
        self.assertCountEqual(g.nodes, [a, c])
        self.assertCountEqual(g.edges, [])
        self.assertCountEqual(a.neighbors, [])
        self.assertCountEqual(c.neighbors, [])
        self.assertTrue(a in g)
        self.assertFalse(b in g)
        self.assertTrue(c in g)
        self.assertFalse(ab in g)
        self.assertFalse(bc in g)

    def test_delete_edge(self):
        g = Graph()
        a = g.nodes.add('a')
        b = g.nodes.add('b')
        c = g.nodes.add('c')
        ab = a.add_edge_to(b, 'ab')
        bc = g.edges.add(b, c, 'bc')
        ab.delete()
        self.assertCountEqual(g.nodes, [a, b, c])
        self.assertCountEqual(g.edges, [bc])
        self.assertCountEqual(a.neighbors, [])
        self.assertCountEqual(b.neighbors, [c])
        self.assertCountEqual(c.neighbors, [b])
        self.assertCountEqual(a.edges, [])
        self.assertCountEqual(b.edges, [bc])
        self.assertCountEqual(c.edges, [bc])
        self.assertCountEqual(bc.nodes, [b, c])
        self.assertTrue(a in g)
        self.assertTrue(b in g)
        self.assertTrue(c in g)
        self.assertFalse(ab in g)
        self.assertTrue(bc in g)


if __name__ == '__main__':
    unittest.main()
