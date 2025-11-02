# 🚀 QUICK START GUIDE

## Get Your Visualizer Running in 60 Seconds!

### Windows Users

1. **Double-click this file:**
   ```
   start-server.bat
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:8000
   ```

3. **Start visualizing!** 🎉

### Mac/Linux Users

1. **Open Terminal in this directory and run:**
   ```bash
   bash start-server.sh
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:8000
   ```

3. **Start visualizing!** 🎉

---

## 📖 First Steps Tutorial

### Create Your First Graph (2 minutes)

1. **Add Nodes:**
   - Click anywhere on the white canvas
   - Each click adds a new node
   - The first node is RED (source)

2. **Set Goal:**
   - Click the "🎯 Set Goal" button
   - Click any node to make it GREEN (goal)

3. **Connect Nodes:**
   - Click the "🔗 Add Edge" button
   - Click one node, then click another
   - An arrow appears connecting them

4. **Run Algorithm:**
   - Select "Breadth-First Search (BFS)" from dropdown
   - Click "▶️ Start Search"
   - Watch it find the path!

### Try Different Algorithms

**Breadth-First Search (BFS)**
- Good for: Shortest path in unweighted graphs
- Speed: Fast
- Memory: Medium

**Depth-First Search (DFS)**
- Good for: Deep exploration
- Speed: Fast
- Memory: Low

**A* Search** (needs heuristics!)
- Good for: Optimal path with smart guessing
- Speed: Very fast with good heuristic
- Memory: Medium

To use A*:
1. Click "🔢 Edit Heuristic" button
2. Click each node and enter a number (distance to goal)
3. Lower numbers = closer to goal
4. Run A* Search

---

## 🎮 Controls Reference

### Graph Building
- **Add Node:** Click canvas
- **Move Node:** Drag any node
- **Delete Node:** Click "Delete Node" tool, then click node
- **Add Edge:** Click "Add Edge", click two nodes
- **Edit Heuristic:** Click tool, click node, enter value

### Animation
- **▶️ Start:** Begin search animation
- **⏸️ Pause:** Pause/resume
- **⏹️ Stop:** Stop and reset
- **⏮️/⏭️:** Step backward/forward frame by frame
- **Speed Slider:** Adjust animation speed (1x - 10x)

### View
- **🔍+:** Zoom in
- **🔍-:** Zoom out
- **🎯:** Reset view to center
- **🏷️:** Show/hide heuristic labels
- **📐:** Show/hide grid background
- **🌙:** Toggle dark mode

### Export
- **📷 PNG:** Save current graph as image
- **🎬 GIF:** Record animation as GIF
- **📄 PDF:** Generate full report
- **💾 JSON:** Save graph to file
- **📊 CSV:** Export metrics

---

## 🎯 Example Workflows

### Workflow 1: Compare BFS vs DFS

1. Load example: Click "Simple Path"
2. Run BFS: Select BFS, click Start
3. Note the path and nodes visited
4. Click "🧹 Clear Path"
5. Run DFS: Select DFS, click Start
6. Compare the results!

### Workflow 2: Test A* Optimality

1. Load example: Click "Weighted Graph"
2. Note the edge weights (numbers on edges)
3. Set heuristics (optional, or use existing)
4. Run A* and note path cost
5. Run UCS and note path cost
6. Both should find optimal path!

### Workflow 3: Create Custom Maze

1. Click "📐" to show grid
2. Add nodes in a grid pattern
3. Connect them like a maze
4. Block some paths (don't add edges)
5. Set start (red) and goal (green)
6. Try different algorithms to solve!

---

## 💡 Pro Tips

### Keyboard Shortcuts
- Press `A` for Add Node tool
- Press `E` for Add Edge tool
- Press `M` for Move Node tool
- Press `D` for Delete Node tool
- Press `G` for Set Goal tool
- Press `H` for Edit Heuristic
- Press `Space` to start/pause search
- Press `←` `→` to step through animation
- Press `Ctrl+Z` to undo
- Press `Ctrl+S` to save graph

### Better Visualizations
1. Use grid for neat layouts
2. Space nodes evenly
3. Add heuristics for informed search
4. Use edge weights for realistic scenarios
5. Export to PNG for presentations

### Performance Tips
- Turn off grid for large graphs (100+ nodes)
- Turn off labels if not needed
- Use lower animation speed for complex graphs
- Close other browser tabs

---

## 🎓 Learn the Algorithms

### When to Use Each Algorithm?

**Need shortest path (unweighted)?**
→ Use BFS or IDS

**Need shortest path (weighted)?**
→ Use UCS or A*

**Have good heuristic available?**
→ Use A* (best choice!)

**Just exploring/memory constrained?**
→ Use DFS

**Need approximate solution quickly?**
→ Use Greedy

**Single known goal, want to be faster?**
→ Use Bidirectional Search

### Understanding the Data Panel

**Fringe (Frontier):**
- Nodes waiting to be explored
- "Next in line" to visit

**Visited (Explored):**
- Nodes already processed
- Won't be visited again

**Traversal Order:**
- Order nodes were visited
- Shows algorithm's path

**Path Found:**
- Final path from source to goal
- Shows shortest/optimal route

---

## 🐛 Troubleshooting

### "Python not found"
**Solution:** Install Python 3 from python.org

### "Page won't load"
**Solution:** 
1. Make sure server is running (check terminal)
2. Try http://127.0.0.1:8000 instead
3. Try different browser

### "Animation is too fast/slow"
**Solution:** Use the Speed Slider (bottom left panel)

### "Can't see heuristics"
**Solution:** Click "🏷️ Toggle Labels" button

### "Undo not working"
**Solution:** Undo only works for graph edits, not animations

### "Export doesn't work"
**Solution:** 
- PNG: Should work always
- GIF: Requires GIF.js (loaded from CDN)
- PDF: Requires jsPDF (loaded from CDN)
- Check internet connection for CDN libraries

---

## 📚 Next Steps

### Learn More:
1. Read `docs/algorithm-guide.md` for detailed algorithm explanations
2. Read `docs/api-reference.md` for technical details
3. Check `PROJECT_STATUS.md` for full feature list

### Deploy to Web:
1. Read `docs/deployment-guide.md`
2. Push to GitHub
3. Enable GitHub Pages
4. Share your URL!

### Build Full App:
1. Follow `nextjs-app/README.md`
2. Add user accounts
3. Save graphs to cloud
4. Share with others

---

## 🎉 Have Fun!

You now have everything you need to:
- ✅ Visualize 8 search algorithms
- ✅ Create custom graphs
- ✅ Export results
- ✅ Learn AI concepts
- ✅ Teach others
- ✅ Deploy online

**Questions?** Check the docs folder or PROJECT_STATUS.md!

**Enjoying it?** Star the project on GitHub! ⭐

---

Made with ❤️ for AI education | October 2025
