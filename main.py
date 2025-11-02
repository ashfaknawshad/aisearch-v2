"""
main.py - Main Brython script for AI Search Algorithm Visualizer
Handles canvas rendering, user interactions, animations, and exports
"""

from browser import document, window, html, timer, alert
from browser.local_storage import storage
import json
import math

# Import our Python modules
from Node import Node
from SearchAgent import SearchAgent

class GraphVisualizer:
    """Main visualizer class managing canvas, graph, and interactions"""
    
    def __init__(self):
        # Canvas setup
        self.canvas = document['graph-canvas']
        self.ctx = self.canvas.getContext('2d')
        self.dpi_scale = 1.0
        self.window_width = 0
        self.window_height = 0
        self.resize_canvas()
        
        # Graph data
        self.nodes = {}  # {node_id: Node}
        self.node_counter = 0
        self.source_node = None
        self.goal_nodes = []  # Can have multiple goals
        
        # View transform
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0  # For smooth zoom interpolation
        self.zoom_speed = 0.15  # Zoom interpolation speed
        self.show_labels = True
        self.show_grid = True
        
        # Interaction state
        self.current_tool = 'add-node'
        self.selected_node = None
        self.dragging_node = None
        self.edge_start_node = None
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.mouse_down_button = -1  # Track which button was pressed
        
        # Animation state
        self.search_agent = None
        self.search_generator = None
        self.animation_states = []
        self.current_state_index = -1
        self.is_animating = False
        self.is_paused = False
        self.animation_speed = 5  # 1-10 scale
        self.animation_timer = None
        
        # Export state
        self.recording_gif = False
        self.gif_frames = []
        
        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []
        
        # Setup event listeners
        self.setup_event_listeners()
        
        # Set initial heuristic button state (disabled for BFS by default)
        self.on_algorithm_change(None)
        
        # Reset view to center (fix any panning issues)
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        
        # Initial render
        self.render()
        self.update_graph_stats()
        
        # Initialize Lucide icons
        timer.set_timeout(lambda: self.safe_lucide_init(), 100)
        
        # Force reset view after a short delay to ensure proper initialization
        timer.set_timeout(lambda: self.force_reset_view(), 200)
        
    def resize_canvas(self):
        """Resize canvas to fit container with proper DPI scaling"""
        # Get device pixel ratio for high-DPI displays (Retina, 4K, etc.)
        self.dpi_scale = window.devicePixelRatio if hasattr(window, 'devicePixelRatio') else 1.0
        
        # Get container size
        container_rect = self.canvas.parentElement.getBoundingClientRect()
        self.window_width = int(container_rect.width)
        self.window_height = int(container_rect.height)
        
        # Set canvas CSS size (display size)
        self.canvas.style.width = f'{self.window_width}px'
        self.canvas.style.height = f'{self.window_height}px'
        
        # Set actual canvas size (accounting for DPI) - use setAttribute for Brython
        target_width = int(self.window_width * self.dpi_scale)
        target_height = int(self.window_height * self.dpi_scale)
        
        # Use setAttribute which works better in Brython
        self.canvas.setAttribute('width', str(target_width))
        self.canvas.setAttribute('height', str(target_height))
        
        # Get context again after resize (important!)
        self.ctx = self.canvas.getContext('2d')
        
        # Enable high-quality image smoothing
        self.ctx.imageSmoothingEnabled = True
        try:
            self.ctx.imageSmoothingQuality = 'high'
        except:
            pass  # Not all browsers support this
        
    # ===== Coordinate Transformations =====
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates with proper bounding rect"""
        # Get canvas bounding rectangle
        rect = self.canvas.getBoundingClientRect()
        
        # Convert screen coords to canvas coords
        canvas_x = screen_x - rect.left
        canvas_y = screen_y - rect.top
        
        # Apply inverse pan and zoom transformations
        world_x = (canvas_x - self.view_offset_x) / self.zoom
        world_y = (canvas_y - self.view_offset_y) / self.zoom
        
        return world_x, world_y
    
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x * self.zoom + self.view_offset_x
        screen_y = world_y * self.zoom + self.view_offset_y
        return screen_x, screen_y
    
    # ===== Rendering =====
    
    def render(self):
        """Main render function"""
        # Reset transform to identity (to clear properly)
        self.ctx.setTransform(1, 0, 0, 1, 0, 0)
        
        # Clear entire canvas
        self.ctx.clearRect(0, 0, self.canvas.width, self.canvas.height)
        
        # Apply the DPI scale
        self.ctx.scale(self.dpi_scale, self.dpi_scale)
        
        # Fill with background color
        if 'dark-mode' in document.body.classList:
            self.ctx.fillStyle = '#0a0a0a'
        else:
            self.ctx.fillStyle = '#ffffff'
        self.ctx.fillRect(0, 0, self.window_width, self.window_height)
        
        # Draw grid BEFORE transformation (in screen space)
        if self.show_grid:
            self.draw_grid()
        
        # Save state before pan/zoom
        self.ctx.save()
        
        # Apply pan and zoom transformations
        self.ctx.translate(self.view_offset_x, self.view_offset_y)
        self.ctx.scale(self.zoom, self.zoom)
        
        # Draw edges
        for node in self.nodes.values():
            for neighbor, weight in node.neighbors.items():
                self.draw_edge(node, neighbor, weight)
        
        # Draw nodes
        for node in self.nodes.values():
            self.draw_node(node)
        
        # Draw labels
        if self.show_labels:
            for node in self.nodes.values():
                self.draw_node_label(node)
        
        # Restore context (removes pan/zoom, keeps DPI scale)
        self.ctx.restore()
        
    def draw_grid(self):
        """Draw background grid with theme awareness"""
        # Theme-aware grid color
        if 'dark-mode' in document.body.classList:
            self.ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
        else:
            self.ctx.strokeStyle = 'rgba(0, 0, 0, 0.05)'
        
        self.ctx.lineWidth = 1
        
        # Grid size in screen space (scales with zoom)
        grid_size = 50 * self.zoom
        offset_x = self.view_offset_x % grid_size
        offset_y = self.view_offset_y % grid_size
        
        # Draw vertical lines
        x = offset_x
        while x < self.window_width:
            self.ctx.beginPath()
            self.ctx.moveTo(x, 0)
            self.ctx.lineTo(x, self.window_height)
            self.ctx.stroke()
            x += grid_size
        
        # Draw horizontal lines
        y = offset_y
        while y < self.window_height:
            self.ctx.beginPath()
            self.ctx.moveTo(0, y)
            self.ctx.lineTo(self.window_width, y)
            self.ctx.stroke()
            y += grid_size
    
    def draw_node(self, node):
        """Draw a node with crisp rendering"""
        colors = {
            'empty': '#ffffff',
            'source': '#ef4444',
            'goal': '#10b981',
            'visited': '#8b5cf6',
            'path': '#f59e0b'
        }
        
        radius = 25
        
        # Node circle
        self.ctx.beginPath()
        self.ctx.arc(node.x, node.y, radius, 0, 2 * math.pi)
        self.ctx.fillStyle = colors.get(node.state, colors['empty'])
        self.ctx.fill()
        
        # Node border
        is_selected = (self.selected_node == node)
        self.ctx.strokeStyle = '#3b82f6' if is_selected else '#374151'
        self.ctx.lineWidth = 4 if is_selected else 3
        self.ctx.stroke()
        
        # Node ID with better font
        self.ctx.font = 'bold 14px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
        self.ctx.textAlign = 'center'
        self.ctx.textBaseline = 'middle'
        text_color = '#111827' if node.state == 'empty' else '#ffffff'
        self.ctx.fillStyle = text_color
        self.ctx.fillText(str(node.name), node.x, node.y - 6)
        
        # Highlight selected node
        if self.selected_node == node:
            self.ctx.strokeStyle = '#3b82f6'
            self.ctx.lineWidth = 3 / self.zoom
            self.ctx.beginPath()
            self.ctx.arc(node.x, node.y, radius + 5, 0, 2 * math.pi)
            self.ctx.stroke()
    
    def draw_node_label(self, node):
        """Draw node heuristic label with better font"""
        if node.heuristic > 0:
            self.ctx.fillStyle = '#6b7280'
            self.ctx.font = '11px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            self.ctx.textAlign = 'center'
            self.ctx.fillText(f'h={node.heuristic}', node.x, node.y + 8)
    
    def draw_edge(self, node1, node2, weight):
        """Draw an edge between two nodes with crisp rendering"""
        # Draw line
        self.ctx.beginPath()
        self.ctx.moveTo(node1.x, node1.y)
        self.ctx.lineTo(node2.x, node2.y)
        self.ctx.strokeStyle = '#94a3b8'
        self.ctx.lineWidth = 3
        self.ctx.stroke()
        
        # Draw arrow head
        self.draw_arrow_head(node1, node2)
        
        # Draw weight label (if weight != 1)
        if weight != 1:
            mid_x = (node1.x + node2.x) / 2
            mid_y = (node1.y + node2.y) / 2
            
            # Draw weight with background for readability
            self.ctx.font = '12px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            self.ctx.textAlign = 'center'
            self.ctx.textBaseline = 'middle'
            
            # Background
            text = str(weight)
            metrics = self.ctx.measureText(text)
            text_width = metrics.width
            padding = 4
            
            # Save fill style
            bg_color = '#0a0a0a' if 'dark-mode' in document.body.classList else '#ffffff'
            self.ctx.fillStyle = bg_color
            self.ctx.fillRect(
                mid_x - text_width / 2 - padding,
                mid_y - 8,
                text_width + padding * 2,
                16
            )
            
            # Text
            self.ctx.fillStyle = '#64748b'
            self.ctx.fillText(text, mid_x, mid_y)
    
    def draw_arrow_head(self, from_node, to_node):
        """Draw arrow head on edge"""
        angle = math.atan2(to_node.y - from_node.y, to_node.x - from_node.x)
        arrow_length = 12
        
        # Calculate arrow position (at edge of node circle)
        node_radius = 25
        end_x = to_node.x - math.cos(angle) * node_radius
        end_y = to_node.y - math.sin(angle) * node_radius
        
        # Arrow points
        self.ctx.beginPath()
        self.ctx.moveTo(end_x, end_y)
        self.ctx.lineTo(
            end_x - arrow_length * math.cos(angle - math.pi / 6),
            end_y - arrow_length * math.sin(angle - math.pi / 6)
        )
        self.ctx.moveTo(end_x, end_y)
        self.ctx.lineTo(
            end_x - arrow_length * math.cos(angle + math.pi / 6),
            end_y - arrow_length * math.sin(angle + math.pi / 6)
        )
        self.ctx.strokeStyle = '#94a3b8'
        self.ctx.lineWidth = 3
        self.ctx.stroke()
    
    # ===== Graph Operations =====
    
    def add_node(self, x, y):
        """Add a new node at position"""
        node = Node(self.node_counter, x, y, 0)
        
        # First node becomes source
        if len(self.nodes) == 0:
            node.state = 'source'
            self.source_node = node
        
        self.nodes[self.node_counter] = node
        self.node_counter += 1
        self.save_state()
        self.render()
        self.update_graph_stats()
        
    def delete_node(self, node):
        """Delete a node and its edges"""
        if node is None:
            return
        
        # Remove edges to this node
        for other_node in self.nodes.values():
            if node in other_node.neighbors:
                other_node.remove_neighbor(node)
        
        # Remove from special roles
        if self.source_node == node:
            self.source_node = None
        if node in self.goal_nodes:
            self.goal_nodes.remove(node)
        
        # Remove node
        del self.nodes[node.name]
        self.save_state()
        self.render()
        self.update_graph_stats()
    
    def add_edge(self, from_node, to_node, weight=1):
        """Add edge between two nodes"""
        if from_node and to_node and from_node != to_node:
            from_node.add_neighbor(to_node, weight)
            self.save_state()
            self.render()
            self.update_graph_stats()
    
    def delete_edge(self, from_node, to_node):
        """Delete edge between two nodes"""
        if from_node and to_node:
            from_node.remove_neighbor(to_node)
            self.save_state()
            self.render()
            self.update_graph_stats()
    
    def set_source(self, node):
        """Set source node"""
        if self.source_node:
            self.source_node.state = 'empty'
        node.state = 'source'
        self.source_node = node
        self.save_state()
        self.render()
    
    def toggle_goal(self, node):
        """Toggle goal state of node"""
        if node.state == 'goal':
            node.state = 'empty'
            if node in self.goal_nodes:
                self.goal_nodes.remove(node)
        else:
            if node.state == 'source':
                return  # Can't be both source and goal
            node.state = 'goal'
            self.goal_nodes.append(node)
        self.save_state()
        self.render()
    
    def set_heuristic(self, node, value):
        """Set heuristic value for node"""
        if node:
            node.heuristic = float(value)
            self.save_state()
            self.render()
    
    def set_edge_weight(self, from_node, to_node, weight):
        """Set edge weight"""
        if from_node and to_node and to_node in from_node.neighbors:
            from_node.neighbors[to_node] = float(weight)
            self.save_state()
            self.render()
    
    # ===== Node Finding =====
    
    def find_node_at(self, x, y):
        """Find node at screen position"""
        world_x, world_y = self.screen_to_world(x, y)
        
        for node in self.nodes.values():
            dx = node.x - world_x
            dy = node.y - world_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= 25:  # Node radius
                return node
        
        return None
    
    def find_edge_at(self, x, y):
        """Find edge at screen position"""
        world_x, world_y = self.screen_to_world(x, y)
        threshold = 10
        
        for node in self.nodes.values():
            for neighbor in node.get_neighbors():
                # Check if point is near line segment
                dist = self.point_to_line_distance(
                    world_x, world_y,
                    node.x, node.y,
                    neighbor.x, neighbor.y
                )
                
                if dist <= threshold:
                    return (node, neighbor)
        
        return None
    
    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Calculate distance from point to line segment"""
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        
        return math.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    # ===== Event Handlers =====
    
    def setup_event_listeners(self):
        """Setup all event listeners"""
        # Canvas events
        self.canvas.bind('mousedown', self.on_mouse_down)
        self.canvas.bind('mousemove', self.on_mouse_move)
        self.canvas.bind('mouseup', self.on_mouse_up)
        self.canvas.bind('wheel', self.on_mouse_wheel)
        self.canvas.bind('contextmenu', self.on_context_menu)  # Prevent right-click menu
        
        # Tool buttons
        tools = ['add-node', 'add-edge', 'move-node', 'delete-node', 
                'delete-edge', 'set-goal', 'edit-heuristic', 'edit-weight']
        for tool in tools:
            btn = document[f'tool-{tool}']
            btn.bind('click', lambda e, t=tool: self.select_tool(t))
        
        # Algorithm selection
        document['algorithm-select'].bind('change', self.on_algorithm_change)
        
        # Animation controls
        document['btn-start'].bind('click', self.start_search)
        document['btn-pause'].bind('click', self.toggle_pause)
        document['btn-stop'].bind('click', self.stop_search)
        document['btn-step-forward'].bind('click', self.step_forward)
        document['btn-step-back'].bind('click', self.step_backward)
        document['speed-slider'].bind('input', self.on_speed_change)
        
        # File operations
        document['btn-save-graph'].bind('click', self.save_graph)
        document['btn-load-graph'].bind('click', lambda e: document['file-input'].click())
        document['file-input'].bind('change', self.load_graph)
        document['btn-reset-canvas'].bind('click', self.reset_canvas)
        document['btn-clear-path'].bind('click', self.clear_path)
        
        # Export buttons
        document['btn-export-png'].bind('click', self.export_png)
        document['btn-export-gif'].bind('click', self.export_gif)
        document['btn-export-pdf'].bind('click', self.export_pdf)
        document['btn-export-svg'].bind('click', self.export_svg)
        document['btn-export-json'].bind('click', self.export_json)
        document['btn-export-csv'].bind('click', self.export_csv)
        
        # View controls
        document['btn-zoom-in'].bind('click', lambda e: self.zoom_by(1.2))
        document['btn-zoom-out'].bind('click', lambda e: self.zoom_by(0.8))
        document['btn-reset-view'].bind('click', self.reset_view)
        document['btn-toggle-labels'].bind('click', self.toggle_labels)
        document['btn-toggle-grid'].bind('click', self.toggle_grid)
        
        # Theme toggle
        document['theme-toggle'].bind('click', self.toggle_theme)
        
        # Example graphs
        document['example-simple'].bind('click', lambda e: self.load_example('simple'))
        document['example-tree'].bind('click', lambda e: self.load_example('tree'))
        document['example-grid'].bind('click', lambda e: self.load_example('grid'))
        document['example-weighted'].bind('click', lambda e: self.load_example('weighted'))
        
        # Keyboard shortcuts
        document.bind('keydown', self.on_key_down)
        
        # Window resize
        window.bind('resize', lambda e: self.on_resize())
    
    def on_mouse_down(self, event):
        """Handle mouse down on canvas"""
        # Track which button was pressed
        self.mouse_down_button = event.button
        self.pan_start_x = event.clientX
        self.pan_start_y = event.clientY
        
        # Right-click (2) or middle-click (1) = start panning
        if event.button == 2 or event.button == 1:
            event.preventDefault()  # Prevent context menu
            self.is_panning = True
            self.canvas.style.cursor = 'grabbing'
            return
        
        # Left-click (0) = tool action
        if event.button != 0:
            return
        
        x = event.clientX
        y = event.clientY
        node = self.find_node_at(x, y)
        
        if self.current_tool == 'add-node' and node is None:
            world_x, world_y = self.screen_to_world(x, y)
            self.add_node(world_x, world_y)
            
        elif self.current_tool == 'move-node' and node:
            self.dragging_node = node
            
        elif self.current_tool == 'delete-node' and node:
            self.delete_node(node)
            
        elif self.current_tool == 'add-edge':
            if node:
                if self.edge_start_node is None:
                    self.edge_start_node = node
                    self.selected_node = node
                    self.render()
                else:
                    self.add_edge(self.edge_start_node, node, 1)
                    self.edge_start_node = None
                    self.selected_node = None
                    
        elif self.current_tool == 'delete-edge':
            edge = self.find_edge_at(x, y)
            if edge:
                self.delete_edge(edge[0], edge[1])
                
        elif self.current_tool == 'set-goal' and node:
            self.toggle_goal(node)
            
        elif self.current_tool == 'edit-heuristic' and node:
            value = window.prompt(f'Enter heuristic value for node {node.name}:', str(node.heuristic))
            if value is not None:
                try:
                    self.set_heuristic(node, value)
                except:
                    alert('Invalid number')
                    
        elif self.current_tool == 'edit-weight':
            edge = self.find_edge_at(x, y)
            if edge:
                from_node, to_node = edge
                current_weight = from_node.get_weight(to_node)
                value = window.prompt(f'Enter edge weight:', str(current_weight))
                if value is not None:
                    try:
                        self.set_edge_weight(from_node, to_node, value)
                    except:
                        alert('Invalid number')
        
        # Start panning on empty space
        if node is None and self.current_tool in ['add-node', 'move-node']:
            self.is_panning = True
            self.pan_start_x = x
            self.pan_start_y = y
    
    def on_mouse_move(self, event):
        """Handle mouse move on canvas"""
        x = event.clientX
        y = event.clientY
        
        if self.is_panning:
            # Calculate delta from last position
            dx = x - self.pan_start_x
            dy = y - self.pan_start_y
            
            # Update pan
            self.view_offset_x += dx
            self.view_offset_y += dy
            
            # Update last position
            self.pan_start_x = x
            self.pan_start_y = y
            
            self.render()
            
        elif self.dragging_node:
            world_x, world_y = self.screen_to_world(x, y)
            self.dragging_node.x = world_x
            self.dragging_node.y = world_y
            self.render()
            
        else:
            # Update cursor based on hover
            node = self.find_node_at(x, y)
            
            if node:
                if self.current_tool == 'move-node':
                    self.canvas.style.cursor = 'grab'
                else:
                    self.canvas.style.cursor = 'pointer'
            else:
                if self.current_tool == 'add-node':
                    self.canvas.style.cursor = 'crosshair'
                elif self.current_tool == 'delete-node':
                    self.canvas.style.cursor = 'not-allowed'
                else:
                    self.canvas.style.cursor = 'default'
    
    def on_mouse_up(self, event):
        """Handle mouse up on canvas"""
        if self.dragging_node:
            self.save_state()
        
        self.dragging_node = None
        self.is_panning = False
        self.mouse_down_button = -1
        
        # Reset cursor
        self.canvas.style.cursor = 'default'
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming with smooth interpolation"""
        event.preventDefault()
        
        # Get mouse position in canvas coordinates
        world_x, world_y = self.screen_to_world(event.clientX, event.clientY)
        
        # Get canvas bounding rect for proper positioning
        rect = self.canvas.getBoundingClientRect()
        mouse_canvas_x = event.clientX - rect.left
        mouse_canvas_y = event.clientY - rect.top
        
        # Calculate zoom factor
        zoom_factor = 0.9 if event.deltaY > 0 else 1.1
        new_zoom = self.zoom * zoom_factor
        
        # Clamp zoom level
        new_zoom = max(0.1, min(5.0, new_zoom))
        
        # Calculate new pan to keep world point under cursor
        # Formula: new_pan = mouse_canvas_pos - (world_pos * new_zoom)
        self.view_offset_x = mouse_canvas_x - (world_x * new_zoom)
        self.view_offset_y = mouse_canvas_y - (world_y * new_zoom)
        
        self.zoom = new_zoom
        self.render()
    
    def on_key_down(self, event):
        """Handle keyboard shortcuts"""
        key = event.key.lower()
        
        if event.ctrlKey:
            if key == 'z':
                event.preventDefault()
                self.undo()
            elif key == 'y':
                event.preventDefault()
                self.redo()
            elif key == 's':
                event.preventDefault()
                self.save_graph(None)
        else:
            if key == 'a':
                self.select_tool('add-node')
            elif key == 'e':
                self.select_tool('add-edge')
            elif key == 'm':
                self.select_tool('move-node')
            elif key == 'd':
                self.select_tool('delete-node')
            elif key == 'g':
                self.select_tool('set-goal')
            elif key == 'h':
                self.select_tool('edit-heuristic')
            elif key == ' ':
                event.preventDefault()
                if self.is_animating:
                    self.toggle_pause(None)
                else:
                    self.start_search(None)
            elif key == 'arrowleft':
                self.step_backward(None)
            elif key == 'arrowright':
                self.step_forward(None)
            elif key == 'r':
                self.reset_view(None)
            elif key == 'l':
                self.toggle_labels(None)
    
    def select_tool(self, tool):
        """Select a tool"""
        self.current_tool = tool
        
        # Update button states
        tools = ['add-node', 'add-edge', 'move-node', 'delete-node', 
                'delete-edge', 'set-goal', 'edit-heuristic', 'edit-weight']
        for t in tools:
            btn = document[f'tool-{t}']
            if t == tool:
                btn.classList.add('active')
            else:
                btn.classList.remove('active')
        
        # Reset edge creation state
        self.edge_start_node = None
        self.selected_node = None
        self.render()
        
        # Re-initialize Lucide icons
        self.safe_lucide_init()
    
    def on_algorithm_change(self, event):
        """Handle algorithm selection change"""
        algo = document['algorithm-select'].value
        
        # Show/hide depth limit for DLS and IDS
        depth_container = document.select_one('.depth-limit-container')
        if algo in ['dls', 'ids']:
            depth_container.style.display = 'block'
        else:
            depth_container.style.display = 'none'
        
        # Algorithm-aware heuristic visibility
        heuristic_algorithms = ['greedy', 'astar']
        uninformed_algorithms = ['bfs', 'dfs', 'dls', 'ids']
        
        heuristic_toggle_btn = document['btn-toggle-labels']
        
        if algo in heuristic_algorithms:
            # Auto-show heuristics for informed algorithms
            if not self.show_labels:
                self.show_labels = True
                self.render()
            # Enable toggle button
            heuristic_toggle_btn.disabled = False
            heuristic_toggle_btn.style.opacity = '1'
            heuristic_toggle_btn.title = 'Toggle heuristic values'
        elif algo in uninformed_algorithms:
            # Auto-hide heuristics for uninformed algorithms
            if self.show_labels:
                self.show_labels = False
                self.render()
            # Disable toggle button
            heuristic_toggle_btn.disabled = True
            heuristic_toggle_btn.style.opacity = '0.5'
            heuristic_toggle_btn.title = 'Heuristics not used by this algorithm'
        else:
            # For UCS and bidirectional, enable but don't auto-toggle
            heuristic_toggle_btn.disabled = False
            heuristic_toggle_btn.style.opacity = '1'
            heuristic_toggle_btn.title = 'Toggle heuristic values'
        
        # Update algorithm info
        self.update_algorithm_info(algo)
        
        # Show/hide informed search info
        info_panel = document['informed-search-info']
        if algo in ['greedy', 'astar', 'ucs']:
            info_panel.style.display = 'block'
        else:
            info_panel.style.display = 'none'
        
        # Re-initialize Lucide icons
        self.safe_lucide_init()
    
    def on_speed_change(self, event):
        """Handle animation speed change"""
        self.animation_speed = int(document['speed-slider'].value)
        document['speed-value'].textContent = f'{self.animation_speed}x'
    
    def on_resize(self):
        """Handle window resize"""
        self.resize_canvas()
        self.render()
    
    def on_context_menu(self, event):
        """Prevent context menu on right-click"""
        event.preventDefault()
        return False
    
    # ===== Search Algorithm Execution =====
    
    def start_search(self, event):
        """Start search animation"""
        if len(self.nodes) == 0:
            alert('Please add nodes to the graph first')
            return
        
        if self.source_node is None:
            alert('Please set a source node')
            return
        
        if len(self.goal_nodes) == 0:
            alert('Please set a goal node')
            return
        
        # Clear previous search
        self.stop_search(None)
        self.clear_path(None)
        
        # Get selected algorithm
        algo = document['algorithm-select'].value
        goal = self.goal_nodes[0]  # Use first goal
        
        # Create search agent
        self.search_agent = SearchAgent(self.nodes, self.source_node, goal)
        
        # Get generator based on algorithm
        if algo == 'bfs':
            self.search_generator = self.search_agent.breadth_first_search()
        elif algo == 'dfs':
            self.search_generator = self.search_agent.depth_first_search()
        elif algo == 'dls':
            depth_limit = int(document['depth-limit'].value)
            self.search_generator = self.search_agent.depth_limited_search(depth_limit)
        elif algo == 'ids':
            max_depth = int(document['depth-limit'].value)
            self.search_generator = self.search_agent.iterative_deepening_search(max_depth)
        elif algo == 'ucs':
            self.search_generator = self.search_agent.uniform_cost_search()
        elif algo == 'bidirectional':
            self.search_generator = self.search_agent.bidirectional_search()
        elif algo == 'greedy':
            self.search_generator = self.search_agent.greedy_best_first_search()
        elif algo == 'astar':
            self.search_generator = self.search_agent.a_star_search()
        
        # Collect all animation states
        self.animation_states = []
        self.current_state_index = -1
        
        try:
            for _ in self.search_generator:
                state = self.capture_search_state()
                self.animation_states.append(state)
        except StopIteration:
            pass
        
        # Start animation
        self.is_animating = True
        self.is_paused = False
        self.current_state_index = -1
        
        # Update UI
        document['btn-start'].disabled = True
        document['btn-pause'].disabled = False
        document['btn-stop'].disabled = False
        document['btn-step-forward'].disabled = False
        document['btn-step-back'].disabled = False
        
        # Start auto-play
        self.animate_next_step()
    
    def capture_search_state(self):
        """Capture current search state for animation"""
        return {
            'fringe': self.search_agent.fringe_list[:],
            'visited': self.search_agent.visited_list[:],
            'traversal': self.search_agent.traversal_array[:],
            'path': self.search_agent.path_found[:],
            'node_states': {name: node.state for name, node in self.nodes.items()},
            'current_info': self.search_agent.current_node_info.copy()
        }
    
    def restore_search_state(self, state):
        """Restore search state from captured state"""
        # Format and update data display with proper styling
        self.update_data_display('fringe-list', state['fringe'])
        self.update_data_display('visited-list', state['visited'])
        self.update_data_display('traversal-list', state['traversal'])
        self.update_data_display('path-list', state['path'])
        
        # Update informed search info
        info = state['current_info']
        document['f-score'].textContent = f"g({info['g']}) + h({info['h']}) = {info['f']}"
        document['path-cost-current'].textContent = str(info['g'])
        
        # Restore node states
        for name, node_state in state['node_states'].items():
            if name in self.nodes:
                self.nodes[name].state = node_state
        
        self.render()
    
    def update_data_display(self, element_id, data_list):
        """Update data display with proper array formatting"""
        element = document[element_id]
        
        if not data_list or len(data_list) == 0:
            if element_id == 'fringe-list':
                element.innerHTML = '<span class="array-empty">Empty</span>'
            elif element_id == 'visited-list':
                element.innerHTML = '<span class="array-empty">Empty</span>'
            elif element_id == 'traversal-list':
                element.innerHTML = '<span class="array-empty">Empty</span>'
            elif element_id == 'path-list':
                element.innerHTML = '<span class="array-empty">No path found yet</span>'
        else:
            # Format as styled array
            formatted_items = []
            for item in data_list:
                formatted_items.append(f'<span class="array-item">{item}</span>')
            
            html = f'<span class="array-bracket">[</span> '
            html += '<span class="array-comma">, </span>'.join(formatted_items)
            html += f' <span class="array-bracket">]</span>'
            
            element.innerHTML = html
    
    def animate_next_step(self):
        """Animate next step"""
        if not self.is_animating or self.is_paused:
            return
        
        if self.current_state_index < len(self.animation_states) - 1:
            self.current_state_index += 1
            self.restore_search_state(self.animation_states[self.current_state_index])
            
            # Capture frame for GIF export
            if self.recording_gif:
                self.capture_gif_frame()
            
            # Calculate delay based on speed
            delay = int(1000 / self.animation_speed)
            
            # Schedule next step
            self.animation_timer = timer.set_timeout(self.animate_next_step, delay)
        else:
            # Animation complete
            self.animation_complete()
    
    def animation_complete(self):
        """Handle animation completion"""
        self.is_animating = False
        self.update_search_results()
        
        document['btn-start'].disabled = False
        document['btn-pause'].disabled = True
        
        if self.recording_gif:
            self.finish_gif_recording()
    
    def step_forward(self, event):
        """Step forward one animation frame"""
        if self.animation_states and self.current_state_index < len(self.animation_states) - 1:
            self.current_state_index += 1
            self.restore_search_state(self.animation_states[self.current_state_index])
            
            if self.current_state_index == len(self.animation_states) - 1:
                self.update_search_results()
    
    def step_backward(self, event):
        """Step backward one animation frame"""
        if self.animation_states and self.current_state_index > 0:
            self.current_state_index -= 1
            self.restore_search_state(self.animation_states[self.current_state_index])
    
    def toggle_pause(self, event):
        """Toggle pause/play"""
        self.is_paused = not self.is_paused
        
        btn = document['btn-pause']
        icon = btn.select_one('[data-lucide]')
        
        if self.is_paused:
            btn.innerHTML = '<i data-lucide="play"></i> Resume'
            if self.animation_timer:
                timer.clear_timeout(self.animation_timer)
        else:
            btn.innerHTML = '<i data-lucide="pause"></i> Pause'
            self.animate_next_step()
        
        # Re-initialize Lucide icons
        self.safe_lucide_init()
    
    def stop_search(self, event):
        """Stop search animation"""
        self.is_animating = False
        self.is_paused = False
        
        if self.animation_timer:
            timer.clear_timeout(self.animation_timer)
        
        document['btn-start'].disabled = False
        document['btn-pause'].disabled = True
        document['btn-stop'].disabled = True
        document['btn-step-forward'].disabled = True
        document['btn-step-back'].disabled = True
    
    def clear_path(self, event):
        """Clear search visualization"""
        for node in self.nodes.values():
            if node.state in ['visited', 'path']:
                node.state = 'empty'
            if node == self.source_node:
                node.state = 'source'
            if node in self.goal_nodes:
                node.state = 'goal'
        
        # Clear data display with empty states
        document['fringe-list'].innerHTML = '<span class="array-empty">Empty</span>'
        document['visited-list'].innerHTML = '<span class="array-empty">Empty</span>'
        document['traversal-list'].innerHTML = '<span class="array-empty">Empty</span>'
        document['path-list'].innerHTML = '<span class="array-empty">No path found yet</span>'
        document['f-score'].textContent = 'g(0) + h(0) = 0'
        document['path-cost-current'].textContent = '0'
        
        document['search-results'].innerHTML = '<p class="status-pending">Ready to start search...</p>'
        
        self.render()
    
    def update_search_results(self):
        """Update search results display"""
        if not self.search_agent:
            return
        
        results_html = ''
        
        if self.search_agent.success:
            results_html += '<p class="status-success">✅ Goal Found!</p>'
            results_html += f'<div class="result-metric"><span>Path Cost:</span><span>{self.search_agent.path_cost}</span></div>'
            results_html += f'<div class="result-metric"><span>Path Length:</span><span>{len(self.search_agent.path_found)} nodes</span></div>'
        else:
            results_html += '<p class="status-failure">❌ No Path Found</p>'
        
        results_html += f'<div class="result-metric"><span>Nodes Explored:</span><span>{self.search_agent.nodes_explored}</span></div>'
        results_html += f'<div class="result-metric"><span>Total States:</span><span>{len(self.animation_states)}</span></div>'
        
        document['search-results'].innerHTML = results_html
    
    # ===== Export Functions =====
    
    def export_png(self, event):
        """Export canvas as PNG"""
        # Create a temporary canvas to capture
        temp_canvas = html.CANVAS()
        temp_canvas.width = self.canvas.width
        temp_canvas.height = self.canvas.height
        temp_ctx = temp_canvas.getContext('2d')
        
        # Draw white background
        temp_ctx.fillStyle = '#ffffff'
        temp_ctx.fillRect(0, 0, temp_canvas.width, temp_canvas.height)
        
        # Draw current canvas content
        temp_ctx.drawImage(self.canvas, 0, 0)
        
        # Convert to PNG and download
        data_url = temp_canvas.toDataURL('image/png')
        self.download_file(data_url, 'graph.png')
    
    def export_gif(self, event):
        """Start GIF recording"""
        if not self.animation_states:
            alert('Please run a search first')
            return
        
        alert('GIF export will begin when you start the search animation. The recording will capture the entire algorithm execution.')
        self.recording_gif = True
        self.gif_frames = []
        
        # Restart animation for recording
        self.current_state_index = -1
        self.is_animating = True
        self.is_paused = False
        self.animate_next_step()
    
    def capture_gif_frame(self):
        """Capture current frame for GIF"""
        # In real implementation, would use gif.js library
        # For now, just collect canvas data URLs
        data_url = self.canvas.toDataURL('image/png')
        self.gif_frames.append(data_url)
    
    def finish_gif_recording(self):
        """Finish GIF recording and generate file"""
        self.recording_gif = False
        alert(f'GIF recording complete! {len(self.gif_frames)} frames captured.')
        # In real implementation, would use gif.js to create animated GIF
        # and trigger download
    
    def export_pdf(self, event):
        """Export comprehensive PDF report"""
        if not window.jsPDF:
            alert('PDF library not loaded')
            return
        
        # Create PDF document
        pdf = window.jsPDF.jsPDF()
        
        # Add title
        pdf.setFontSize(20)
        pdf.text('AI Search Algorithm Report', 20, 20)
        
        # Add metadata
        pdf.setFontSize(12)
        pdf.text(f'Algorithm: {document["algorithm-select"].options[document["algorithm-select"].selectedIndex].text}', 20, 35)
        pdf.text(f'Date: {window.Date().new().toLocaleString()}', 20, 42)
        
        # Add graph image
        data_url = self.canvas.toDataURL('image/png')
        pdf.addImage(data_url, 'PNG', 20, 50, 170, 100)
        
        # Add results
        pdf.setFontSize(14)
        pdf.text('Search Results:', 20, 160)
        pdf.setFontSize(10)
        
        y_pos = 170
        if self.search_agent:
            if self.search_agent.success:
                pdf.text(f'Status: Goal Found', 20, y_pos)
                y_pos += 7
                pdf.text(f'Path Cost: {self.search_agent.path_cost}', 20, y_pos)
                y_pos += 7
                pdf.text(f'Path: {" -> ".join(map(str, self.search_agent.path_found))}', 20, y_pos)
            else:
                pdf.text('Status: No Path Found', 20, y_pos)
            
            y_pos += 7
            pdf.text(f'Nodes Explored: {self.search_agent.nodes_explored}', 20, y_pos)
        
        # Save PDF
        pdf.save('search-report.pdf')
    
    def export_svg(self, event):
        """Export graph as SVG"""
        svg_content = self.generate_svg()
        blob = window.Blob.new([svg_content], {'type': 'image/svg+xml'})
        url = window.URL.createObjectURL(blob)
        self.download_file(url, 'graph.svg')
    
    def generate_svg(self):
        """Generate SVG representation of graph"""
        svg = f'<svg width="{self.canvas.width}" height="{self.canvas.height}" xmlns="http://www.w3.org/2000/svg">\n'
        
        # Add background
        svg += f'  <rect width="100%" height="100%" fill="#ffffff"/>\n'
        
        # Add edges
        for node in self.nodes.values():
            for neighbor, weight in node.neighbors.items():
                svg += f'  <line x1="{node.x}" y1="{node.y}" x2="{neighbor.x}" y2="{neighbor.y}" '
                svg += f'stroke="#9ca3af" stroke-width="2"/>\n'
                
                # Add weight label
                if weight != 1:
                    mid_x = (node.x + neighbor.x) / 2
                    mid_y = (node.y + neighbor.y) / 2
                    svg += f'  <text x="{mid_x}" y="{mid_y - 10}" text-anchor="middle" font-size="12">{weight}</text>\n'
        
        # Add nodes
        colors = {
            'empty': '#ffffff',
            'source': '#ef4444',
            'goal': '#10b981',
            'visited': '#8b5cf6',
            'path': '#f59e0b'
        }
        
        for node in self.nodes.values():
            color = colors.get(node.state, '#ffffff')
            svg += f'  <circle cx="{node.x}" cy="{node.y}" r="20" fill="{color}" stroke="#374151" stroke-width="2"/>\n'
            svg += f'  <text x="{node.x}" y="{node.y}" text-anchor="middle" dominant-baseline="middle" font-size="14">{node.name}</text>\n'
        
        svg += '</svg>'
        return svg
    
    def export_json(self, event):
        """Export graph data as JSON"""
        graph_data = {
            'metadata': {
                'version': '1.0',
                'created': str(window.Date().new().toISOString()),
                'algorithm': document['algorithm-select'].value,
                'node_count': len(self.nodes),
                'edge_count': sum(len(node.neighbors) for node in self.nodes.values())
            },
            'graph': {
                'nodes': [node.to_dict() for node in self.nodes.values()],
                'source': self.source_node.name if self.source_node else None,
                'goals': [node.name for node in self.goal_nodes]
            }
        }
        
        if self.search_agent:
            graph_data['results'] = {
                'success': self.search_agent.success,
                'path': self.search_agent.path_found,
                'path_cost': self.search_agent.path_cost,
                'nodes_explored': self.search_agent.nodes_explored
            }
        
        json_str = json.dumps(graph_data, indent=2)
        blob = window.Blob.new([json_str], {'type': 'application/json'})
        url = window.URL.createObjectURL(blob)
        self.download_file(url, 'graph.json')
    
    def export_csv(self, event):
        """Export performance metrics as CSV"""
        if not self.search_agent:
            alert('Please run a search first')
            return
        
        csv = 'Metric,Value\n'
        csv += f'Algorithm,{document["algorithm-select"].value}\n'
        csv += f'Success,{self.search_agent.success}\n'
        csv += f'Path Cost,{self.search_agent.path_cost}\n'
        csv += f'Nodes Explored,{self.search_agent.nodes_explored}\n'
        csv += f'Path Length,{len(self.search_agent.path_found)}\n'
        csv += f'Total States,{len(self.animation_states)}\n'
        csv += f'Node Count,{len(self.nodes)}\n'
        csv += f'Edge Count,{sum(len(node.neighbors) for node in self.nodes.values())}\n'
        
        blob = window.Blob.new([csv], {'type': 'text/csv'})
        url = window.URL.createObjectURL(blob)
        self.download_file(url, 'metrics.csv')
    
    def download_file(self, url, filename):
        """Trigger file download"""
        a = html.A()
        a.href = url
        a.download = filename
        a.click()
    
    # ===== File Operations =====
    
    def save_graph(self, event):
        """Save graph to JSON file"""
        self.export_json(None)
    
    def load_graph(self, event):
        """Load graph from JSON file"""
        file_input = document['file-input']
        if len(file_input.files) == 0:
            return
        
        file = file_input.files[0]
        reader = window.FileReader.new()
        
        def on_load(e):
            try:
                data = json.loads(e.target.result)
                self.load_graph_from_data(data)
            except Exception as ex:
                alert(f'Error loading graph: {ex}')
        
        reader.bind('load', on_load)
        reader.readAsText(file)
    
    def load_graph_from_data(self, data):
        """Load graph from data dictionary"""
        # Clear current graph
        self.nodes = {}
        self.node_counter = 0
        self.source_node = None
        self.goal_nodes = []
        
        # Load nodes
        for node_data in data['graph']['nodes']:
            node = Node(node_data['name'], node_data['x'], node_data['y'], node_data['heuristic'])
            node.state = node_data.get('state', 'empty')
            self.nodes[node.name] = node
            self.node_counter = max(self.node_counter, node.name + 1)
        
        # Load edges
        for node_data in data['graph']['nodes']:
            node = self.nodes[node_data['name']]
            for neighbor_name, weight in node_data.get('neighbors', {}).items():
                neighbor = self.nodes[int(neighbor_name)]
                node.add_neighbor(neighbor, weight)
        
        # Set source and goals
        if data['graph']['source'] is not None:
            self.source_node = self.nodes[data['graph']['source']]
        
        for goal_name in data['graph'].get('goals', []):
            self.goal_nodes.append(self.nodes[goal_name])
        
        self.render()
        self.update_graph_stats()
    
    def reset_canvas(self, event):
        """Reset canvas to empty"""
        if not window.confirm('Are you sure you want to clear the entire graph?'):
            return
        
        self.nodes = {}
        self.node_counter = 0
        self.source_node = None
        self.goal_nodes = []
        
        self.clear_path(None)
        self.stop_search(None)
        
        self.render()
        self.update_graph_stats()
    
    # ===== View Controls =====
    
    def zoom_by(self, factor):
        """Zoom by factor"""
        # Zoom toward center
        center_x = self.canvas.width / 2
        center_y = self.canvas.height / 2
        
        world_x_before, world_y_before = self.screen_to_world(center_x, center_y)
        self.zoom *= factor
        self.zoom = max(0.1, min(5.0, self.zoom))
        world_x_after, world_y_after = self.screen_to_world(center_x, center_y)
        
        self.view_offset_x += (world_x_after - world_x_before) * self.zoom
        self.view_offset_y += (world_y_after - world_y_before) * self.zoom
        
        self.render()
    
    def reset_view(self, event):
        """Reset view to default"""
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.render()
    
    def force_reset_view(self):
        """Force reset view on initialization"""
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.render()
    
    def toggle_labels(self, event):
        """Toggle heuristic labels"""
        self.show_labels = not self.show_labels
        self.render()
        
        # Update button state
        btn = document['btn-toggle-labels']
        if self.show_labels:
            btn.classList.add('active')
        else:
            btn.classList.remove('active')
    
    def safe_lucide_init(self):
        """Safely initialize Lucide icons"""
        try:
            if hasattr(window, 'lucide'):
                window.lucide.createIcons()
        except Exception as e:
            print(f"Lucide icons initialization error: {e}")
    
    def toggle_grid(self, event):
        """Toggle grid background"""
        self.show_grid = not self.show_grid
        self.render()
    
    def toggle_theme(self, event):
        """Toggle dark mode"""
        document.body.classList.toggle('dark-mode')
        btn = document['theme-toggle']
        
        # Get the icon element
        icon = btn.select_one('[data-lucide]')
        
        if 'dark-mode' in document.body.classList:
            # Switch to sun icon for dark mode
            icon.setAttribute('data-lucide', 'sun')
        else:
            # Switch to moon icon for light mode
            icon.setAttribute('data-lucide', 'moon')
        
        # Re-initialize Lucide icons
        self.safe_lucide_init()
        self.render()
    
    # ===== Undo/Redo =====
    
    def save_state(self):
        """Save current state for undo"""
        state = {
            'nodes': {name: node.to_dict() for name, node in self.nodes.items()},
            'node_counter': self.node_counter,
            'source': self.source_node.name if self.source_node else None,
            'goals': [node.name for node in self.goal_nodes]
        }
        
        self.undo_stack.append(json.dumps(state))
        self.redo_stack = []  # Clear redo stack on new action
        
        # Limit undo stack size
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
    
    def undo(self):
        """Undo last action"""
        if len(self.undo_stack) > 0:
            current = json.dumps({
                'nodes': {name: node.to_dict() for name, node in self.nodes.items()},
                'node_counter': self.node_counter,
                'source': self.source_node.name if self.source_node else None,
                'goals': [node.name for node in self.goal_nodes]
            })
            self.redo_stack.append(current)
            
            state = json.loads(self.undo_stack.pop())
            self.restore_state(state)
    
    def redo(self):
        """Redo last undone action"""
        if len(self.redo_stack) > 0:
            current = json.dumps({
                'nodes': {name: node.to_dict() for name, node in self.nodes.items()},
                'node_counter': self.node_counter,
                'source': self.source_node.name if self.source_node else None,
                'goals': [node.name for node in self.goal_nodes]
            })
            self.undo_stack.append(current)
            
            state = json.loads(self.redo_stack.pop())
            self.restore_state(state)
    
    def restore_state(self, state):
        """Restore graph state"""
        self.nodes = {}
        self.node_counter = state['node_counter']
        
        # Restore nodes
        for name, node_data in state['nodes'].items():
            node = Node(node_data['name'], node_data['x'], node_data['y'], node_data['heuristic'])
            node.state = node_data['state']
            self.nodes[int(name)] = node
        
        # Restore edges
        for name, node_data in state['nodes'].items():
            node = self.nodes[int(name)]
            for neighbor_name, weight in node_data['neighbors'].items():
                neighbor = self.nodes[int(neighbor_name)]
                node.add_neighbor(neighbor, weight)
        
        # Restore source and goals
        if state['source'] is not None:
            self.source_node = self.nodes[state['source']]
        else:
            self.source_node = None
        
        self.goal_nodes = [self.nodes[name] for name in state['goals']]
        
        self.render()
        self.update_graph_stats()
    
    # ===== UI Updates =====
    
    def update_graph_stats(self):
        """Update graph statistics display"""
        node_count = len(self.nodes)
        edge_count = sum(len(node.neighbors) for node in self.nodes.values())
        avg_degree = edge_count / node_count if node_count > 0 else 0
        
        document['stat-nodes'].textContent = str(node_count)
        document['stat-edges'].textContent = str(edge_count)
        document['stat-avg-degree'].textContent = f'{avg_degree:.2f}'
    
    def update_algorithm_info(self, algo):
        """Update algorithm information panel"""
        info_data = {
            'bfs': {
                'name': 'Breadth-First Search (BFS)',
                'strategy': 'Explores nodes level by level using a FIFO queue.',
                'complete': 'Yes',
                'optimal': 'Yes (for unweighted graphs)',
                'time': 'O(V + E)',
                'space': 'O(V)'
            },
            'dfs': {
                'name': 'Depth-First Search (DFS)',
                'strategy': 'Explores as deep as possible using a LIFO stack.',
                'complete': 'No (can get stuck in cycles)',
                'optimal': 'No',
                'time': 'O(V + E)',
                'space': 'O(V)'
            },
            'dls': {
                'name': 'Depth-Limited Search (DLS)',
                'strategy': 'DFS with a maximum depth limit to prevent infinite loops.',
                'complete': 'No (only if goal within limit)',
                'optimal': 'No',
                'time': 'O(b^l)',
                'space': 'O(l)'
            },
            'ids': {
                'name': 'Iterative Deepening Search (IDS)',
                'strategy': 'Repeatedly applies DLS with increasing limits.',
                'complete': 'Yes',
                'optimal': 'Yes (for unweighted graphs)',
                'time': 'O(b^d)',
                'space': 'O(d)'
            },
            'ucs': {
                'name': 'Uniform Cost Search (UCS)',
                'strategy': 'Always expands the lowest-cost node using a priority queue.',
                'complete': 'Yes',
                'optimal': 'Yes',
                'time': 'O(b^(1 + C*/ε))',
                'space': 'O(b^(1 + C*/ε))'
            },
            'bidirectional': {
                'name': 'Bidirectional Search',
                'strategy': 'Searches from both source and goal simultaneously.',
                'complete': 'Yes',
                'optimal': 'Yes (for unweighted graphs)',
                'time': 'O(b^(d/2))',
                'space': 'O(b^(d/2))'
            },
            'greedy': {
                'name': 'Greedy Best-First Search',
                'strategy': 'Expands node that appears closest to goal using heuristic h(n).',
                'complete': 'No',
                'optimal': 'No',
                'time': 'O(b^m)',
                'space': 'O(b^m)'
            },
            'astar': {
                'name': 'A* Search',
                'strategy': 'Uses f(n) = g(n) + h(n) to find optimal path efficiently.',
                'complete': 'Yes',
                'optimal': 'Yes (with admissible heuristic)',
                'time': 'O(b^d)',
                'space': 'O(b^d)'
            }
        }
        
        info = info_data.get(algo, info_data['bfs'])
        
        html_content = f'''
            <h4>{info['name']}</h4>
            <p><strong>Strategy:</strong> {info['strategy']}</p>
            <p><strong>Complete:</strong> {info['complete']}</p>
            <p><strong>Optimal:</strong> {info['optimal']}</p>
            <p><strong>Time:</strong> {info['time']}</p>
            <p><strong>Space:</strong> {info['space']}</p>
        '''
        
        document['algorithm-info'].innerHTML = html_content
    
    # ===== Example Graphs =====
    
    def load_example(self, example_type):
        """Load example graph"""
        if example_type == 'simple':
            self.load_simple_example()
        elif example_type == 'tree':
            self.load_tree_example()
        elif example_type == 'grid':
            self.load_grid_example()
        elif example_type == 'weighted':
            self.load_weighted_example()
    
    def load_simple_example(self):
        """Load simple path example"""
        self.reset_canvas(None)
        
        # Create nodes in a simple path
        positions = [(100, 200), (250, 150), (400, 200), (550, 150), (700, 200)]
        for i, (x, y) in enumerate(positions):
            node = Node(i, x, y, len(positions) - 1 - i)
            if i == 0:
                node.state = 'source'
                self.source_node = node
            elif i == len(positions) - 1:
                node.state = 'goal'
                self.goal_nodes.append(node)
            self.nodes[i] = node
        
        # Add edges
        for i in range(len(positions) - 1):
            self.nodes[i].add_neighbor(self.nodes[i + 1], 1)
        
        self.node_counter = len(positions)
        self.render()
        self.update_graph_stats()
    
    def load_tree_example(self):
        """Load binary tree example"""
        self.reset_canvas(None)
        
        # Create tree structure
        positions = [
            (400, 100),  # 0 - root
            (250, 200),  # 1 - left
            (550, 200),  # 2 - right
            (150, 300),  # 3 - left-left
            (350, 300),  # 4 - left-right
            (450, 300),  # 5 - right-left
            (650, 300),  # 6 - right-right
        ]
        
        for i, (x, y) in enumerate(positions):
            node = Node(i, x, y, abs(6 - i))
            if i == 0:
                node.state = 'source'
                self.source_node = node
            elif i == 6:
                node.state = 'goal'
                self.goal_nodes.append(node)
            self.nodes[i] = node
        
        # Add tree edges
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        for from_idx, to_idx in edges:
            self.nodes[from_idx].add_neighbor(self.nodes[to_idx], 1)
        
        self.node_counter = len(positions)
        self.render()
        self.update_graph_stats()
    
    def load_grid_example(self):
        """Load grid graph example"""
        self.reset_canvas(None)
        
        # Create 3x3 grid
        rows, cols = 3, 3
        spacing = 150
        start_x, start_y = 200, 150
        
        idx = 0
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing
                y = start_y + row * spacing
                manhattan_dist = abs(rows - 1 - row) + abs(cols - 1 - col)
                node = Node(idx, x, y, manhattan_dist)
                
                if row == 0 and col == 0:
                    node.state = 'source'
                    self.source_node = node
                elif row == rows - 1 and col == cols - 1:
                    node.state = 'goal'
                    self.goal_nodes.append(node)
                
                self.nodes[idx] = node
                idx += 1
        
        # Add grid edges
        for row in range(rows):
            for col in range(cols):
                idx = row * cols + col
                # Right
                if col < cols - 1:
                    self.nodes[idx].add_neighbor(self.nodes[idx + 1], 1)
                # Down
                if row < rows - 1:
                    self.nodes[idx].add_neighbor(self.nodes[idx + cols], 1)
        
        self.node_counter = rows * cols
        self.render()
        self.update_graph_stats()
    
    def load_weighted_example(self):
        """Load weighted graph example"""
        self.reset_canvas(None)
        
        # Create nodes
        positions = [(150, 200), (350, 150), (550, 150), (350, 300), (550, 300), (700, 225)]
        for i, (x, y) in enumerate(positions):
            node = Node(i, x, y, abs(5 - i))
            if i == 0:
                node.state = 'source'
                self.source_node = node
            elif i == 5:
                node.state = 'goal'
                self.goal_nodes.append(node)
            self.nodes[i] = node
        
        # Add weighted edges
        edges = [
            (0, 1, 2), (0, 3, 5),
            (1, 2, 3), (1, 3, 2),
            (2, 4, 1), (2, 5, 7),
            (3, 4, 1), (4, 5, 2)
        ]
        
        for from_idx, to_idx, weight in edges:
            self.nodes[from_idx].add_neighbor(self.nodes[to_idx], weight)
        
        self.node_counter = len(positions)
        self.render()
        self.update_graph_stats()

# Initialize visualizer
visualizer = GraphVisualizer()
