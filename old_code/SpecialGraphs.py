from Graph import Graph
# some special cases of graphs

def GraphNet(M, N):
    """create an MxN net of nodes
    
    Each node is connected to adjacent nodes in the cardinal directions.
    Nodes are identified as tuples (m,n)
    """
    G = Graph();
    def in_bounds(m, n):
        return 1 <= m <= M and 1 <= n <= N;
    for m in range(1,M+1):
        for n in range(1,N+1):
            node = (m,n);
            adjs = [(m-1,n), (m+1,n), (m, n-1), (m, n+1)];
            adjs = filter(lambda (a, b): in_bounds(a, b), adjs);
            for a in adjs:
                G.addEdge((node, a));
    return G;

def graph_net_sortfunc_row_inc(node):
    (r, c) = node;
    return -r;

def graph_net_sortfunc_row_dec(node):
    (r, c) = node;
    return r;

def graph_net_sortfunc_col_inc(node):
    (r, c) = node;
    return -c;

def graph_net_sortfunc_col_dec(node):
    (r, c) = node;
    return c;
    