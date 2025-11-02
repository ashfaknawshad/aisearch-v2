# 🎨 CRITICAL: Canvas Implementation & UI/UX Requirements

## ⚠️ IMPLEMENTATION NOTE

**The GitHub Pages and Next.js applications have been created, but are missing critical features and user experience elements. This document provides the EXACT specifications needed to replicate the superior canvas implementation and UI/UX from the reference application.**

---

## 🖼️ CANVAS IMPLEMENTATION (HIGHEST PRIORITY)

### Technology Stack for Canvas

**MUST USE:**
- **HTML5 Canvas API** - Native canvas element for rendering
- **Brython** (Python in browser) - For algorithm logic
- **Vanilla JavaScript** - For canvas interactions and event handling
- **No React Canvas Libraries** - Keep it simple and performant

### Canvas Core Features (MANDATORY)

#### 1. **Pan & Zoom (Infinite Canvas)**

```python
# Global state variables
pan_x = 0          # X-axis offset
pan_y = 0          # Y-axis offset
zoom_level = 1.0   # Scale factor (0.1 to 5.0)

# Mouse wheel zooming
def handle_wheel(event):
    """Zoom in/out with mouse wheel, zoom towards cursor position"""
    event.preventDefault()
    
    # Get mouse position BEFORE zoom
    mouse_x = event.clientX
    mouse_y = event.clientY
    
    # Calculate zoom factor
    zoom_factor = 1.1 if event.deltaY < 0 else 0.9
    new_zoom = zoom_level * zoom_factor
    
    # Clamp zoom level
    new_zoom = max(0.1, min(5.0, new_zoom))
    
    # Zoom towards cursor (keep point under cursor stationary)
    # Calculate canvas coordinates before zoom
    canvas_x = (mouse_x - pan_x) / zoom_level
    canvas_y = (mouse_y - pan_y) / zoom_level
    
    # Update zoom
    zoom_level = new_zoom
    
    # Adjust pan to keep same point under cursor
    pan_x = mouse_x - (canvas_x * zoom_level)
    pan_y = mouse_y - (canvas_y * zoom_level)
    
    graph_updated = True

# Click and drag panning
is_panning = False
last_pan_x = 0
last_pan_y = 0

def handle_mouse_down(event):
    """Start panning or node interaction"""
    global is_panning, last_pan_x, last_pan_y
    
    # Right-click or middle-click = pan
    if event.button == 2 or event.button == 1:
        is_panning = True
        last_pan_x = event.clientX
        last_pan_y = event.clientY
        canvas.style.cursor = "grabbing"
        event.preventDefault()

def handle_mouse_move(event):
    """Pan the canvas or drag nodes"""
    global pan_x, pan_y, graph_updated
    
    if is_panning:
        dx = event.clientX - last_pan_x
        dy = event.clientY - last_pan_y
        pan_x += dx
        pan_y += dy
        last_pan_x = event.clientX
        last_pan_y = event.clientY
        graph_updated = True

def handle_mouse_up(event):
    """Stop panning"""
    global is_panning
    is_panning = False
    canvas.style.cursor = "default"
```

#### 2. **Coordinate Transformation System**

```python
def transform_point(screen_x, screen_y):
    """Convert screen coordinates to canvas coordinates"""
    canvas_x = (screen_x - pan_x) / zoom_level
    canvas_y = (screen_y - pan_y) / zoom_level
    return canvas_x, canvas_y

def inverse_transform_point(canvas_x, canvas_y):
    """Convert canvas coordinates to screen coordinates"""
    screen_x = canvas_x * zoom_level + pan_x
    screen_y = canvas_y * zoom_level + pan_y
    return screen_x, screen_y
```

#### 3. **Grid Background (Visual Reference)**

```python
def draw_grid():
    """Draw subtle grid lines for spatial reference"""
    ctx.save()
    
    # Theme-aware grid color
    if document.body.classList.contains('light-mode'):
        ctx.strokeStyle = "rgba(0, 0, 0, 0.05)"
    else:
        ctx.strokeStyle = "rgba(255, 255, 255, 0.1)"
    
    ctx.lineWidth = 1
    
    # Grid size scales with zoom
    grid_size = 50 * zoom_level
    offset_x = pan_x % grid_size
    offset_y = pan_y % grid_size
    
    # Draw vertical lines
    x = offset_x
    while x < window_width:
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, window_height)
        ctx.stroke()
        x += grid_size
    
    # Draw horizontal lines
    y = offset_y
    while y < window_height:
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(window_width, y)
        ctx.stroke()
        y += grid_size
    
    ctx.restore()
```

#### 4. **Rendering Pipeline with Transform Context**

```python
def draw():
    """Main rendering function"""
    global graph_updated
    
    if not graph_updated:
        return
    
    # Clear canvas
    ctx.clearRect(0, 0, window_width, window_height)
    
    # Fill with background color from CSS variable
    canvas_bg = get_canvas_bg_color()
    ctx.fillStyle = canvas_bg
    ctx.fillRect(0, 0, window_width, window_height)
    
    # Draw grid background
    draw_grid()
    
    # CRITICAL: Apply pan/zoom transformation
    ctx.save()
    ctx.translate(pan_x, pan_y)
    ctx.scale(zoom_level, zoom_level)
    
    # Draw edges first (below nodes)
    draw_edges()
    
    # Draw nodes on top
    draw_nodes()
    
    # Restore transformation
    ctx.restore()
    
    graph_updated = False
```

#### 5. **Interactive Tools (Context-Aware Cursor)**

