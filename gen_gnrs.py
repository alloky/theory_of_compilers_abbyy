#!/usr/bin/env python3

import argparse
import itertools
from dotlib import Graph, to_dot


def parse_args():
    parser = argparse.ArgumentParser(description='Generate a G(n, r, s) graph - a graph of all r-sized subsets '
                                     'of {1..n} intersecting by s elements')
    parser.add_argument('set_size', metavar='N', type=int, help='size of the set')
    parser.add_argument('subset_size', metavar='R', type=int, help='size of the subsets')
    parser.add_argument('intersection_size', metavar='S', type=int, help='size of the subset intersection')
    return parser.parse_args()


def main():
    args = parse_args()
    graph = Graph()
    nodes = {}
    for subset in itertools.combinations(set(range(1, args.set_size + 1)), args.subset_size):
        subset = set(subset)
        node = graph.nodes.add(str(subset))
        nodes[node] = subset
        for node2, subset2 in nodes.items():
            if len(subset.intersection(subset2)) == args.intersection_size:
                node.add_edge_to(node2)

    print(to_dot(graph))


if __name__ == '__main__':
    main()
