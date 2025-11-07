import os
from pathlib import Path
from collections import deque
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Header, Footer, Static, Input, Label, RichLog
from textual.binding import Binding
from textual.reactive import reactive


# ==================== DATA STRUCTURES ====================

class TreeNode:
    """Tree data structure for directory hierarchy"""
    def __init__(self, path: Path, parent: Optional['TreeNode'] = None):
        self.path = path
        self.parent = parent
        self.children: list['TreeNode'] = []
        self.is_expanded = False
    
    def add_child(self, child: 'TreeNode'):
        self.children.append(child)
        child.parent = self


class NavigationStack:
    """Stack data structure for back/forward navigation"""
    def __init__(self):
        self.stack: list[Path] = []
    
    def push(self, path: Path):
        self.stack.append(path)
    
    def pop(self) -> Optional[Path]:
        return self.stack.pop() if self.stack else None
    
    def is_empty(self) -> bool:
        return len(self.stack) == 0


class SearchQueue:
    """Queue data structure for BFS file searching"""
    def __init__(self):
        self.queue: deque[Path] = deque()
    
    def enqueue(self, path: Path):
        self.queue.append(path)
    
    def dequeue(self) -> Optional[Path]:
        return self.queue.popleft() if self.queue else None
    
    def is_empty(self) -> bool:
        return len(self.queue) == 0


# ==================== WIDGETS ====================

class FileList(RichLog):
    """Middle panel showing files"""
    
    def __init__(self):
        super().__init__(highlight=True, markup=True)
        self.current_path = Path.cwd()
        self.files: list[Path] = []
        self.selected_idx = 0
        self.show_hidden = False  # Toggle for hidden files
    
    def load_directory(self, path: Path):
        self.current_path = path
        self.selected_idx = 0
        try:
            items = list(path.iterdir())
            # Filter hidden files if disabled
            if not self.show_hidden:
                items = [i for i in items if not i.name.startswith('.')]
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            self.files = items[:300]
        except (PermissionError, OSError):
            self.files = []
        self.render_list()
    
    def render_list(self):
        self.clear()
        self.scroll_home(animate=False)  # Scroll to top
        for idx, item in enumerate(self.files):
            icon = "📁" if item.is_dir() else "📄"
            
            # Show file size for files
            size_str = ""
            if item.is_file():
                try:
                    size = item.stat().st_size
                    size_str = f" [{self.format_size(size)}]"
                except:
                    pass
            
            if idx == self.selected_idx:
                self.write(f"[black on cyan]> {icon} {item.name}{size_str}[/]")
            else:
                self.write(f"  {icon} {item.name}[dim]{size_str}[/]")
    
    def format_size(self, size: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.0f}{unit}" if size >= 10 else f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def toggle_hidden(self):
        """Toggle visibility of hidden files"""
        self.show_hidden = not self.show_hidden
        self.load_directory(self.current_path)
    
    def move_selection(self, delta: int):
        if not self.files:
            return
        self.selected_idx = max(0, min(len(self.files) - 1, self.selected_idx + delta))
        self.render_list()
    
    def get_selected(self) -> Optional[Path]:
        if 0 <= self.selected_idx < len(self.files):
            return self.files[self.selected_idx]
        return None