```python
# Tool states
selected_tool = "add_node"  # Current tool
selected_node_name = None   # For dragging/editing

# Tools available:
TOOLS = {
    "add_node": "Click to add node",
    "move_node": "Drag nodes to reposition",
    "add_edge": "Click two nodes to connect",
    "delete_node": "Click node to delete",
    "delete_edge": "Click edge midpoint to delete",
    "toggle_goal": "Click node to set/unset as goal",
    "update_heuristic": "Click node to change heuristic",
    "update_weight": "Click edge to change weight"
}

def handle_tool_action(event):
    """Handle tool-based interactions"""
    # Transform screen to canvas coordinates
    screen_x = event.clientX
    screen_y = event.clientY
    x, y = transform_point(screen_x, screen_y)
    
    # Check if clicked on node
    node_name = get_clicked_node_name(x, y, circle_radius)
    
    if selected_tool == "add_node" and node_name == -1:
        # Add node at clicked position
        create_node(x, y)
    elif selected_tool == "move_node" and node_name != -1:
        # Start dragging node
        start_drag(node_name)
    # ... other tools
```

#### 6. **Visual Feedback (Hover & Selection)**

```python
# Node colors based on state
node_colors = {
    "empty": "#ffffff",        # White - unvisited
    "unvisited": "#ffffff",    # White
    "source": "#ef4444",       # Red - start node
    "goal": "#10b981",         # Green - goal nodes
    "visited": "#8b5cf6",      # Purple - explored
    "path": "#f59e0b"          # Orange - solution path
}

# Circle styling
circle_colors = {
    "unselected": "#64748b",   # Slate border
    "selected": "#3b82f6"      # Blue border (active node)
}

def draw_nodes():
    """Draw all graph nodes with proper styling"""
    for node in search_agent.graph.values():
        # Check if selected
        is_selected = (node.name == selected_node_name)
        
        # Draw circle
        ctx.strokeStyle = circle_colors["selected"] if is_selected else circle_colors["unselected"]
        ctx.lineWidth = 4 if is_selected else 3
        
        ctx.beginPath()
        ctx.arc(*node.position, circle_radius, 0, 2 * Math.PI)
        ctx.fillStyle = node_colors[node.state]
        ctx.fill()
        ctx.stroke()
        
        # Draw label (node name)
        ctx.font = 'bold 14px Inter, sans-serif'
        # Dark text for light nodes, white text for dark nodes
        ctx.fillStyle = "#1e293b" if node.state in ["empty", "unvisited"] else "white"
        ctx.fillText(str(node.name), node.position[0], node.position[1] - 6)
        
        # Draw heuristic value (ONLY for heuristic algorithms AND if labels enabled)
        if show_labels and needs_heuristics(selected_search_algorithm):
            ctx.font = '11px Inter, sans-serif'
            ctx.fillText(f"h={node.heuristic}", node.position[0], node.position[1] + 8)
```

#### 7. **Smart Heuristic Toggle (Algorithm-Aware)**

```python
# Global state
show_labels = False  # Heuristic visibility toggle
selected_search_algorithm = "breadth-first"  # Current algorithm

def needs_heuristics(algorithm):
    """Check if algorithm uses heuristics"""
    heuristic_algorithms = ['greedy', 'a*']
    return algorithm in heuristic_algorithms

def handle_algo_change():
    """Handle algorithm selection change - auto-show/hide heuristics"""
    global selected_search_algorithm, show_labels
    
    selector = document["algo_selector"]
    selected_search_algorithm = selector.value
    
    # Automatically show heuristics for heuristic algorithms
    if needs_heuristics(selected_search_algorithm):
        if not show_labels:
            toggle_labels()  # Auto-enable heuristics
    else:
        # Hide heuristics for uninformed algorithms
        if show_labels:
            toggle_labels()  # Auto-disable heuristics
    
    print(f"Algorithm changed to: {selected_search_algorithm}")
    print(f"Heuristics visible: {show_labels}")

def toggle_labels():
    """Toggle heuristic label visibility"""
    global show_labels, graph_updated
    
    show_labels = not show_labels
    
    # Update button state
    toggle_btn = document["toggle_labels"]
    if show_labels:
        toggle_btn.classList.add("active")
        toggle_btn.innerHTML = '<i data-lucide="eye"></i> Hide Heuristics'
    else:
        toggle_btn.classList.remove("active")
        toggle_btn.innerHTML = '<i data-lucide="eye-off"></i> Show Heuristics'
    
    # Re-initialize Lucide icons
    window.lucide.createIcons()
    
    graph_updated = True
    print(f"Heuristics {'shown' if show_labels else 'hidden'}")

# Disable heuristic toggle for non-heuristic algorithms
def update_heuristic_button_state():
    """Enable/disable heuristic toggle based on algorithm"""
    toggle_btn = document["toggle_labels"]
    
    if needs_heuristics(selected_search_algorithm):
        toggle_btn.disabled = False
        toggle_btn.style.opacity = "1"
        toggle_btn.title = "Toggle heuristic values"
    else:
        toggle_btn.disabled = True
        toggle_btn.style.opacity = "0.5"
        toggle_btn.title = "Heuristics not used by this algorithm"
```

### Canvas Performance Optimizations

```python
# Only redraw when necessary
graph_updated = False  # Set to True when changes occur

# Smooth infinite canvas
def ensure_smooth_rendering():
    """Ensure 60 FPS rendering with infinite canvas"""
    # Use double buffering if needed
    # Optimize draw calls
    # Only draw visible elements
    pass

# Use requestAnimationFrame for smooth rendering
def animation_loop(event=None):
    # Only draw if graph changed
    draw()
    window.requestAnimationFrame(animation_loop)

# Start animation loop
window.requestAnimationFrame(animation_loop)
```

### Canvas Infinite Smoothness Requirements

**CRITICAL for smooth panning/zooming:**

1. **Hardware Acceleration**
```css
canvas {
  /* Enable GPU acceleration */
  transform: translateZ(0);
  will-change: transform;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}
```

