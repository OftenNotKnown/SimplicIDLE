import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os, shutil, json, types, io, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
os.makedirs(PROJECTS_DIR, exist_ok=True)

default_settings = {
    "theme": "Dark",
    "font_size": 12,
    "auto_save_on_run": True,
    "default_run_file": "",
    "sdk_path": ""
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return default_settings.copy()
    return default_settings.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

class RedirectStdout(io.StringIO):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
    def write(self, s):
        self.widget.insert(tk.END, s)
        self.widget.see(tk.END)
    def flush(self): pass

class AndroidStudioLikeIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Android IDE")
        self.root.geometry("1300x750")

        self.settings = load_settings()
        self.current_file = None
        self.project_root = PROJECTS_DIR

        self.create_topbar()
        self.create_main_layout()
        self.create_bottom_console()
        self.create_context_menu()
        self.apply_settings()

    def create_topbar(self):
        topbar = tk.Frame(self.root, height=40)
        topbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(topbar, text="📂 Open Project", command=self.open_project).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(topbar, text="🆕 Create Project", command=self.create_project).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(topbar, text="💾 Save", command=self.save_file).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(topbar, text="▶ Run", command=self.run_code).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(topbar, text="📦 Build APK", command=self.build_apk).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(topbar, text="⚙ Settings", command=self.open_settings).pack(side=tk.RIGHT, padx=5, pady=5)

        self.mode_var = tk.StringVar(value="Python")
        ttk.Combobox(topbar, textvariable=self.mode_var, values=["Python", "Kotlin/XML"], width=15).pack(side=tk.RIGHT, padx=5)

    def create_main_layout(self):
        main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=4)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.project_tree = ttk.Treeview(main_frame)
        self.project_tree.heading("#0", text="Project", anchor=tk.W)
        self.project_tree.bind("<Button-3>", self.show_context_menu)
        self.project_tree.bind("<Double-1>", self.open_file_in_editor)
        main_frame.add(self.project_tree, width=250)

        editor_frame = tk.Frame(main_frame)
        self.editor = tk.Text(editor_frame, wrap="none")
        self.editor.pack(fill=tk.BOTH, expand=True)
        main_frame.add(editor_frame, width=600)

        self.preview_frame = tk.LabelFrame(main_frame, text="Preview")
        self.preview_frame.pack_propagate(False)
        self.preview_content = tk.Frame(self.preview_frame)
        self.preview_content.pack(fill=tk.BOTH, expand=True)
        main_frame.add(self.preview_frame, width=400)

    def create_bottom_console(self):
        console_frame = tk.Frame(self.root, height=120)
        console_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(console_frame, text="Console Output:").pack(anchor="w")
        self.console = tk.Text(console_frame, height=6)
        self.console.pack(fill=tk.BOTH, expand=True)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Create File", command=lambda: self.create_item(True))
        self.context_menu.add_command(label="Create Folder", command=lambda: self.create_item(False))
        self.context_menu.add_command(label="Delete", command=self.delete_item)

    def show_context_menu(self, event):
        item = self.project_tree.identify_row(event.y)
        if item:
            self.project_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def open_project(self):
        folder = filedialog.askdirectory(initialdir=PROJECTS_DIR)
        if folder:
            self.project_root = folder
            self.load_project()

    def create_project(self):
        name = simpledialog.askstring("Create Project", "Enter project name:")
        if name:
            new_path = os.path.join(PROJECTS_DIR, name)
            os.makedirs(new_path, exist_ok=True)
            self.project_root = new_path
            self.load_project()

    def load_project(self):
        self.project_tree.delete(*self.project_tree.get_children())
        if os.path.isdir(self.project_root):
            self.insert_tree_nodes("", self.project_root)

    def insert_tree_nodes(self, parent, path):
        node = self.project_tree.insert(parent, "end", text=os.path.basename(path), open=True)
        if os.path.isdir(path):
            for item in sorted(os.listdir(path)):
                self.insert_tree_nodes(node, os.path.join(path, item))

    def get_path(self, item):
        parts = []
        while item:
            parts.insert(0, self.project_tree.item(item, "text"))
            item = self.project_tree.parent(item)
        return os.path.join(self.project_root, *parts[1:])  # skip root name

    def create_item(self, is_file):
        selected = self.project_tree.selection()
        if not selected: return
        parent_path = self.get_path(selected[0])
        if not os.path.isdir(parent_path):
            parent_path = os.path.dirname(parent_path)
        name = simpledialog.askstring("Create", "Enter name:")
        if not name: return
        new_path = os.path.join(parent_path, name + (".py" if is_file else ""))
        if is_file:
            open(new_path, "w").close()
        else:
            os.makedirs(new_path, exist_ok=True)
        self.load_project()

    def delete_item(self):
        selected = self.project_tree.selection()
        if not selected: return
        path = self.get_path(selected[0])
        if messagebox.askyesno("Delete", f"Delete {path}?"):
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)
            self.load_project()

    def open_file_in_editor(self, event):
        selected = self.project_tree.selection()
        if not selected: return
        path = self.get_path(selected[0])
        if os.path.isfile(path) and path.endswith(".py"):
            self.current_file = path
            with open(path, "r", encoding="utf-8") as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", f.read())

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))

    def run_code(self):
        if not self.current_file:
            default = self.settings.get("default_run_file", "")
            if default and os.path.exists(default):
                self.current_file = default
            else:
                messagebox.showerror("Error", "No file opened and no default run file set.")
                return

        if self.settings.get("auto_save_on_run", True):
            self.save_file()

        self.console.delete("1.0", tk.END)
        for w in self.preview_content.winfo_children():
            w.destroy()

        stdout_redirect = RedirectStdout(self.console)
        old_stdout = sys.stdout
        sys.stdout = stdout_redirect

        try:
            code = open(self.current_file, "r", encoding="utf-8").read()

            def custom_tk(): return self.preview_content
            fake_tk = types.SimpleNamespace(
                Tk=custom_tk,
                Frame=lambda *a, **k: tk.Frame(self.preview_content, *a, **k),
                Button=lambda *a, **k: tk.Button(self.preview_content, *a, **k),
                Label=lambda *a, **k: tk.Label(self.preview_content, *a, **k),
                Text=lambda *a, **k: tk.Text(self.preview_content, *a, **k),
                Entry=lambda *a, **k: tk.Entry(self.preview_content, *a, **k)
            )

            exec(code, {"__builtins__": __builtins__, "__name__": "__main__", "tk": fake_tk})
            print("✅ Code executed successfully!")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            sys.stdout = old_stdout

    def build_apk(self):
        if not self.current_file:
            messagebox.showerror("Error", "Open a project first.")
            return
        project_dir = os.path.dirname(self.current_file)
        gradle_dir = os.path.join(project_dir, "AndroidProject")
        os.makedirs(os.path.join(gradle_dir, "app", "src", "main", "java", "com", "example", "app"), exist_ok=True)
        os.makedirs(os.path.join(gradle_dir, "app", "src", "main", "res", "layout"), exist_ok=True)

        manifest = """<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">
    <application android:label="MyApp">
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>"""
        with open(os.path.join(gradle_dir, "app", "src", "main", "AndroidManifest.xml"), "w") as f:
            f.write(manifest)

        activity = """package com.example.app;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import com.chaquo.python.Python;
import com.chaquo.python.PyObject;
import android.widget.TextView;
public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Python py = Python.getInstance();
        PyObject pyObj = py.getModule("main").callAttr("run");
        TextView tv = findViewById(R.id.myText);
        tv.setText(pyObj.toString());
    }
}"""
        with open(os.path.join(gradle_dir, "app", "src", "main", "java", "com", "example", "app", "MainActivity.java"), "w") as f:
            f.write(activity)

        layout = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <Button android:id="@+id/myButton" android:text="Click Me"
        android:layout_width="wrap_content" android:layout_height="wrap_content"/>
    <TextView android:id="@+id/myText" android:text="Waiting..."
        android:layout_width="wrap_content" android:layout_height="wrap_content"/>