class Preview(RichLog):
    """Right panel"""
    
    def __init__(self):
        super().__init__(highlight=True, markup=True)
    
    def show_preview(self, path: Path):
        self.clear()
        self.scroll_home(animate=False)  # Always scroll to top
        
        if not path.exists():
            self.write("[red]File not found[/]")
            return
        
        if path.is_dir():
            try:
                items = list(path.iterdir())
                items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                
                # Show directory stats
                dirs = sum(1 for i in items if i.is_dir())
                files = len(items) - dirs
                self.write(f"[cyan bold]Directory: {path.name}[/]")
                self.write(f"[yellow]📁 {dirs} folders  📄 {files} files[/]\n")
                
                for item in items[:80]:
                    icon = "📁" if item.is_dir() else "📄"
                    self.write(f"{icon} {item.name}")
            except (PermissionError, OSError):
                self.write("[red]Permission denied[/]")
        else:
            self.show_file_info(path)
    
    def show_file_info(self, path: Path):
        """Show detailed file information based on type"""
        try:
            stat = path.stat()
            size = stat.st_size
            suffix = path.suffix.lower()
            
            # Basic info header
            self.write(f"[cyan bold]File: {path.name}[/]")
            self.write(f"[yellow]Size: {self.format_size(size)}[/]\n")
            
            # Image files
            if suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico', '.svg']:
                self.write(f"[green]🖼️  Image File[/]")
                self.write(f"Format: {suffix[1:].upper()}")
                try:
                    from PIL import Image
                    img = Image.open(path)
                    self.write(f"Dimensions: {img.width} x {img.height}")
                    self.write(f"Mode: {img.mode}")
                except:
                    self.write("(Install PIL/Pillow for more details)")
            
            # Video files
            elif suffix in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']:
                self.write(f"[green]🎬 Video File[/]")
                self.write(f"Format: {suffix[1:].upper()}")
                self.write(f"Size: {self.format_size(size)}")
            
            # Audio files
            elif suffix in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma']:
                self.write(f"[green]🎵 Audio File[/]")
                self.write(f"Format: {suffix[1:].upper()}")
            
            # Archive files
            elif suffix in ['.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar']:
                self.write(f"[green]📦 Archive File[/]")
                self.write(f"Format: {suffix[1:].upper()}")
                if suffix == '.zip':
                    try:
                        import zipfile
                        with zipfile.ZipFile(path, 'r') as zf:
                            files = zf.namelist()
                            self.write(f"Contains {len(files)} files:\n")
                            for f in files[:30]:
                                self.write(f"  - {f}")
                            if len(files) > 30:
                                self.write(f"  ... and {len(files) - 30} more")
                    except:
                        pass
            
            # PDF files
            elif suffix == '.pdf':
                self.write(f"[green]📕 PDF Document[/]")
                try:
                    import PyPDF2
                    with open(path, 'rb') as f:
                        pdf = PyPDF2.PdfReader(f)
                        self.write(f"Pages: {len(pdf.pages)}")
                except:
                    self.write("(Install PyPDF2 for more details)")
            
            # Text/code files - show content
            elif suffix in ['.py', '.txt', '.md', '.json', '.yaml', '.toml', '.cpp', '.c', 
                           '.js', '.html', '.css', '.sh', '.rs', '.go', '.java', '.rb']:
                self.write(f"[green]📝 Text/Code File[/]")
                self.write(f"Type: {suffix[1:].upper()}\n")
                content = path.read_text(errors='ignore')[:2000]
                lines = content.split('\n')[:100]
                for line in lines:
                    self.write(line)
                if len(content) > 2000:
                    self.write("\n[yellow]... (truncated)[/]")
            
            # Executable files
            elif suffix in ['.exe', '.dll', '.so', '.dylib', '.app']:
                self.write(f"[green]⚙️  Executable/Library[/]")
                self.write(f"Type: {suffix[1:].upper()}")
            
            # Database files
            elif suffix in ['.db', '.sqlite', '.sqlite3']:
                self.write(f"[green]🗄️  Database File[/]")
                self.write(f"Type: SQLite")
            
            # Everything else
            else:
                self.write(f"[yellow]📄 Binary/Unknown File[/]")
                self.write(f"Extension: {suffix or '(none)'}")
                
        except Exception as e:
            self.write(f"[red]Cannot preview: {e}[/]")
    
    def format_size(self, size: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"


class SearchPanel(RichLog):
    """Search results"""
    
    def __init__(self):
        super().__init__(highlight=True, markup=True)
    
    def show_results(self, results: list[Path], query: str):
        self.clear()
        if not results:
            self.write(f"[yellow]No matches for '{query}'[/]")
        else:
            self.write(f"[green bold]Found {len(results)} matches:[/]\n")
            for path in results[:150]:
                self.write(f"📄 {path}")


# ==================== MAIN APP ====================

class FileExplorer(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #main-container {
        height: 1fr;
        layout: horizontal;
    }
    
    FileList {
        width: 40%;
        border: solid cyan;
    }
    
    Preview {
        width: 60%;
        border: solid green;
    }
    
    SearchPanel {
        width: 100%;
        border: solid yellow;
    }
    
    #search-box {
        height: 3;
        dock: bottom;
        border: solid yellow;
    }
    
    #path-label {
        dock: top;
        background: $boost;
        padding: 0 1;
        height: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j", "down", "Down"),
        Binding("k", "up", "Up"),
        Binding("h", "back", "Back"),
        Binding("l", "enter", "Enter"),
        Binding("enter", "enter", "Enter"),
        Binding("backspace", "back", "Back"),
        Binding("/", "search_mode", "Search"),
        Binding("escape", "normal_mode", "Cancel"),
        Binding("g", "top", "Top"),
        Binding("G", "bottom", "Bottom"),
        Binding("f", "filter_mode", "Filter"),
        Binding(".", "toggle_hidden", "Hidden"),
        Binding("~", "go_home", "Home"),
    ]
    
    def __init__(self):
        super().__init__()
        self.nav_stack = NavigationStack()
        self.search_active = False
        self.filter_active = False
        self.current_filter = ""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("", id="path-label")
        with Horizontal(id="main-container"):
            yield FileList()
            yield Preview()
            yield SearchPanel()
        yield Input(placeholder="Search files (BFS)... or press 'f' for filter", id="search-box")
        yield Footer()
    
    def on_mount(self):
        file_list = self.query_one(FileList)
        file_list.load_directory(Path.cwd())
        self.update_path_label()
        
        selected = file_list.get_selected()
        if selected:
            self.query_one(Preview).show_preview(selected)
        
        self.query_one(SearchPanel).display = False
        self.query_one("#search-box").display = False
    
    def update_path_label(self):
        file_list = self.query_one(FileList)
        hidden_status = " [dim](hidden: on)[/]" if file_list.show_hidden else ""
        self.query_one("#path-label", Label).update(f"📂 {file_list.current_path}{hidden_status}")
    
    def action_down(self):
        if self.search_active:
            return
        file_list = self.query_one(FileList)
        file_list.move_selection(1)
        self.update_preview()
    
    def action_up(self):
        if self.search_active:
            return
        file_list = self.query_one(FileList)
        file_list.move_selection(-1)
        self.update_preview()
    
    def action_top(self):
        if self.search_active:
            return
        file_list = self.query_one(FileList)
        file_list.selected_idx = 0
        file_list.render_list()
        self.update_preview()
    
    def action_bottom(self):
        if self.search_active:
            return
        file_list = self.query_one(FileList)
        if file_list.files:
            file_list.selected_idx = len(file_list.files) - 1
            file_list.render_list()
            self.update_preview()
    
    def action_enter(self):
        if self.search_active:
            return
        file_list = self.query_one(FileList)
        selected = file_list.get_selected()
        if selected and selected.is_dir():
            self.nav_stack.push(file_list.current_path)
            file_list.load_directory(selected)
            self.update_path_label()
            self.update_preview()
    
    def action_back(self):
        if self.search_active or self.filter_active:
            self.action_normal_mode()
            return
        if not self.nav_stack.is_empty():
            prev_path = self.nav_stack.pop()
            self.query_one(FileList).load_directory(prev_path)
            self.update_path_label()
            self.update_preview()
    
    def action_toggle_hidden(self):
        """Toggle hidden files visibility"""
        if self.search_active or self.filter_active:
            return
        file_list = self.query_one(FileList)
        file_list.toggle_hidden()
        self.update_path_label()
        self.update_preview()
    
    def action_go_home(self):
        """Jump to home directory"""
        if self.search_active or self.filter_active:
            return
        file_list = self.query_one(FileList)
        home = Path.home()
        if file_list.current_path != home:
            self.nav_stack.push(file_list.current_path)
            file_list.load_directory(home)
            self.update_path_label()
            self.update_preview()
    
    def action_search_mode(self):
        self.search_active = True
        self.filter_active = False
        self.query_one(FileList).display = False
        self.query_one(Preview).display = False
        self.query_one(SearchPanel).display = True
        search_box = self.query_one("#search-box", Input)
        search_box.placeholder = "Search files (BFS)..."
        search_box.display = True
        search_box.focus()
    
    def action_filter_mode(self):
        """Filter current directory by extension"""
        self.filter_active = True
        self.search_active = False
        search_box = self.query_one("#search-box", Input)
        search_box.placeholder = "Filter by extension (e.g., .py .txt) or type (img, video, audio)..."
        search_box.display = True
        search_box.focus()
    
    def action_normal_mode(self):
        self.search_active = False
        self.filter_active = False
        self.current_filter = ""
        self.query_one(FileList).display = True
        self.query_one(Preview).display = True
        self.query_one(SearchPanel).display = False
        search_box = self.query_one("#search-box", Input)
        search_box.display = False
        search_box.value = ""
        # Reload without filter
        self.query_one(FileList).load_directory(self.query_one(FileList).current_path)
    
    def update_preview(self):
        file_list = self.query_one(FileList)
        selected = file_list.get_selected()
        if selected:
            self.query_one(Preview).show_preview(selected)
    
    def on_input_changed(self, event: Input.Changed):
        if self.search_active and len(event.value) >= 2:
            self.set_timer(0.4, lambda: self.do_search(event.value))
        elif self.filter_active:
            self.apply_filter(event.value)
    
    def apply_filter(self, filter_text: str):
        """Filter files in current directory"""
        file_list = self.query_one(FileList)
        path = file_list.current_path
        filter_lower = filter_text.lower().strip()
        
        if not filter_lower:
            file_list.load_directory(path)
            return
        
        # Type-based filters
        type_filters = {
            'img': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico', '.svg'],
            'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico', '.svg'],
            'vid': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'],
            'doc': ['.pdf', '.doc', '.docx', '.txt', '.md'],
            'code': ['.py', '.js', '.cpp', '.c', '.java', '.rs', '.go', '.rb', '.php'],
            'archive': ['.zip', '.tar', '.gz', '.bz2', '.7z', '.rar'],
        }
        
        try:
            items = list(path.iterdir())
            
            # Check if it's a type filter
            if filter_lower in type_filters:
                extensions = type_filters[filter_lower]
                filtered = [i for i in items if i.suffix.lower() in extensions]
            # Check if it's an extension filter
            elif filter_lower.startswith('.'):
                filtered = [i for i in items if i.suffix.lower() == filter_lower]
            # Name-based filter
            else:
                filtered = [i for i in items if filter_lower in i.name.lower()]
            
            filtered.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            file_list.files = filtered[:300]
            file_list.selected_idx = 0
            file_list.render_list()
            
        except (PermissionError, OSError):
            pass
    
    def do_search(self, query: str):
        if not self.search_active:
            return
        results = self.bfs_search(self.query_one(FileList).current_path, query.lower())
        self.query_one(SearchPanel).show_results(results, query)
    
    def bfs_search(self, root: Path, query: str, max_results: int = 150) -> list[Path]:
        """BFS search using Queue"""
        search_queue = SearchQueue()
        search_queue.enqueue(root)
        results = []
        visited = set()
        max_dirs = 300
        
        while not search_queue.is_empty() and len(results) < max_results and len(visited) < max_dirs:
            current = search_queue.dequeue()
            
            if current in visited:
                continue
            visited.add(current)
            
            try:
                if current.is_dir():
                    for item in current.iterdir():
                        if query in item.name.lower():
                            results.append(item)
                        if item.is_dir():
                            search_queue.enqueue(item)
            except (PermissionError, OSError):
                continue
        
        return results


if __name__ == "__main__":
    app = FileExplorer()
    app.run()
