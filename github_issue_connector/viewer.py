"""A small desktop viewer; database reads are local and read-only."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
import webbrowser

from .database import DEFAULT_DB_PATH, read_repository_counts, read_saved_issues
from .errors import ConnectorError


# Shared colors keep ttk widgets and the plain Tk detail panel in the same theme.
COLORS = {
    "canvas": "#0d1117",
    "header": "#010409",
    "surface": "#161b22",
    "button": "#21262d",
    "border": "#30363d",
    "text": "#e6edf3",
    "muted": "#8b949e",
    "link": "#58a6ff",
    "selected": "#1c2d41",
    "green": "#238636",
    "green_hover": "#2ea043",
}


def apply_theme(root: tk.Tk | tk.Toplevel) -> None:
    """Apply a GitHub-inspired dark palette to this desktop's Tk widgets."""
    root.configure(background=COLORS["canvas"])
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=COLORS["canvas"])
    style.configure("Header.TFrame", background=COLORS["header"])
    style.configure(
        "Card.TFrame", background=COLORS["surface"], borderwidth=1, relief="solid",
        bordercolor=COLORS["border"], lightcolor=COLORS["border"], darkcolor=COLORS["border"],
    )
    style.configure(
        "TLabel", background=COLORS["canvas"], foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Title.TLabel", background=COLORS["header"], font=("Segoe UI", 20, "bold")
    )
    style.configure("Heading.TLabel", font=("Segoe UI", 13, "bold"))
    style.configure("Repository.TLabel", foreground=COLORS["link"], font=("Segoe UI", 16, "bold"))
    style.configure("Muted.TLabel", foreground=COLORS["muted"])
    style.configure("Card.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
    style.configure(
        "Badge.TLabel", background=COLORS["button"], foreground=COLORS["muted"],
        font=("Segoe UI", 9, "bold"), padding=(10, 5),
    )
    style.configure(
        "TButton", padding=(12, 7), font=("Segoe UI", 10),
        background=COLORS["button"], foreground=COLORS["text"],
        bordercolor=COLORS["border"], lightcolor=COLORS["border"],
        darkcolor=COLORS["border"], focuscolor=COLORS["link"], borderwidth=1,
    )
    style.map(
        "TButton", background=[("disabled", COLORS["surface"]), ("active", COLORS["border"])],
        foreground=[("disabled", "#6e7681")], bordercolor=[("focus", COLORS["link"])],
    )
    style.configure(
        "Accent.TButton", background=COLORS["green"], foreground="white",
        bordercolor=COLORS["green_hover"], lightcolor=COLORS["green"],
    )
    style.map(
        "Accent.TButton",
        background=[("disabled", "#1b4428"), ("active", COLORS["green_hover"])],
        foreground=[("disabled", COLORS["muted"]), ("!disabled", "white")],
        bordercolor=[("disabled", "#1b4428"), ("focus", COLORS["link"]), ("!disabled", COLORS["green_hover"])],
        lightcolor=[("disabled", "#1b4428"), ("!disabled", COLORS["green"])],
        darkcolor=[("disabled", "#1b4428"), ("!disabled", COLORS["green"])],
    )
    for widget in ("TEntry", "TCombobox"):
        style.configure(
            widget, fieldbackground=COLORS["canvas"], foreground=COLORS["text"],
            background=COLORS["button"], insertcolor=COLORS["text"],
            bordercolor=COLORS["border"], lightcolor=COLORS["border"],
            darkcolor=COLORS["border"], arrowcolor=COLORS["muted"],
            selectbackground="#1f6feb", selectforeground="white", padding=(8, 6),
        )
        style.map(
            widget, fieldbackground=[("readonly", COLORS["canvas"])],
            foreground=[("readonly", COLORS["text"])],
            bordercolor=[("focus", COLORS["link"])],
            lightcolor=[("focus", COLORS["link"])], darkcolor=[("focus", COLORS["link"])],
        )
    root.option_add("*TCombobox*Listbox.background", COLORS["surface"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", "#1f6feb")
    root.option_add("*TCombobox*Listbox.selectForeground", "white")
    style.configure("TPanedwindow", background=COLORS["canvas"])
    style.configure(
        "Vertical.TScrollbar", background=COLORS["border"], troughcolor=COLORS["canvas"],
        arrowcolor=COLORS["muted"], bordercolor=COLORS["canvas"],
        lightcolor=COLORS["border"], darkcolor=COLORS["border"],
    )
    style.map("Vertical.TScrollbar", background=[("active", "#484f58")])
    style.configure(
        "Treeview", rowheight=34, font=("Segoe UI", 10),
        background=COLORS["canvas"], fieldbackground=COLORS["canvas"],
        foreground=COLORS["text"], bordercolor=COLORS["border"],
        lightcolor=COLORS["border"], darkcolor=COLORS["border"],
    )
    style.configure(
        "Treeview.Heading", font=("Segoe UI", 9, "bold"), padding=(10, 9),
        background=COLORS["surface"], foreground=COLORS["muted"],
        bordercolor=COLORS["border"], lightcolor=COLORS["border"],
        darkcolor=COLORS["border"], relief="flat",
    )
    style.map("Treeview.Heading", background=[("active", COLORS["button"])])
    style.map(
        "Treeview", background=[("selected", COLORS["selected"])],
        foreground=[("selected", "white")],
    )
    style.configure("Repositories.Treeview", foreground=COLORS["link"])


def find_databases(directory: Path) -> list[str]:
    """Find SQLite filenames directly in one directory, without opening them."""
    return sorted(
        str(path.absolute())
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}
    )


class IssueViewer:
    """Keep selection state and Tk event handlers together in one window."""

    def __init__(self, root: tk.Tk | tk.Toplevel, db_path: str | Path | None = None) -> None:
        self.root = root
        self.loaded_path = None
        self.database_summary = ""
        self.repository = None
        self.issues = []
        self.selected_issue = None
        self.db_path = tk.StringVar(root)
        self.search = tk.StringVar(root)
        self.repo_summary = tk.StringVar(root, value="Repositories")
        self.heading = tk.StringVar(root, value="Choose a repository")
        self.issue_summary = tk.StringVar(root, value="All saved issues appear here.")
        self.status = tk.StringVar(root)

        root.title("GitHub Issue Library")
        root.geometry("1180x780")
        root.minsize(900, 640)
        apply_theme(root)

        page = ttk.Frame(root, padding=16)
        page.pack(fill="both", expand=True)
        page.columnconfigure(0, weight=1)
        page.rowconfigure(3, weight=1)
        header = ttk.Frame(page, style="Header.TFrame", padding=(16, 8))
        header.grid(row=0, sticky="ew")
        icon = tk.Canvas(
            header, width=30, height=30, background=COLORS["header"], highlightthickness=0
        )
        icon.create_oval(4, 4, 26, 26, outline=COLORS["green_hover"], width=2)
        icon.create_oval(13, 13, 17, 17, fill=COLORS["green_hover"], outline="")
        icon.pack(side="left", padx=(0, 12))
        ttk.Label(header, text="Issue Library", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="LOCAL SNAPSHOTS", style="Badge.TLabel").pack(side="right")
        ttk.Label(
            page, text="Explore your imported GitHub issues.", style="Muted.TLabel"
        ).grid(row=1, sticky="w", pady=(8, 12))

        toolbar = ttk.Frame(page, style="Card.TFrame", padding=(12, 8))
        toolbar.grid(row=2, sticky="ew", pady=(0, 12))
        ttk.Label(toolbar, text="Database", style="Card.TLabel").pack(side="left", padx=(0, 12))
        self.database_picker = ttk.Combobox(toolbar, textvariable=self.db_path, state="readonly")
        self.database_picker.pack(side="left", fill="x", expand=True)
        self.database_picker.bind("<<ComboboxSelected>>", self.load_database)
        self.browse_button = ttk.Button(toolbar, text="Browse…", command=self.browse_database)
        self.browse_button.pack(side="left", padx=8)
        self.refresh_button = ttk.Button(toolbar, text="Refresh", command=self.refresh)
        self.refresh_button.pack(side="left")

        panes = ttk.Panedwindow(page, orient="horizontal")
        panes.grid(row=3, sticky="nsew")
        sidebar = ttk.Frame(panes, padding=(0, 0, 16, 0), width=300)
        content = ttk.Frame(panes, padding=(16, 0, 0, 0))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(3, weight=1)
        panes.add(sidebar, weight=1)
        panes.add(content, weight=3)
        ttk.Label(
            sidebar, textvariable=self.repo_summary, style="Heading.TLabel"
        ).pack(anchor="w", pady=(0, 12))
        self.repositories = self.make_table(sidebar, ("repository", "count"))
        self.repositories.configure(style="Repositories.Treeview")
        self.repositories.heading("repository", text="Repository")
        self.repositories.heading("count", text="Saved")
        self.repositories.column("repository", width=235, minwidth=100)
        self.repositories.column("count", width=60, minwidth=55, stretch=False, anchor="center")
        self.repositories.bind("<<TreeviewSelect>>", self.select_repository)

        ttk.Label(content, textvariable=self.heading, style="Repository.TLabel").grid(row=0, sticky="w")
        ttk.Label(
            content, textvariable=self.issue_summary, style="Muted.TLabel"
        ).grid(row=1, sticky="w", pady=(4, 12))
        search_row = ttk.Frame(content)
        search_row.grid(row=2, sticky="ew", pady=(0, 8))
        ttk.Label(search_row, text="Search title or #number").pack(side="left", padx=(0, 12))
        ttk.Entry(search_row, textvariable=self.search).pack(side="left", fill="x", expand=True)
        ttk.Button(
            search_row, text="Clear", command=lambda: self.search.set("")
        ).pack(side="left", padx=(8, 0))
        table_area = ttk.Frame(content)
        table_area.grid(row=3, sticky="nsew")
        self.issue_table = self.make_table(table_area, ("number", "title"))
        self.issue_table.heading("number", text="Issue")
        self.issue_table.heading("title", text="Title")
        self.issue_table.column("number", width=85, minwidth=75, stretch=False)
        self.issue_table.column("title", width=560, minwidth=180)
        self.issue_table.bind("<<TreeviewSelect>>", self.select_issue)
        self.issue_table.bind("<Double-1>", self.open_issue)
        self.issue_table.bind("<Return>", self.open_issue)

        ttk.Label(
            content, text="Selected issue", style="Heading.TLabel"
        ).grid(row=4, sticky="w", pady=(12, 6))
        detail_frame = ttk.Frame(content, style="Card.TFrame", padding=1)
        detail_frame.grid(row=5, sticky="ew")
        self.details = tk.Text(
            detail_frame, height=4, wrap="word", font=("Segoe UI", 10),
            background=COLORS["surface"], foreground=COLORS["text"],
            selectbackground="#1f6feb", selectforeground="white",
            relief="flat", padx=12, pady=10,
        )
        detail_scroll = ttk.Scrollbar(detail_frame, orient="vertical", command=self.details.yview)
        self.details.configure(yscrollcommand=detail_scroll.set)
        self.details.tag_configure("url", foreground=COLORS["link"])
        detail_scroll.pack(side="right", fill="y")
        self.details.pack(fill="x")
        actions = ttk.Frame(content)
        actions.grid(row=6, sticky="ew", pady=(10, 0))
        self.open_button = ttk.Button(
            actions, text="Open on GitHub ↗", style="Accent.TButton", command=self.open_issue
        )
        self.open_button.pack(side="left")
        self.copy_button = ttk.Button(actions, text="Copy URL", command=self.copy_url)
        self.copy_button.pack(side="left", padx=8)
        ttk.Label(
            page, text="Saved snapshots may include issues that have since closed.",
            style="Muted.TLabel",
        ).grid(row=4, sticky="w", pady=(10, 2))
        ttk.Label(
            page, textvariable=self.status, style="Muted.TLabel", wraplength=840
        ).grid(row=5, sticky="w")

        self.search.trace_add("write", self.filter_issues)
        self.clear_details()
        if db_path is not None:
            self.db_path.set(str(Path(db_path).absolute()))
        self.refresh()

    @staticmethod
    def make_table(parent, columns):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        table = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        table.pack(fill="both", expand=True)
        return table

    def refresh(self):
        try:
            paths = find_databases(Path.cwd())
        except OSError as error:
            self.status.set(f"Could not list database files: {error}")
            return
        selected = self.db_path.get()
        if not selected:
            default = str(Path(DEFAULT_DB_PATH).absolute())
            selected = default if default in paths else (paths[0] if paths else "")
            self.db_path.set(selected)
        if selected and selected not in paths:
            paths.append(selected)
        self.database_picker.configure(values=paths)
        self.load_database()

    def browse_database(self):
        selected = filedialog.askopenfilename(
            parent=self.root,
            title="Choose an issue database",
            initialdir=str(
                Path(self.db_path.get()).parent if self.db_path.get() else Path.cwd()
            ),
            filetypes=[("SQLite databases", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")],
        )
        if selected:
            self.db_path.set(str(Path(selected).absolute()))
            self.refresh()

    def load_database(self, _event=None):
        selected = self.db_path.get()
        previous_repo = self.repository if selected == self.loaded_path else None
        self.loaded_path = selected
        self.repository = None
        self.repositories.delete(*self.repositories.get_children())
        self.repo_summary.set("Repositories")
        self.heading.set("Choose a repository")
        self.issues = []
        self.search.set("")
        if not selected:
            self.status.set("Choose a database with Browse to get started.")
            return
        try:
            if not Path(selected).is_file():
                self.status.set(f"Database file does not exist: {selected}")
                return
            repositories = read_repository_counts(selected)
        except (ConnectorError, OSError) as error:
            self.status.set(str(error))
            return
        for item in repositories:
            self.repositories.insert(
                "", "end", iid=item["repository"], values=(item["repository"], item["count"])
            )
        self.repo_summary.set(f"Repositories ({len(repositories)})")
        total = sum(item["count"] for item in repositories)
        self.database_summary = (
            f"Read only  •  {total} saved issues in this database"
            if repositories else "No saved repositories in this database."
        )
        self.status.set(self.database_summary)
        if repositories:
            target = (
                previous_repo if previous_repo and self.repositories.exists(previous_repo)
                else repositories[0]["repository"]
            )
            self.repositories.selection_set(target)
            self.repositories.focus(target)
            self.select_repository()

    def select_repository(self, _event=None):
        selection = self.repositories.selection()
        if not selection:
            return
        self.repository = selection[0]
        self.heading.set(self.repository)
        self.issues = []
        try:
            self.issues = read_saved_issues(self.repository, self.loaded_path)
            self.status.set(self.database_summary)
        except ConnectorError as error:
            self.status.set(str(error))
        self.search.set("")

    def filter_issues(self, *_args):
        self.issue_table.delete(*self.issue_table.get_children())
        self.clear_details()
        query = self.search.get().strip().casefold()
        for index, issue in enumerate(self.issues):
            if query in f"#{issue['issue_number']} {issue['title']}".casefold():
                self.issue_table.insert(
                    "", "end", iid=str(index),
                    values=(f"#{issue['issue_number']}", issue["title"]),
                )
        shown = len(self.issue_table.get_children())
        self.issue_summary.set(
            f"{shown} of {len(self.issues)} saved issues"
            if query else f"{len(self.issues)} saved issues"
        )
        if query and not shown:
            self.issue_summary.set("No issues match your search.")

    def clear_details(self):
        self.selected_issue = None
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", "Select an issue to see its full title and URL.")
        self.details.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")

    def select_issue(self, _event=None):
        selection = self.issue_table.selection()
        if not selection:
            self.clear_details()
            return
        self.selected_issue = self.issues[int(selection[0])]
        issue = self.selected_issue
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", f"#{issue['issue_number']}  {issue['title']}\n\n{issue['url']}")
        self.details.tag_add("url", "end-1c linestart", "end-1c")
        self.details.configure(state="disabled")
        self.open_button.configure(state="normal")
        self.copy_button.configure(state="normal")

    def open_issue(self, _event=None):
        if self.selected_issue:
            url = self.selected_issue["url"]
            # External files can contain arbitrary text; only web URLs are opened.
            if not url.startswith(("https://", "http://")):
                self.status.set("This issue does not have an HTTP or HTTPS URL.")
                return
            try:
                opened = webbrowser.open(url, new=2)
            except webbrowser.Error as error:
                self.status.set(f"Could not open the browser: {error}")
                return
            self.status.set(
                "Opened issue in your browser." if opened
                else "Could not open the browser. Use Copy URL instead."
            )

    def copy_url(self):
        if self.selected_issue:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.selected_issue["url"])
            self.status.set("Issue URL copied.")


def run_viewer(db_path: str | Path | None = None) -> None:
    root = tk.Tk()
    IssueViewer(root, db_path)
    root.mainloop()
