# 🤖 AI Search Algorithm Visualizer

An interactive web-based visualizer for classic AI search algorithms built with Brython (Python in the browser).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://ashfaknawshad.github.io/aisearch-v2/)

## 🚀 [**View Live Demo**](https://ashfaknawshad.github.io/aisearch-v2/)

## ✨ Features

### 8 Search Algorithms Implemented

**Uninformed Search:**
- 🔵 Breadth-First Search (BFS)
- 🔴 Depth-First Search (DFS)
- 🟡 Depth-Limited Search (DLS)
- 🟢 Iterative Deepening Search (IDS)
- 🟣 Uniform Cost Search (UCS)
- 🔶 Bidirectional Search

**Informed Search:**
- 🟠 Greedy Best-First Search
- ⭐ A* Search

### Interactive Visualization

- **Step-by-step animation** with play/pause controls
- **Forward/backward stepping** through algorithm execution
- **Adjustable animation speed** (1x to 10x)
- **Real-time data display** showing Fringe, Visited, and Path
- **Color-coded node states** for easy tracking
- **Responsive canvas** with zoom, pan, and grid

### Graph Building Tools

- ➕ Add/Delete Nodes
- 🔗 Add/Delete Edges
- ✋ Drag to move nodes
- 🎯 Set source and goal nodes
- 🔢 Edit heuristic values
- ⚖️ Edit edge weights
- 🔄 Undo/Redo support

### Export Capabilities

- 📷 **PNG**: Export static graph images
- 🎬 **GIF**: Record animated algorithm execution
- 📄 **PDF**: Generate comprehensive reports
- 🎨 **SVG**: Vector graphics for publications
- 💾 **JSON**: Save/load graph structures
- 📊 **CSV**: Export performance metrics

### Two Deployment Options

1. **Standalone Version** (GitHub Pages)
   - No installation required
   - Works entirely in the browser
   - Uses Brython (Python in browser)
   - Perfect for quick demonstrations

2. **Next.js Application** (Full-featured)
   - User authentication (email/password, OAuth)
   - Save and manage multiple graphs
   - Version history
   - Sharing capabilities
   - Advanced analytics

## 🚀 Quick Start

### Standalone Version (GitHub Pages)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ashfaknawshad/aisearch-v2.git
   cd aisearch-v2
   ```

2. **Open in browser:**
   Simply open `index.html` in your web browser, or:
   ```bash
   # Using Python's built-in server
   python -m http.server 8000
   ```
   Then navigate to `http://localhost:8000`

3. **Deploy to GitHub Pages:**
   - Push to GitHub
   - Go to repository Settings → Pages
   - Select `main` branch as source
   - Your site will be live at `https://yourusername.github.io/aisearch-v2/`

### Windows Fully Portable EXE

Use this build when you want a download-and-run Windows app:

- File name: `AI Search Algorithm Visualizer Fully Portable.exe`
- Output location: `release/AI Search Algorithm Visualizer Fully Portable.exe`
- Works offline after download
- No Python/Node install required on the target PC
- Includes bundled WebView2 fixed runtime for portability across Windows 10/11

Build command:
```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows-exe.ps1
```


## 📖 Usage

### Building a Graph

1. **Add Nodes**: Click "Add Node" tool and click on canvas
2. **Connect Nodes**: Click "Add Edge" tool, click two nodes to connect
3. **Set Source**: The first node is automatically the source (red)
4. **Set Goal**: Click "Set Goal" tool and click a node (green)
5. **Add Heuristics**: For A*/Greedy, click "Edit Heuristic" and click a node
6. **Add Weights**: For UCS/A*, click "Edit Weight" and click an edge

### Running Algorithms

