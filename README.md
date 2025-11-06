# 🚀 TUI File Explorer

A blazing-fast, feature-rich **Terminal User Interface (TUI)** file explorer built with Python and Textual. Navigate your file system with vim-like keybindings and enjoy rich file previews, smart filtering, and BFS-powered search—all from your terminal.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)

## ✨ Features

### 🎯 Core Functionality
- **Vim-like Navigation**: Navigate with `j`/`k`/`h`/`l` keybindings
- **Dual-Panel Layout**: File list (40%) + Preview panel (60%)
- **Smart File Preview**: Automatic content detection and formatting
- **Hidden Files Toggle**: Show/hide dotfiles with `.` key
- **Quick Home Jump**: Press `~` to instantly jump to your home directory

### 🔍 Search & Filter
- **BFS Search**: Lightning-fast breadth-first search across directories
- **Smart Filtering**: Filter by extension, file type, or name
  - Extension: `.py`, `.txt`, `.md`
  - Type: `img`, `video`, `audio`, `code`, `doc`, `archive`
  - Name: Any substring match

### 📄 Rich File Previews
- **Images** 🖼️: Format, dimensions, color mode (with PIL/Pillow)
- **Videos** 🎬: Format, size information
- **Audio** 🎵: Format detection
- **Archives** 📦: File count and contents (for .zip)
- **PDFs** 📕: Page count (with PyPDF2)
- **Code/Text** 📝: Syntax-highlighted preview (100 lines)
- **Directories** 📁: Folder statistics and contents

### 🛠️ Data Structures
- **TreeNode**: Directory hierarchy representation
- **NavigationStack**: Back/forward navigation using stack
- **SearchQueue**: BFS implementation using deque

## 🚀 Installation

### Prerequisites
```bash
# Required
pip install textual

# Optional (for enhanced previews)
pip install pillow      # Image dimensions
pip install PyPDF2      # PDF page count
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/02Aditya2323/TuiFileExplorer.git
cd TuiFileExplorer

# Install dependencies
pip install textual

# Run the file explorer
python chut.py
```

## ⌨️ Keybindings

| Key | Action | Description |
|-----|--------|-------------|
| `j` / `↓` | Down | Move selection down |
| `k` / `↑` | Up | Move selection up |
| `l` / `Enter` | Enter | Open directory |
| `h` / `Backspace` | Back | Go to parent directory |
| `g` | Top | Jump to first item |
| `G` | Bottom | Jump to last item |
| `.` | Toggle Hidden | Show/hide hidden files |
| `~` | Home | Jump to home directory |
| `/` | Search | BFS search mode |
| `f` | Filter | Filter current directory |
| `Esc` | Cancel | Exit search/filter mode |
| `q` | Quit | Exit application |

## 🎨 Screenshots

```
┌────────────────────────────────────────────────────────────────┐
│ 📂 /Users/aditya4/Desktop                                      │
├──────────────────────┬─────────────────────────────────────────┤
│ Files (40%)          │ Preview (60%)                           │
├──────────────────────┼─────────────────────────────────────────┤
│ > 📁 projects        │ Directory: projects                     │
│   📁 documents       │ 📁 12 folders  📄 8 files               │
│   📁 downloads       │                                         │
│   📄 README.md [5KB] │ 📁 python-scripts                       │
│   📄 notes.txt [2KB] │ 📁 web-dev                              │
│                      │ 📄 config.json                          │
└──────────────────────┴─────────────────────────────────────────┘
```

## 🔧 Usage Examples

### Search for Files
Press `/` to activate search mode, then type your query:
```
Search: python
```
Results are displayed using BFS traversal (up to 150 matches).

### Filter by Type
Press `f` to activate filter mode:
```
Filter: .py          # All Python files
Filter: img          # All images
Filter: code         # All code files
Filter: test         # Files with "test" in name
```

### Navigate Efficiently
```
g       # Jump to top
G       # Jump to bottom
~       # Go to home directory
.       # Toggle hidden files
```

## 📂 Project Structure

```
TuiFileExplorer/
├── chut.py          # Main application
└── README.md        # This file
```

### Code Architecture
- **Data Structures**: TreeNode, NavigationStack, SearchQueue
- **Widgets**: FileList, Preview, SearchPanel
- **Main App**: FileExplorer (Textual App)

## 🌟 Highlights

- **Performance**: Limited to 300 files per directory for speed
- **Safety**: Permission error handling for protected directories
- **UX**: Auto-scroll to top on navigation, human-readable file sizes
- **Extensibility**: Easy to add new file type handlers

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with [Textual](https://github.com/Textualize/textual) - the amazing TUI framework for Python.

## 📬 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ and Python** | Happy Exploring! 🎉
