"""
SearchAgent.py - Implementation of 8 search algorithms with visualization support
All algorithms use generator functions (yield) for step-by-step animation
"""

from Node import Node
from PriorityQueue import PriorityQueue, Queue, Stack


class SearchAgent:
    """
    Search Agent implementing 8 search algorithms:
    - Breadth-First Search (BFS)
    - Depth-First Search (DFS)  
    - Depth-Limited Search (DLS)
    - Iterative Deepening Search (IDS)
    - Uniform Cost Search (UCS)
    - Bidirectional Search
    - Greedy Best-First Search
    - A* Search
    
    Manages visualization state through fringe_list, visited_list, and traversal_array
    """
    
    def __init__(self, graph, source, goal=None, goal_nodes=None):
        """
        Initialize search agent
        
        Args:
            graph (dict): Dictionary mapping node names to Node objects
            source (Node): Starting node
            goal (Node): Goal node (for backward compatibility, can be None)
            goal_nodes (list): List of goal nodes (supports multiple goals)
        """
        self.graph = graph
        self.source = source
        self.goal = goal
        self.goal_nodes = goal_nodes if goal_nodes else ([goal] if goal else [])
        
        # Visualization state
        self.fringe_list = []      # Nodes waiting to be explored
        self.visited_list = []     # Nodes already expanded
        self.traversal_array = []  # Order nodes were visited
        self.path_found = []       # Final path from source to goal
        
        # Algorithm metrics
        self.nodes_explored = 0
        self.path_cost = 0
        self.success = False
        self.failure_reason = None  # Track why algorithm failed
        
        # For informed search display
        self.current_node_info = {
            'g': 0,  # Cost so far
            'h': 0,  # Heuristic
            'f': 0   # Total estimate
        }
        
    def reset_state(self):
        """Reset all visualization state"""
        self.fringe_list = []
        self.visited_list = []
        self.traversal_array = []
        self.path_found = []
        self.nodes_explored = 0
        self.path_cost = 0
        self.success = False
        self.failure_reason = None
        
        # Reset all node states except source and goal
        for node in self.graph.values():
            if node and node.state not in ['source', 'goal']:
                node.state = 'empty'
            node.parent = None
            node.cost = 0
    
    def reconstruct_path(self, goal_node):
        """
        Reconstruct path from source to goal using parent pointers
        
        Args:
            goal_node (Node): The goal node reached
            
        Returns:
            list: List of node names in path from source to goal
        """
        path = []
        current = goal_node
        cost = 0
        
        while current is not None:
            path.append(current.name)
            if current.parent:
                cost += current.parent.get_weight(current)
            current = current.parent
            
        path.reverse()
        self.path_cost = cost
        return path
    
    def is_goal(self, node):
        """
        Check if a node is a goal node
        
        Args:
            node (Node): Node to check
            
        Returns:
            bool: True if node is in goal_nodes list
        """
        return node in self.goal_nodes
    
    def get_node_by_name(self, node_name):
        """
        Get a node from the graph by its name property
        
        Args:
            node_name: The name to search for (can be string or int)
            
        Returns:
            Node: The node with matching name, or None if not found
        """
        for node in self.graph.values():
            if str(node.name) == str(node_name):
                return node
        return None
    
    def get_sorted_neighbors(self, node):
        """
        Get neighbors sorted by X-coordinate (left to right) for visual determinism
        
        Args:
            node (Node): Node whose neighbors to retrieve
            
        Returns:
            list: Sorted list of neighbor nodes (left to right by x position, then by y if tied)
        """
        return sorted(node.get_neighbors(), key=lambda n: (n.x, n.y))
    
    def breadth_first_search(self):
        """
        Breadth-First Search (BFS)
        
        Uses FIFO queue for frontier
        Explores nodes level by level
        Guarantees shortest path (by number of edges)
        
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        Complete: Yes
        Optimal: Yes (for unweighted graphs)
        
        Yields after each state change for animation
        """
        self.reset_state()
        
        if self.goal is None:
            return
        
        # Initialize frontier with source
        frontier = Queue()
        frontier.push(self.source)
        self.fringe_list = [self.source.name]
        visited = set()
        
        yield  # Show initial state
        
        while not frontier.is_empty():
            # Pop node from frontier
            current = frontier.pop()
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            
            # Mark as visited (turn purple)
            if current.state != 'source' and current.state != 'goal':
                current.state = 'visited'
            
            yield  # Show node turning purple BEFORE adding to visited list
            
            # Now add to visited list
            self.visited_list.append(current.name)
            self.traversal_array.append(current.name)
            visited.add(current)
            self.nodes_explored += 1
            
            # Check if goal reached
            if self.is_goal(current):
                self.success = True
                self.path_found = self.reconstruct_path(current)
                # Mark path nodes
                for node_name in self.path_found:
                    node = self.get_node_by_name(node_name)
                    if node and node.state not in ['source', 'goal']:
                        node.state = 'path'
                yield
                return
            
            # Expand neighbors (sorted for deterministic behavior)
            for neighbor in self.get_sorted_neighbors(current):
                if neighbor not in visited and neighbor not in frontier:
                    neighbor.parent = current
                    frontier.push(neighbor)
            
            # Update fringe list after expansion
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            yield
        
        # No path found
        self.success = False
        yield
    
    def depth_first_search(self):
        """
        Depth-First Search (DFS)
        
        Uses LIFO stack for frontier
        Explores as deep as possible before backtracking
        Does not guarantee shortest path
        
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        Complete: No (can get stuck in infinite paths)
        Optimal: No
        
        Yields after each state change for animation
        """
        self.reset_state()
        
        if self.goal is None:
            return
        
        # Initialize frontier with source
        frontier = Stack()
        frontier.push(self.source)
        self.fringe_list = [self.source.name]
        visited = set()
        
        yield  # Show initial state
        
        while not frontier.is_empty():
            # Pop node from frontier
            current = frontier.pop()
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            
            # Skip if already visited
            if current in visited:
                continue
            
            # Mark as visited (turn purple)
            if current.state != 'source' and current.state != 'goal':
                current.state = 'visited'
            
            yield  # Show node turning purple BEFORE adding to visited list
            
            # Now add to visited list
            self.visited_list.append(current.name)
            self.traversal_array.append(current.name)
            visited.add(current)
            self.nodes_explored += 1
            
            # Check if goal reached
            if self.is_goal(current):
                self.success = True
                self.path_found = self.reconstruct_path(current)
                # Mark path nodes
                for node_name in self.path_found:
                    node = self.get_node_by_name(node_name)
                    if node and node.state not in ['source', 'goal']:
                        node.state = 'path'
                yield
                return
            
            # Expand neighbors (sorted and reversed for consistent right-to-left stack behavior)
            neighbors = self.get_sorted_neighbors(current)
            for neighbor in reversed(neighbors):
                if neighbor not in visited:
                    neighbor.parent = current
                    frontier.push(neighbor)
            
            # Update fringe list after expansion
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            yield
        
        # No path found
        self.success = False
        yield
    
    def depth_limited_search(self, depth_limit=5):
        """
        Depth-Limited Search (DLS)
        
        DFS with a maximum depth limit
        Prevents infinite loops in infinite state spaces
        
        Args:
            depth_limit (int): Maximum depth to search
        
        Time Complexity: O(b^l) where b=branching factor, l=limit
        Space Complexity: O(l)
        Complete: No (only if goal within limit)
        Optimal: No
        
        Yields after each state change for animation
        """
        self.reset_state()
        
        if self.goal is None:
            return
        
        # Initialize frontier with (node, depth) tuples
        frontier = Stack()
        frontier.push((self.source, 0))
        self.fringe_list = [self.source.name]
        visited = set()
        
        yield  # Show initial state
        
        while not frontier.is_empty():
            # Pop node and its depth
            current, depth = frontier.pop()
            self.fringe_list = [n.name if isinstance(n, Node) else n[0].name 
                               for n in frontier.get_all_nodes()]
            
            # Skip if already visited
            if current in visited:
                continue
            
            # Mark as visited (turn purple)
            if current.state != 'source' and current.state != 'goal':
                current.state = 'visited'
            
            yield  # Show node turning purple BEFORE adding to visited list
            
            # Now add to visited list
            self.visited_list.append(current.name)
            self.traversal_array.append(current.name)
            visited.add(current)
            self.nodes_explored += 1
            
            # Check if goal reached
            if self.is_goal(current):
                self.success = True
                self.path_found = self.reconstruct_path(current)
                # Mark path nodes
                for node_name in self.path_found:
                    node = self.get_node_by_name(node_name)
                    if node and node.state not in ['source', 'goal']:
                        node.state = 'path'
                yield
                return
            
            # Expand neighbors only if within depth limit (sorted for determinism)
            if depth < depth_limit:
                neighbors = self.get_sorted_neighbors(current)
                for neighbor in reversed(neighbors):
                    if neighbor not in visited:
                        neighbor.parent = current
                        frontier.push((neighbor, depth + 1))
            
            # Update fringe list after expansion
            self.fringe_list = [n.name if isinstance(n, Node) else n[0].name 
                               for n in frontier.get_all_nodes()]
            yield
        
        # No path found
        self.success = False
        yield
    
    def iterative_deepening_search(self, max_depth=10):
        """
        Iterative Deepening Search (IDS)
        
        Repeatedly applies DLS with increasing depth limits
        Combines benefits of BFS (completeness, optimality) and DFS (space efficiency)
        
        Args:
            max_depth (int): Maximum depth to try
        
        Time Complexity: O(b^d)
        Space Complexity: O(d)
        Complete: Yes
        Optimal: Yes (for unweighted graphs)
        
        Yields after each state change for animation
        """
        self.reset_state()
        
        if self.goal is None:
            return
        
        # Try increasing depth limits
        for limit in range(max_depth + 1):
            # Reset for new iteration
            for node in self.graph.values():
                if node and node.state not in ['source', 'goal']:
                    node.state = 'empty'
                node.parent = None
            
            visited = set()
            frontier = Stack()
            frontier.push((self.source, 0))
            self.fringe_list = [self.source.name]
            
            yield  # Show new iteration starting
            
            while not frontier.is_empty():
                current, depth = frontier.pop()
                self.fringe_list = [n.name if isinstance(n, Node) else n[0].name 
                                   for n in frontier.get_all_nodes()]
                
                if current in visited:
                    continue
                
                # Mark as visited
                if current.state != 'source' and current.state != 'goal':
                    current.state = 'visited'
                
                yield
                
                self.visited_list.append(current.name)
                self.traversal_array.append(current.name)
                visited.add(current)
                self.nodes_explored += 1
                
                # Check if goal reached
                if self.is_goal(current):
                    self.success = True
                    self.path_found = self.reconstruct_path(current)
                    for node_name in self.path_found:
                        node = self.get_node_by_name(node_name)
                        if node and node.state not in ['source', 'goal']:
                            node.state = 'path'
                    yield
                    return
                
                # Expand if within limit (sorted for determinism)
                if depth < limit:
                    neighbors = self.get_sorted_neighbors(current)
                    for neighbor in reversed(neighbors):
                        if neighbor not in visited:
                            neighbor.parent = current
                            frontier.push((neighbor, depth + 1))
                
                self.fringe_list = [n.name if isinstance(n, Node) else n[0].name 
                                   for n in frontier.get_all_nodes()]
                yield
        
        # No path found within max_depth
        self.success = False
        yield
    
    def uniform_cost_search(self):
        """
        Uniform Cost Search (UCS)
        
        Uses priority queue ordered by path cost g(n)
        Always expands lowest-cost node first
        Guarantees optimal path
        
        Time Complexity: O(b^(1 + C*/ε))
        Space Complexity: O(b^(1 + C*/ε))
        Complete: Yes
        Optimal: Yes
        
        Yields after each state change for animation
        """
        self.reset_state()
        
        if self.goal is None:
            return
        
        # Initialize frontier with source (priority = cost)
        frontier = PriorityQueue()
        self.source.cost = 0
        frontier.push(self.source, 0)
        self.fringe_list = [self.source.name]
        visited = set()
        
        yield  # Show initial state
        
        while not frontier.is_empty():
            # Pop lowest cost node
            current = frontier.pop()
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            
            # Skip if already visited
            if current in visited:
                continue
            
            # Mark as visited
            if current.state != 'source' and current.state != 'goal':
                current.state = 'visited'
            
            self.current_node_info['g'] = current.cost
            self.current_node_info['h'] = 0
            self.current_node_info['f'] = current.cost
            
            yield  # Show node turning purple BEFORE adding to visited list
            
            # Now add to visited list
            self.visited_list.append(current.name)
            self.traversal_array.append(current.name)
            visited.add(current)
            self.nodes_explored += 1
            
            # Check if goal reached
            if self.is_goal(current):
                self.success = True
                self.path_found = self.reconstruct_path(current)
                for node_name in self.path_found:
                    node = self.get_node_by_name(node_name)
                    if node and node.state not in ['source', 'goal']:
                        node.state = 'path'
                yield
                return
            
            # Expand neighbors (sorted for deterministic tie-breaking when costs are equal)
            for neighbor in self.get_sorted_neighbors(current):
                if neighbor not in visited:
                    new_cost = current.cost + current.get_weight(neighbor)
                    
                    # Add or update neighbor in frontier
                    if neighbor not in frontier or new_cost < neighbor.cost:
                        neighbor.cost = new_cost
                        neighbor.parent = current
                        frontier.push(neighbor, new_cost)
            
            # Update fringe list after expansion
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            yield
        
        # No path found
        self.success = False
        yield
    
    def greedy_best_first_search(self):
        """
        Greedy Best-First Search
        
        Uses priority queue ordered by heuristic h(n)
        Always expands node that appears closest to goal
        Fast but not optimal
        
        Time Complexity: O(b^m)
        Space Complexity: O(b^m)
        Complete: No
        Optimal: No
        
        Yields after each state change for animation
        """
        self.reset_state()
        
        if self.goal is None:
            return
        
        # Initialize frontier with source (priority = heuristic)
        frontier = PriorityQueue()
        frontier.push(self.source, self.source.heuristic)
        self.fringe_list = [self.source.name]
        visited = set()
        stuck_counter = 0  # Track consecutive dead-ends
        last_frontier_size = 1
        
        yield  # Show initial state
        
        while not frontier.is_empty():
            # Pop node with lowest heuristic
            current = frontier.pop()
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            
            # Skip if already visited
            if current in visited:
                continue
            
            # Mark as visited
            if current.state != 'source' and current.state != 'goal':
                current.state = 'visited'
            
            self.current_node_info['g'] = current.cost
            self.current_node_info['h'] = current.heuristic
            self.current_node_info['f'] = current.heuristic
            
            yield  # Show node turning purple BEFORE adding to visited list
            
            # Now add to visited list
            self.visited_list.append(current.name)
            self.traversal_array.append(current.name)
            visited.add(current)
            self.nodes_explored += 1
            
            # Check if goal reached
            if self.is_goal(current):
                self.success = True
                self.path_found = self.reconstruct_path(current)
                for node_name in self.path_found:
                    node = self.get_node_by_name(node_name)
                    if node and node.state not in ['source', 'goal']:
                        node.state = 'path'
                yield
                return
            
            # Count unvisited neighbors before expansion
            unvisited_neighbors = [n for n in self.get_sorted_neighbors(current) 
                                  if n not in visited and n not in frontier]
            
            # Expand neighbors (sorted for deterministic tie-breaking)
            for neighbor in unvisited_neighbors:
                neighbor.cost = current.cost + current.get_weight(neighbor)
                neighbor.parent = current
                frontier.push(neighbor, neighbor.heuristic)
            
            # Check if greedy is stuck (no new nodes added to frontier)
            current_frontier_size = len(frontier.get_all_nodes())
            if len(unvisited_neighbors) == 0 and current_frontier_size == 0:
                # Dead-end: no unvisited neighbors and frontier is empty
                self.success = False
                self.failure_reason = "Greedy search got stuck in a dead-end"
                yield
                return
            
            # Update fringe list after expansion
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            yield
        
        # Frontier exhausted without finding goal
        self.success = False
        self.failure_reason = "No path found - all reachable nodes explored"
        yield
    
    def a_star_search(self):
        """
        A* Search
        
        Uses priority queue ordered by f(n) = g(n) + h(n)
        Optimal if heuristic is admissible and consistent
        Best of both worlds: complete, optimal, and efficient
        
        Time Complexity: O(b^d)
        Space Complexity: O(b^d)
        Complete: Yes
        Optimal: Yes (with admissible heuristic)
        
        Yields after each state change for animation
        """
        self.reset_state()
        
        if self.goal is None:
            return
        
        # Initialize frontier with source (priority = f(n) = g(n) + h(n))
        frontier = PriorityQueue()
        self.source.cost = 0
        frontier.push(self.source, self.source.f_score())
        self.fringe_list = [self.source.name]
        visited = set()
        
        yield  # Show initial state
        
        while not frontier.is_empty():
            # Pop node with lowest f(n)
            current = frontier.pop()
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            
            # Skip if already visited
            if current in visited:
                continue
            
            # Mark as visited
            if current.state != 'source' and current.state != 'goal':
                current.state = 'visited'
            
            self.current_node_info['g'] = current.cost
            self.current_node_info['h'] = current.heuristic
            self.current_node_info['f'] = current.f_score()
            
            yield  # Show node turning purple BEFORE adding to visited list
            
            # Now add to visited list
            self.visited_list.append(current.name)
            self.traversal_array.append(current.name)
            visited.add(current)
            self.nodes_explored += 1
            
            # Check if goal reached
            if self.is_goal(current):
                self.success = True
                self.path_found = self.reconstruct_path(current)
                for node_name in self.path_found:
                    node = self.get_node_by_name(node_name)
                    if node and node.state not in ['source', 'goal']:
                        node.state = 'path'
                yield
                return
            
            # Expand neighbors (sorted for deterministic tie-breaking)
            for neighbor in self.get_sorted_neighbors(current):
                if neighbor not in visited:
                    new_cost = current.cost + current.get_weight(neighbor)
                    
                    # Add or update neighbor in frontier if better path found
                    if neighbor not in frontier or new_cost < neighbor.cost:
                        neighbor.cost = new_cost
                        neighbor.parent = current
                        frontier.push(neighbor, neighbor.f_score())
            
            # Update fringe list after expansion
            self.fringe_list = [n.name for n in frontier.get_all_nodes()]
            yield
        
        # No path found
        self.success = False
        yield
    
    def bidirectional_search(self):
        """
        Bidirectional Search
        
        Searches from both source and goal simultaneously
        Meets in the middle, reducing search space
        Requires goal to be known and reversible edges
        
        Time Complexity: O(b^(d/2))
        Space Complexity: O(b^(d/2))
        Complete: Yes
        Optimal: Yes (for unweighted graphs)
        
        Yields after each state change for animation
        """
        self.reset_state()
        
        if self.goal is None:
            return
        
        # Two frontiers: forward from source, backward from goal
        forward_frontier = Queue()
        backward_frontier = Queue()
        
        forward_frontier.push(self.source)
        backward_frontier.push(self.goal)
        
        forward_visited = {self.source: None}  # node: parent
        backward_visited = {self.goal: None}
        
        self.fringe_list = [self.source.name, self.goal.name]
        
        yield  # Show initial state
        
        while not forward_frontier.is_empty() and not backward_frontier.is_empty():
            # Expand from forward direction
            if not forward_frontier.is_empty():
                current = forward_frontier.pop()
                
                # Mark as visited
                if current.state != 'source' and current.state != 'goal':
                    current.state = 'visited'
                
                yield
                
                self.visited_list.append(current.name)
                self.traversal_array.append(current.name)
                self.nodes_explored += 1
                
                # Check if paths meet
                if current in backward_visited:
                    self.success = True
                    # Reconstruct path from both directions
                    forward_path = []
                    node = current
                    while node is not None:
                        forward_path.append(node.name)
                        node = forward_visited[node]
                    forward_path.reverse()
                    
                    backward_path = []
                    node = backward_visited[current]
                    while node is not None:
                        backward_path.append(node.name)
                        node = backward_visited[node]
                    
                    self.path_found = forward_path + backward_path
                    
                    # Calculate actual path cost using edge weights
                    cost = 0
                    for i in range(len(self.path_found) - 1):
                        from_node = self.get_node_by_name(self.path_found[i])
                        to_node = self.get_node_by_name(self.path_found[i + 1])
                        if from_node and to_node:
                            cost += from_node.get_weight(to_node)
                    self.path_cost = cost
                    
                    # Mark path
                    for node_name in self.path_found:
                        node = self.get_node_by_name(node_name)
                        if node and node.state not in ['source', 'goal']:
                            node.state = 'path'
                    yield
                    return
                
                # Expand forward neighbors (sorted for determinism)
                for neighbor in self.get_sorted_neighbors(current):
                    if neighbor not in forward_visited:
                        forward_visited[neighbor] = current
                        forward_frontier.push(neighbor)
                
                # Update fringe list
                self.fringe_list = ([n.name for n in forward_frontier.get_all_nodes()] +
                                   [n.name for n in backward_frontier.get_all_nodes()])
                yield
            
            # Expand from backward direction
            if not backward_frontier.is_empty():
                current = backward_frontier.pop()
                
                # Mark as visited
                if current.state != 'source' and current.state != 'goal':
                    current.state = 'visited'
                
                yield
                
                self.visited_list.append(current.name)
                self.traversal_array.append(current.name)
                self.nodes_explored += 1
                
                # Check if paths meet
                if current in forward_visited:
                    self.success = True
                    # Reconstruct path from both directions
                    forward_path = []
                    node = current
                    while node is not None:
                        forward_path.append(node.name)
                        node = forward_visited[node]
                    forward_path.reverse()
                    
                    backward_path = []
                    node = backward_visited[current]
                    while node is not None:
                        backward_path.append(node.name)
                        node = backward_visited[node]
                    
                    self.path_found = forward_path + backward_path
                    
                    # Calculate actual path cost using edge weights
                    cost = 0
                    for i in range(len(self.path_found) - 1):
                        from_node = self.get_node_by_name(self.path_found[i])
                        to_node = self.get_node_by_name(self.path_found[i + 1])
                        if from_node and to_node:
                            cost += from_node.get_weight(to_node)
                    self.path_cost = cost
                    
                    # Mark path
                    for node_name in self.path_found:
                        node = self.get_node_by_name(node_name)
                        if node and node.state not in ['source', 'goal']:
                            node.state = 'path'
                    yield
                    return
                
                # Expand backward neighbors (reverse edges, sorted left-to-right for visual determinism)
                for other_node in sorted(self.graph.values(), key=lambda n: (n.x, n.y)):
                    if current in other_node.get_neighbors() and other_node not in backward_visited:
                        backward_visited[other_node] = current
                        backward_frontier.push(other_node)
                
                # Update fringe list
                self.fringe_list = ([n.name for n in forward_frontier.get_all_nodes()] +
                                   [n.name for n in backward_frontier.get_all_nodes()])
                yield
        
        # No path found
        self.success = False
        yield
