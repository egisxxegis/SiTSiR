from SPARQL.graph import Graph


class GraphTraveler:
    def __init__(self, root_graph: Graph):
        self.graph_root = root_graph
        self.last_returned = root_graph
        self.level_now = 1

    def get_next_recursive(self, graph_for_reference: Graph, last_visited_graph=None) -> Graph:
        # root -> .child -> None                      = root.child
        #      -> .next -> .child -> None             = root.next
        #               -> .next  -> .child -> None   = root.next.next
        #                         -> .next  -> None   = root
        if graph_for_reference is None:
            self.level_now = 1
            return self.graph_root
        elif graph_for_reference.next == last_visited_graph and last_visited_graph is not None:
            # step up, because we have already visit this.child and this.next
            self.level_now -= 1
            return self.get_next_recursive(graph_for_reference.parent, graph_for_reference)
        elif graph_for_reference.child == last_visited_graph and last_visited_graph is not None:
            if graph_for_reference.next is not None:
                return graph_for_reference.next
            self.level_now -= 1
            return self.get_next_recursive(graph_for_reference.parent, graph_for_reference)
        elif graph_for_reference.child is not None:
            self.level_now += 1
            return graph_for_reference.child
        elif graph_for_reference.next is not None:
            return graph_for_reference.next
        else:
            self.level_now -= 1
            return self.get_next_recursive(graph_for_reference.parent, graph_for_reference)

    def get_next_or_root(self) -> Graph:
        self.last_returned = self.get_next_recursive(self.last_returned)
        return self.last_returned
