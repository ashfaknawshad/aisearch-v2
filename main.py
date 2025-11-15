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
        
        
        # Algorithm type for conditional rendering
        self.current_algo_type = 'uninformed'  # Default to uninformed (BFS)
        
        # Graph mode (None = not set yet, True = undirected, False = directed)
        self.graph_is_undirected = None
        self.pending_node_position = None  # Store position when modal is shown
        
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
        
        # Path edges for highlighting
        self.path_edges = set()  # Store (from_node.name, to_node.name) tuples
        
        # Export state
        self.recording_gif = False
        self.gif_frames = []
        self.sequence_frame_index = 0  # For image sequence export
        
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
        
        # Node ID with smart text color based on node state
        # Black text for light nodes (empty=white, path=yellow)
        # White text for dark nodes (source=red, goal=green, visited=purple)
        self.ctx.font = 'bold 14px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
        self.ctx.textAlign = 'center'
        self.ctx.textBaseline = 'middle'
        
        if node.state in ['empty', 'path']:
            text_color = '#111827'  # Black for white/yellow nodes
        else:
            text_color = '#ffffff'  # White for red/green/purple nodes
        
        self.ctx.fillStyle = text_color
        # Use custom_name if available, otherwise use node.name
        display_name = node.custom_name if hasattr(node, 'custom_name') else str(node.name)
        self.ctx.fillText(display_name, node.x, node.y - 6)
        
        # Highlight selected node
        if self.selected_node == node:
            self.ctx.strokeStyle = '#3b82f6'
            self.ctx.lineWidth = 3 / self.zoom
            self.ctx.beginPath()
            self.ctx.arc(node.x, node.y, radius + 5, 0, 2 * math.pi)
            self.ctx.stroke()
    
    def draw_node_label(self, node):
        """Draw node heuristic label (only for informed algorithms)"""
        # Only show heuristic for informed algorithms (A*, Greedy)
        should_show_heuristic = (
            node.heuristic > 0 and 
            hasattr(self, 'current_algo_type') and 
            self.current_algo_type == 'informed'
        )
        
        if should_show_heuristic:
            # Smart color based on node state (same logic as node name)
            # Black text for light nodes (empty=white, path=yellow)
            # White text for dark nodes (source=red, goal=green, visited=purple)
            if node.state in ['empty', 'path']:
                text_color = '#111827'  # Black for white/yellow nodes
            else:
                text_color = '#ffffff'  # White for red/green/purple nodes
            
            self.ctx.fillStyle = text_color
            self.ctx.font = 'bold 12px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            self.ctx.textAlign = 'center'
            # Format as integer (no decimal point)
            h_value = int(node.heuristic)
            self.ctx.fillText(f'h={h_value}', node.x, node.y + 8)
    
    def draw_node_on_context(self, ctx, node):
        """Draw a node on a specific context (for export)"""
        colors = {
            'empty': '#ffffff',
            'source': '#ef4444',
            'goal': '#10b981',
            'visited': '#8b5cf6',
            'path': '#f59e0b'
        }
        
        radius = 25
        
        # Node circle
        ctx.beginPath()
        ctx.arc(node.x, node.y, radius, 0, 2 * math.pi)
        ctx.fillStyle = colors.get(node.state, colors['empty'])
        ctx.fill()
        
        # Node border
        is_selected = (self.selected_node == node)
        ctx.strokeStyle = '#3b82f6' if is_selected else '#374151'
        ctx.lineWidth = 4 if is_selected else 3
        ctx.stroke()
        
        # Node ID
        ctx.font = 'bold 14px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        text_color = '#111827' if node.state == 'empty' else '#ffffff'
        ctx.fillStyle = text_color
        ctx.fillText(str(node.name), node.x, node.y - 6)
    
    def draw_node_label_on_context(self, ctx, node):
        """Draw node heuristic label on a specific context (for export)"""
        # Only show heuristic for informed algorithms
        should_show_heuristic = (
            node.heuristic > 0 and 
            hasattr(self, 'current_algo_type') and 
            self.current_algo_type == 'informed'
        )
        
        if should_show_heuristic:
            # Theme-aware text color
            is_dark = 'dark-mode' in document.body.classList
            text_color = '#ffffff' if is_dark else '#1f2937'
            
            ctx.fillStyle = text_color
            ctx.font = 'bold 12px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            ctx.textAlign = 'center'
            ctx.fillText(f'h={node.heuristic}', node.x, node.y + 8)
    
    def draw_edge_on_context(self, ctx, node1, node2, weight):
        """Draw an edge on a specific context (for export)"""
        # For undirected graphs, draw simple line without arrow
        if self.graph_is_undirected:
            self.draw_undirected_edge_on_context(ctx, node1, node2, weight)
            return
        
        # For directed graphs: check if there's a reverse edge (bidirectional)
        has_reverse = node2 in self.nodes.values() and node1 in node2.neighbors
        
        # Calculate offset for bidirectional edges
        offset_x = 0
        offset_y = 0
        if has_reverse:
            dx = node2.x - node1.x
            dy = node2.y - node1.y
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                offset_x = -dy / length * 10
                offset_y = dx / length * 10
        
        # Draw line with offset
        ctx.beginPath()
        ctx.moveTo(node1.x + offset_x, node1.y + offset_y)
        ctx.lineTo(node2.x + offset_x, node2.y + offset_y)
        ctx.strokeStyle = '#94a3b8'
        ctx.lineWidth = 3
        ctx.stroke()
        
        # Draw arrow head with offset
        angle = math.atan2(node2.y - node1.y, node2.x - node1.x)
        arrow_length = 12
        node_radius = 25
        end_x = node2.x - math.cos(angle) * node_radius + offset_x
        end_y = node2.y - math.sin(angle) * node_radius + offset_y
        
        ctx.beginPath()
        ctx.moveTo(end_x, end_y)
        ctx.lineTo(
            end_x - arrow_length * math.cos(angle - math.pi / 6),
            end_y - arrow_length * math.sin(angle - math.pi / 6)
        )
        ctx.moveTo(end_x, end_y)
        ctx.lineTo(
            end_x - arrow_length * math.cos(angle + math.pi / 6),
            end_y - arrow_length * math.sin(angle + math.pi / 6)
        )
        ctx.strokeStyle = '#94a3b8'
        ctx.lineWidth = 3
        ctx.stroke()
        
        # Draw weight label: show when labels are enabled (users can toggle labels)
        # This allows BFS/DFS/DLS/etc. to show path/edge costs when users enable labels.
        should_show_weight = (
            hasattr(self, 'show_labels') and self.show_labels
        )
        if should_show_weight:
            # Apply offset to label position
            mid_x = (node1.x + node2.x) / 2 + offset_x
            mid_y = (node1.y + node2.y) / 2 + offset_y
            
            ctx.font = 'bold 13px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            
            # Background
            text = str(int(weight)) if weight == int(weight) else str(weight)
            metrics = ctx.measureText(text)
            text_width = metrics.width
            padding = 5
            
            # Theme-aware colors
            is_dark = 'dark-mode' in document.body.classList
            bg_color = '#0a0a0a' if is_dark else '#ffffff'
            text_color = '#ffffff' if is_dark else '#1f2937'
            
            ctx.fillStyle = bg_color
            ctx.fillRect(
                mid_x - text_width / 2 - padding,
                mid_y - 9,
                text_width + padding * 2,
                18
            )
            
            # Text with theme-aware color
            ctx.fillStyle = text_color
            ctx.fillText(text, mid_x, mid_y)
    
    def draw_edge(self, node1, node2, weight):
        """Draw an edge between two nodes (line for undirected, arrow for directed)"""
        # For undirected graphs, draw simple line without arrow
        if self.graph_is_undirected:
            self.draw_undirected_edge(node1, node2, weight)
            return
        
        # For directed graphs: check if there's a reverse edge (bidirectional in directed graph)
        has_reverse = node2 in self.nodes.values() and node1 in node2.neighbors
        
        # Calculate offset for bidirectional edges in directed graphs
        offset = 0
        if has_reverse:
            # Offset perpendicular to the edge direction
            dx = node2.x - node1.x
            dy = node2.y - node1.y
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                # Perpendicular vector (normalized and scaled)
                offset_x = -dy / length * 10  # 10 pixels offset
                offset_y = dx / length * 10
            else:
                offset_x = 0
                offset_y = 0
        else:
            offset_x = 0
            offset_y = 0
        
        # Check if this edge is part of the final path
        edge_key = (node1.name, node2.name)
        is_path_edge = edge_key in self.path_edges
        
        # Draw line with offset - bright color if path edge, gray otherwise
        self.ctx.beginPath()
        self.ctx.moveTo(node1.x + offset_x, node1.y + offset_y)
        self.ctx.lineTo(node2.x + offset_x, node2.y + offset_y)
        self.ctx.strokeStyle = '#00ff00' if is_path_edge else '#94a3b8'  # Bright lime for path, gray for others
        self.ctx.lineWidth = 5 if is_path_edge else 3  # Thicker for path edges
        self.ctx.stroke()
        
        # Draw arrow head with offset
        self.draw_arrow_head(node1, node2, offset_x, offset_y, is_path_edge)
        
        # Show weight label when labels are enabled (users can toggle labels)
        should_show_weight = (hasattr(self, 'show_labels') and self.show_labels)
        if should_show_weight:
            # Apply offset to label position for bidirectional edges
            mid_x = (node1.x + node2.x) / 2 + offset_x
            mid_y = (node1.y + node2.y) / 2 + offset_y
            
            # Draw weight with background for readability
            self.ctx.font = 'bold 13px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            self.ctx.textAlign = 'center'
            self.ctx.textBaseline = 'middle'
            
            # Background
            text = str(int(weight)) if weight == int(weight) else str(weight)
            metrics = self.ctx.measureText(text)
            text_width = metrics.width
            padding = 5
            
            # Theme-aware colors
            is_dark = 'dark-mode' in document.body.classList
            bg_color = '#0a0a0a' if is_dark else '#ffffff'
            text_color = '#ffffff' if is_dark else '#1f2937'  # White in dark mode, dark in light mode
            
            self.ctx.fillStyle = bg_color
            self.ctx.fillRect(
                mid_x - text_width / 2 - padding,
                mid_y - 9,
                text_width + padding * 2,
                18
            )
            
            # Text with theme-aware color
            self.ctx.fillStyle = text_color
            self.ctx.fillText(text, mid_x, mid_y)
    
    def draw_undirected_edge(self, node1, node2, weight):
        """Draw an undirected edge (simple line without arrow)"""
        # Check if this edge is part of the final path
        edge_key = (node1.name, node2.name)
        reverse_edge_key = (node2.name, node1.name)
        is_path_edge = edge_key in self.path_edges or reverse_edge_key in self.path_edges
        
        # Draw line - bright color if path edge, gray otherwise
        self.ctx.beginPath()
        self.ctx.moveTo(node1.x, node1.y)
        self.ctx.lineTo(node2.x, node2.y)
        self.ctx.strokeStyle = '#00ff00' if is_path_edge else '#94a3b8'  # Bright lime for path, gray for others
        self.ctx.lineWidth = 5 if is_path_edge else 3  # Thicker for path edges
        self.ctx.stroke()
        
        # Show weight label when labels are enabled (users can toggle labels)
        should_show_weight = (hasattr(self, 'show_labels') and self.show_labels)

        if should_show_weight:
            mid_x = (node1.x + node2.x) / 2
            mid_y = (node1.y + node2.y) / 2
            
            self.ctx.font = 'bold 13px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            self.ctx.textAlign = 'center'
            self.ctx.textBaseline = 'middle'
            
            text = str(int(weight)) if weight == int(weight) else str(weight)
            metrics = self.ctx.measureText(text)
            text_width = metrics.width
            padding = 5
            
            is_dark = 'dark-mode' in document.body.classList
            bg_color = '#0a0a0a' if is_dark else '#ffffff'
            text_color = '#ffffff' if is_dark else '#1f2937'
            
            self.ctx.fillStyle = bg_color
            self.ctx.fillRect(
                mid_x - text_width / 2 - padding,
                mid_y - 9,
                text_width + padding * 2,
                18
            )
            
            self.ctx.fillStyle = text_color
            self.ctx.fillText(text, mid_x, mid_y)
    
    def draw_undirected_edge_on_context(self, ctx, node1, node2, weight):
        """Draw an undirected edge on export context (simple line without arrow)"""
        # Draw line
        ctx.beginPath()
        ctx.moveTo(node1.x, node1.y)
        ctx.lineTo(node2.x, node2.y)
        ctx.strokeStyle = '#94a3b8'
        ctx.lineWidth = 3
        ctx.stroke()
        
        # Draw weight label if applicable
        should_show_weight = (
            weight != 1 and 
            hasattr(self, 'current_algo_type') and 
            self.current_algo_type in ['informed', 'cost_only']
        )
        
        if should_show_weight:
            mid_x = (node1.x + node2.x) / 2
            mid_y = (node1.y + node2.y) / 2
            
            ctx.font = 'bold 13px Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            
            text = str(int(weight)) if weight == int(weight) else str(weight)
            metrics = ctx.measureText(text)
            text_width = metrics.width
            padding = 5
            
            is_dark = 'dark-mode' in document.body.classList
            bg_color = '#0a0a0a' if is_dark else '#ffffff'
            text_color = '#ffffff' if is_dark else '#1f2937'
            
            ctx.fillStyle = bg_color
            ctx.fillRect(
                mid_x - text_width / 2 - padding,
                mid_y - 9,
                text_width + padding * 2,
                18
            )
            
            ctx.fillStyle = text_color
            ctx.fillText(text, mid_x, mid_y)
    
    def draw_arrow_head(self, from_node, to_node, offset_x=0, offset_y=0, is_path_edge=False):
        """Draw arrow head on edge with optional offset for bidirectional edges"""
        angle = math.atan2(to_node.y - from_node.y, to_node.x - from_node.x)
        arrow_length = 12
        
        # Calculate arrow position (at edge of node circle) with offset
        node_radius = 25
        end_x = to_node.x - math.cos(angle) * node_radius + offset_x
        end_y = to_node.y - math.sin(angle) * node_radius + offset_y
        
        # Arrow color - bright for path, gray for others
        arrow_color = '#00ff00' if is_path_edge else '#94a3b8'
        arrow_width = 4 if is_path_edge else 3
        
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
        self.ctx.strokeStyle = arrow_color
        self.ctx.lineWidth = arrow_width
        self.ctx.stroke()
    
    # ===== Graph Operations =====
    
    def show_graph_type_modal(self):
        """Show modal to choose graph type"""
        modal = document['graph-type-modal']
        modal.style.display = 'flex'
        
        # Reinitialize Lucide icons in modal
        timer.set_timeout(lambda: self.safe_lucide_init(), 50)
    
    def hide_graph_type_modal(self):
        """Hide graph type modal"""
        modal = document['graph-type-modal']
        modal.style.display = 'none'
    
    def set_graph_type_directed(self, event=None):
        """User selected DIRECTED graph type"""
        self.graph_is_undirected = False
        self.hide_graph_type_modal()
        self.update_graph_type_indicator()
        print('📊 Graph type set to: DIRECTED (edges shown as arrows)')
        
        # Now create the first node
        if self.pending_node_position:
            x, y = self.pending_node_position
            self.pending_node_position = None
            self.add_node(x, y)
    
    def set_graph_type_undirected(self, event=None):
        """User selected UNDIRECTED graph type"""
        self.graph_is_undirected = True
        self.hide_graph_type_modal()
        self.update_graph_type_indicator()
        print('📊 Graph type set to: UNDIRECTED (edges shown as lines)')
        
        # Now create the first node
        if self.pending_node_position:
            x, y = self.pending_node_position
            self.pending_node_position = None
            self.add_node(x, y)
    
    def update_graph_type_indicator(self):
        """Update the graph type indicator in the control panel"""
        indicator = document['graph-type-indicator']
        text_elem = document['graph-type-text']
        dropdown = document['graph-type-select']
        
        if self.graph_is_undirected is None:
            indicator.style.display = 'none'
            # Keep dropdown enabled for initial selection
        else:
            indicator.style.display = 'block'
            if self.graph_is_undirected:
                text_elem.textContent = 'Undirected'
                indicator.style.background = 'rgba(16, 185, 129, 0.1)'
                indicator.style.borderColor = 'rgba(16, 185, 129, 0.3)'
                dropdown.value = 'undirected'
            else:
                text_elem.textContent = 'Directed'
                indicator.style.background = 'rgba(59, 130, 246, 0.1)'
                indicator.style.borderColor = 'rgba(59, 130, 246, 0.3)'
                dropdown.value = 'directed'
            
            # Reinitialize Lucide icons
            timer.set_timeout(lambda: self.safe_lucide_init(), 50)
    
    def add_node(self, x, y):
        """Add a new node at position with optional custom name"""
        # First node: ask if graph is directed or undirected using modal
        if len(self.nodes) == 0 and self.graph_is_undirected is None:
            # Store position for later use
            self.pending_node_position = (x, y)
            # Show modal and wait for user selection
            self.show_graph_type_modal()
            return  # Exit early - modal buttons will call add_node_with_type()
        
        # Store position and show node name modal
        self.pending_node_position = (x, y)
        self.show_node_name_modal()
    
    def is_modal_open(self):
        """Check if any modal is currently open"""
        graph_type_modal = document['graph-type-modal']
        node_name_modal = document['node-name-modal']
        
        return (graph_type_modal.style.display == 'flex' or 
                node_name_modal.style.display == 'flex')
    
    def show_node_name_modal(self):
        """Show modal to enter node name"""
        modal = document['node-name-modal']
        input_field = document['node-name-input']
        
        # Set default value
        default_name = str(self.node_counter)
        input_field.value = default_name
        
        # Show modal and focus input
        modal.style.display = 'flex'
        timer.set_timeout(lambda: input_field.focus(), 50)
        timer.set_timeout(lambda: input_field.select(), 100)
        
        # Reinitialize Lucide icons
        timer.set_timeout(lambda: self.safe_lucide_init(), 50)
    
    def hide_node_name_modal(self):
        """Hide node name modal"""
        modal = document['node-name-modal']
        modal.style.display = 'none'
    
    def create_node_with_name(self, event=None):
        """Create node with the name from modal"""
        input_field = document['node-name-input']
        name = input_field.value.strip()
        
        # If empty, use default number
        if name == '':
            name = str(self.node_counter)
        
        # Check if name already exists
        for existing_node in self.nodes.values():
            if str(existing_node.name) == name:
                alert(f'Node "{name}" already exists! Using default number.')
                name = str(self.node_counter)
                break
        
        # Get stored position
        if not self.pending_node_position:
            self.hide_node_name_modal()
            return
        
        x, y = self.pending_node_position
        self.pending_node_position = None
        
        # Create the node with node_counter as ID
        node = Node(self.node_counter, x, y, 0)
        node.custom_name = name  # Store custom name separately
        
        # First node becomes source
        if len(self.nodes) == 0:
            node.state = 'source'
            self.source_node = node
        
        self.nodes[self.node_counter] = node
        self.node_counter += 1
        self.save_state()
        self.render()
        self.update_graph_stats()
        
        # Hide modal
        self.hide_node_name_modal()
    
    def cancel_node_creation(self, event=None):
        """Cancel node creation"""
        self.pending_node_position = None
        self.hide_node_name_modal()
    
    def on_node_name_keypress(self, event):
        """Handle Enter key in node name input"""
        if event.key == 'Enter' or event.keyCode == 13:
            event.preventDefault()
            self.create_node_with_name()
        elif event.key == 'Escape' or event.keyCode == 27:
            event.preventDefault()
            self.cancel_node_creation()
        
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
        
        # Clear selection if this node was selected
        if self.selected_node == node:
            self.selected_node = None
        
        # Clear edge start if this node was being used for edge creation
        if self.edge_start_node == node:
            self.edge_start_node = None
        
        # Remove node from dictionary
        del self.nodes[node.name]
        
        self.save_state()
        self.render()
        self.update_graph_stats()
    
    def add_edge(self, from_node, to_node, weight=1):
        """Add edge between two nodes (adds reverse edge if undirected graph)"""
        if from_node and to_node and from_node != to_node:
            from_node.add_neighbor(to_node, weight)
            # If undirected graph, add reverse edge with same weight
            if self.graph_is_undirected:
                to_node.add_neighbor(from_node, weight)
            self.save_state()
            self.render()
            self.update_graph_stats()
    
    def delete_edge(self, from_node, to_node):
        """Delete edge between two nodes (deletes reverse edge if undirected graph)"""
        if from_node and to_node:
            from_node.remove_neighbor(to_node)
            # If undirected graph, also delete reverse edge
            if self.graph_is_undirected:
                to_node.remove_neighbor(from_node)
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
    
    def toggle_source(self, node):
        """Toggle source state of node"""
        if node.state == 'source':
            # Remove source
            node.state = 'empty'
            self.source_node = None
        else:
            # Set as source (remove from goals if needed)
            if node in self.goal_nodes:
                self.goal_nodes.remove(node)
            # Clear previous source
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
        """Set edge weight (updates both directions in undirected graph)"""
        if from_node and to_node and to_node in from_node.neighbors:
            from_node.neighbors[to_node] = float(weight)
            # If undirected graph, also update reverse edge weight
            if self.graph_is_undirected and from_node in to_node.neighbors:
                to_node.neighbors[from_node] = float(weight)
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
        """Find edge at screen position, considering bidirectional edge offsets"""
        world_x, world_y = self.screen_to_world(x, y)
        threshold = 10
        
        # Track closest edge
        closest_edge = None
        closest_dist = float('inf')
        
        for node in self.nodes.values():
            for neighbor in node.get_neighbors():
                # Check if there's a reverse edge (bidirectional)
                has_reverse = neighbor in self.nodes.values() and node in neighbor.neighbors
                
                # Calculate offset for bidirectional edges
                offset_x = 0
                offset_y = 0
                if has_reverse:
                    dx = neighbor.x - node.x
                    dy = neighbor.y - node.y
                    length = math.sqrt(dx * dx + dy * dy)
                    if length > 0:
                        offset_x = -dy / length * 10
                        offset_y = dx / length * 10
                
                # Check if point is near the offset line segment
                dist = self.point_to_line_distance(
                    world_x, world_y,
                    node.x + offset_x, node.y + offset_y,
                    neighbor.x + offset_x, neighbor.y + offset_y
                )
                
                # Keep track of closest edge
                if dist < closest_dist and dist <= threshold:
                    closest_dist = dist
                    closest_edge = (node, neighbor)
        
        return closest_edge
    
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
                'delete-edge', 'set-source', 'set-goal', 'edit-heuristic', 'edit-weight', 'rename-node']
        for tool in tools:
            btn = document[f'tool-{tool}']
            btn.bind('click', lambda e, t=tool: self.select_tool(t))
        
        # Algorithm selection
        document['algorithm-select'].bind('change', self.on_algorithm_change)
        document['graph-type-select'].bind('change', self.on_graph_type_change)
        
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
        document['btn-export-sequence'].bind('click', self.export_sequence)
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

        
        
        # Graph type modal buttons
        document['modal-btn-directed'].bind('click', self.set_graph_type_directed)
        document['modal-btn-undirected'].bind('click', self.set_graph_type_undirected)
        
        # Node name modal buttons
        document['modal-btn-node-ok'].bind('click', self.create_node_with_name)
        document['modal-btn-node-cancel'].bind('click', self.cancel_node_creation)
        document['node-name-input'].bind('keypress', self.on_node_name_keypress)
        
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
        # Ignore if any modal is open
        if self.is_modal_open():
            return
        
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
                    # Complete edge
                    self.add_edge(self.edge_start_node, node, 1)
                    self.edge_start_node = None
                    self.selected_node = None

        elif self.current_tool == 'delete-edge':
            edge = self.find_edge_at(x, y)
            if edge:
                self.delete_edge(edge[0], edge[1])
        
        elif self.current_tool == 'set-source' and node:
            self.toggle_source(node)
                
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
        
        elif self.current_tool == 'rename-node' and node:
            new_name = window.prompt(f'Enter new name for node {node.name}:', str(node.name))
            if new_name is not None and new_name.strip() != '':
                new_name = new_name.strip()
                # Check if name already exists
                name_exists = False
                for existing_node in self.nodes.values():
                    if existing_node != node and str(existing_node.name) == new_name:
                        alert(f'Node "{new_name}" already exists!')
                        name_exists = True
                        break
                
                if not name_exists:
                    node.name = new_name
                    self.save_state()
                    self.render()
        
        # Start panning on empty space (only for move-node tool, not add-node)
        # Don't enable panning for add-node to prevent unwanted pan mode after creating nodes
        if node is None and self.current_tool == 'move-node':
            self.is_panning = True
            self.pan_start_x = x
            self.pan_start_y = y
    
    def on_mouse_move(self, event):
        """Handle mouse move on canvas"""
        # Ignore if any modal is open
        if self.is_modal_open():
            return
        
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
                elif self.current_tool in ['rename-node', 'edit-heuristic']:
                    self.canvas.style.cursor = 'text'
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
        # Ignore if any modal is open
        if self.is_modal_open():
            return
        
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
        # Don't process shortcuts if a modal is open (prevents shortcuts from triggering while typing node names)
        if self.is_modal_open():
            return
        
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
            elif key == 's':
                self.select_tool('set-source')
            elif key == 'g':
                self.select_tool('set-goal')
            elif key == 'h':
                self.select_tool('edit-heuristic')
            elif key == 'w':
                self.select_tool('edit-weight')
            elif key == 'n':
                self.select_tool('rename-node')
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
                'delete-edge', 'set-source', 'set-goal', 'edit-heuristic', 'edit-weight', 'rename-node']
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
        
        # Show/hide depth limit for DLS only (IDS automatically tries increasing depths)
        depth_container = document.select_one('.depth-limit-container')
        if algo == 'dls':
            depth_container.style.display = 'block'
        else:
            depth_container.style.display = 'none'
        
        # Algorithm categories
        informed_algorithms = ['greedy', 'astar']  # Use both heuristic and path cost for decisions
        cost_algorithms = ['ucs']  # Use only path cost (edge weights) for decisions
        uninformed_algorithms = ['bfs', 'dfs', 'dls', 'ids', 'bidirectional']  # Don't use weights for decisions, but still calculate path cost
        
        heuristic_toggle_btn = document['btn-toggle-labels']
        
        # Store current algorithm type for rendering decisions
        self.current_algo_type = None
        
        # Get tool buttons
        edit_heuristic_btn = document['tool-edit-heuristic']
        edit_weight_btn = document['tool-edit-weight']
        
        if algo in informed_algorithms:
            # Informed search: Show heuristics and enable path cost editing
            self.current_algo_type = 'informed'
            if not self.show_labels:
                self.show_labels = True
                self.render()
            heuristic_toggle_btn.disabled = False
            heuristic_toggle_btn.style.opacity = '1'
            heuristic_toggle_btn.title = 'Toggle heuristic values'
            
            # Enable both editing tools
            edit_heuristic_btn.disabled = False
            edit_heuristic_btn.style.opacity = '1'
            edit_heuristic_btn.title = 'Edit Heuristic (H)'
            
            edit_weight_btn.disabled = False
            edit_weight_btn.style.opacity = '1'
            edit_weight_btn.title = 'Edit Weight (W)'
            
            print(f'ℹ️ {algo.upper()}: Uses heuristics and path costs for decisions')
            
        elif algo in cost_algorithms:
            # UCS: Enable label toggle to show path costs
            self.current_algo_type = 'cost_only'
            if not self.show_labels:
                self.show_labels = True
                self.render()
            # Allow the user to toggle labels (show/hide path costs)
            heuristic_toggle_btn.disabled = False
            heuristic_toggle_btn.style.opacity = '1'
            heuristic_toggle_btn.title = 'Toggle labels (path cost)'
            
            # Disable heuristic editing, enable weight editing
            edit_heuristic_btn.disabled = True
            edit_heuristic_btn.style.opacity = '0.5'
            edit_heuristic_btn.title = 'Heuristics not used by UCS'
            
            edit_weight_btn.disabled = False
            edit_weight_btn.style.opacity = '1'
            edit_weight_btn.title = 'Edit Weight (W)'
            
            print(f'ℹ️ UCS: Uses path costs (edge weights) for decisions')
            
        elif algo in uninformed_algorithms:
            # Uninformed: Hide heuristics, but ALLOW weight editing (path cost still calculated)
            self.current_algo_type = 'uninformed'
            if self.show_labels:
                self.show_labels = False
                self.render()
            # Allow the user to toggle labels (show/hide) even for uninformed algorithms
            heuristic_toggle_btn.disabled = False
            heuristic_toggle_btn.style.opacity = '1'
            heuristic_toggle_btn.title = 'Toggle labels (heuristics / path cost)'
            
            # Enable weight editing for all algorithms (path cost always displayed)
            edit_heuristic_btn.disabled = True
            edit_heuristic_btn.style.opacity = '0.5'
            edit_heuristic_btn.title = 'Heuristics not used by uninformed search'
            
            edit_weight_btn.disabled = False
            edit_weight_btn.style.opacity = '1'
            edit_weight_btn.title = 'Edit Weight (W) - Path cost will be calculated and displayed'
            
            print(f'ℹ️ {algo.upper()}: Doesn\'t use weights for decisions, but path cost is calculated')
        else:
            # Default for bidirectional
            self.current_algo_type = 'uninformed'
            heuristic_toggle_btn.disabled = True
            heuristic_toggle_btn.style.opacity = '0.5'
            heuristic_toggle_btn.title = 'Toggle heuristic values'
            
            # Disable both editing tools
            edit_heuristic_btn.disabled = True
            edit_heuristic_btn.style.opacity = '0.5'
            edit_heuristic_btn.title = 'Heuristics not used'
            
            edit_weight_btn.disabled = True
            edit_weight_btn.style.opacity = '0.5'
            edit_weight_btn.title = 'Edge weights not used'
        
        # Update algorithm info
        self.update_algorithm_info(algo)
        
        # Show/hide informed search info
        info_panel = document['informed-search-info']
        if algo in ['greedy', 'astar', 'ucs']:
            info_panel.style.display = 'block'
            
            # Update f(n) label based on algorithm
            if algo == 'greedy':
                document['f-score'].textContent = 'h(0) = 0'
            else:
                document['f-score'].textContent = 'g(0) + h(0) = 0'
            
            document['path-cost-current'].textContent = '0'
        else:
            info_panel.style.display = 'none'
        
        # Re-render to update visible weights/heuristics
        self.render()
        
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
        
        # Get selected algorithm
        algo = document['algorithm-select'].value
        
        # Validate heuristics for informed search algorithms
        if algo in ['greedy', 'astar']:
            # Check if any goal node has non-zero heuristic or if any node has heuristic set
            has_heuristics = False
            for node in self.nodes.values():
                if node.heuristic > 0:
                    has_heuristics = True
                    break
            
            if not has_heuristics:
                algo_name = 'Greedy Best-First Search' if algo == 'greedy' else 'A* Search'
                alert(f'{algo_name} requires heuristic values!\n\n'
                      f'Please use the "Edit Heuristic" tool to set h(n) values for your nodes.\n\n'
                      f'Heuristic = estimated cost from each node to the goal.')
                return
        
        # Clear previous search
        self.stop_search(None)
        self.clear_path(None)
        
        goal = self.goal_nodes[0]  # For backward compatibility with single goal
        
        # Create search agent with all goal nodes
        self.search_agent = SearchAgent(self.nodes, self.source_node, goal, self.goal_nodes)
        
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
        
        # Build path edges set for highlighting
        path_list = state['path']
        self.path_edges.clear()
        for i in range(len(path_list) - 1):
            from_node_name = path_list[i]
            to_node_name = path_list[i + 1]
            self.path_edges.add((from_node_name, to_node_name))
        
        # Update informed search info
        info = state['current_info']
        algo = document['algorithm-select'].value
        
        # Display correct formula based on algorithm
        if algo == 'greedy':
            # Greedy only uses h(n)
            document['f-score'].textContent = f"h({info['h']}) = {info['h']}"
        elif algo == 'astar':
            # A* uses g(n) + h(n)
            document['f-score'].textContent = f"g({info['g']}) + h({info['h']}) = {info['f']}"
        else:
            # UCS or other cost-based
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
            # Format as styled array - convert node IDs to display names
            formatted_items = []
            for item in data_list:
                # Look up node to get custom_name if available
                display_name = item
                if item in self.nodes:
                    node = self.nodes[item]
                    display_name = node.custom_name if hasattr(node, 'custom_name') else str(item)
                formatted_items.append(f'<span class="array-item">{display_name}</span>')
            
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
        
        # Clear path edges highlighting
        self.path_edges.clear()
        
        # Clear data display with empty states
        document['fringe-list'].innerHTML = '<span class="array-empty">Empty</span>'
        document['visited-list'].innerHTML = '<span class="array-empty">Empty</span>'
        document['traversal-list'].innerHTML = '<span class="array-empty">Empty</span>'
        document['path-list'].innerHTML = '<span class="array-empty">No path found yet</span>'
        
        # Reset f-score based on current algorithm
        algo = document['algorithm-select'].value
        if algo == 'greedy':
            document['f-score'].textContent = 'h(0) = 0'
        else:
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
            failure_msg = self.search_agent.failure_reason if self.search_agent.failure_reason else 'No Path Found'
            results_html += f'<p class="status-failure">❌ {failure_msg}</p>'
        
        results_html += f'<div class="result-metric"><span>Nodes Explored:</span><span>{self.search_agent.nodes_explored}</span></div>'
        results_html += f'<div class="result-metric"><span>Total States:</span><span>{len(self.animation_states)}</span></div>'
        
        document['search-results'].innerHTML = results_html
    
    # ===== Export Functions =====
    
    def export_png(self, event):
        """Export canvas as PNG - direct method like V1"""
        # Directly export the canvas without any intermediate copying
        # This is exactly how V1 does it: canvas.toDataURL()
        data_url = self.canvas.toDataURL('image/png')
        self.download_file(data_url, f'ai-search-{int(window.Date.now())}.png')
        
        print(f'✓ PNG exported: {self.canvas.width}x{self.canvas.height}px')
    
    def export_gif(self, event):
        """Start GIF recording - V1 approach with workers"""
        if not self.animation_states:
            alert('Please run a search first')
            return
        
        # Check if gif.js is available
        if not hasattr(window, 'GIF'):
            alert('GIF library not loaded. Please check your internet connection and refresh the page.')
            return
        
        # Count frames for better feedback
        frame_count = len(self.animation_states)
        alert(f'GIF export will begin.\n\n• {frame_count} frames to capture\n• Animation will replay automatically\n• Please wait for download...')
        
        print(f'📐 GIF dimensions: {self.window_width}x{self.window_height}px (canvas buffer: {self.canvas.width}x{self.canvas.height}px, DPI: {self.dpi_scale})')
        
        # Initialize GIF encoder with workers (V1 approach)
        gif_options = window.Object.new()
        gif_options.workers = 2  # Use workers like V1
        gif_options.quality = 10
        gif_options.width = self.window_width
        gif_options.height = self.window_height
        gif_options.workerScript = 'gif.worker.js'  # Local worker file to avoid CORS
        
        self.gif_encoder = window.GIF.new(gif_options)
        
        # Store reference to self for callback
        visualizer = self
        
        # Progress callback
        def on_gif_progress(progress):
            print(f'GIF encoding: {int(progress * 100)}%')
        
        self.gif_encoder.on('progress', on_gif_progress)
        
        # Set up finish callback (gif.js passes blob as first arg)
        def on_gif_finished(*args):
            try:
                blob = args[0]  # First argument is the blob
                print(f'✅ GIF encoding finished! Blob size: {blob.size} bytes')
                
                # Create download link
                url = window.URL.createObjectURL(blob)
                visualizer.download_file(url, f'search_animation_{int(window.Date.now())}.gif')
                
                # Clean up URL after a short delay
                def cleanup():
                    try:
                        window.URL.revokeObjectURL(url)
                    except:
                        pass
                timer.set_timeout(cleanup, 1000)
                
                alert(f'GIF export complete! {len(visualizer.gif_frames)} frames encoded.')
                visualizer.recording_gif = False
                visualizer.gif_frames = []
            except Exception as e:
                print(f'❌ Error in GIF finished callback: {e}')
                import traceback
                traceback.print_exc()
                alert(f'Error saving GIF: {e}')
                visualizer.recording_gif = False
        
        # Bind the callback
        self.gif_encoder.on('finished', on_gif_finished)
        
        self.recording_gif = True
        self.gif_frames = []
        
        # Restart animation for recording
        self.current_state_index = -1
        self.is_animating = True
        self.is_paused = False
        self.animate_next_step()
    
    def capture_gif_frame(self):
        """Capture current frame - V1 approach"""
        if not self.recording_gif or not hasattr(self, 'gif_encoder'):
            return
        
        try:
            # Calculate delay based on animation speed (1-10)
            delay = 1050 - (self.animation_speed * 100)
            
            # Add current canvas state to GIF (V1 approach)
            frame_options = window.Object.new()
            frame_options.copy = True
            frame_options.delay = delay
            
            self.gif_encoder.addFrame(self.canvas, frame_options)
            self.gif_frames.append(True)  # Track frame count
            
            # Log progress
            frame_num = len(self.gif_frames)
            total_frames = len(self.animation_states)
            if frame_num % 5 == 0 or frame_num == total_frames:
                print(f'✓ Captured frame {frame_num}/{total_frames} ({int(frame_num/total_frames*100)}%)')
        except Exception as e:
            print(f'❌ Error capturing frame: {e}')
            import traceback
            traceback.print_exc()
    
    def finish_gif_recording(self):
        """Finish GIF recording and render"""
        if not self.recording_gif or not hasattr(self, 'gif_encoder'):
            return
        
        # Check if we captured any frames
        if len(self.gif_frames) == 0:
            alert('No frames captured for GIF')
            self.recording_gif = False
            return
        
        print(f'\n🎬 Frame capture complete! Captured {len(self.gif_frames)} frames')
        
        # Download all frames as individual PNGs
        print(f'📥 Downloading {len(self.gif_frames)} frames...')
        
        try:
            # Render the GIF (V1 approach - will trigger 'finished' callback)
            self.gif_encoder.render()
        except Exception as e:
            print(f'Error rendering GIF: {e}')
            import traceback
            traceback.print_exc()
            alert(f'Error rendering GIF: {e}')
            self.recording_gif = False
            return
    
    def export_sequence(self, event):
        """Export animation frames as PNG in a ZIP file"""
        if not self.animation_states:
            alert('Run search first')
            return
        
        if not hasattr(window, 'JSZip'):
            alert('ZIP library not loaded')
            return
        
        self.zip_file = window.JSZip.new()
        self.sequence_frame_index = 0
        self.export_next_zip_frame()
    
    def export_next_zip_frame(self):
        """Add next frame to ZIP"""
        if self.sequence_frame_index >= len(self.animation_states):
            self.finish_zip_export()
            return
        
        state = self.animation_states[self.sequence_frame_index]
        self.restore_search_state(state)
        
        frame_num = self.sequence_frame_index + 1
        filename = f'frame_{frame_num:04d}.png'
        data_url = self.canvas.toDataURL('image/png')
        base64_data = data_url.split('base64,')[1]
        self.zip_file.file(filename, base64_data, {'base64': True})
        
        self.sequence_frame_index += 1
        timer.set_timeout(self.export_next_zip_frame, 10)
    
    def finish_zip_export(self):
        """Generate and download ZIP"""
        zip_blob = self.zip_file.generateAsync({'type': 'blob'})
        
        def on_zip_ready(blob):
            url = window.URL.createObjectURL(blob)
            self.download_file(url, f'frames_{int(window.Date.now())}.zip')
            timer.set_timeout(lambda: window.URL.revokeObjectURL(url), 2000)
        
        zip_blob.then(on_zip_ready)

    
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
                failure_msg = self.search_agent.failure_reason if self.search_agent.failure_reason else 'No Path Found'
                pdf.text(f'Status: {failure_msg}', 20, y_pos)
            
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
                
                # Add weight label when labels are enabled
                if hasattr(self, 'show_labels') and self.show_labels:
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
                'created': str(window.Date.new().toISOString()),
                'algorithm': document['algorithm-select'].value,
                'node_count': len(self.nodes),
                'edge_count': sum(len(node.neighbors) for node in self.nodes.values()),
                'is_undirected': self.graph_is_undirected
            },
            'graph': {
                'nodes': [node.to_dict() for node in self.nodes.values()],
                'source': (self.source_node.custom_name if hasattr(self.source_node, 'custom_name') else self.source_node.name) if self.source_node else None,
                'goals': [node.custom_name if hasattr(node, 'custom_name') else node.name for node in self.goal_nodes]
            }
        }
        
        if self.search_agent:
            # Handle Infinity path_cost (when no path found) - convert to null for valid JSON
            path_cost = self.search_agent.path_cost
            if path_cost == float('inf'):
                path_cost = None
            
            # Convert path node IDs to custom names
            path_with_names = []
            for node_id in self.search_agent.path_found:
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    path_with_names.append(node.custom_name if hasattr(node, 'custom_name') else node_id)
                else:
                    path_with_names.append(node_id)
            
            graph_data['results'] = {
                'success': self.search_agent.success,
                'path': path_with_names,
                'path_cost': path_cost,
                'nodes_explored': self.search_agent.nodes_explored,
                'failure_reason': self.search_agent.failure_reason
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
        if self.search_agent.failure_reason:
            csv += f'Failure Reason,{self.search_agent.failure_reason}\n'
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
                import traceback
                error_msg = str(ex)
                print(f'Error loading graph: {error_msg}')
                print(traceback.format_exc())
                alert(f'Error loading graph: {error_msg}')
        
        reader.bind('load', on_load)
        reader.readAsText(file)
    
    def load_graph_from_data(self, data):
        """Load graph from data dictionary"""
        # Clear current graph
        self.nodes = {}
        self.node_counter = 0
        self.source_node = None
        self.goal_nodes = []
        
        # Load graph type (directed or undirected)
        self.graph_is_undirected = data.get('metadata', {}).get('is_undirected', False)
        mode_text = "UNDIRECTED" if self.graph_is_undirected else "DIRECTED"
        print(f'📊 Loaded graph type: {mode_text}')
        self.update_graph_type_indicator()  # Show the indicator
        
        # Create a temporary mapping from name to node for lookups
        name_to_node = {}
        
        # Load nodes - create them with node_counter as ID
        for node_data in data['graph']['nodes']:
            node_name = node_data['name']
            
            # Create node with node_counter as ID
            node = Node(self.node_counter, node_data['x'], node_data['y'], node_data['heuristic'])
            node.state = node_data.get('state', 'empty')
            
            # Store custom name if it's not just a number
            if isinstance(node_name, str) and not node_name.isdigit():
                node.custom_name = node_name
            elif isinstance(node_name, int):
                node.custom_name = str(node_name)
            
            # Store node with node_counter as key
            self.nodes[self.node_counter] = node
            # Keep mapping from original name to node for edge loading
            # Store both string and int versions for JSON compatibility
            name_to_node[node_name] = node
            if isinstance(node_name, int):
                name_to_node[str(node_name)] = node
            elif isinstance(node_name, str) and node_name.isdigit():
                name_to_node[int(node_name)] = node
            
            self.node_counter += 1
        
        # Load edges using the name mapping
        for node_data in data['graph']['nodes']:
            node = name_to_node[node_data['name']]
            for neighbor_name, weight in node_data.get('neighbors', {}).items():
                # Try both string and int versions for neighbor lookup
                neighbor = name_to_node.get(neighbor_name)
                if not neighbor and isinstance(neighbor_name, str) and neighbor_name.isdigit():
                    neighbor = name_to_node.get(int(neighbor_name))
                elif not neighbor and isinstance(neighbor_name, int):
                    neighbor = name_to_node.get(str(neighbor_name))
                
                if neighbor:
                    node.add_neighbor(neighbor, weight)
        
        # Set source and goals using name mapping
        if data['graph']['source'] is not None:
            source = data['graph']['source']
            self.source_node = name_to_node.get(source)
            if not self.source_node and isinstance(source, str) and source.isdigit():
                self.source_node = name_to_node.get(int(source))
            elif not self.source_node and isinstance(source, int):
                self.source_node = name_to_node.get(str(source))
        
        for goal_name in data['graph'].get('goals', []):
            goal_node = name_to_node.get(goal_name)
            if not goal_node and isinstance(goal_name, str) and goal_name.isdigit():
                goal_node = name_to_node.get(int(goal_name))
            elif not goal_node and isinstance(goal_name, int):
                goal_node = name_to_node.get(str(goal_name))
            
            if goal_node:
                self.goal_nodes.append(goal_node)
        
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
        self.graph_is_undirected = None  # Reset graph type
        self.update_graph_type_indicator()  # Hide the indicator
        
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

    def on_graph_type_change(self, event):
        """Handle graph type dropdown change"""
        dropdown = document['graph-type-select']
        selected_type = dropdown.value
        
        if selected_type == '':
            return
        
        # If graph already has nodes and type is being changed
        if len(self.nodes) > 0 and self.graph_is_undirected is not None:
            # Ask for confirmation
            if not window.confirm('Changing graph type will modify existing edges. Continue?'):
                # Reset dropdown to current type
                if self.graph_is_undirected:
                    dropdown.value = 'undirected'
                else:
                    dropdown.value = 'directed'
                return
        
        # Set the new graph type
        new_type = (selected_type == 'undirected')
        
        # If we're switching from directed to undirected, add reverse edges
        if self.graph_is_undirected is not None and new_type and not self.graph_is_undirected:
            edges_to_add = []
            for node in self.nodes.values():
                for neighbor, weight in list(node.neighbors.items()):
                    # Check if reverse edge exists
                    if node not in neighbor.neighbors:
                        edges_to_add.append((neighbor, node, weight))
            
            # Add missing reverse edges
            for from_node, to_node, weight in edges_to_add:
                from_node.add_neighbor(to_node, weight)
        
        self.graph_is_undirected = new_type
        self.update_graph_type_indicator()
        self.render()
        
        mode = "UNDIRECTED" if self.graph_is_undirected else "DIRECTED"
        print(f'📊 Graph type set to: {mode}')
    
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
