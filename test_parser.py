from parser import MiniJavaParser
from lexer import MiniJavaLexer
from dotlib import Graph, to_dot
import subprocess

def ast_to_graph(ast_root):
    ast_graph = Graph()
    def node_to_grpah(g, curr_node):
        print(str(curr_node))
        node_vertex = g.nodes.add(str(curr_node))
        for child in curr_node.children:
            child_vertex = node_to_grpah(g, child)
            node_vertex.add_edge_to(child_vertex)
        return node_vertex
    node_to_grpah(ast_graph, ast_root)
    return ast_graph

def tree_to_svg(tree, filename):
    with open(filename + ".dot", "w+") as f:
        f.write(to_dot(ast_to_graph(tree)))
    subprocess.run([
        "dot", 
        "-Tsvg", 
        filename + ".dot",
        "-o",
        filename + ".svg" 
    ])

mjl = MiniJavaLexer()
mjl.build()
mpj = MiniJavaParser()
mpj.build()

prog_ast = mpj.get_AST(
    """

class main {

    public static void main(String[] args) {

    }

}

class User {

    int somefield;

    public int getRand( int pram ) {
        return 2*2 + 3;
    }

}

    """, lexer=mjl.lexer)

tree_to_svg(prog_ast, "test_prog") 

