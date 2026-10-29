"""待办清单 —— 桌面版（Python + Tkinter，无需浏览器、不占端口）"""

import json
import sys
import uuid
from datetime import date
from pathlib import Path

import tkinter as tk
from tkinter import font as tkfont

# ---------- 外观 ----------
BG = "#eef2ff"
CARD = "#ffffff"
TEXT = "#1f2937"
MUTED = "#9ca3af"
LINE = "#eef0f4"
ACCENT = "#6366f1"
ACCENT_DARK = "#4f46e5"
DANGER = "#ef4444"
FONT = "Microsoft YaHei UI"

STORAGE = Path.home() / ".vibecoding_todos.json"


def enable_dpi_awareness():
    """让界面在高分屏上不发虚（Windows 可选）。"""
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


class TodoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.todos = self.load()
        self.current_filter = "all"
        self.filter_buttons = {}

        self._build_ui()
        self.render()

    # ---------- 数据 ----------

    def load(self):
        try:
            data = json.loads(STORAGE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [
                    {"id": str(t.get("id") or uuid.uuid4().hex), "text": str(t["text"]), "done": bool(t.get("done"))}
                    for t in data
                    if isinstance(t, dict) and t.get("text")
                ]
        except (OSError, ValueError, KeyError):
            pass
        return []

    def save(self):
        try:
            STORAGE.write_text(json.dumps(self.todos, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            print("保存失败：", exc, file=sys.stderr)

    # ---------- 界面 ----------

    def _build_ui(self):
        self.root.title("待办清单")
        self.root.configure(bg=BG)
        self.root.minsize(400, 520)

        w, h = 480, 640
        x = (self.root.winfo_screenwidth() - w) // 2
        y = max(0, (self.root.winfo_screenheight() - h) // 2 - 30)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        outer = tk.Frame(self.root, bg=BG, padx=24, pady=24)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=CARD, padx=28, pady=24)
        card.pack(fill="both", expand=True)

        # 标题
        tk.Label(card, text="待办清单", bg=CARD, fg=TEXT, font=(FONT, 20, "bold")).pack(anchor="w")
        tk.Label(
            card,
            text=date.today().strftime("%Y 年 %m 月 %d 日"),
            bg=CARD,
            fg=MUTED,
            font=(FONT, 9),
        ).pack(anchor="w", pady=(2, 0))

        # 输入行
        form = tk.Frame(card, bg=CARD)
        form.pack(fill="x", pady=(20, 16))

        border = tk.Frame(form, bg="#e3e5ec", padx=1, pady=1)
        border.pack(side="left", fill="x", expand=True)
        inner = tk.Frame(border, bg=CARD)
        inner.pack(fill="both", expand=True)
        self.entry = tk.Entry(
            inner,
            bd=0,
            relief="flat",
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            font=(FONT, 11),
        )
        self.entry.pack(fill="both", expand=True, padx=12, pady=9)
        self.entry.bind("<Return>", lambda e: self.add_todo())
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)
        self._set_placeholder()

        add_btn = tk.Button(
            form,
            text="添加",
            command=self.add_todo,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_DARK,
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=20,
            pady=9,
            cursor="hand2",
            font=(FONT, 10, "bold"),
        )
        add_btn.pack(side="left", padx=(10, 0))

        # 筛选
        filters = tk.Frame(card, bg=CARD)
        filters.pack(fill="x")
        for key, label in (("all", "全部"), ("active", "未完成"), ("completed", "已完成")):
            btn = tk.Button(
                filters,
                text=label,
                command=lambda k=key: self.set_filter(k),
                bg=CARD,
                fg=MUTED,
                activebackground=CARD,
                activeforeground=ACCENT_DARK,
                bd=0,
                relief="flat",
                padx=10,
                pady=4,
                cursor="hand2",
                font=(FONT, 9),
            )
            btn.pack(side="left")
            self.filter_buttons[key] = btn

        # 列表（可滚动）
        list_wrap = tk.Frame(card, bg=CARD)
        list_wrap.pack(fill="both", expand=True, pady=(8, 0))

        self.canvas = tk.Canvas(list_wrap, bg=CARD, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(list_wrap, orient="vertical", command=self.canvas.yview, width=10)
        self.list_frame = tk.Frame(self.canvas, bg=CARD)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # 鼠标滚轮
        self.canvas.bind("<Enter>", lambda e: self._bind_wheel(True))
        self.canvas.bind("<Leave>", lambda e: self._bind_wheel(False))

        # 底部
        tk.Frame(card, bg=LINE, height=1).pack(fill="x", pady=(12, 0))
        footer = tk.Frame(card, bg=CARD)
        footer.pack(fill="x", pady=(10, 0))

        self.summary = tk.Label(footer, text="共 0 项", bg=CARD, fg=MUTED, font=(FONT, 9))
        self.summary.pack(side="left")

        self.clear_btn = tk.Button(
            footer,
            text="清除已完成",
            command=self.clear_completed,
            bg=CARD,
            fg=MUTED,
            activebackground=CARD,
            activeforeground=DANGER,
            bd=0,
            relief="flat",
            cursor="hand2",
            font=(FONT, 9),
        )
        self.clear_btn.pack(side="right")

        self.text_labels = []

    # ---------- 占位符 ----------

    def _set_placeholder(self):
        if not self.entry.get():
            self.entry.insert(0, "今天要做什么？")
            self.entry.configure(fg=MUTED)
            self._placeholder_active = True
        else:
            self._placeholder_active = False

    def _clear_placeholder(self, _event=None):
        if getattr(self, "_placeholder_active", False):
            self.entry.delete(0, "end")
            self.entry.configure(fg=TEXT)
            self._placeholder_active = False

    def _restore_placeholder(self, _event=None):
        if not self.entry.get().strip():
            self.entry.delete(0, "end")
            self._set_placeholder()

    def _entry_text(self):
        if getattr(self, "_placeholder_active", False):
            return ""
        return self.entry.get().strip()

    # ---------- 操作 ----------

    def add_todo(self):
        text = self._entry_text()
        if not text:
            self.entry.focus_set()
            return
        self.todos.insert(0, {"id": uuid.uuid4().hex, "text": text, "done": False})
        self.save()
        self.entry.delete(0, "end")
        self._placeholder_active = False
        self.render()

    def toggle_todo(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["done"] = not todo["done"]
                break
        self.save()
        self.render()

    def delete_todo(self, todo_id):
        self.todos = [t for t in self.todos if t["id"] != todo_id]
        self.save()
        self.render()

    def clear_completed(self):
        if not any(t["done"] for t in self.todos):
            return
        self.todos = [t for t in self.todos if not t["done"]]
        self.save()
        self.render()

    def set_filter(self, key):
        self.current_filter = key
        self.render()

    # ---------- 渲染 ----------

    def visible_todos(self):
        if self.current_filter == "active":
            return [t for t in self.todos if not t["done"]]
        if self.current_filter == "completed":
            return [t for t in self.todos if t["done"]]
        return self.todos

    def _on_canvas_resize(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)
        for label in self.text_labels:
            label.configure(wraplength=max(120, event.width - 80))

    def _bind_wheel(self, active):
        if active:
            self.canvas.bind_all("<MouseWheel>", self._on_wheel)
        else:
            self.canvas.unbind_all("<MouseWheel>")

    def _on_wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _mk_check(self, parent, done, todo_id):
        size = 22
        canvas = tk.Canvas(parent, width=size, height=size, bg=CARD, highlightthickness=0, cursor="hand2")
        if done:
            canvas.create_oval(1, 1, size - 2, size - 2, fill=ACCENT, outline=ACCENT)
            canvas.create_text(size / 2, size / 2, text="✓", fill="white", font=(FONT, 10, "bold"))
        else:
            canvas.create_oval(2, 2, size - 3, size - 3, outline="#d1d5db", width=2)
        canvas.bind("<Button-1>", lambda e: self.toggle_todo(todo_id))
        return canvas

    def _mk_delete(self, parent, todo_id):
        label = tk.Label(
            parent,
            text="×",
            bg=CARD,
            fg="#d7dbe3",
            font=(FONT, 13),
            cursor="hand2",
            padx=6,
        )
        label.bind("<Button-1>", lambda e: self.delete_todo(todo_id))
        label.bind("<Enter>", lambda e: label.configure(fg=DANGER))
        label.bind("<Leave>", lambda e: label.configure(fg="#d7dbe3"))
        return label

    def render(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.text_labels = []

        visible = self.visible_todos()

        if not visible:
            msg = "这里空空如也，添加一条待办吧 ✨" if not self.todos else "没有符合当前筛选的待办"
            tk.Label(self.list_frame, text=msg, bg=CARD, fg=MUTED, font=(FONT, 10)).pack(pady=40)
        else:
            wrap = max(120, self.canvas.winfo_width() - 80)
            for todo in visible:
                row = tk.Frame(self.list_frame, bg=CARD)
                row.pack(fill="x")
                row.columnconfigure(0, weight=1)

                content = tk.Frame(row, bg=CARD)
                content.grid(row=0, column=0, sticky="ew", pady=10)
                content.columnconfigure(1, weight=1)

                self._mk_check(content, todo["done"], todo["id"]).grid(row=0, column=0, padx=(0, 12))

                text_font = tkfont.Font(family=FONT, size=11, overstrike=todo["done"])
                text_label = tk.Label(
                    content,
                    text=todo["text"],
                    bg=CARD,
                    fg=MUTED if todo["done"] else TEXT,
                    font=text_font,
                    anchor="w",
                    justify="left",
                    wraplength=wrap,
                )
                text_label.grid(row=0, column=1, sticky="ew")
                self.text_labels.append(text_label)

                self._mk_delete(content, todo["id"]).grid(row=0, column=2, padx=(8, 0))

                tk.Frame(row, bg=LINE, height=1).grid(row=1, column=0, sticky="ew")

        counts = {
            "all": len(self.todos),
            "active": sum(1 for t in self.todos if not t["done"]),
            "completed": sum(1 for t in self.todos if t["done"]),
        }
        labels = {"all": "全部", "active": "未完成", "completed": "已完成"}
        for key, btn in self.filter_buttons.items():
            active = key == self.current_filter
            btn.configure(
                text=f"{labels[key]} {counts[key]}",
                fg=ACCENT_DARK if active else MUTED,
                font=(FONT, 9, "bold") if active else (FONT, 9),
                bg=CARD,
            )

        self.summary.configure(text=f"共 {len(self.todos)} 项 · 已完成 {counts['completed']} 项")
        self.clear_btn.configure(state="normal" if counts["completed"] else "disabled")


def main():
    enable_dpi_awareness()
    root = tk.Tk()
    TodoApp(root)

    if "--smoke" in sys.argv:
        root.update_idletasks()
        root.update()
        root.destroy()
        print("SMOKE OK")
        return

    root.mainloop()


if __name__ == "__main__":
    main()
