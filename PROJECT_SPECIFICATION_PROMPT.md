# Comprehensive Project Specification Prompt

## Generate a detailed markdown specification document for building an AI Search Algorithm Visualizer with the following requirements:

---

## 📋 PROJECT OVERVIEW

Create a comprehensive specification document (PROJECT_SPEC.md) for building a **dual-deployment AI Search Algorithm Visualizer** that includes:

1. **Standalone Visualizer** (Root Directory) - Deployable to GitHub Pages, no login required
2. **Next.js Application** (Subdirectory) - Full-featured app with authentication, user accounts, and graph saving

---

## 🏗️ PROJECT STRUCTURE REQUIREMENTS

### Root Directory Structure
```
/
├── index.html                  # Standalone visualizer entry point
├── main.py                     # Brython-based Python logic
├── SearchAgent.py             # Search algorithm implementations
├── Node.py                    # Node data structure
├── PriorityQueue.py          # Priority queue for informed search
├── styles.css                 # Standalone visualizer styles
├── README.md                  # Project documentation
├── LICENSE
├── .gitignore
├── docs/                      # GitHub Pages documentation
│   ├── algorithm-guide.md
│   ├── api-reference.md
│   └── deployment-guide.md
└── nextjs-app/               # Next.js application folder
    ├── package.json
    ├── next.config.js
    ├── tsconfig.json
    ├── .env.local
    ├── prisma/
    │   └── schema.prisma
    ├── public/
    │   ├── main.py           # Embedded visualizer
    │   ├── SearchAgent.py
    │   ├── Node.py
    │   └── PriorityQueue.py
    ├── src/
    │   ├── app/
    │   ├── components/
    │   ├── lib/
    │   └── types/
    └── README.md
```

---

## 🎯 CORE FUNCTIONALITY REQUIREMENTS

### 1. Search Algorithms (8 Total)

#### Uninformed Search Algorithms
- **Breadth-First Search (BFS)**
- **Depth-First Search (DFS)**
- **Depth-Limited Search (DLS)**
- **Iterative Deepening Search (IDS)**
- **Uniform Cost Search (UCS)**
- **Bidirectional Search**

#### Informed Search Algorithms
- **Greedy Best-First Search**
- **A* Search**

### 2. Algorithm Implementation Requirements

**For EACH algorithm, specify:**

1. **Data Structures Used**
   - Fringe/Frontier type (Queue, Stack, Priority Queue)
   - Visited/Explored set structure
   - Path tracking mechanism

2. **Step-by-Step Execution Flow**
   - Initialization phase
   - Main loop logic
   - Node expansion process
   - Goal test timing
   - Termination conditions

3. **Visualization State Management**
   - When to update Fringe list (frontier)
   - When to update Visited list (explored)
   - When to yield for animation frame
   - Correct timing of state changes vs. visual updates

4. **Critical Implementation Details**
   - Fringe list should show nodes **waiting to be explored**
   - Visited list should show nodes **already expanded**
   - Node should turn purple (visited) **BEFORE** being added to Visited
   - Yield should happen **BEFORE** adding to Visited list
   - Path reconstruction for successful search
   - Handling of failure cases

---

## 🎨 VISUALIZATION REQUIREMENTS

### Canvas-Based Graph Visualization

