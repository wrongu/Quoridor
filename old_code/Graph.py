from collections import deque
from pprint import pprint
import Helpers as h

# graph error classes
class GraphError(Exception):
    def __init__(self, message, values=0):
        self.message = message
        self.values = values
    def __str__(self):
        return self.message

class NodeNotExistError(GraphError):
    def __init__(self, node=None):
        GraphError("Node {0}does not exist".format(str(node) if node is not None else ""))
        
# Graph class
class Graph:
    """Abstract graph type with any immutable type as value at each node and weighted edges
    
    Node values must be unique.
    
    The graph is represented as a dictionary where nodes are keys and the value
    is a list of tuples, where each tuple contains (next_node, weight)
    """
    
    def __init__(self, nodes=[], edges=[], graph_in=None, directed=True):
        """Constructor.
        
        if input is list of nodes and list of edges, add each node
        and each edge, all with weight 1
            - nodes: list of some immutable type
            - edges: list of tuples as either (node1, node2) or (node1, node2, weight)
        
        if not directed, edges are added in both directions
        """
        
        self.graph_dict = {}
        if graph_in:
            for k, v in graph_in.graph_dict.iteritems():
                self.graph_dict[k] = h.list_copy(v)
        
        # loop through all edges. add both nodes and weight.
        for e in edges:
            self.addEdge(e, directed)
         
         # add all other nodes
        for n in nodes:
            if not self.graph_dict.has_key(n):
                self.graph_dict[n] = []
        
    def __repr__(self):
        return repr(self.graph_dict)
                
    def addEdge(self, e, directed=True):
        """Add edge to graph.
        
        Edge should be of form (node1, node2) or (node1, node2, weight).
        if given an edge with nodes that do not exist yet, those nodes are added
        """
        
        try:
            node1, node2, weight = e
        except ValueError:
            node1, node2 = e
            weight = 1
        
        # add nodes if not already there
        self.addNode(node1)
        self.addNode(node2)
        
        # add edge from node1 to node2 if not already there
        connection = (node2, weight)
        if node1 is not None and node2 is not None and (connection not in self.graph_dict[node1]):
            self.graph_dict[node1].append(connection)
        
        # if undirected, add reverse edge
        if not directed:
            self.addEdge((node2, node1, weight), True)
    
    def addNode(self, node):
        if node is not None and not self.hasNode(node):
            self.graph_dict[node] = []
            
    def removeEdge(self, edge, directed=True):
        """Remove edge from graph.
        
        Edge should be in same form as in addEdge()
        if not directed, removes edge in both directions
        """
        
        try:
            node1, node2, weight = edge
        except ValueError:
            node1, node2 = edge
            weight = 1
        
        connection = (node2, weight)
        if self.hasNode(node1):
            try:
                self.graph_dict[node1].remove(connection)
            except:
                pass
        
        # if undirected, remove reverse edge
        if not directed:
            self.removeEdge((node2, node1, weight), True)
    
    # wrapper for size of dict
    def size(self):
        return len(self.graph_dict)
    
    # wrapper for has_key of dict
    def hasNode(self, node):
        return self.graph_dict.has_key(node)
    
    def hasEdge(self, edge):
        # Edge should be of form (node1, node2) or (node1, node2, weight).
        try:
            node1, node2, weight = edge
        except ValueError:
            node1, node2 = edge
            weight = 1
            
        try:
            return (node2, weight) in self.graph_dict[node1]
        except:
            return False
    
    # depth-first search
    # given start node and list of goal nodes (reaching any considered 'success')
    # sortfunc - optional parameter. a function that maps a node to a number such that a list of nodes is sortable by this mapping.
    def findPathDepthFirst(self, startnode, goalnodes, sortfunc=None):
        # first check if both nodes exist
        if not self.hasNode(startnode):
            raise NodeNotExistError(startnode)
        for goalnode in goalnodes:
            if not self.hasNode(goalnode):
                raise NodeNotExistError(goalnode)
        
        closed_nodes = []
        cur_node = startnode
        path = [cur_node]
        # cur node is always path[-1]
        while not cur_node in goalnodes:  
            # print "DFS cur =", cur_node
            # select next
            next_nodes = self.get_adj_nodes(cur_node)
            next_nodes = [node for node in next_nodes if node not in closed_nodes+path]
            # if no options, back up and add current node to list of closed
            if len(next_nodes) == 0:
                closed_nodes.append(cur_node)
                if len(path) <= 1:
                    return None
                else:                    
                    cur_node = path[-2]
                    path.pop()
            else:
                # if a sortfunc is given, select node with smallest dist to goalnodes
                if sortfunc:
                    min_node = next_nodes[0]
                    min_dist = sortfunc(min_node)
                    for node in next_nodes[1:]:
#                        print "\tmin_node:", min_node
                        dist = sortfunc(node)
                        if dist < min_dist:
                            min_node = node
                            min_dist = dist
                    next_node = min_node
                else:
                    next_node = next_nodes[0]
                # update current node
                cur_node = next_node 
               # update path
                path.append(cur_node)
        
        return path        
    
    # breadth-first search: use Queue of next items
    # returns path as list of nodes
    def findPathBreadthFirst(self, startnode, goalnode):
        # first check if both nodes exist
        if not self.hasNode(startnode):
            raise NodeNotExistError(startnode)
        if not self.hasNode(goalnode):
            raise NodeNotExistError(goalnode)
    
        bfs_tree = self.build_BFS_tree(startnode)
        return self.pathFromBFSTree(bfs_tree, startnode, goalnode)
    
    # get path from BFS tree
    def pathFromBFSTree(self, bfs_tree, root, goal):
        if not bfs_tree.hasNode(goal):
            return None
        path = [goal]
        while path[0] is not root:
            adj = bfs_tree.get_adj_nodes(path[0])
            if adj:
                path.insert(0,adj[0])
            else:
                #pprint(bfs_tree.graph_dict)
                #print "path so far:"
                #pprint(path)
                #print "root-goal:"
                #print root,"-",goal
                path = None
                break
        return path
    
    # build breadth-first-search tree as a graph.
    # edge weights ignored.
    # if goal_nodes provided, stops when it gets to one of them
    def build_BFS_tree(self, root_node, goal_nodes=None):
        if not self.hasNode(root_node):
            raise NodeNotExistError(root_node)
        
        # initialize tree to graph with single node: the root
        bfs_tree = Graph(nodes=[root_node])
        # list of nodes already encountered_nodes along search
        encountered_nodes = [root_node]
        # queue of next edges to look at
        next_edges = deque()
        # initialize next_edges
        next_edges.append((None, root_node))
        
        while len(next_edges) > 0:
            (parent, this_node) = next_edges.popleft()
            #print "\nbfs: (parent, this):", (parent, this_node)
            #print "bfs: encountered:", encountered_nodes
            # add this node to bfs tree by putting edge pointing from here back to root
            if parent is not None:
                bfs_tree.addEdge((this_node, parent, 1), directed=True)
            if goal_nodes and (this_node in goal_nodes):
                return bfs_tree
            # get all adjacent nodes
            adj_nodes = self.get_adj_nodes(this_node)
            #print "bfs: adj:", adj_nodes
            # filter only ones not encountered
            adj_nodes = filter(lambda n: n not in encountered_nodes, adj_nodes)
            #print "bfs: adj-post-filter:", adj_nodes
            # update which nodes have been encountered
            encountered_nodes.extend(adj_nodes)
            # add new adjacent nodes to queue
            for adj in adj_nodes:
                next_edges.append((this_node, adj))
        
        return bfs_tree
        
    def get_adj_nodes(self, node):
        if not self.hasNode(node):
            return None          
        return [n for (n, w) in self.graph_dict[node]]