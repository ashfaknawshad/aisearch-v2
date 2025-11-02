# Algorithm Guide

Complete guide to all 8 search algorithms implemented in the AI Search Visualizer.

## Table of Contents

1. [Uninformed Search Algorithms](#uninformed-search)
   - [Breadth-First Search (BFS)](#breadth-first-search)
   - [Depth-First Search (DFS)](#depth-first-search)
   - [Depth-Limited Search (DLS)](#depth-limited-search)
   - [Iterative Deepening Search (IDS)](#iterative-deepening-search)
   - [Uniform Cost Search (UCS)](#uniform-cost-search)
   - [Bidirectional Search](#bidirectional-search)
2. [Informed Search Algorithms](#informed-search)
   - [Greedy Best-First Search](#greedy-best-first-search)
   - [A* Search](#a-star-search)
3. [Algorithm Comparison](#algorithm-comparison)
4. [Choosing the Right Algorithm](#choosing-the-right-algorithm)

---

## Uninformed Search Algorithms

Uninformed search algorithms (also called blind search) have no additional information about states beyond the problem definition. They can only generate successors and distinguish a goal state from a non-goal state.

### Breadth-First Search (BFS)

**Overview:**  
BFS explores the search space level by level, expanding all nodes at depth d before expanding any nodes at depth d+1.

**Data Structure:** FIFO Queue

**Algorithm:**
```
function BFS(graph, source, goal):
    frontier = Queue()
    frontier.push(source)
    visited = Set()
    
    while frontier is not empty:
        current = frontier.pop()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == goal:
            return reconstruct_path(current)
        
        for neighbor in current.neighbors:
            if neighbor not in visited:
                neighbor.parent = current
                frontier.push(neighbor)
    
    return failure
```

**Properties:**
- **Complete:** Yes (if branching factor b is finite)
- **Optimal:** Yes (for unweighted graphs)
- **Time Complexity:** O(V + E) where V = vertices, E = edges
- **Space Complexity:** O(V)

**Advantages:**
- Guarantees shortest path in unweighted graphs
- Simple to implement
- Complete if solution exists

**Disadvantages:**
- Memory intensive for large graphs
- Not optimal for weighted graphs
- Explores many irrelevant nodes

**Use Cases:**
- Finding shortest path in unweighted graphs
- Web crawling
- Social network analysis (finding connections)
- GPS navigation (unweighted roads)

---

### Depth-First Search (DFS)

**Overview:**  
DFS explores as deep as possible along each branch before backtracking.

**Data Structure:** LIFO Stack

**Algorithm:**
```
function DFS(graph, source, goal):
    frontier = Stack()
    frontier.push(source)
    visited = Set()
    
    while frontier is not empty:
        current = frontier.pop()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == goal:
            return reconstruct_path(current)
        
        for neighbor in reversed(current.neighbors):
            if neighbor not in visited:
                neighbor.parent = current
                frontier.push(neighbor)
    
    return failure
```

**Properties:**
- **Complete:** No (can get stuck in infinite loops)
- **Optimal:** No
- **Time Complexity:** O(V + E)
- **Space Complexity:** O(V) - but typically better than BFS

**Advantages:**
- Memory efficient
- Fast for deep solutions
- Good for exploring complete trees

**Disadvantages:**
- Can get trapped in infinite loops
- Not guaranteed to find shortest path
- May explore very deep paths unnecessarily

**Use Cases:**
- Maze solving
- Topological sorting
- Finding connected components
- Puzzle solving (when solution is deep)

---

### Depth-Limited Search (DLS)

**Overview:**  
DFS with a predetermined depth limit l to prevent infinite loops.

**Data Structure:** LIFO Stack with depth tracking

**Algorithm:**
```
function DLS(graph, source, goal, limit):
    frontier = Stack()
    frontier.push((source, 0))
    visited = Set()
    
    while frontier is not empty:
        current, depth = frontier.pop()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == goal:
            return reconstruct_path(current)
        
        if depth < limit:
            for neighbor in reversed(current.neighbors):
                if neighbor not in visited:
                    neighbor.parent = current
                    frontier.push((neighbor, depth + 1))
    
    return failure
```

**Properties:**
- **Complete:** No (only if goal within limit)
- **Optimal:** No
- **Time Complexity:** O(b^l) where b = branching factor, l = depth limit
- **Space Complexity:** O(bl)

**Advantages:**
- Solves infinite-path problem of DFS
- Memory efficient
- Faster than BFS if limit is appropriate

**Disadvantages:**
- Fails if goal beyond depth limit
- Choosing appropriate limit is difficult
- Still not optimal

**Use Cases:**
- Puzzles with known solution depth
- Game playing with depth constraints
- Resource-constrained pathfinding

---

### Iterative Deepening Search (IDS)

**Overview:**  
Repeatedly applies DLS with increasing depth limits (0, 1, 2, ..., d).

**Algorithm:**
```
function IDS(graph, source, goal, max_depth):
    for limit from 0 to max_depth:
        result = DLS(graph, source, goal, limit)
        if result != failure:
            return result
    
    return failure
```

**Properties:**
- **Complete:** Yes (if solution exists within max_depth)
- **Optimal:** Yes (for unweighted graphs)
- **Time Complexity:** O(b^d)
- **Space Complexity:** O(bd)

**Advantages:**
- Combines BFS completeness/optimality with DFS space efficiency
- Optimal for unweighted graphs
- No need to know depth limit in advance

**Disadvantages:**
- Revisits states multiple times
- Slower than single DFS
- Still not good for weighted graphs

**Use Cases:**
- Finding optimal solution with memory constraints
- Unknown solution depth
- Game playing (chess, checkers)

---

### Uniform Cost Search (UCS)

**Overview:**  
Expands the node with the lowest path cost g(n) from the start node.

**Data Structure:** Priority Queue (ordered by path cost)

**Algorithm:**
```
function UCS(graph, source, goal):
    frontier = PriorityQueue()
    frontier.push(source, 0)
    visited = Set()
    source.cost = 0
    
    while frontier is not empty:
        current = frontier.pop()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == goal:
            return reconstruct_path(current)
        
        for neighbor in current.neighbors:
            new_cost = current.cost + cost(current, neighbor)
            
            if neighbor not in visited:
                if neighbor not in frontier or new_cost < neighbor.cost:
                    neighbor.cost = new_cost
                    neighbor.parent = current
                    frontier.push(neighbor, new_cost)
    
    return failure
```

**Properties:**
- **Complete:** Yes (if step costs ≥ ε > 0)
- **Optimal:** Yes
- **Time Complexity:** O(b^(1 + ⌊C*/ε⌋))
- **Space Complexity:** O(b^(1 + ⌊C*/ε⌋))

**Advantages:**
- Guarantees optimal solution
- Works with weighted graphs
- Complete

**Disadvantages:**
- Can be slow for large graphs
- Memory intensive
- No heuristic guidance

**Use Cases:**
- Weighted pathfinding (GPS with traffic)
- Resource optimization
- Network routing
- Any problem with varying edge costs

---

### Bidirectional Search

**Overview:**  
Runs two simultaneous searches: forward from start, backward from goal. Stops when they meet.

**Algorithm:**
```
function BidirectionalSearch(graph, source, goal):
    forward_frontier = Queue()
    backward_frontier = Queue()
    forward_visited = Map()
    backward_visited = Map()
    
    forward_frontier.push(source)
    backward_frontier.push(goal)
    forward_visited[source] = null
    backward_visited[goal] = null
    
    while forward_frontier and backward_frontier not empty:
        # Expand forward
        current = forward_frontier.pop()
        if current in backward_visited:
            return merge_paths(current, forward_visited, backward_visited)
        
        for neighbor in current.neighbors:
            if neighbor not in forward_visited:
                forward_visited[neighbor] = current
                forward_frontier.push(neighbor)
        
        # Expand backward
        current = backward_frontier.pop()
        if current in forward_visited:
            return merge_paths(current, forward_visited, backward_visited)
        
        for neighbor with edge to current:
            if neighbor not in backward_visited:
                backward_visited[neighbor] = current
                backward_frontier.push(neighbor)
    
    return failure
```

**Properties:**
- **Complete:** Yes
- **Optimal:** Yes (for unweighted graphs)
- **Time Complexity:** O(b^(d/2))
- **Space Complexity:** O(b^(d/2))

**Advantages:**
- Much faster than single-direction search
- Reduces search space dramatically
- Still optimal (for unweighted)

**Disadvantages:**
- Requires goal to be known
- Requires reversible edges
- More complex implementation
- Not suitable for multiple goals

**Use Cases:**
- Single-pair shortest path
- Social networks (finding connection)
- Road networks with known destination

---

## Informed Search Algorithms

Informed search algorithms use problem-specific knowledge beyond the problem definition in the form of a heuristic function h(n) that estimates the cost from node n to the goal.

### Greedy Best-First Search

**Overview:**  
Expands the node that appears closest to the goal according to the heuristic h(n).

**Data Structure:** Priority Queue (ordered by heuristic)

**Algorithm:**
```
function GreedyBestFirst(graph, source, goal):
    frontier = PriorityQueue()
    frontier.push(source, source.heuristic)
    visited = Set()
    
    while frontier is not empty:
        current = frontier.pop()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == goal:
            return reconstruct_path(current)
        
        for neighbor in current.neighbors:
            if neighbor not in visited:
                neighbor.parent = current
                frontier.push(neighbor, neighbor.heuristic)
    
    return failure
```

**Properties:**
- **Complete:** No
- **Optimal:** No
- **Time Complexity:** O(b^m) where m = maximum depth
- **Space Complexity:** O(b^m)

**Advantages:**
- Very fast when heuristic is good
- Uses domain knowledge
- Memory efficient compared to A*

**Disadvantages:**
- Not optimal
- Can be misled by bad heuristics
- Not complete

**Use Cases:**
- Quick approximate solutions
- Real-time pathfinding (games)
- When optimality not required
- Good heuristics available

---

### A* Search

**Overview:**  
Expands nodes based on f(n) = g(n) + h(n), where g(n) is the cost from start and h(n) is the heuristic to goal.

**Data Structure:** Priority Queue (ordered by f-score)

**Algorithm:**
```
function AStar(graph, source, goal):
    frontier = PriorityQueue()
    source.g = 0
    source.f = source.g + source.heuristic
    frontier.push(source, source.f)
    visited = Set()
    
    while frontier is not empty:
        current = frontier.pop()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == goal:
            return reconstruct_path(current)
        
        for neighbor in current.neighbors:
            if neighbor not in visited:
                tentative_g = current.g + cost(current, neighbor)
                
                if neighbor not in frontier or tentative_g < neighbor.g:
                    neighbor.g = tentative_g
                    neighbor.f = neighbor.g + neighbor.heuristic
                    neighbor.parent = current
                    frontier.push(neighbor, neighbor.f)
    
    return failure
```

**Properties:**
- **Complete:** Yes
- **Optimal:** Yes (if heuristic is admissible)
- **Time Complexity:** O(b^d)
- **Space Complexity:** O(b^d)

**Admissible Heuristic:**  
h(n) ≤ h*(n) where h*(n) is the true cost to goal. Must never overestimate.

**Consistent Heuristic:**  
h(n) ≤ c(n, n') + h(n') for all neighbors n'. Triangle inequality.

**Common Heuristics:**
- **Manhattan Distance:** |x1 - x2| + |y1 - y2| (grid, 4-connected)
- **Euclidean Distance:** √((x1 - x2)² + (y1 - y2)²) (any space)
- **Chebyshev Distance:** max(|x1 - x2|, |y1 - y2|) (grid, 8-connected)

**Advantages:**
- Optimal with admissible heuristic
- Complete
- Efficient with good heuristic
- Industry standard for pathfinding

**Disadvantages:**
- Memory intensive
- Requires good heuristic
- Can be slow with poor heuristic

**Use Cases:**
- GPS navigation
- Game AI pathfinding
- Robotics path planning
- Puzzle solving (15-puzzle, Rubik's cube)

---

## Algorithm Comparison

| Algorithm | Complete | Optimal | Time | Space | Best For |
|-----------|----------|---------|------|-------|----------|
| **BFS** | ✅ Yes | ✅ Yes* | O(V+E) | O(V) | Unweighted shortest path |
| **DFS** | ❌ No | ❌ No | O(V+E) | O(V) | Deep solutions, memory-constrained |
| **DLS** | ❌ No** | ❌ No | O(b^l) | O(bl) | Known depth limit |
| **IDS** | ✅ Yes | ✅ Yes* | O(b^d) | O(bd) | Unknown depth, memory-constrained |
| **UCS** | ✅ Yes | ✅ Yes | O(b^C*) | O(b^C*) | Weighted graphs, no heuristic |
| **Bidirectional** | ✅ Yes | ✅ Yes* | O(b^(d/2)) | O(b^(d/2)) | Single known goal |
| **Greedy** | ❌ No | ❌ No | O(b^m) | O(b^m) | Fast approximate solutions |
| **A*** | ✅ Yes | ✅ Yes*** | O(b^d) | O(b^d) | Optimal path with heuristic |

\* For unweighted graphs  
\** Only if goal within limit  
\*** With admissible heuristic

---

## Choosing the Right Algorithm

### Decision Tree

```
Is the graph weighted?
├─ NO (unweighted)
│  ├─ Memory constrained?
│  │  ├─ YES → IDS or DFS
│  │  └─ NO → BFS
│  └─ Have good heuristic?
│     └─ YES → A* (with h = Manhattan/Euclidean)
│
└─ YES (weighted)
   ├─ Have heuristic?
   │  ├─ YES
   │  │  ├─ Need optimal? → A*
   │  │  └─ Fast approx OK? → Greedy
   │  └─ NO → UCS
   └─ Single known goal?
      └─ YES → Consider Bidirectional BFS/UCS
```

### Use Case Recommendations

**GPS Navigation:**
- Use A* with Euclidean distance heuristic
- Alt: UCS if no heuristic available

**Game AI (real-time):**
- Use A* for important paths
- Use Greedy for many NPCs
- Pre-compute with Dijkstra if static map

**Web Crawling:**
- Use BFS for breadth-first exploration
- Use DFS for specific deep content

**Puzzle Solving:**
- Use A* with domain-specific heuristic
- Use IDS if heuristic unavailable

**Social Networks:**
- Use BFS for shortest connection
- Use Bidirectional BFS for faster results

**Robot Path Planning:**
- Use A* with obstacle-aware heuristic
- Use D* for dynamic environments

---

## Advanced Topics

### Heuristic Design

**Good Heuristic Properties:**
1. **Admissible:** Never overestimates
2. **Consistent:** Satisfies triangle inequality
3. **Informative:** Close to true cost
4. **Efficient:** Fast to compute

**Pattern Databases:**
Pre-computed optimal solutions for sub-problems.

**Differential Heuristics:**
Use pre-computed distances to landmark nodes.

### Algorithm Variants

**Weighted A*:**
f(n) = g(n) + w × h(n) where w > 1  
Faster but sacrifices optimality.

**IDA* (Iterative Deepening A*):**
Memory-efficient A* using iterative deepening.

**Jump Point Search:**
Optimization for uniform-cost grid maps.

**Theta*:**
Any-angle pathfinding on grids.

---

## References

1. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.)
2. Cormen, T. H., et al. (2009). *Introduction to Algorithms* (3rd ed.)
3. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A Formal Basis for the Heuristic Determination of Minimum Cost Paths
4. Korf, R. E. (1985). Depth-first Iterative-Deepening: An Optimal Admissible Tree Search

---

**Next:** [API Reference](api-reference.md) | [Deployment Guide](deployment-guide.md) | [Back to README](../README.md)