2. **Efficient Rendering**
```python
def draw():
    """Optimized drawing with dirty region tracking"""
    if not graph_updated:
        return  # Skip unnecessary redraws
    
    # Use canvas double buffering
    # Clear only changed regions (if possible)
    ctx.clearRect(0, 0, window_width, window_height)
    
    # Draw background
    ctx.fillStyle = get_canvas_bg_color()
    ctx.fillRect(0, 0, window_width, window_height)
    
    # Draw grid (cached if not zooming/panning)
    draw_grid()
    
    # Apply transform ONCE
    ctx.save()
    ctx.translate(pan_x, pan_y)
    ctx.scale(zoom_level, zoom_level)
    
    # Batch draw operations
    draw_all_edges()  # Draw all edges at once
    draw_all_nodes()  # Draw all nodes at once
    
    ctx.restore()
    
    graph_updated = False
```

3. **Smooth Zoom Interpolation**
```python
# Target-based smooth zoom
target_zoom = 1.0
current_zoom = 1.0
zoom_speed = 0.15

def smooth_zoom_to_target():
    """Interpolate to target zoom smoothly"""
    global current_zoom
    
    if abs(current_zoom - target_zoom) > 0.001:
        current_zoom += (target_zoom - current_zoom) * zoom_speed
        graph_updated = True
        return True  # Still animating
    else:
        current_zoom = target_zoom
        return False  # Animation complete

def handle_wheel(event):
    """Smooth zoom with interpolation"""
    global target_zoom
    
    event.preventDefault()
    
    # Update target zoom
    zoom_factor = 1.1 if event.deltaY < 0 else 0.9
    target_zoom *= zoom_factor
    target_zoom = max(0.1, min(5.0, target_zoom))
    
    # Smooth interpolation will happen in animation loop
```

4. **Momentum Panning** (Optional but smooth)
```python
# Pan with momentum/inertia
pan_velocity_x = 0
pan_velocity_y = 0
pan_friction = 0.9

def apply_pan_momentum():
    """Apply momentum to panning for smooth feel"""
    global pan_x, pan_y, pan_velocity_x, pan_velocity_y
    
    if abs(pan_velocity_x) > 0.1 or abs(pan_velocity_y) > 0.1:
        pan_x += pan_velocity_x
        pan_y += pan_velocity_y
        
        # Apply friction
        pan_velocity_x *= pan_friction
        pan_velocity_y *= pan_friction
        
        graph_updated = True
        return True
    return False
```

---

## 🎨 LUCIDE ICONS INTEGRATION

### Installation & Setup

```html
<!-- Include Lucide Icons CDN -->
<script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>

<!-- Or via npm -->
<!-- npm install lucide -->
```

### Icon Usage

```html
<!-- Use data-lucide attribute for icons -->
<button class="btn-icon" id="play-pause">
  <i data-lucide="play"></i>
</button>

<button class="btn-icon" id="step-forward">
  <i data-lucide="skip-forward"></i>
</button>

<button class="btn-icon" id="step-backward">
  <i data-lucide="skip-back"></i>
</button>

<button class="btn-icon" id="zoom-in">
  <i data-lucide="zoom-in"></i>
</button>

<button class="btn-icon" id="zoom-out">
  <i data-lucide="zoom-out"></i>
</button>

<button class="btn-icon" id="toggle-labels">
  <i data-lucide="eye"></i>
</button>

<button class="btn-icon" id="theme-toggle">
  <i data-lucide="sun"></i>
</button>

<button class="btn-icon" id="download">
  <i data-lucide="download"></i>
</button>

<button class="btn-icon" id="save">
  <i data-lucide="save"></i>
</button>

<button class="btn-icon" id="settings">
  <i data-lucide="settings"></i>
</button>
```

### Complete Icon Set for App

```javascript
// Initialize Lucide icons
lucide.createIcons();

// Icon reference for all features:
const ICONS = {
  // Playback controls
  play: 'play',
  pause: 'pause',
  stop: 'square',
  stepForward: 'skip-forward',
  stepBackward: 'skip-back',
  
  // Tools
  addNode: 'plus-circle',
  moveNode: 'move',
  deleteNode: 'trash-2',
  addEdge: 'git-branch',
  deleteEdge: 'scissors',
  
  // View controls
  zoomIn: 'zoom-in',
  zoomOut: 'zoom-out',
  resetView: 'maximize-2',
  toggleLabels: 'eye',
  hideLabels: 'eye-off',
  
  // File operations
  save: 'save',
  download: 'download',
  upload: 'upload',
  export: 'share',
  
  // UI controls
  settings: 'settings',
  theme: 'sun',
  themeDark: 'moon',
  menu: 'menu',
  close: 'x',
  
  // Recording
  record: 'circle',
  stopRecord: 'square',
  
  // Info
  info: 'info',
  help: 'help-circle',
  
  // Navigation
  back: 'arrow-left',
  forward: 'arrow-right',
  dashboard: 'home',
  
  // Status
  success: 'check-circle',
  error: 'x-circle',
  warning: 'alert-triangle'
};
```

### Safe Lucide Initialization

```python
def safe_lucide_init():
    """Initialize Lucide icons safely"""
    try:
        if hasattr(window, 'lucide'):
            window.lucide.createIcons()
    except Exception as e:
        print(f"Lucide icons initialization error: {e}")

# Call after DOM updates
safe_lucide_init()

# Call after dynamic content changes
def update_ui():
    # ... update DOM ...
    window.setTimeout(lambda: safe_lucide_init(), 10)
    window.setTimeout(lambda: safe_lucide_init(), 100)
```

### Dynamic Icon Updates

