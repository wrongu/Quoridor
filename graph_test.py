# graph test

from Graph import Graph;
from pprint import pprint;
import SpecialGraphs;

E = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 4), (4, 5), (5, 6), (3, 6)];
G = Graph(edges = E, directed=False);
pprint(G.graph_dict);
pprint(G.findPathBreadthFirst(0,6));

print "\n\n"

E = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 4), (4, 5), (5, 6), (3, 6)];
E2 = [(7,8),(8,9),(9,10),(10,7)];
E.extend(E2);
G = Graph(edges = E, directed=False);
pprint(G.graph_dict);
pprint(G.findPathBreadthFirst(0,10));

print "\n\n"

G = SpecialGraphs.GraphNet(4,4);
pprint(G.graph_dict);
print ""
G = SpecialGraphs.GraphNet(2,3);
pprint(G.graph_dict);