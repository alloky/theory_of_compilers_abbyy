def escape(string):
    return string.replace('\\', '\\\\').replace('"', '\"')


def to_dot(graph):
    lines = []
    node_number = 1
    numbers = {}
    for node in graph.nodes:
        numbers[node] = node_number
        lines.append(f'{node_number} [label="{escape(node.name)}"];')
        node_number += 1

    for edge in graph.edges:
        lines.append(f'{numbers[edge.nodes[0]]} -- {numbers[edge.nodes[1]]} [label="{escape(edge.name)}"];')

    return 'graph {\n' + '\n'.join(lines) + '\n}'
