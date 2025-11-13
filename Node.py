"""
Node.py - Node data structure for graph representation
Represents a single node in the search graph with position, connections, and state
"""

class Node:
    """
    Node class representing a vertex in the search graph
    
    Attributes:
        name (int): Unique identifier for the node
        x (float): X-coordinate position on canvas
        y (float): Y-coordinate position on canvas
        heuristic (float): Heuristic value for informed search (default 0)
        neighbors (dict): Dictionary of {neighbor_node: edge_weight}
        state (str): Current state ('empty', 'source', 'goal', 'visited', 'path')
        parent (Node): Parent node in the search path (for path reconstruction)
        cost (float): Cumulative cost from source (g(n) for A*)
    """
    
    def __init__(self, name, x=0, y=0, heuristic=0):
        """
        Initialize a new node
        
        Args:
            name (int): Unique node identifier
            x (float): X-coordinate on canvas
            y (float): Y-coordinate on canvas
            heuristic (float): Heuristic value for informed search
        """
        self.name = name
        self.x = x
        self.y = y
        self.heuristic = heuristic
        self.neighbors = {}  # {neighbor_node: weight}
        self.state = 'empty'  # 'empty', 'source', 'goal', 'visited', 'path'
        self.parent = None
        self.cost = 0  # g(n) - cost from start
        
    def add_neighbor(self, neighbor, weight=99):
        """
        Add a neighbor with an edge weight
        
        Args:
            neighbor (Node): The neighboring node
            weight (float): Weight/cost of the edge (default 99)
        """
        self.neighbors[neighbor] = weight
        
    def remove_neighbor(self, neighbor):
        """
        Remove a neighbor connection
        
        Args:
            neighbor (Node): The neighbor to remove
        """
        if neighbor in self.neighbors:
            del self.neighbors[neighbor]
            
    def get_neighbors(self):
        """
        Get list of all neighbors
        
        Returns:
            list: List of neighboring Node objects
        """
        return list(self.neighbors.keys())
    
    def get_weight(self, neighbor):
        """
        Get edge weight to a specific neighbor
        
        Args:
            neighbor (Node): The neighbor node
            
        Returns:
            float: Weight of edge to neighbor, or infinity if not connected
        """
        return self.neighbors.get(neighbor, float('inf'))
    
    def f_score(self):
        """
        Calculate f(n) = g(n) + h(n) for A* search
        
        Returns:
            float: Total estimated cost (actual cost + heuristic)
        """
        return self.cost + self.heuristic
    
    def distance_to(self, other_node):
        """
        Calculate Euclidean distance to another node (for visualization)
        
        Args:
            other_node (Node): Another node
            
        Returns:
            float: Euclidean distance
        """
        return ((self.x - other_node.x) ** 2 + (self.y - other_node.y) ** 2) ** 0.5
    
    def __str__(self):
        """String representation of node"""
        return f"Node({self.name})"
    
    def __repr__(self):
        """Detailed representation for debugging"""
        return f"Node({self.name}, x={self.x}, y={self.y}, h={self.heuristic}, state={self.state})"
    
    def __eq__(self, other):
        """Equality based on node name"""
        if not isinstance(other, Node):
            return False
        return self.name == other.name
    
    def __hash__(self):
        """Hash based on node name for use in sets/dicts"""
        return hash(self.name)
    
    def to_dict(self):
        """
        Convert node to dictionary for JSON serialization
        
        Returns:
            dict: Node data as dictionary
        """
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'heuristic': self.heuristic,
            'state': self.state,
            'neighbors': {n.name: w for n, w in self.neighbors.items()}
        }
    
    @staticmethod
    def from_dict(data, nodes_dict):
        """
        Create node from dictionary (for JSON deserialization)
        
        Args:
            data (dict): Node data
            nodes_dict (dict): Dictionary of all nodes for neighbor lookup
            
        Returns:
            Node: Reconstructed node
        """
        node = Node(data['name'], data['x'], data['y'], data['heuristic'])
        node.state = data.get('state', 'empty')
        
        # Restore neighbor connections
        for neighbor_name, weight in data.get('neighbors', {}).items():
            if neighbor_name in nodes_dict:
                node.add_neighbor(nodes_dict[neighbor_name], weight)
        
        return node
