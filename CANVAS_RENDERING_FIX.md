# 🔧 CANVAS RENDERING & INTERACTION FIX

## 🚨 CRITICAL ISSUES TO FIX

Your canvas implementation has the following problems:

1. **Blurry/pixelated nodes** - Canvas resolution too low
2. **Nodes appearing in wrong position** - Coordinate transformation broken
3. **Right-click creates nodes** - Event handling incorrect
4. **Wrong cursor during pan** - Should show grab/grabbing cursor
5. **Canvas stretched** - DPI scaling not handled
6. **Low resolution** - Not accounting for high-DPI displays

---

## ✅ COMPLETE CANVAS SOLUTION

### 1. HIGH-DPI CANVAS SETUP (CRITICAL)

```python
# Global canvas variables
canvas = None
ctx = None
window_width = 0
window_height = 0
dpi_scale = 1.0

def init_canvas():
    """Initialize canvas with proper DPI scaling for crisp rendering"""
    global canvas, ctx, window_width, window_height, dpi_scale
    
    canvas = document["graph-canvas"]
    ctx = canvas.getContext("2d")
    
    # Get device pixel ratio for high-DPI displays (Retina, 4K, etc.)
    dpi_scale = window.devicePixelRatio or 1.0
    
    # Set display size (CSS pixels)
    window_width = window.innerWidth
    window_height = window.innerHeight
    
    # Set canvas style size
    canvas.style.width = f"{window_width}px"
    canvas.style.height = f"{window_height}px"
    
    # Set actual canvas size (accounting for DPI)
    canvas.width = int(window_width * dpi_scale)
    canvas.height = int(window_height * dpi_scale)
    
    # Scale all drawing operations by DPI scale
    ctx.scale(dpi_scale, dpi_scale)
    
    # Enable image smoothing for crisp rendering
    ctx.imageSmoothingEnabled = True
    ctx.imageSmoothingQuality = "high"
    
    print(f"Canvas initialized: {window_width}x{window_height} (DPI: {dpi_scale})")

# Handle window resize
def handle_resize(event=None):
    """Reinitialize canvas on window resize"""
    init_canvas()
    graph_updated = True

# Bind resize event
window.addEventListener("resize", handle_resize)
```

### 2. COORDINATE TRANSFORMATION (FIX POSITIONING)

```python
# Pan and zoom state
pan_x = 0
pan_y = 0
zoom_level = 1.0

def transform_point(screen_x, screen_y):
    """
    Convert SCREEN coordinates to CANVAS coordinates
    This fixes nodes appearing in wrong positions
    """
    # Get canvas bounding rect
    rect = canvas.getBoundingClientRect()
    
    # Convert screen coords to canvas coords
    canvas_x = screen_x - rect.left
    canvas_y = screen_y - rect.top
    
    # Apply inverse pan and zoom transformations
    world_x = (canvas_x - pan_x) / zoom_level
    world_y = (canvas_y - pan_y) / zoom_level
    
    return world_x, world_y

def inverse_transform_point(world_x, world_y):
    """
    Convert CANVAS coordinates to SCREEN coordinates
    """
    screen_x = world_x * zoom_level + pan_x
    screen_y = world_y * zoom_level + pan_y
    return screen_x, screen_y
```

### 3. MOUSE EVENT HANDLING (FIX RIGHT-CLICK)