```python
def toggle_play_pause():
    """Toggle play/pause with dynamic icon change"""
    button = document["play_pause"]
    
    if is_auto_playing:
        # Switch to pause
        is_auto_playing = False
        button.innerHTML = '<i data-lucide="play"></i>'
        button.title = "Play"
    else:
        # Switch to play
        is_auto_playing = True
        button.innerHTML = '<i data-lucide="pause"></i>'
        button.title = "Pause"
    
    # Re-initialize icons
    safe_lucide_init()

def toggle_theme():
    """Toggle theme with icon change"""
    body = document.body
    icon = document["theme-icon"]
    
    if body.classList.contains('light-mode'):
        body.classList.remove('light-mode')
        icon.setAttribute('data-lucide', 'moon')
    else:
        body.classList.add('light-mode')
        icon.setAttribute('data-lucide', 'sun')
    
    safe_lucide_init()
```

### Icon Styling

```css
/* Lucide icon styling */
[data-lucide] {
  width: 18px;
  height: 18px;
  stroke-width: 2;
  color: currentColor;
}

/* Icon in buttons */
.btn-icon [data-lucide] {
  width: 20px;
  height: 20px;
}

/* Small icons */
.icon-sm [data-lucide] {
  width: 16px;
  height: 16px;
}

/* Large icons */
.icon-lg [data-lucide] {
  width: 24px;
  height: 24px;
}

/* Icon colors */
.icon-primary [data-lucide] {
  color: var(--accent-primary);
}

.icon-success [data-lucide] {
  color: #10b981;
}

.icon-error [data-lucide] {
  color: #ef4444;
}

.icon-warning [data-lucide] {
  color: #f59e0b;
}
```

---

## 🎮 ANIMATION CONTROLS (CRITICAL MISSING FEATURE)

### Step-by-Step Playback System

**THIS IS THE MOST IMPORTANT MISSING FEATURE!**

```python
# Animation state
animation_states = []   # Store all algorithm states
current_step = -1       # Current position in history
is_auto_playing = False # Auto-advance vs manual stepping
animation_paused = True # Start paused by default

def save_animation_state():
    """Capture current graph state for stepping"""
    state = {}
    for name, node in search_agent.graph.items():
        state[name] = {
            'state': node.state,
            'position': node.position,
            'heuristic': node.heuristic,
            'children': dict(node.children)
        }
    
    # If stepped back, truncate future states
    if current_step < len(animation_states) - 1:
        animation_states = animation_states[:current_step + 1]
    
    animation_states.append(state)
    current_step = len(animation_states) - 1
    
    # Update data panel
    update_data_panel()

def step_forward():
    """Advance one step in algorithm execution"""
    global current_step, graph_updated
    
    # If we have cached states ahead, restore next state
    if current_step < len(animation_states) - 1:
        current_step += 1
        restore_animation_state(current_step)
        graph_updated = True
        document["step_backward"].disabled = False
        return
    
    # If search is still running, advance generator
    if search_agent.is_agent_searching:
        try:
            next(search_generator)
            save_animation_state()
            graph_updated = True
            update_data_panel()
        except StopIteration:
            # Search completed
            search_agent.is_agent_searching = False
            animation_paused = True

def step_backward():
    """Go back one step in algorithm execution"""
    global current_step, graph_updated
    
    if current_step <= 0:
        return
    
    current_step -= 1
    restore_animation_state(current_step)
    graph_updated = True
    update_data_panel()
    
    document["step_forward"].disabled = False
    document["step_backward"].disabled = (current_step <= 0)

def restore_animation_state(step_index):
    """Restore graph to specific animation frame"""
    if step_index < 0 or step_index >= len(animation_states):
        return
    
    state = animation_states[step_index]
    
    for name, node_data in state.items():
        if name in search_agent.graph:
            node = search_agent.graph[name]
            node.state = node_data['state']
            node.position = node_data['position']
            node.heuristic = node_data['heuristic']
            node.children = node_data['children']
    
    update_data_panel()

def toggle_play_pause():
    """Toggle between auto-play and paused"""
    global animation_paused, is_auto_playing
    
    if is_auto_playing:
        # Pause
        animation_paused = True
        is_auto_playing = False
        button.innerHTML = '<i data-lucide="play"></i>'
        document["step_forward"].disabled = False
        document["step_backward"].disabled = (current_step <= 0)
    else:
        # Play
        animation_paused = False
        is_auto_playing = True
        button.innerHTML = '<i data-lucide="pause"></i>'
        document["step_forward"].disabled = True
        document["step_backward"].disabled = True
```

### Animation Speed Control

```python
animation_speed = 5  # 1 (slowest) to 10 (fastest)

def update_speed():
    """Update animation speed from slider"""
    global animation_speed
    slider = document["speed_slider"]
    animation_speed = int(slider.value)
    
    speed_labels = {
        1: "Very Slow (1x)",
        2: "Slow (2x)",
        3: "Slower (3x)",
        4: "Below Normal (4x)",
        5: "Normal (5x)",
        6: "Above Normal (6x)",
        7: "Faster (7x)",
        8: "Fast (8x)",
        9: "Very Fast (9x)",
        10: "Maximum (10x)"
    }
    document["speed_value"].textContent = speed_labels[animation_speed]

def animation_loop():
    """Main animation loop with speed control"""
    if search_agent.is_agent_searching and not animation_paused and is_auto_playing:
        now = Date.now()
        # Calculate delay: Speed 1=1000ms, Speed 10=50ms
        delay = 1050 - (animation_speed * 100)
        
        if now - start_date >= delay:
            try:
                next(search_generator)
                save_animation_state()
                graph_updated = True
                update_data_panel()
                start_date = now
            except StopIteration:
                search_agent.is_agent_searching = False
                animation_paused = True
    
    draw()
    window.requestAnimationFrame(animation_loop)
```

---

## 🎨 UI/UX DESIGN REQUIREMENTS (CRITICAL)

