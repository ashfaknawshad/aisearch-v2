# 🚀 GitHub Pages Deployment Instructions

## Quick Setup (2 minutes)

Your code is already pushed to: https://github.com/ashfaknawshad/aisearch-v2

### Enable GitHub Pages:

1. **Go to your repository settings:**
   - Visit: https://github.com/ashfaknawshad/aisearch-v2/settings/pages

2. **Configure GitHub Pages:**
   - Under "Source", select: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ (root)**
   - Click **Save**

3. **Wait 1-2 minutes for deployment**

4. **Your site will be live at:**
   ```
   https://ashfaknawshad.github.io/aisearch-v2/
   ```

## What's Deployed?

✅ **Core Files:**
- `index.html` - Main application
- `styles.css` - Styling
- `main.py` - Main Python/Brython code
- `Node.py`, `PriorityQueue.py`, `SearchAgent.py` - Core logic
- `gif.worker.js` - GIF export functionality

✅ **Features:**
- 8 search algorithms (BFS, DFS, DLS, IDS, UCS, Bidirectional, Greedy, A*)
- Modal-based UI (no browser prompts)
- Directed/Undirected graph support
- Custom node naming (letters or numbers)
- PNG/GIF export
- Save/Load graphs
- Algorithm-aware UI
- Dark mode

## Windows Fully Portable Build

If you need a fully portable Windows app file, build:

- `release/AI Search Algorithm Visualizer Fully Portable.exe`

Build command:

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows-exe.ps1
```

Notes:
- Designed for Windows 10/11.
- Works offline.
- No Python/Node dependency on target PCs.

## Troubleshooting

If the site doesn't work:
- Wait 2-3 minutes for GitHub Pages to build
- Check that all files are in the root directory (they are!)
- Make sure GitHub Pages is enabled in settings
- Clear your browser cache

## Future Development

The `nextjs-app` folder was removed for now. You can work on it separately and deploy it later to a different URL or subdomain.

---

**Repository:** https://github.com/ashfaknawshad/aisearch-v2
**Live Site:** https://ashfaknawshad.github.io/aisearch-v2/ (once enabled)

---

### Note on Windows Executables (Git LFS)
The `release/` folder contains the `.exe` files tracked using Git LFS. The large `.cab` files (WebView2 runtime installers) are intentionally ignored in Git to save space. If you are building the Native app yourself or need the Fixed Version Runtime, the build script `build-windows-exe.ps1` will automatically download them for you if they are missing.