</LinearLayout>"""
        with open(os.path.join(gradle_dir, "app", "src", "main", "res", "layout", "activity_main.xml"), "w") as f:
            f.write(layout)

        messagebox.showinfo("Build APK", f"Gradle project created at:\n{gradle_dir}")

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("350x400")

        tk.Label(win, text="⚙ Settings", font=("Arial", 14)).pack(pady=10)

        theme_var = tk.StringVar(value=self.settings["theme"])
        tk.Label(win, text="Theme:").pack(anchor="w", padx=20)
        tk.OptionMenu(win, theme_var, "Dark", "Light").pack(anchor="w", padx=20)

        font_size_var = tk.IntVar(value=self.settings["font_size"])
        tk.Label(win, text="Font Size:").pack(anchor="w", padx=20)
        tk.Spinbox(win, from_=8, to=30, textvariable=font_size_var).pack(anchor="w", padx=20)

        auto_save_var = tk.BooleanVar(value=self.settings["auto_save_on_run"])
        tk.Checkbutton(win, text="Auto-Save on Run", variable=auto_save_var).pack(anchor="w", padx=20)

        def apply():
            self.settings.update({
                "theme": theme_var.get(),
                "font_size": font_size_var.get(),
                "auto_save_on_run": auto_save_var.get()
            })
            save_settings(self.settings)
            self.apply_settings()
            win.destroy()

        tk.Button(win, text="💾 Save", command=apply).pack(pady=20)

    def apply_settings(self):
        self.editor.config(font=("Consolas", self.settings["font_size"]))
        self.console.config(font=("Consolas", self.settings["font_size"] - 2))
        if self.settings["theme"] == "Light":
            self.set_light_theme()
        else:
            self.set_dark_theme()

    def set_dark_theme(self):
        colors = {"bg": "#1E1E1E", "fg": "white"}
        self.root.config(bg=colors["bg"])
        self.editor.config(bg=colors["bg"], fg=colors["fg"], insertbackground="white")
        self.console.config(bg=colors["bg"], fg=colors["fg"])
        self.preview_frame.config(bg="#252526", fg="white")
        self.preview_content.config(bg=colors["bg"])
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=colors["bg"], fieldbackground=colors["bg"], foreground="white")

    def set_light_theme(self):
        colors = {"bg": "white", "fg": "black"}
        self.root.config(bg=colors["bg"])
        self.editor.config(bg=colors["bg"], fg=colors["fg"], insertbackground="black")
        self.console.config(bg=colors["bg"], fg=colors["fg"])
        self.preview_frame.config(bg="#E0E0E0", fg="black")
        self.preview_content.config(bg=colors["bg"])
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=colors["bg"], fieldbackground=colors["bg"], foreground="black")

if __name__ == "__main__":
    root = tk.Tk()
    app = AndroidStudioLikeIDE(root)
    root.mainloop()