### ❌ AVOID: VS Code-Like Gradients and Styling

**The current implementation looks too much like VS Code. We need a cleaner, more professional look.**

### ✅ REQUIRED: Clean, Modern Design System

#### Color Scheme Philosophy

**SIMPLICITY IS KEY:**
- **Primary Colors**: Black and White foundation
- **Accent Colors**: ONE carefully chosen accent color (Blue, Purple, or Teal)
- **Avoid**: Multi-color gradients, rainbow effects, excessive color variation
- **Use**: Subtle single-color gradients for depth (e.g., `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`)

#### Dark Mode (Default)

```css
:root {
  /* Background - Pure dark, not gray */
  --canvas-bg: #0a0a0a;
  --sidebar-bg: #111111;
  --panel-bg: #1a1a1a;
  
  /* Text - High contrast */
  --text-primary: #ffffff;
  --text-secondary: #a3a3a3;
  --text-muted: #666666;
  
  /* Accent - Single color, professional */
  --accent-primary: #3b82f6;    /* Blue */
  --accent-hover: #60a5fa;
  --accent-active: #2563eb;
  
  /* Borders - Subtle */
  --border-color: #2a2a2a;
  --border-hover: #3a3a3a;
  
  /* Node colors (from algorithm) */
  --node-empty: #ffffff;
  --node-source: #ef4444;
  --node-goal: #10b981;
  --node-visited: #8b5cf6;
  --node-path: #f59e0b;
  
  /* Surfaces */
  --card-bg: #1a1a1a;
  --card-hover: #222222;
  
  /* Shadows - Subtle depth */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
}

/* Light mode - Clean white */
body.light-mode {
  --canvas-bg: #ffffff;
  --sidebar-bg: #f9fafb;
  --panel-bg: #f3f4f6;
  
  --text-primary: #111111;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;
  
  --border-color: #e5e7eb;
  --border-hover: #d1d5db;
  
  --card-bg: #ffffff;
  --card-hover: #f9fafb;
  
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

#### Button Styling (NOT VS Code Style)

```css
/* Primary button - Clean, modern */
.btn-primary {
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.btn-primary:active {
  background: var(--accent-active);
  transform: translateY(0);
}

/* Secondary button - Subtle */
.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--card-hover);
  border-color: var(--border-hover);
}

/* Icon button - Minimal */
.btn-icon {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--card-hover);
  color: var(--text-primary);
}

.btn-icon.active {
  background: var(--accent-primary);
  color: white;
}
```

#### Panel Design (Clean Cards)

```css
.panel {
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-md);
}