1. **Select Algorithm**: Choose from the dropdown menu
2. **Start Search**: Click "▶️ Start Search" to begin animation
3. **Control Playback**: Use Pause, Step Forward/Back buttons
4. **Adjust Speed**: Use the slider to control animation speed
5. **View Results**: Check the right panel for statistics and path found

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `A` | Add Node tool |
| `E` | Add Edge tool |
| `M` | Move Node tool |
| `D` | Delete Node tool |
| `G` | Set Goal tool |
| `H` | Edit Heuristic tool |
| `Space` | Start/Pause search |
| `←/→` | Step Backward/Forward |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+S` | Save Graph |
| `R` | Reset View |
| `L` | Toggle Labels |

## 📚 Documentation

- **[Algorithm Guide](docs/algorithm-guide.md)** - Detailed explanation of all 8 algorithms
- **[API Reference](docs/api-reference.md)** - Python class documentation
- **[Deployment Guide](docs/deployment-guide.md)** - Step-by-step deployment instructions

## 🏗️ Project Structure

```
ai-search-v2/
├── index.html              # Standalone visualizer entry point
├── main.py                 # Brython visualization logic
├── SearchAgent.py          # Algorithm implementations
├── Node.py                 # Node data structure
├── PriorityQueue.py        # Priority queue & data structures
├── styles.css              # Styling with dark mode
├── README.md               # This file
├── LICENSE                 # MIT License
├── .gitignore             # Git ignore rules
├── docs/                   # Documentation
│   ├── algorithm-guide.md
│   ├── api-reference.md
│   └── deployment-guide.md
└── nextjs-app/            # Next.js application
    ├── package.json
    ├── next.config.js
    ├── tsconfig.json
    ├── prisma/
    │   └── schema.prisma
    ├── src/
    │   ├── app/
    │   ├── components/
    │   └── lib/
    └── public/
```

## 🎯 Algorithm Comparison

| Algorithm | Complete | Optimal | Time Complexity | Space Complexity |
|-----------|----------|---------|-----------------|------------------|
| BFS | ✅ Yes | ✅ Yes* | O(V + E) | O(V) |
| DFS | ❌ No | ❌ No | O(V + E) | O(V) |
| DLS | ❌ No** | ❌ No | O(b^l) | O(l) |
| IDS | ✅ Yes | ✅ Yes* | O(b^d) | O(d) |
| UCS | ✅ Yes | ✅ Yes | O(b^(1+⌊C*/ε⌋)) | O(b^(1+⌊C*/ε⌋)) |
| Bidirectional | ✅ Yes | ✅ Yes* | O(b^(d/2)) | O(b^(d/2)) |
| Greedy | ❌ No | ❌ No | O(b^m) | O(b^m) |
| A* | ✅ Yes | ✅ Yes*** | O(b^d) | O(b^d) |

\* For unweighted graphs  
\** Only if goal within depth limit  
\*** With admissible heuristic

## 🎓 Educational Use

This visualizer is perfect for:

- **Computer Science students** learning AI search algorithms
- **Teachers** demonstrating algorithm behavior
- **Researchers** prototyping and testing heuristics
- **Interview preparation** for algorithm questions
- **Self-learners** understanding pathfinding concepts

## 🛠️ Technology Stack

### Standalone Version
- **HTML5 Canvas** for rendering
- **Brython** (Python in browser)
- **Vanilla CSS** with CSS variables
- **GIF.js** for animation export
- **jsPDF** for PDF reports

### Next.js Application
- **Next.js 14+** (App Router)
- **TypeScript**
- **Prisma ORM**
- **NextAuth.js**
- **Tailwind CSS**
- **PostgreSQL/MongoDB**
- **Lucide Icons**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Algorithm concepts from "Artificial Intelligence: A Modern Approach" by Russell & Norvig
- Inspired by various online pathfinding visualizers
- Built with ❤️ for the AI education community

## 📧 Contact

- GitHub: [@ashfaknawshad](https://github.com/ashfaknawshad)
- Project Link: [https://github.com/ashfaknawshad/aisearch-v2](https://github.com/ashfaknawshad/aisearch-v2)

## 🗺️ Roadmap

- [ ] Add more algorithms (Dijkstra's, Bellman-Ford)
- [ ] 3D graph visualization
- [ ] Collaborative editing
- [ ] Mobile app version
- [ ] Algorithm performance comparison tool
- [ ] Custom algorithm plugin system
- [ ] Tutorial mode with guided walkthroughs
- [ ] Integration with graph theory libraries

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

Made by [Ashfak Nawshad] | [License](LICENSE) | [Changelog](CHANGELOG.md)