**Node States & Colors:**
- `empty/unvisited`: White (#ffffff)
- `source`: Red (#ef4444)
- `goal`: Green (#10b981)
- `visited`: Purple (#8b5cf6)
- `path`: Orange (#f59e0b)

**Interactive Features:**
1. **Graph Building Tools**
   - Add Node (click on canvas)
   - Move Node (drag and drop)
   - Add Edge (click two nodes)
   - Delete Node
   - Delete Edge
   - Set Goal Node (toggle)
   - Update Heuristic Value (for informed search)
   - Update Edge Weight

2. **View Controls**
   - Zoom In/Out (mouse wheel + buttons)
   - Pan (click + drag on empty space)
   - Reset View
   - Toggle Labels (show/hide heuristics)
   - Theme Toggle (light/dark mode)
   - Grid Background

3. **Canvas State Management**
   - Undo/Redo (Ctrl+Z / Ctrl+Y)
   - Save Graph (JSON export)
   - Load Graph (JSON import)
   - Reset Canvas (clear all)
   - **Export Graph as Image (PNG)**
   - **Export Search Animation as GIF**
   - **Export Documentation as PDF**

---

## 🎮 ANIMATION CONTROLS (CRITICAL)

### Required Controls
1. **Start Search Button** - Begins auto-play animation
2. **Stop Search Button** - Stops running search
3. **Play/Pause Button** - Toggle auto-play during search
4. **Step Forward Button** - Advance one algorithm step
5. **Step Backward Button** - Go back one algorithm step
6. **Speed Slider** - 1x to 10x speed control (1=slow, 10=fast)
7. **Algorithm Selector** - Dropdown to choose search algorithm

### Animation State Management
```
Animation States Flow:
1. Initial State: Fringe=[source], Visited=[], source=red
2. First Step: Fringe=[], Visited=[], source=purple (YIELD HERE)
3. After Expansion: Fringe=[children], Visited=[source], source=purple
4. Continue until goal found or failure
```

---

## 📊 DATA DISPLAY REQUIREMENTS

### Live Data Panel (Must Show for All Algorithms)

**For Uninformed Search (BFS, DFS, DLS, IDS, UCS, Bidirectional):**
```
Fringe (Frontier):   [1, 2, 3]
Visited (Explored):  [0]
Traversal Order:     [0, 1]
Path Found:          []
```

**For Informed Search (Greedy, A*):**
```
Fringe (Frontier):   [1, 2, 3]
Visited (Explored):  [0]
Traversal Order:     [0, 1]
Path Found:          []
Current Node f(n):   g(0) + h(5) = 5
Path Cost So Far:    0
```

### Search Results Display
**On Completion, Show:**
- Goal Found / No Path Found
- Total Path Cost (number of edges)
- Total Nodes Visited
- Time Taken (with disclaimer about animation delays)
- Final Path Visualization (orange nodes)

---

## 🔧 TECHNICAL IMPLEMENTATION DETAILS

### Standalone Visualizer (GitHub Pages Deployment)

**Technology Stack:**
- HTML5 Canvas for rendering
- Brython (Python in browser) for logic
- Vanilla CSS for styling
- No build step required
- No external dependencies (except Brython CDN)

**Deployment Requirements:**
- Must work as static files on GitHub Pages
- Single-page application
- No server-side code
- All assets self-contained
- Mobile-responsive design

### Next.js Application

**Technology Stack:**
- Next.js 14+ (App Router)
- TypeScript
- Prisma ORM
- PostgreSQL / MongoDB
- NextAuth.js for authentication
- Tailwind CSS
- Lucide Icons
- React Hook Form + Zod validation

**Features:**
1. **Authentication System**
   - Email/Password signup
   - OAuth (Google, GitHub)
   - Password reset
   - Email verification

2. **User Dashboard**
   - List saved graphs
   - Create new graph
   - Edit existing graph
   - Delete graph
   - Share graph (read-only link)
   - Export/Import graphs (JSON)
   - **Export graph as PNG image**
   - **Export search animation as GIF**
   - **Export results as PDF report**

3. **Graph Management**
   - Auto-save functionality
   - Version history
   - Graph metadata (name, description, tags)
   - Thumbnail generation
   - Search and filter graphs

4. **Embedded Visualizer**
   - Same functionality as standalone
   - Integration with user account
   - Save to database
   - Load from database

---

## 📚 DOCUMENTATION REQUIREMENTS

### For Each Algorithm, Document:

1. **Algorithm Overview**
   - Description and use case
   - Time complexity
   - Space complexity
   - Optimality guarantee
   - Completeness guarantee

2. **Pseudocode**
   - Clear step-by-step pseudocode
   - Variable explanations
   - Edge cases handling

3. **Example Walkthrough**
   - Sample graph
   - Step-by-step execution trace
   - OPEN/CLOSED list at each step
   - Final path result

4. **Implementation Notes**
   - Language-specific considerations
   - Common pitfalls
   - Optimization opportunities
   - Testing strategies

### API Documentation

**For SearchAgent class:**
```python
class SearchAgent:
    def __init__(self, graph: dict, source: Node):
        """Initialize search agent"""
        
    def breadth_first_search(self) -> Generator:
        """
        Performs BFS on the graph.
        
        Yields after each state change for visualization.
        Updates self.fringe_list, self.visited_list, self.traversal_array
        
        Returns: Generator that yields at each step
        """
        
    # Document all 8 search methods...
```

### User Guide

**Create detailed user guides for:**
1. Getting started (both versions)
2. Building a graph
3. Running search algorithms
4. Understanding results
5. Saving and sharing graphs (Next.js version)
6. Keyboard shortcuts
7. Troubleshooting

---

## 🧪 TESTING REQUIREMENTS

### Test Coverage Needed

1. **Algorithm Correctness**
   - Test each algorithm on known graphs
   - Verify optimal paths for BFS, UCS, A*
   - Verify completeness
   - Test edge cases (disconnected graphs, unreachable goals)

2. **Visualization Accuracy**
   - Fringe/Visited lists update correctly
   - Node colors change at right time
   - Path reconstruction is correct
   - Animation stepping works bidirectionally

3. **UI/UX Testing**
   - All tools work correctly
   - Undo/redo functionality
   - Save/load graphs
   - Responsive design
   - Cross-browser compatibility

4. **Performance Testing**
   - Large graphs (1000+ nodes)
   - Animation performance
   - Memory usage
   - Database query optimization (Next.js)

---

## 🔒 SECURITY REQUIREMENTS (Next.js App)

1. **Authentication & Authorization**
   - Secure password hashing (bcrypt)
   - JWT token management
   - CSRF protection
   - Rate limiting on API routes

2. **Data Validation**
   - Input sanitization
   - Schema validation (Zod)
   - SQL injection prevention (Prisma)
   - XSS protection

3. **Environment Variables**
   - Never commit secrets
   - Use .env.local for development
   - Secure production environment variables

---

## 🚀 DEPLOYMENT GUIDE

### GitHub Pages (Standalone)
```bash
# Build and deploy steps
1. Commit all files to main branch
2. Enable GitHub Pages in repository settings
3. Select source: main branch, /root
4. Access at: https://username.github.io/repo-name/
```

### Vercel (Next.js App)
```bash
# Deployment steps
1. Connect GitHub repository to Vercel
2. Configure environment variables
3. Set build command: npm run build
4. Set output directory: .next
5. Deploy automatically on push to main
```

---

## 📝 CODE QUALITY REQUIREMENTS

1. **Code Organization**
   - Modular structure
   - Single Responsibility Principle
   - Clear separation of concerns
   - Reusable components

2. **Code Style**
   - Consistent naming conventions
   - Comprehensive comments
   - Type annotations (TypeScript)
   - ESLint/Prettier configuration

3. **Error Handling**
   - Try-catch blocks
   - User-friendly error messages
   - Graceful degradation
   - Logging system

4. **Performance Optimization**
   - Lazy loading
   - Code splitting
   - Image optimization
   - Caching strategies

---

## 🎓 EDUCATIONAL FEATURES

### Algorithm Comparison Tool
Allow users to:
- Run multiple algorithms on same graph
- Compare performance metrics
- Visualize differences
- Export comparison reports

### Tutorial Mode
- Interactive guided tour
- Step-by-step explanations
- Example problems
- Quiz/challenges

---

## 🔮 FUTURE-PROOFING

**Design for extensibility:**
1. Plugin system for new algorithms
2. Custom visualization themes
3. **Export to various formats:**
   - **PNG**: Static graph snapshot (current state)
   - **GIF**: Animated search visualization (entire algorithm run)
   - **PDF**: Comprehensive report with graph, algorithm details, and results
   - **SVG**: Vector format for high-quality scaling
   - **JSON**: Graph data structure
   - **CSV**: Algorithm performance metrics
4. API for programmatic access
5. Graph templates/presets
6. Collaborative editing (future feature)

---

## 📋 DELIVERABLE SPECIFICATION

**The generated markdown document should include:**

1. **Executive Summary** (2-3 pages)
2. **Technical Architecture** (10-15 pages)
3. **Feature Specifications** (20-30 pages)
4. **Algorithm Implementation Guide** (30-40 pages)
5. **UI/UX Design Specifications** (10-15 pages)
6. **API Documentation** (10-15 pages)
7. **Testing Strategy** (10-15 pages)
8. **Deployment Guide** (5-10 pages)
9. **User Documentation** (15-20 pages)
10. **Developer Guide** (15-20 pages)
11. **Appendices** (Code examples, diagrams, flowcharts)

**Total: 150-200 pages of comprehensive documentation**

---

## 🎯 SUCCESS CRITERIA

The application is considered successful when:

✅ All 8 search algorithms work correctly
✅ Fringe/Visited lists update at correct times
✅ Animation can be stepped forward and backward
✅ Speed control works smoothly
✅ Standalone version deploys to GitHub Pages
✅ Next.js version has working authentication
✅ Graphs can be saved and loaded
✅ Mobile-responsive design
✅ Comprehensive documentation
✅ Test coverage > 80%
✅ No critical bugs
✅ Performance is smooth (60 fps animation)

---

## 🚨 CRITICAL IMPLEMENTATION RULES

### Fringe/Visited List Management (MUST FOLLOW)

```python
# CORRECT IMPLEMENTATION
while fringe:
    node = fringe.pop()
    self.fringe_list = [n.name for n in fringe]  # Update Fringe after pop
    self.set_node_state(node, "visited")         # Turn node purple
    yield                                         # YIELD BEFORE adding to Visited
    self.visited_list.append(node.name)          # Now add to Visited
    self.traversal_array.append(node.name)
    
    if is_goal(node):
        # Handle goal
        return
        
    for child in expand(node):
        if not_visited(child) and child not in self.fringe_list:
            fringe.append(child)
    
    self.fringe_list = [n.name for n in fringe]  # Update Fringe after expansion
```

### Visualization Timing

**STATE FLOW:**
```
1. Pop node from Fringe
2. Show node as purple (visited)
3. Display: Fringe=[...], Visited=[], node=purple
4. User sees this state
5. THEN add node to Visited
6. Expand children
7. Update Fringe with new children
```

---

## � EXPORT FUNCTIONALITY REQUIREMENTS

### 1. PNG Export (Static Image)
**Feature:** Export current graph state as PNG image

**Requirements:**
- Capture current canvas state (all nodes, edges, colors)
- Include graph metadata in image (algorithm used, timestamp)
- Options for image quality (low/medium/high)
- Options for resolution (1x, 2x, 4x for retina displays)
- Transparent or solid background option
- Download directly to user's device

**Use Cases:**
- Share graph on social media
- Include in presentations
- Documentation purposes
- Print-friendly format

### 2. GIF Export (Animation Recording)
**Feature:** Record entire search algorithm execution as animated GIF

**Requirements:**
- Start/Stop recording button
- Record all animation frames during search
- Configurable frame rate (5-30 fps)
- Configurable playback speed (matches animation speed)
- Optional loop setting (loop infinitely or play once)
- File size optimization
- Progress indicator during GIF generation
- Preview before download

**Technical Implementation:**
- Use gif.js or similar library for browser-based GIF encoding
- Capture canvas frames at each yield/animation step
- Compress frames to reduce file size
- Show estimated file size before generation

**Use Cases:**
- Create tutorials/educational content
- Share algorithm visualization on forums
- Demonstrate algorithm behavior
- Create portfolio content

### 3. PDF Export (Comprehensive Report)
**Feature:** Generate detailed PDF report with graph, algorithm info, and results

**Report Contents:**
1. **Cover Page**
   - Graph title
   - Algorithm used
   - Date/time generated
   - User info (if logged in)

2. **Graph Visualization**
   - High-resolution graph image (current state or final state)
   - Node and edge details table

3. **Algorithm Details**
   - Algorithm description
   - Pseudocode
   - Time/space complexity
   - Optimality/completeness info

4. **Search Results**
   - Path found (if successful)
   - Nodes visited count
   - Path cost
   - Execution time
   - Fringe/Visited lists at key steps

5. **Performance Metrics**
   - Graph statistics (node count, edge count, average degree)
   - Algorithm performance comparison (if multiple runs)

**Technical Implementation:**
- Use jsPDF or similar library for browser-based PDF generation
- Include charts/graphs using Chart.js
- Support custom branding (logo, colors)
- Optimized for printing (A4/Letter size)

**Use Cases:**
- Academic submissions
- Research documentation
- Teaching materials
- Professional reports

### 4. SVG Export (Vector Graphics)
**Feature:** Export graph as scalable vector graphics

**Requirements:**
- Preserve all visual elements (nodes, edges, labels)
- Infinite scaling without quality loss
- Editable in vector graphics software (Illustrator, Inkscape)
- Include metadata (node IDs, edge weights)
- Option to include or exclude heuristic labels

**Use Cases:**
- High-quality publications
- Further editing in graphic design software
- Responsive web displays
- Professional documentation

### 5. JSON Export (Data Structure)
**Feature:** Export graph structure and algorithm results as JSON

**JSON Structure:**
```json
{
  "metadata": {
    "version": "1.0",
    "created": "2025-10-31T10:30:00Z",
    "algorithm": "a-star",
    "user": "username"
  },
  "graph": {
    "nodes": [
      {"id": 0, "x": 100, "y": 200, "heuristic": 5, "state": "source"},
      {"id": 1, "x": 300, "y": 200, "heuristic": 3, "state": "goal"}
    ],
    "edges": [
      {"from": 0, "to": 1, "weight": 4}
    ]
  },
  "results": {
    "success": true,
    "path": [0, 1],
    "pathCost": 4,
    "nodesVisited": 5,
    "executionTime": 0.45,
    "fringeHistory": [[0], [1, 2], [2, 3]],
    "visitedHistory": [[], [0], [0, 1]]
  }
}
```

**Use Cases:**
- Import/export between sessions
- Programmatic analysis
- Integration with other tools
- Backup and version control

### 6. CSV Export (Performance Metrics)
**Feature:** Export algorithm performance data for analysis

**CSV Contents:**
- Algorithm comparison data (if multiple runs)
- Step-by-step execution log
- Node visit order
- Fringe/Visited sizes over time
- Memory usage estimates

**Use Cases:**
- Statistical analysis
- Performance benchmarking
- Research data collection
- Spreadsheet integration

### Export UI/UX Requirements

**Export Menu Design:**
```
📤 Export Options
├── 📷 Export as Image (PNG)
├── 🎬 Export Animation (GIF)
├── 📄 Export Report (PDF)
├── 🎨 Export Vector (SVG)
├── 💾 Export Data (JSON)
└── 📊 Export Metrics (CSV)
```

**Settings Modal:**
- Resolution/quality settings
- Format-specific options
- File naming convention
- Preview before download
- Batch export option (multiple formats at once)

**Keyboard Shortcuts:**
- `Ctrl+S`: Quick save as JSON
- `Ctrl+Shift+S`: Save as PNG
- `Ctrl+E`: Open export menu

---

## �💡 ADDITIONAL NOTES

- Use generator functions for algorithm implementations (Python `yield`)
- Implement frame-by-frame animation state saving
- Support undo/redo on graph edits
- Provide keyboard shortcuts for power users
- Include example graphs (sample problems)
- Add tooltips and help text throughout UI
- Implement analytics (for Next.js version)
- **Support multiple export formats (PNG, GIF, PDF, SVG, JSON, CSV)**
- Add print-friendly CSS for documentation
- **GIF recording with optimized frame capture**
- **PDF generation with comprehensive algorithm reports**

---

## 🔗 REFERENCE MATERIALS TO INCLUDE

1. Links to algorithm research papers
2. Textbook references (Russell & Norvig, etc.)
3. Visualization best practices
4. Accessibility guidelines (WCAG)
5. Performance benchmarks
6. Browser compatibility matrix

---

## END OF PROMPT

**Use this prompt to generate a comprehensive PROJECT_SPEC.md file that developers can follow to build the entire application from scratch with zero ambiguity.**
