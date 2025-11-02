# API Reference

Complete API documentation for the AI Search Algorithm Visualizer Python classes.

## Table of Contents

- [Node Class](#node-class)
- [PriorityQueue Classes](#priorityqueue-classes)
- [SearchAgent Class](#searchagent-class)
- [GraphVisualizer Class](#graphvisualizer-class)

---

## Node Class

Represents a vertex in the search graph.

### Constructor

```python
Node(name, x=0, y=0, heuristic=0)
```

**Parameters:**
- `name` (int): Unique node identifier
- `x` (float): X-coordinate on canvas
- `y` (float): Y-coordinate on canvas  
- `heuristic` (float): Heuristic value for informed search

### Attributes

- `name` (int): Unique identifier
- `x` (float): X position
- `y` (float): Y position
- `heuristic` (float): Heuristic value h(n)
- `neighbors` (dict): {Node: weight} dictionary
- `state` (str): Current state ('empty', 'source', 'goal', 'visited', 'path')
- `parent` (Node): Parent for path reconstruction
- `cost` (float): Path cost g(n) from source

### Methods

#### add_neighbor(neighbor, weight=1)
Add a neighbor with edge weight.

```python
node1.add_neighbor(node2, 5)  # Add edge with weight 5
```

#### remove_neighbor(neighbor)
Remove a neighbor connection.

#### get_neighbors()
Returns list of all neighboring nodes.

#### get_weight(neighbor)
Get edge weight to a specific neighbor.

#### f_score()
Calculate f(n) = g(n) + h(n) for A* search.

#### to_dict()
Convert node to dictionary for JSON serialization.

#### from_dict(data, nodes_dict) [static]
Create node from dictionary.

---

## PriorityQueue Classes

### PriorityQueue

Priority queue for informed search (UCS, Greedy, A*).

#### Constructor
```python
pq = PriorityQueue()
```

#### Methods

**push(node, priority)**
```python
pq.push(node, node.f_score())
```
Add node with given priority (lower = higher priority).

**pop()**
```python
node = pq.pop()
```
Remove and return lowest priority node.

**is_empty()**
```python
if pq.is_empty():
    # handle empty queue
```

**get_all_nodes()**
```python
nodes = pq.get_all_nodes()  # For visualization
```

### Queue

Simple FIFO queue for BFS.

```python
q = Queue()
q.push(node)
node = q.pop()
```

### Stack

Simple LIFO stack for DFS.

```python
s = Stack()
s.push(node)
node = s.pop()
```

---

## SearchAgent Class

Implements all 8 search algorithms with visualization support.

### Constructor

```python
SearchAgent(graph, source, goal=None)
```

**Parameters:**
- `graph` (dict): {node_name: Node} dictionary
- `source` (Node): Starting node
- `goal` (Node): Goal node (optional for some algorithms)

### Attributes

**Visualization State:**
- `fringe_list` (list): Nodes waiting to be explored
- `visited_list` (list): Nodes already expanded
- `traversal_array` (list): Order nodes were visited
- `path_found` (list): Final path from source to goal

**Metrics:**
- `nodes_explored` (int): Count of nodes visited
- `path_cost` (float): Total cost of found path
- `success` (bool): Whether goal was reached

**For Informed Search:**
- `current_node_info` (dict): {'g': 0, 'h': 0, 'f': 0}

### Methods

#### breadth_first_search()
```python
for _ in agent.breadth_first_search():
    # Process animation frame
    update_visualization()
```

**Returns:** Generator yielding at each animation frame

**Algorithm:** FIFO queue, level-by-level exploration

**Complexity:** O(V + E) time, O(V) space

#### depth_first_search()
```python
for _ in agent.depth_first_search():
    update_visualization()
```

**Returns:** Generator yielding at each frame

**Algorithm:** LIFO stack, deep exploration

#### depth_limited_search(depth_limit=5)
```python
for _ in agent.depth_limited_search(depth_limit=10):
    update_visualization()
```

**Parameters:**
- `depth_limit` (int): Maximum depth to search

#### iterative_deepening_search(max_depth=10)
```python
for _ in agent.iterative_deepening_search(max_depth=15):
    update_visualization()
```

**Parameters:**
- `max_depth` (int): Maximum depth limit to try

#### uniform_cost_search()
```python
for _ in agent.uniform_cost_search():
    update_visualization()
```

**Algorithm:** Priority queue ordered by path cost g(n)

**Guarantees:** Optimal solution

#### bidirectional_search()
```python
for _ in agent.bidirectional_search():
    update_visualization()
```

**Algorithm:** Simultaneous forward and backward search

#### greedy_best_first_search()
```python
for _ in agent.greedy_best_first_search():
    update_visualization()
```

**Algorithm:** Priority queue ordered by heuristic h(n)

**Requires:** Heuristic values set on nodes

#### a_star_search()
```python
for _ in agent.a_star_search():
    update_visualization()
```

**Algorithm:** Priority queue ordered by f(n) = g(n) + h(n)

**Requires:** Admissible heuristic

**Guarantees:** Optimal solution (if heuristic admissible)

### Helper Methods

#### reset_state()
Reset all visualization state and node states.

#### reconstruct_path(goal_node)
Reconstruct path from source to goal using parent pointers.

**Returns:** List of node names in path

---

## GraphVisualizer Class (Brython)

Main visualizer class managing canvas, graph, and interactions.

### Constructor

```python
visualizer = GraphVisualizer()
```

Automatically initializes canvas, event listeners, and rendering.

### Graph Operations

#### add_node(x, y)
```python
visualizer.add_node(100, 200)
```

#### delete_node(node)
```python
visualizer.delete_node(selected_node)
```

#### add_edge(from_node, to_node, weight=1)
```python
visualizer.add_edge(node1, node2, 5)
```

#### set_source(node)
Set node as source (red).

#### toggle_goal(node)
Toggle node as goal (green).

#### set_heuristic(node, value)
Set heuristic value for informed search.

### Search Execution

#### start_search(event)
```python
visualizer.start_search(None)
```

Start animated search execution.

**Process:**
1. Validates graph (has nodes, source, goal)
2. Creates SearchAgent
3. Collects all animation states
4. Begins auto-play animation

#### stop_search(event)
Stop current search animation.

#### toggle_pause(event)
Toggle pause/resume during animation.

#### step_forward(event)
Advance one animation frame.

#### step_backward(event)
Go back one animation frame.

### File Operations

#### save_graph(event)
Export graph as JSON file.

#### load_graph(event)
Import graph from JSON file.

#### reset_canvas(event)
Clear entire graph.

### Export Functions

#### export_png(event)
Export current canvas as PNG image.

#### export_gif(event)
Record and export search animation as GIF.

#### export_pdf(event)
Generate comprehensive PDF report.

#### export_svg(event)
Export graph as SVG vector image.

#### export_json(event)
Export graph data as JSON.

#### export_csv(event)
Export performance metrics as CSV.

### View Controls

#### zoom_by(factor)
```python
visualizer.zoom_by(1.2)  # Zoom in
visualizer.zoom_by(0.8)  # Zoom out
```

#### reset_view(event)
Reset zoom and pan to defaults.

#### toggle_labels(event)
Show/hide heuristic labels.

#### toggle_grid(event)
Show/hide background grid.

#### toggle_theme(event)
Switch between light/dark mode.

### Undo/Redo

#### save_state()
Save current state to undo stack.

#### undo()
Undo last action.

#### redo()
Redo last undone action.

---

## Usage Examples

### Example 1: Create Graph Programmatically

```python
from Node import Node
from SearchAgent import SearchAgent

# Create nodes
nodes = {}
nodes[0] = Node(0, 100, 100, 5)
nodes[1] = Node(1, 200, 100, 3)
nodes[2] = Node(2, 300, 100, 0)

# Set states
nodes[0].state = 'source'
nodes[2].state = 'goal'

# Add edges
nodes[0].add_neighbor(nodes[1], 2)
nodes[1].add_neighbor(nodes[2], 3)

# Run A* search
agent = SearchAgent(nodes, nodes[0], nodes[2])
for _ in agent.a_star_search():
    print(f"Fringe: {agent.fringe_list}")
    print(f"Visited: {agent.visited_list}")

print(f"Path found: {agent.path_found}")
print(f"Path cost: {agent.path_cost}")
```

### Example 2: Custom Heuristic

```python
def manhattan_distance(node, goal):
    return abs(node.x - goal.x) + abs(node.y - goal.y)

# Set heuristics
for node in nodes.values():
    node.heuristic = manhattan_distance(node, goal_node)
```

### Example 3: Export Results

```python
# After search completes
results = {
    'algorithm': 'A*',
    'success': agent.success,
    'path': agent.path_found,
    'cost': agent.path_cost,
    'nodes_explored': agent.nodes_explored
}

import json
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## Events and Callbacks

### Canvas Events

**Mouse Events:**
- `mousedown`: Start node/edge creation or dragging
- `mousemove`: Update dragging or panning
- `mouseup`: Finish dragging
- `wheel`: Zoom in/out

**Keyboard Events:**
- `A`: Select Add Node tool
- `E`: Select Add Edge tool
- `M`: Select Move Node tool
- `D`: Select Delete Node tool
- `G`: Select Set Goal tool
- `H`: Select Edit Heuristic tool
- `Space`: Start/Pause search
- `←/→`: Step backward/forward
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Ctrl+S`: Save graph

---

## Data Structures

### Graph JSON Format

```json
{
  "metadata": {
    "version": "1.0",
    "created": "2025-10-31T10:30:00Z",
    "algorithm": "astar",
    "node_count": 5,
    "edge_count": 6
  },
  "graph": {
    "nodes": [
      {
        "name": 0,
        "x": 100,
        "y": 200,
        "heuristic": 5,
        "state": "source",
        "neighbors": {
          "1": 2,
          "2": 3
        }
      }
    ],
    "source": 0,
    "goals": [4]
  },
  "results": {
    "success": true,
    "path": [0, 1, 3, 4],
    "path_cost": 8,
    "nodes_explored": 5
  }
}
```

---

## Error Handling

### Common Errors

**"Please add nodes to the graph first"**
- Graph is empty
- Add at least 2 nodes before searching

**"Please set a source node"**
- No source node defined
- First node auto-becomes source, or click a node with source tool

**"Please set a goal node"**
- No goal node defined
- Use Set Goal tool and click a node

**"Invalid number"**
- Non-numeric input for heuristic or weight
- Enter valid numbers only

### Validation

The visualizer automatically validates:
- Graph has nodes before search
- Source node exists
- At least one goal exists
- No self-loops (prevented in UI)
- Valid numeric inputs

---

## Performance Considerations

### Large Graphs

For graphs with 1000+ nodes:
- Use Grid Background: Off
- Use Labels: Off for better performance
- Consider using Greedy/A* instead of BFS
- Lower animation speed

### Memory Usage

Approximate memory per node:
- Node object: ~200 bytes
- Animation state: ~100 bytes per frame

For 100 nodes, 1000 animation frames:
- ~100 KB total memory usage

---

## Browser Compatibility

**Tested Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Requirements:**
- JavaScript enabled
- HTML5 Canvas support
- Local storage (for themes)

---

**Next:** [Deployment Guide](deployment-guide.md) | [Algorithm Guide](algorithm-guide.md) | [Back to README](../README.md)