```python
# Mouse state
is_panning = False
is_dragging_node = False
drag_node = None
last_mouse_x = 0
last_mouse_y = 0
mouse_down_button = -1

def handle_mouse_down(event):
    """
    Handle mouse down events
    Left-click (0) = tool action
    Right-click (2) = start panning
    Middle-click (1) = start panning
    """
    global is_panning, is_dragging_node, drag_node, last_mouse_x, last_mouse_y
    global mouse_down_button
    
    mouse_down_button = event.button
    last_mouse_x = event.clientX
    last_mouse_y = event.clientY
    
    # Right-click or middle-click = panning
    if event.button == 2 or event.button == 1:
        event.preventDefault()  # Prevent context menu
        is_panning = True
        canvas.style.cursor = "grabbing"
        return
    
    # Left-click = tool action or node dragging
    if event.button == 0:
        # Transform to canvas coordinates
        world_x, world_y = transform_point(event.clientX, event.clientY)
        
        # Check if clicking on a node
        clicked_node = get_clicked_node(world_x, world_y)
        
        if clicked_node and selected_tool == "move_node":
            # Start dragging node
            is_dragging_node = True
            drag_node = clicked_node
            canvas.style.cursor = "grabbing"
        else:
            # Handle tool action
            handle_tool_action(event)

def handle_mouse_move(event):
    """Handle mouse move - panning or dragging"""
    global pan_x, pan_y, graph_updated, last_mouse_x, last_mouse_y
    
    if is_panning:
        # Calculate delta
        dx = event.clientX - last_mouse_x
        dy = event.clientY - last_mouse_y
        
        # Update pan
        pan_x += dx
        pan_y += dy
        
        # Update last position
        last_mouse_x = event.clientX
        last_mouse_y = event.clientY
        
        graph_updated = True
    
    elif is_dragging_node and drag_node:
        # Transform to world coordinates
        world_x, world_y = transform_point(event.clientX, event.clientY)
        
        # Update node position
        drag_node.position = [world_x, world_y]
        
        graph_updated = True
    
    else:
        # Update cursor based on hover
        world_x, world_y = transform_point(event.clientX, event.clientY)
        hovered_node = get_clicked_node(world_x, world_y)
        
        if hovered_node:
            if selected_tool == "move_node":
                canvas.style.cursor = "grab"
            else:
                canvas.style.cursor = "pointer"
        else:
            canvas.style.cursor = "default"

def handle_mouse_up(event):
    """Handle mouse up - stop panning or dragging"""
    global is_panning, is_dragging_node, drag_node, mouse_down_button
    
    is_panning = False
    is_dragging_node = False
    drag_node = None
    mouse_down_button = -1
    
    # Reset cursor
    canvas.style.cursor = "default"

# Prevent context menu on right-click
def handle_context_menu(event):
    """Prevent default context menu"""
    event.preventDefault()
    return False
```

### 4. TOOL ACTION HANDLER (FIX NODE CREATION)

```python
def handle_tool_action(event):
    """
    Handle tool-specific actions (left-click only)
    This should NOT trigger on right-click
    """
    # Only handle left-click
    if event.button != 0:
        return
    
    # Transform to canvas coordinates
    world_x, world_y = transform_point(event.clientX, event.clientY)
    
    # Check if clicking on a node
    node_name = get_clicked_node_name(world_x, world_y)
    
    if selected_tool == "add_node" and node_name == -1:
        # Add node only if NOT clicking on existing node
        add_new_node(world_x, world_y)
    
    elif selected_tool == "delete_node" and node_name != -1:
        # Delete the clicked node
        delete_node(node_name)
    
    elif selected_tool == "toggle_goal" and node_name != -1:
        # Toggle goal state
        toggle_goal_state(node_name)
    
    elif selected_tool == "add_edge":
        # Handle edge creation
        handle_edge_creation(node_name)
    
    # ... other tools

def get_clicked_node(world_x, world_y):
    """
    Get node at world coordinates (returns Node object or None)
    """
    for node in search_agent.graph.values():
        dx = world_x - node.position[0]
        dy = world_y - node.position[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= circle_radius:
            return node
    
    return None

def get_clicked_node_name(world_x, world_y):
    """
    Get node name at world coordinates (returns name or -1)
    """
    node = get_clicked_node(world_x, world_y)
    return node.name if node else -1
```

### 5. RENDERING PIPELINE (FIX BLURRINESS)

