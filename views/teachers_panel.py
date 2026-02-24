"""
views/teachers_panel.py - Teacher Management CRUD panel (Admin only)
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from utils.ui_helpers import (
    scrollable_treeview, make_entry, make_label,
    confirm_delete, show_error, show_success, show_info
)


class TeachersPanel(tk.Frame):
    def __init__(self, parent, teacher_svc, subject_svc):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.teacher_svc = teacher_svc
        self.subject_svc = subject_svc
        self._selected_id = None
        self.pack(fill="both", expand=True)
        self._build()
        self._load()

    def _build(self):
        toolbar = tk.Frame(self, bg=COLORS["bg_medium"], pady=10)
        toolbar.pack(fill="x", padx=16)
        make_label(toolbar, "Teacher Management", "subheading").pack(side="left")
        for text, bg, cmd in [
            ("+ Add Teacher", COLORS["primary"], self._open_add),
            ("Edit", COLORS["secondary"], self._open_edit),
            ("Delete", COLORS["danger"], self._do_delete),
        ]:
            tk.Button(toolbar, text=text, font=FONTS["body_bold"],
                      bg=bg, fg="white", relief="flat", cursor="hand2",
                      padx=12, pady=5, command=cmd).pack(side="right", padx=4)

        cols = ("id", "name", "email", "subjects", "created")
        headings = ("ID", "Full Name", "Email", "Assigned Subjects", "Created")
        frame, self.tree = scrollable_treeview(self, cols, headings, height=24)
        frame.pack(fill="both", expand=True, padx=16, pady=8)
        widths = [40, 180, 200, 200, 120]
        for col, w in zip(cols, widths):
            self.tree.column(col, width=w, minwidth=w)
        self.tree.tag_configure("odd", background=COLORS["table_odd"])
        self.tree.tag_configure("even", background=COLORS["table_even"])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._on_select())

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        teachers = self.teacher_svc.get_all()
        for i, t in enumerate(teachers):
            subj_names = ", ".join(s.subject_name for s in t.subjects) or "—"
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=str(t.id), tags=(tag,), values=(
                t.id, t.full_name, t.email, subj_names,
                t.created_at.strftime("%Y-%m-%d"),
            ))

    def _on_select(self):
        sel = self.tree.selection()
        self._selected_id = int(sel[0]) if sel else None

    def _open_add(self):
        TeacherFormDialog(self, self.teacher_svc, on_save=self._load)

    def _open_edit(self):
        if not self._selected_id:
            show_info("Select", "Please select a teacher.")
            return
        teacher = self.teacher_svc.get_by_id(self._selected_id)
        TeacherFormDialog(self, self.teacher_svc, teacher=teacher, on_save=self._load)

    def _do_delete(self):
        if not self._selected_id:
            show_info("Select", "Please select a teacher.")
            return
        t = self.teacher_svc.get_by_id(self._selected_id)
        if t and confirm_delete(t.full_name):
            try:
                self.teacher_svc.delete(self._selected_id)
                self._selected_id = None
                self._load()
                show_success("Deleted", "Teacher deleted.")
            except Exception as e:
                show_error("Error", str(e))


class TeacherFormDialog(tk.Toplevel):
    def __init__(self, parent, teacher_svc, teacher=None, on_save=None):
        super().__init__(parent)
        self.teacher_svc = teacher_svc
        self.teacher = teacher
        self.on_save = on_save
        self.title("Edit Teacher" if teacher else "Add Teacher")
        self.configure(bg=COLORS["bg_medium"])
        self.resizable(False, False)
        self.grab_set()
        self._build()
        if teacher:
            self._fill(teacher)

    def _build(self):
        form = tk.Frame(self, bg=COLORS["bg_medium"], padx=30, pady=20)
        form.pack()
        for lbl, attr in [("Full Name", "name_var"), ("Email", "email_var"),
                           ("Password (leave blank to keep)", "pass_var")]:
            tk.Label(form, text=lbl, font=FONTS["body_bold"],
                     bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]).pack(anchor="w")
            var = tk.StringVar()
            setattr(self, attr, var)
            show = "•" if "pass" in attr.lower() else ""
            e = make_entry(form, textvariable=var, width=38, show=show or None)
            e.configure(bg=COLORS["bg_light"])
            e.pack(fill="x", pady=(4, 10))
        btn_row = tk.Frame(form, bg=COLORS["bg_medium"])
        btn_row.pack(fill="x", pady=(6, 0))
        tk.Button(btn_row, text="Save", font=FONTS["body_bold"],
                  bg=COLORS["primary"], fg="white", relief="flat",
                  cursor="hand2", padx=20, pady=6,
                  command=self._save).pack(side="right", padx=6)
        tk.Button(btn_row, text="Cancel", font=FONTS["body"],
                  bg=COLORS["bg_light"], fg=COLORS["text_primary"],
                  relief="flat", cursor="hand2", padx=20, pady=6,
                  command=self.destroy).pack(side="right")

    def _fill(self, t):
        self.name_var.set(t.full_name)
        self.email_var.set(t.email)

    def _save(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.pass_var.get().strip()
        if not name or not email:
            show_error("Validation", "Name and email are required.")
            return
        if not self.teacher and not password:
            show_error("Validation", "Password is required for new teacher.")
            return
        try:
            if self.teacher:
                self.teacher_svc.update(self.teacher.id, name, email, password or None)
                show_success("Updated", "Teacher updated.")
            else:
                self.teacher_svc.create(name, email, password)
                show_success("Added", "Teacher added.")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            show_error("Error", str(e))