.panel-header {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.panel-content {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
}
```

#### Data Display (Arrays) - Clean Typography

```css
/* Fringe and Visited arrays */
.data-array {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.8;
  padding: 12px 16px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin: 8px 0;
}

.array-bracket {
  color: var(--text-muted);
  font-weight: bold;
}

.array-item {
  color: var(--accent-primary);
  font-weight: 500;
  padding: 2px 6px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 4px;
  margin: 0 2px;
}

.array-comma {
  color: var(--text-muted);
}

.array-empty {
  color: var(--text-muted);
  font-style: italic;
}
```

#### Layout Structure

```html
<!-- Clean, non-VS Code layout -->
<div class="app-container">
  <!-- Left Sidebar - Tools -->
  <aside class="sidebar-left">
    <div class="tool-section">
      <h3 class="section-title">Tools</h3>
      <div class="tool-grid">
        <!-- Tool buttons -->
      </div>
    </div>
    
    <div class="tool-section">
      <h3 class="section-title">View</h3>
      <div class="button-group">
        <!-- Zoom controls -->
      </div>
    </div>
  </aside>
  
  <!-- Main Canvas Area -->
  <main class="canvas-container">
    <canvas id="graph-canvas"></canvas>
    
    <!-- Top Control Bar -->
    <div class="control-bar">
      <div class="control-section">
        <select class="algo-select">
          <option>Breadth-First Search</option>
          <!-- Other algorithms -->
        </select>
        <button class="btn-primary">Start Search</button>
        <button class="btn-secondary">Stop</button>
      </div>
      
      <div class="control-section">
        <button class="btn-icon" id="play-pause">
          <i data-lucide="play"></i>
        </button>
        <button class="btn-icon" id="step-back">
          <i data-lucide="skip-back"></i>
        </button>
        <button class="btn-icon" id="step-forward">
          <i data-lucide="skip-forward"></i>
        </button>
      </div>
      
      <div class="control-section speed-control">
        <span class="speed-label">Speed</span>
        <input type="range" min="1" max="10" value="5" class="speed-slider">
        <span class="speed-value">5x</span>
      </div>
    </div>
  </main>
  
  <!-- Right Sidebar - Data Panel -->
  <aside class="sidebar-right">
    <div class="data-panel">
      <h3 class="panel-header">Algorithm Data</h3>
      
      <div class="data-section">
        <label>Fringe (Frontier)</label>
        <div class="data-array" id="fringe-display">
          <span class="array-empty">Empty</span>
        </div>
      </div>
      
      <div class="data-section">
        <label>Visited (Explored)</label>
        <div class="data-array" id="visited-display">
          <span class="array-empty">No nodes explored yet</span>
        </div>
      </div>
      
      <div class="data-section">
        <label>Traversal Order</label>
        <div class="data-array" id="traversal-display">
          <span class="array-empty">No traversal yet</span>
        </div>
      </div>
      
      <div class="data-section">
        <label>Path Found</label>
        <div class="data-array" id="path-display">
          <span class="array-empty">No path found yet</span>
        </div>
      </div>
    </div>
  </aside>
</div>
```

---

## 📦 GIF Export Implementation

### Technology: gif.js Library

```html
<!-- Include gif.js in HTML -->
<script src="https://cdn.jsdelivr.net/npm/gif.js@0.2.0/dist/gif.js"></script>
```

### Implementation

```python
# GIF Recorder class
class GIFRecorder:
    def __init__(self):
        self.recording = False
        self.gif = None
        self.frames = []
    
    def start_recording(self):
        """Start GIF recording"""
        self.recording = True
        self.frames = []
        
        # Create GIF encoder
        self.gif = window.GIF.new({
            'workers': 2,
            'quality': 10,
            'width': canvas.width,
            'height': canvas.height,
            'workerScript': 'https://cdn.jsdelivr.net/npm/gif.js@0.2.0/dist/gif.worker.js'
        })
        
        print("GIF recording started")
    
    def capture_frame(self):
        """Capture current canvas frame"""
        if not self.recording:
            return
        
        # Add current canvas state to GIF
        # Calculate delay based on animation speed
        delay = 1050 - (animation_speed * 100)
        
        self.gif.addFrame(canvas, {'copy': True, 'delay': delay})
        print(f"Frame captured (delay: {delay}ms)")
    
    def stop_recording(self):
        """Stop recording and generate GIF"""
        if not self.recording:
            return
        
        self.recording = False
        
        # Render GIF
        self.gif.on('finished', lambda blob: self.download_gif(blob))
        self.gif.render()
        
        print("Generating GIF...")
    
    def download_gif(self, blob):
        """Download generated GIF"""
        url = window.URL.createObjectURL(blob)
        link = document.createElement('a')
        link.href = url
        link.download = f'search_animation_{Date.now()}.gif'
        link.click()
        window.URL.revokeObjectURL(url)
        
        print("GIF downloaded successfully")

# Global recorder instance
gif_recorder = GIFRecorder()

# Capture frame at each animation step
def animation_loop():
    if search_agent.is_agent_searching and not animation_paused:
        # ... advance search ...
        
        # Capture frame if recording
        if gif_recorder.recording:
            gif_recorder.capture_frame()
    
    draw()
    window.requestAnimationFrame(animation_loop)

# UI buttons
def start_gif_recording():
    gif_recorder.start_recording()
    document["gif-record-btn"].innerHTML = '<i data-lucide="square"></i> Stop Recording'
    document["gif-record-btn"].onclick = stop_gif_recording

def stop_gif_recording():
    gif_recorder.stop_recording()
    document["gif-record-btn"].innerHTML = '<i data-lucide="circle"></i> Record GIF'
    document["gif-record-btn"].onclick = start_gif_recording
```

---

## 🎯 CRITICAL REQUIREMENTS CHECKLIST

### ✅ Canvas Features (MUST HAVE)

- [ ] **Pan & Zoom** - Mouse wheel zoom, click-drag pan, zoom towards cursor
- [ ] **Infinite Canvas** - No boundaries, smooth panning in all directions
- [ ] **Smooth Zoom** - 60 FPS interpolated zoom (0.1x to 5x)
- [ ] **Momentum Panning** - Inertia/friction on pan release (optional but nice)
- [ ] **Grid Background** - Subtle grid for spatial reference
- [ ] **Coordinate Transform** - Proper screen-to-canvas coordinate mapping
- [ ] **Smooth Rendering** - 60 FPS with requestAnimationFrame
- [ ] **Hardware Acceleration** - GPU-accelerated canvas rendering
- [ ] **Interactive Tools** - All 8 tools with visual feedback
- [ ] **Hover Effects** - Node highlighting on hover
- [ ] **Selection State** - Visual indication of selected nodes
- [ ] **Theme Toggle** - Light/dark mode with proper grid colors
- [ ] **Smart Heuristic Toggle** - Auto-show/hide based on algorithm
- [ ] **Algorithm-Aware UI** - Disable heuristic button for BFS/DFS/DLS/IDS
- [ ] **Lucide Icons** - Consistent icon system throughout app

### ✅ Animation Controls (MUST HAVE)

- [ ] **Play/Pause Toggle** - Start/stop auto-play
- [ ] **Step Forward** - Advance one algorithm step
- [ ] **Step Backward** - Go back one algorithm step
- [ ] **Speed Slider** - 1x to 10x speed control
- [ ] **State History** - Save all states for stepping
- [ ] **Frame Counter** - Show current step (e.g., "Step 5 / 23")

### ✅ Data Display (MUST HAVE)

- [ ] **Fringe List** - Real-time frontier display
- [ ] **Visited List** - Real-time explored nodes display
- [ ] **Traversal Order** - Order nodes were visited
- [ ] **Path Found** - Final solution path
- [ ] **Live Updates** - Update on every step (forward/backward)
- [ ] **Empty States** - Show "Empty" when lists are empty

### ✅ Export Features (MUST HAVE)

- [ ] **GIF Recording** - Start/stop recording with gif.js
- [ ] **PNG Export** - Current canvas snapshot
- [ ] **PDF Report** - Comprehensive algorithm report
- [ ] **JSON Export** - Graph structure + results

### ✅ UI/UX Design (MUST HAVE)

- [ ] **NOT VS Code Style** - Avoid gradient backgrounds and multi-color schemes
- [ ] **Clean Color Scheme** - Black/white + single accent color
- [ ] **Subtle Shadows** - Depth without heavy effects
- [ ] **Rounded Corners** - Modern 8-12px border radius
- [ ] **Proper Typography** - Inter for UI, JetBrains Mono for code/data
- [ ] **Hover States** - Clear visual feedback on all interactive elements
- [ ] **Loading States** - Show progress during GIF generation
- [ ] **Responsive Layout** - Mobile-friendly design

---

## 📝 IMPLEMENTATION PRIORITY

### Phase 1: Critical Canvas Features (Week 1)
1. Pan & Zoom implementation
2. Grid background
3. Coordinate transformation
4. Basic rendering pipeline

### Phase 2: Animation Controls (Week 1-2)
1. State history system
2. Step forward/backward
3. Play/pause toggle
4. Speed control

### Phase 3: Data Display (Week 2)
1. Fringe/Visited panels
2. Live updates on step
3. Array formatting
4. Empty states

### Phase 4: Export Features (Week 3)
1. GIF recording with gif.js
2. PNG export
3. PDF generation
4. JSON export

### Phase 5: UI/UX Polish (Week 3-4)
1. Design system implementation
2. Color scheme refinement
3. Animations and transitions
4. Responsive design
5. Accessibility (ARIA labels, keyboard nav)

---

## 🚨 COMMON MISTAKES TO AVOID

### ❌ DON'T:
1. Use React canvas libraries (keep it simple)
2. Implement zoom without cursor-position anchoring
3. Forget to transform coordinates for interactions
4. Apply VS Code-style gradients and colors
5. Skip the step backward feature
6. Update data panels only on search completion
7. Use heavy shadows and excessive effects
8. Forget to save animation states
9. Make GIF recording automatic (user should control it)
10. Use multiple accent colors (pick ONE)
11. **Show heuristics for BFS, DFS, DLS, or IDS algorithms**
12. **Forget to auto-toggle heuristics based on algorithm selection**
13. **Use generic icons instead of Lucide icons**
14. **Create a bounded canvas (it must be infinite)**
15. **Implement laggy zoom/pan (must be 60 FPS smooth)**

### ✅ DO:
1. Use native HTML5 Canvas API
2. Implement proper coordinate transformation
3. Save state at EVERY algorithm step
4. Update data panels in real-time
5. Use clean, minimal design
6. Test on multiple browsers
7. Optimize for 60 FPS rendering
8. Provide visual feedback for all interactions
9. Use CSS variables for theming
10. Keep color scheme simple (black/white + one accent)
11. **Auto-hide heuristics for uninformed search algorithms**
12. **Auto-show heuristics for Greedy and A* algorithms**
13. **Use Lucide icons consistently (via CDN)**
14. **Implement infinite smooth canvas with hardware acceleration**
15. **Test zoom smoothness at all scales (0.1x to 5x)**
16. **Disable heuristic toggle button for non-heuristic algorithms**
17. **Show visual feedback (button state) for disabled features**

---

## 📚 REFERENCE IMPLEMENTATION

**The reference implementation** (current working app) demonstrates:
- Smooth pan & zoom
- Perfect coordinate transformation
- Clean, professional UI (not VS Code-like)
- Real-time data panel updates
- Step forward/backward functionality
- Speed control that works correctly
- GIF export capability
- Theme toggle with proper colors

**Study the existing main.py and styles.css** for exact implementation details.

---

## ✨ PERFECTION REQUIREMENTS

### What "Perfect" Means for This Application

#### 1. **Infinite Smooth Canvas**
- **Zero lag** during pan/zoom operations
- **60 FPS** minimum at all times
- **Smooth interpolation** for zoom transitions
- **Hardware accelerated** rendering
- **No boundaries** - infinite canvas in all directions
- **Responsive** at any zoom level (0.1x to 5x)

#### 2. **Intelligent UI**
- **Algorithm-aware** heuristic visibility
- **Context-sensitive** tooltips
- **Disabled state** visual feedback
- **Loading states** for async operations
- **Error handling** with user-friendly messages

#### 3. **Pixel-Perfect Design**
- **Consistent spacing** (8px grid system)
- **Aligned elements** (no misaligned pixels)
- **Sharp rendering** (crisp edges, no blur)
- **Proper font rendering** (anti-aliasing)
- **Icon alignment** (vertically centered in buttons)

#### 4. **Smooth Animations**
- **Easing functions** for all transitions
- **No jarring movements** (ease-in-out)
- **Consistent timing** (200ms for UI, variable for algorithm)
- **Cancel animations** on rapid interaction

#### 5. **Accessibility**
- **Keyboard navigation** (Tab, Enter, Space, Arrow keys)
- **ARIA labels** for screen readers
- **Focus indicators** (visible keyboard focus)
- **Color contrast** (WCAG AA minimum)
- **Tooltips** for all icons

#### 6. **Performance**
- **Instant interactions** (<16ms response)
- **No memory leaks** (proper cleanup)
- **Efficient rendering** (only redraw when needed)
- **Optimized assets** (compressed images, minified code)

### Perfection Checklist

#### Canvas Perfection
- [ ] Zoom is buttery smooth (interpolated, not instant)
- [ ] Pan works in all directions infinitely
- [ ] Zoom maintains cursor position (zooms towards mouse)
- [ ] Grid scales properly with zoom
- [ ] No flickering during rapid zoom/pan
- [ ] Canvas maintains 60 FPS with 1000+ nodes
- [ ] Touch gestures work on mobile (pinch zoom, two-finger pan)

#### Algorithm Perfection
- [ ] Heuristics auto-hide for BFS/DFS/DLS/IDS
- [ ] Heuristics auto-show for Greedy/A*
- [ ] Toggle button disabled when not applicable
- [ ] Data panels update on EVERY step
- [ ] Step backward works from any point
- [ ] Speed control affects all algorithms consistently
- [ ] No duplicate nodes in Fringe/Visited lists

#### Visual Perfection
- [ ] All icons use Lucide (no mixing)
- [ ] Icons render at correct size (18-20px)
- [ ] Buttons have hover states
- [ ] Active states clearly visible
- [ ] Disabled states have 50% opacity
- [ ] Shadows are subtle (not heavy)
- [ ] Border radius consistent (8-12px)
- [ ] No VS Code-style gradients

#### Interaction Perfection
- [ ] Every button has a tooltip
- [ ] Hover states appear within 100ms
- [ ] Click feedback is immediate
- [ ] Drag operations are smooth
- [ ] No accidental double-clicks
- [ ] Undo/redo works flawlessly
- [ ] Keyboard shortcuts work everywhere

#### Data Display Perfection
- [ ] Arrays formatted consistently
- [ ] Empty states show helpful messages
- [ ] Numbers formatted properly (no trailing decimals)
- [ ] Monospace font for data arrays
- [ ] Color-coded array items
- [ ] Brackets and commas styled
- [ ] Updates are instant (no delay)

#### Export Perfection
- [ ] GIF captures at correct frame rate
- [ ] PNG export at high resolution
- [ ] PDF includes all relevant data
- [ ] File names include timestamp
- [ ] Progress indicators during generation
- [ ] No browser crashes with large exports

### Quality Assurance Tests

#### Performance Tests
```javascript
// Canvas should maintain 60 FPS
function testCanvasPerformance() {
  let frameCount = 0;
  let startTime = performance.now();
  
  function countFrames() {
    frameCount++;
    if (performance.now() - startTime < 1000) {
      requestAnimationFrame(countFrames);
    } else {
      console.log(`FPS: ${frameCount}`);
      // Should be 60 FPS ± 2
      assert(frameCount >= 58 && frameCount <= 62);
    }
  }
  
  requestAnimationFrame(countFrames);
}

// Zoom should be smooth (no instant jumps)
function testSmoothZoom() {
  let zoomValues = [];
  
  function captureZoom() {
    zoomValues.push(zoom_level);
    if (zoomValues.length < 10) {
      requestAnimationFrame(captureZoom);
    } else {
      // Values should change gradually, not jump
      for (let i = 1; i < zoomValues.length; i++) {
        let diff = Math.abs(zoomValues[i] - zoomValues[i-1]);
        assert(diff < 0.1); // Max change per frame
      }
    }
  }
  
  // Trigger zoom
  handleWheel({deltaY: -100, clientX: 400, clientY: 300});
  requestAnimationFrame(captureZoom);
}
```

#### Functional Tests
```python
# Test heuristic visibility
def test_heuristic_visibility():
    # Select BFS
    select_algorithm('breadth-first')
    assert show_labels == False, "Heuristics should be hidden for BFS"
    assert document["toggle_labels"].disabled == True
    
    # Select A*
    select_algorithm('a*')
    assert show_labels == True, "Heuristics should be shown for A*"
    assert document["toggle_labels"].disabled == False

# Test step backward
def test_step_backward():
    start_search()
    step_forward()
    step_forward()
    step_forward()
    
    current = current_step
    step_backward()
    assert current_step == current - 1, "Step backward failed"
    
    # Verify state restored correctly
    state = animation_states[current_step]
    for name, data in state.items():
        node = search_agent.graph[name]
        assert node.state == data['state'], "Node state not restored"
```

### Code Review Checklist

Before considering the implementation "perfect":

#### Code Quality
- [ ] No console errors
- [ ] No console warnings
- [ ] All variables properly scoped
- [ ] No magic numbers (use named constants)
- [ ] Functions are single-purpose
- [ ] Comments explain "why", not "what"
- [ ] Error handling for all async operations
- [ ] No TODO comments left in code

#### Documentation
- [ ] README explains all features
- [ ] Setup instructions are clear
- [ ] API documentation complete
- [ ] Code comments for complex logic
- [ ] Examples for common tasks
- [ ] Troubleshooting guide

#### Testing
- [ ] All features manually tested
- [ ] Edge cases covered
- [ ] Error conditions handled
- [ ] Performance benchmarked
- [ ] Cross-browser tested
- [ ] Mobile responsiveness verified

---

## 🎓 FINAL NOTES

**THIS IS NOT OPTIONAL:**
The canvas implementation and animation controls are the CORE USER EXPERIENCE. A graph visualizer without proper pan/zoom and step-by-step playback is fundamentally broken.

**INFINITE SMOOTH CANVAS IS CRITICAL:**
The canvas MUST be infinite (no boundaries) and MUST run at 60 FPS with smooth interpolated zoom and pan. Users should be able to zoom from 0.1x to 5x smoothly, and pan infinitely in all directions. Hardware acceleration is mandatory.

**HEURISTIC VISIBILITY IS ALGORITHM-AWARE:**
Heuristics should ONLY be visible for Greedy Best-First and A* algorithms. When users select BFS, DFS, DLS, or IDS, heuristics must be automatically hidden. The toggle button should be disabled for non-heuristic algorithms. This is not optional - it's confusing to show irrelevant data.

**LUCIDE ICONS EVERYWHERE:**
Use Lucide icons consistently throughout the entire application. No mixing with other icon sets. No Font Awesome, no Material Icons - only Lucide. Initialize icons properly after every DOM update.

**VISUAL DESIGN MATTERS:**
The app should look PROFESSIONAL, not like VS Code or a code editor. Think Apple's design language - clean, minimal, focused. One accent color is enough.

**TEST THOROUGHLY:**
- Test zoom at different scales (0.1x to 5x) - must be smooth
- Test pan with large graphs - must be infinite
- Test step backward from any point
- Test speed slider at all levels (1x to 10x)
- Test heuristic auto-hide/show when changing algorithms
- Test on Chrome, Firefox, Safari, Edge
- Test on mobile devices
- Test light and dark modes
- Test Lucide icons render properly

**PRIORITIZE USER EXPERIENCE:**
Users need to SEE what's happening in the algorithm. The Fringe and Visited lists must update on EVERY step, not just at the end. The ability to step backward is CRUCIAL for understanding.

---

END OF CANVAS & UI/UX IMPLEMENTATION GUIDE