```python
# Rendering constants
circle_radius = 25  # Node radius in world units

def draw():
    """
    Main rendering function with crisp output
    """
    global graph_updated
    
    if not graph_updated:
        return
    
    # Clear entire canvas
    ctx.clearRect(0, 0, window_width, window_height)
    
    # Fill background
    canvas_bg = get_canvas_bg_color()
    ctx.fillStyle = canvas_bg
    ctx.fillRect(0, 0, window_width, window_height)
    
    # Draw grid (before transform)
    draw_grid()
    
    # Save context state
    ctx.save()
    
    # Apply pan and zoom transformation
    ctx.translate(pan_x, pan_y)
    ctx.scale(zoom_level, zoom_level)
    
    # Set rendering quality
    ctx.imageSmoothingEnabled = True
    ctx.imageSmoothingQuality = "high"
    
    # Draw edges first (behind nodes)
    draw_edges()
    
    # Draw nodes on top
    draw_nodes()
    
    # Restore context state
    ctx.restore()
    
    graph_updated = False

def draw_nodes():
    """Draw all nodes with crisp rendering"""
    for node in search_agent.graph.values():
        x, y = node.position
        
        # Determine if selected
        is_selected = (node.name == selected_node_name)
        
        # Draw node circle
        ctx.beginPath()
        ctx.arc(x, y, circle_radius, 0, 2 * 3.14159265359)
        
        # Fill color based on state
        ctx.fillStyle = node_colors[node.state]
        ctx.fill()
        
        # Stroke (border)
        ctx.strokeStyle = circle_colors["selected"] if is_selected else circle_colors["unselected"]
        ctx.lineWidth = 4 if is_selected else 3
        ctx.stroke()
        
        # Draw node label (name)
        ctx.font = "bold 14px Inter, -apple-system, BlinkMacSystemFont, sans-serif"
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"
        
        # Text color based on node state
        if node.state in ["empty", "unvisited"]:
            ctx.fillStyle = "#1e293b"  # Dark text on light background
        else:
            ctx.fillStyle = "#ffffff"  # White text on dark background
        
        ctx.fillText(str(node.name), x, y - 6)
        
        # Draw heuristic (if enabled and algorithm needs it)
        if show_labels and needs_heuristics(selected_search_algorithm):
            ctx.font = "11px Inter, -apple-system, BlinkMacSystemFont, sans-serif"
            ctx.fillText(f"h={node.heuristic}", x, y + 8)

def draw_edges():
    """Draw all edges with crisp rendering"""
    drawn_edges = set()  # Avoid drawing edges twice
    
    for node in search_agent.graph.values():
        for child_name, weight in node.children.items():
            # Create edge key (sorted to avoid duplicates)
            edge_key = tuple(sorted([node.name, child_name]))
            
            if edge_key in drawn_edges:
                continue
            
            drawn_edges.add(edge_key)
            
            child = search_agent.graph[child_name]
            
            x1, y1 = node.position
            x2, y2 = child.position
            
            # Draw edge line
            ctx.strokeStyle = "#94a3b8"
            ctx.lineWidth = 3
            ctx.beginPath()
            ctx.moveTo(x1, y1)
            ctx.lineTo(x2, y2)
            ctx.stroke()
            
            # Draw weight label (if labels enabled)
            if show_labels:
                # Calculate midpoint
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                
                # Draw weight background (for readability)
                ctx.font = "12px Inter, -apple-system, BlinkMacSystemFont, sans-serif"
                ctx.textAlign = "center"
                ctx.textBaseline = "middle"
                
                # Measure text
                text_width = ctx.measureText(str(weight)).width
                padding = 4
                
                # Background
                ctx.fillStyle = get_canvas_bg_color()
                ctx.fillRect(
                    mid_x - text_width / 2 - padding,
                    mid_y - 8,
                    text_width + padding * 2,
                    16
                )
                
                # Text
                ctx.fillStyle = "#64748b"
                ctx.fillText(str(weight), mid_x, mid_y)

def draw_grid():
    """Draw subtle grid background"""
    ctx.save()
    
    # Grid color based on theme
    if document.body.classList.contains('light-mode'):
        ctx.strokeStyle = "rgba(0, 0, 0, 0.05)"
    else:
        ctx.strokeStyle = "rgba(255, 255, 255, 0.05)"
    
    ctx.lineWidth = 1
    
    # Grid size in screen space
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

def get_canvas_bg_color():
    """Get background color from CSS variable"""
    try:
        styles = window.getComputedStyle(document.body)
        color = styles.getPropertyValue('--canvas-bg').strip()
        return color if color else '#0a0a0a'
    except:
        return '#0a0a0a'
```

### 6. ZOOM HANDLING (FIX POSITIONING)

```python
def handle_wheel(event):
    """
    Handle mouse wheel for zooming
    Zoom towards cursor position
    """
    global zoom_level, pan_x, pan_y, graph_updated
    
    event.preventDefault()
    
    # Get mouse position in canvas coordinates
    world_x, world_y = transform_point(event.clientX, event.clientY)
    
    # Calculate zoom factor
    zoom_factor = 0.9 if event.deltaY > 0 else 1.1
    new_zoom = zoom_level * zoom_factor
    
    # Clamp zoom level
    new_zoom = max(0.1, min(5.0, new_zoom))
    
    # Calculate new pan to keep world point under cursor
    # Before zoom: world_x = (mouse_x - pan_x) / zoom_level
    # After zoom: world_x = (mouse_x - new_pan_x) / new_zoom
    # Solve for new_pan_x: new_pan_x = mouse_x - (world_x * new_zoom)
    
    rect = canvas.getBoundingClientRect()
    mouse_canvas_x = event.clientX - rect.left
    mouse_canvas_y = event.clientY - rect.top
    
    pan_x = mouse_canvas_x - (world_x * new_zoom)
    pan_y = mouse_canvas_y - (world_y * new_zoom)
    
    zoom_level = new_zoom
    graph_updated = True
```

