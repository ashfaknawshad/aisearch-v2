"""
PriorityQueue.py - Priority queue implementation for informed search algorithms
Maintains nodes ordered by priority (f-score, cost, or heuristic)
"""

import heapq

class PriorityQueue:
    """
    Priority Queue implementation using heapq
    Used for Uniform Cost Search, Greedy Best-First, and A* Search
    
    Attributes:
        heap (list): Internal heap structure
        counter (int): Tie-breaker for equal priorities (FIFO)
        entry_finder (dict): Map from node to entry for membership testing
    """
    
    def __init__(self):
        """Initialize empty priority queue"""
        self.heap = []
        self.counter = 0  # Unique sequence count for tie-breaking
        self.entry_finder = {}  # Map node to entry
        self.REMOVED = '<removed-task>'  # Placeholder for removed entries
        
    def push(self, node, priority):
        """
        Add a node with given priority
        
        Args:
            node (Node): Node to add
            priority (float): Priority value (lower = higher priority)
        """
        if node in self.entry_finder:
            self.remove(node)
        
        count = self.counter
        self.counter += 1
        entry = [priority, count, node]
        self.entry_finder[node] = entry
        heapq.heappush(self.heap, entry)
        
    def remove(self, node):
        """
        Mark an existing node as removed
        
        Args:
            node (Node): Node to remove
            
        Raises:
            KeyError: If node not found
        """
        entry = self.entry_finder.pop(node)
        entry[-1] = self.REMOVED
        
    def pop(self):
        """
        Remove and return the lowest priority node
        
        Returns:
            Node: Node with lowest priority
            
        Raises:
            KeyError: If queue is empty
        """
        while self.heap:
            priority, count, node = heapq.heappop(self.heap)
            if node is not self.REMOVED:
                del self.entry_finder[node]
                return node
        raise KeyError('pop from an empty priority queue')
    
    def peek(self):
        """
        Return the lowest priority node without removing it
        
        Returns:
            Node: Node with lowest priority (or None if empty)
        """
        while self.heap:
            priority, count, node = self.heap[0]
            if node is not self.REMOVED:
                return node
            heapq.heappop(self.heap)
        return None
    
    def is_empty(self):
        """
        Check if queue is empty
        
        Returns:
            bool: True if empty, False otherwise
        """
        return len(self.entry_finder) == 0
    
    def __len__(self):
        """
        Get number of items in queue
        
        Returns:
            int: Number of items
        """
        return len(self.entry_finder)
    
    def __contains__(self, node):
        """
        Check if node is in queue
        
        Args:
            node (Node): Node to check
            
        Returns:
            bool: True if node in queue
        """
        return node in self.entry_finder
    
    def get_all_nodes(self):
        """
        Get all nodes currently in queue (for visualization)
        Does not remove them
        
        Returns:
            list: List of all nodes in queue
        """
        return [node for node in self.entry_finder.keys() if node is not self.REMOVED]
    
    def clear(self):
        """Clear the queue"""
        self.heap = []
        self.counter = 0
        self.entry_finder = {}


class Queue:
    """
    Simple FIFO Queue for BFS
    """
    
    def __init__(self):
        """Initialize empty queue"""
        self.items = []
        
    def push(self, item):
        """Add item to end of queue"""
        self.items.append(item)
        
    def pop(self):
        """Remove and return item from front of queue"""
        if self.is_empty():
            raise IndexError("pop from empty queue")
        return self.items.pop(0)
    
    def peek(self):
        """Return front item without removing"""
        if self.is_empty():
            return None
        return self.items[0]
    
    def is_empty(self):
        """Check if queue is empty"""
        return len(self.items) == 0
    
    def __len__(self):
        """Get queue size"""
        return len(self.items)
    
    def __contains__(self, item):
        """Check if item in queue"""
        return item in self.items
    
    def get_all_nodes(self):
        """Get all nodes in queue"""
        return self.items.copy()
    
    def clear(self):
        """Clear the queue"""
        self.items = []


class Stack:
    """
    Simple LIFO Stack for DFS
    """
    
    def __init__(self):
        """Initialize empty stack"""
        self.items = []
        
    def push(self, item):
        """Push item onto stack"""
        self.items.append(item)
        
    def pop(self):
        """Pop item from stack"""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self.items.pop()
    
    def peek(self):
        """Return top item without removing"""
        if self.is_empty():
            return None
        return self.items[-1]
    
    def is_empty(self):
        """Check if stack is empty"""
        return len(self.items) == 0
    
    def __len__(self):
        """Get stack size"""
        return len(self.items)
    
    def __contains__(self, item):
        """Check if item in stack"""
        return item in self.items
    
    def get_all_nodes(self):
        """Get all nodes in stack"""
        return self.items.copy()
    
    def clear(self):
        """Clear the stack"""
        self.items = []