### 7. CURSOR MANAGEMENT

```python
def update_cursor():
    """Update cursor based on current tool and state"""
    if is_panning:
        canvas.style.cursor = "grabbing"
    elif is_dragging_node:
        canvas.style.cursor = "grabbing"
    elif selected_tool == "move_node":
        canvas.style.cursor = "grab"
    elif selected_tool == "add_node":
        canvas.style.cursor = "crosshair"
    elif selected_tool == "delete_node":
        canvas.style.cursor = "not-allowed"
    else:
        canvas.style.cursor = "default"
```

### 8. EVENT BINDING

```python
def main():
    """Initialize application"""
    # Initialize canvas with proper DPI
    init_canvas()
    
    # Bind canvas events
    canvas.addEventListener("wheel", handle_wheel, {"passive": False})
    canvas.addEventListener("mousedown", handle_mouse_down)
    canvas.addEventListener("mousemove", handle_mouse_move)
    canvas.addEventListener("mouseup", handle_mouse_up)
    canvas.addEventListener("contextmenu", handle_context_menu)  # Prevent right-click menu
    
    # Bind window events
    window.addEventListener("resize", handle_resize)
    
    # Start animation loop
    window.requestAnimationFrame(animation_loop)
    
    print("Canvas initialized successfully")

# Animation loop
def animation_loop(timestamp=None):
    """Main animation loop"""
    draw()
    window.requestAnimationFrame(animation_loop)
```

---

## 🎨 CSS FOR CANVAS

```css
/* Canvas container */
.canvas-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: var(--canvas-bg);
}

/* Canvas element */
#graph-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  
  /* Hardware acceleration */
  transform: translateZ(0);
  will-change: transform;
  
  /* Prevent text selection during drag */
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  
  /* Touch action */
  touch-action: none;
  
  /* Default cursor */
  cursor: default;
}

/* Cursor classes */
.canvas-container.panning #graph-canvas {
  cursor: grabbing !important;
}

.canvas-container.tool-move #graph-canvas {
  cursor: grab;
}

.canvas-container.tool-add #graph-canvas {
  cursor: crosshair;
}

.canvas-container.tool-delete #graph-canvas {
  cursor: not-allowed;
}
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Phase 1: Canvas Setup
- [ ] Initialize canvas with `devicePixelRatio` for high-DPI
- [ ] Set canvas width/height accounting for DPI scale
- [ ] Scale context by DPI scale
- [ ] Enable high-quality image smoothing
- [ ] Handle window resize properly

### Phase 2: Coordinate Transformation
- [ ] Implement `transform_point()` with canvas bounding rect
- [ ] Implement `inverse_transform_point()`
- [ ] Use transformed coordinates in all mouse handlers
- [ ] Test on different screen positions (not just fullscreen)

### Phase 3: Mouse Event Handling
- [ ] Left-click (button 0) = tool actions
- [ ] Right-click (button 2) = panning
- [ ] Middle-click (button 1) = panning
- [ ] Prevent context menu on right-click
- [ ] Track mouse button in `mousedown` handler
- [ ] Only trigger tools on left-click

### Phase 4: Cursor Management
- [ ] Show "grabbing" during pan
- [ ] Show "grab" on hover (move tool)
- [ ] Show "crosshair" for add node tool
- [ ] Show "pointer" on node hover
- [ ] Show "default" otherwise
- [ ] Never show cross/plus during pan

### Phase 5: Rendering Quality
- [ ] Use high-quality image smoothing
- [ ] Draw with proper line widths
- [ ] Use web-safe fonts with fallbacks
- [ ] Draw edges before nodes (layering)
- [ ] Clear canvas completely before each frame
- [ ] Apply transformations correctly (save/restore)

### Phase 6: Testing
- [ ] Test on Retina/4K displays (should be crisp)
- [ ] Test node positioning (click where you see it)
- [ ] Test right-click panning (no nodes created)
- [ ] Test zoom towards cursor
- [ ] Test window resize
- [ ] Test all tools with proper coordinates

---

## 🚨 COMMON MISTAKES TO AVOID

### ❌ DON'T:
1. Forget `devicePixelRatio` - causes blurry canvas
2. Use `event.clientX/Y` directly - needs canvas bounding rect
3. Trigger tools on right-click - check `event.button`
4. Forget to prevent context menu - right-click shows menu
5. Use wrong cursor during pan - should be "grabbing"
6. Scale canvas without scaling context - causes blur
7. Draw text without font fallbacks - looks bad on some systems
8. Apply transformations without save/restore - breaks rendering
9. Set canvas size in CSS only - causes stretching
10. Forget to clear canvas before drawing - causes artifacts

### ✅ DO:
1. Use `window.devicePixelRatio` for DPI scaling
2. Use `canvas.getBoundingClientRect()` for coordinates
3. Check `event.button` before handling clicks
4. Prevent default on right-click and context menu
5. Update cursor based on action (grab, grabbing, crosshair)
6. Set both canvas size AND context scale
7. Use font stacks: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
8. Use ctx.save() and ctx.restore() around transformations
9. Set canvas width/height in JavaScript, not CSS
10. Clear canvas with clearRect() before every draw

---

## 🧪 TESTING CODE

```python
def test_canvas_quality():
    """Test canvas rendering quality"""
    print(f"Canvas size: {canvas.width}x{canvas.height}")
    print(f"Display size: {window_width}x{window_height}")
    print(f"DPI scale: {dpi_scale}")
    print(f"Expected: {window_width * dpi_scale}x{window_height * dpi_scale}")
    
    assert canvas.width == int(window_width * dpi_scale), "Canvas width incorrect"
    assert canvas.height == int(window_height * dpi_scale), "Canvas height incorrect"

def test_coordinate_transform():
    """Test coordinate transformation"""
    # Test point at canvas center
    center_x = window_width / 2
    center_y = window_height / 2
    
    # Transform to world and back
    world_x, world_y = transform_point(center_x, center_y)
    screen_x, screen_y = inverse_transform_point(world_x, world_y)
    
    # Should be approximately equal (within 1 pixel)
    assert abs(screen_x - center_x) < 1, "X transform failed"
    assert abs(screen_y - center_y) < 1, "Y transform failed"
    
    print("✓ Coordinate transformation working correctly")

def test_right_click():
    """Test that right-click doesn't create nodes"""
    initial_count = len(search_agent.graph)
    
    # Simulate right-click
    event = {"button": 2, "clientX": 400, "clientY": 300}
    handle_mouse_down(event)
    
    # Node count should not change
    assert len(search_agent.graph) == initial_count, "Right-click created node!"
    
    print("✓ Right-click handling correct")
```

---

## 📝 COMPLETE HTML STRUCTURE

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Search Visualizer</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdn.jsdelivr.net/npm/brython@3.11.0/brython.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
</head>
<body onload="brython()">
    <div class="canvas-container">
        <canvas id="graph-canvas"></canvas>
        
        <!-- Control bar overlay -->
        <div class="control-bar">
            <!-- Controls here -->
        </div>
    </div>
    
    <script type="text/python" src="Node.py"></script>
    <script type="text/python" src="PriorityQueue.py"></script>
    <script type="text/python" src="SearchAgent.py"></script>
    <script type="text/python" src="main.py"></script>
</body>
</html>
```

---

## 🎯 FINAL VERIFICATION

After implementing all fixes, verify:

1. **Open DevTools Console** - Check canvas size:
   ```javascript
   canvas = document.getElementById('graph-canvas');
   console.log(`Canvas: ${canvas.width}x${canvas.height}`);
   console.log(`DPI: ${window.devicePixelRatio}`);
   ```
   - Canvas width should be `window.innerWidth * devicePixelRatio`
   - Canvas height should be `window.innerHeight * devicePixelRatio`

2. **Test Node Positioning**:
   - Click exactly where you want a node
   - Node should appear exactly where you clicked
   - No offset or misalignment

3. **Test Right-Click**:
   - Right-click anywhere on canvas
   - Should pan, NOT create nodes
   - Context menu should NOT appear

4. **Test Cursor**:
   - Right-click and drag: cursor = "grabbing" (closed hand)
   - Hover with move tool: cursor = "grab" (open hand)
   - Hover with add node: cursor = "crosshair"
   - Never show cross/plus during panning

5. **Test Visual Quality**:
   - Nodes should be perfectly round and crisp
   - Text should be sharp and readable
   - Lines should be smooth (anti-aliased)
   - No pixelation or blur at any zoom level

---

END OF CANVAS RENDERING FIX GUIDE
