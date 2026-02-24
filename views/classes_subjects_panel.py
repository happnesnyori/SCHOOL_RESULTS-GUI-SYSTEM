"""
views/classes_subjects_panel.py - Classes and Subjects management (tabbed)
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from utils.ui_helpers import (
    scrollable_treeview, make_entry, make_label,
    confirm_delete, show_error, show_success, show_info
)


class ClassesSubjectsPanel(tk.Frame):
    def __init__(self, parent, class_svc, subject_svc, teacher_svc):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.class_svc = class_svc
        self.subject_svc = subject_svc
        self.teacher_svc = teacher_svc
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=12)

        # Classes tab
        classes_tab = tk.Frame(nb, bg=COLORS["bg_medium"])
        nb.add(classes_tab, text="  Classes  ")
        ClassesTab(classes_tab, self.class_svc)

        # Subjects tab
        subjects_tab = tk.Frame(nb, bg=COLORS["bg_medium"])
        nb.add(subjects_tab, text="  Subjects  ")
        SubjectsTab(subjects_tab, self.subject_svc, self.class_svc, self.teacher_svc)


class ClassesTab(tk.Frame):
    def __init__(self, parent, class_svc):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.class_svc = class_svc
        self._selected_id = None
        self.pack(fill="both", expand=True)
        self._build()
        self._load()

    def _build(self):
        # Inline form
        form_card = tk.Frame(self, bg=COLORS["card"], padx=16, pady=14)
        form_card.pack(fill="x", pady=(8, 0))
        make_label(form_card, "Add / Edit Class", "body_bold").grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

        tk.Label(form_card, text="Class Name", font=FONTS["body_bold"],
                 bg=COLORS["card"], fg=COLORS["text_secondary"]).grid(
            row=1, column=0, sticky="w", padx=(0, 8))
        self.name_var = tk.StringVar()
        make_entry(form_card, textvariable=self.name_var, width=22).grid(
            row=1, column=1, padx=(0, 20))

        tk.Label(form_card, text="Academic Year", font=FONTS["body_bold"],
                 bg=COLORS["card"], fg=COLORS["text_secondary"]).grid(
            row=1, column=2, sticky="w", padx=(0, 8))
        self.year_var = tk.StringVar()
        make_entry(form_card, textvariable=self.year_var, width=16).grid(
            row=1, column=3, padx=(0, 20))

        tk.Button(form_card, text="Save", font=FONTS["body_bold"],
                  bg=COLORS["primary"], fg="white", relief="flat",
                  cursor="hand2", padx=14, pady=4,
                  command=self._save).grid(row=1, column=4, padx=4)
        tk.Button(form_card, text="Clear", font=FONTS["body"],
                  bg=COLORS["bg_light"], fg=COLORS["text_primary"],
                  relief="flat", cursor="hand2", padx=14, pady=4,
                  command=self._clear).grid(row=1, column=5, padx=4)

        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS["bg_medium"], pady=6)
        toolbar.pack(fill="x")
        tk.Button(toolbar, text="Delete Selected", font=FONTS["body"],
                  bg=COLORS["danger"], fg="white", relief="flat",
                  cursor="hand2", padx=10,
                  command=self._delete).pack(side="right")

        cols = ("id", "name", "year", "students", "subjects")
        headings = ("ID", "Class Name", "Academic Year", "Students", "Subjects")
        frame, self.tree = scrollable_treeview(self, cols, headings, height=18)
        frame.pack(fill="both", expand=True, pady=6)
        widths = [40, 160, 100, 80, 80]
        for col, w in zip(cols, widths):
            self.tree.column(col, width=w, minwidth=w)
        self.tree.tag_configure("odd", background=COLORS["table_odd"])
        self.tree.tag_configure("even", background=COLORS["table_even"])
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for i, c in enumerate(self.class_svc.get_all()):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=str(c.id), tags=(tag,), values=(
                c.id, c.class_name, c.academic_year,
                len(c.students), len(c.subjects),
            ))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if sel:
            self._selected_id = int(sel[0])
            c = self.class_svc.get_by_id(self._selected_id)
            if c:
                self.name_var.set(c.class_name)
                self.year_var.set(c.academic_year)

    def _save(self):
        name = self.name_var.get().strip()
        year = self.year_var.get().strip()
        if not name or not year:
            show_error("Validation", "Class name and academic year are required.")
            return
        try:
            if self._selected_id:
                self.class_svc.update(self._selected_id, name, year)
                show_success("Updated", "Class updated.")
            else:
                self.class_svc.create(name, year)
                show_success("Added", "Class added.")
            self._clear()
            self._load()
        except Exception as e:
            show_error("Error", str(e))

    def _clear(self):
        self._selected_id = None
        self.name_var.set("")
        self.year_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def _delete(self):
        if not self._selected_id:
            show_info("Select", "Please select a class.")
            return
        c = self.class_svc.get_by_id(self._selected_id)
        if c and confirm_delete(c.class_name):
            try:
                self.class_svc.delete(self._selected_id)
                self._clear()
                self._load()
            except Exception as e:
                show_error("Error", str(e))


class SubjectsTab(tk.Frame):
    def __init__(self, parent, subject_svc, class_svc, teacher_svc):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.subject_svc = subject_svc
        self.class_svc = class_svc
        self.teacher_svc = teacher_svc
        self._selected_id = None
        self.pack(fill="both", expand=True)
        self._build()
        self._load()

    def _build(self):
        form_card = tk.Frame(self, bg=COLORS["card"], padx=16, pady=14)
        form_card.pack(fill="x", pady=(8, 0))
        make_label(form_card, "Add / Edit Subject", "body_bold").grid(
            row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))

        tk.Label(form_card, text="Subject Name", font=FONTS["body_bold"],
                 bg=COLORS["card"], fg=COLORS["text_secondary"]).grid(row=1, column=0, sticky="w", padx=(0, 4))
        self.name_var = tk.StringVar()
        make_entry(form_card, textvariable=self.name_var, width=22).grid(row=1, column=1, padx=(0, 16))

        classes = self.class_svc.get_all()
        self._class_map = {"—": None, **{c.class_name: c.id for c in classes}}
        teachers = self.teacher_svc.get_all()
        self._teacher_map = {"—": None, **{t.full_name: t.id for t in teachers}}

        tk.Label(form_card, text="Class", font=FONTS["body_bold"],
                 bg=COLORS["card"], fg=COLORS["text_secondary"]).grid(row=1, column=2, sticky="w", padx=(0, 4))
        self.class_var = tk.StringVar(value="—")
        ttk.Combobox(form_card, textvariable=self.class_var,
                     values=list(self._class_map.keys()), width=16, state="readonly").grid(
            row=1, column=3, padx=(0, 16))

        tk.Label(form_card, text="Teacher", font=FONTS["body_bold"],
                 bg=COLORS["card"], fg=COLORS["text_secondary"]).grid(row=1, column=4, sticky="w", padx=(0, 4))
        self.teacher_var = tk.StringVar(value="—")
        ttk.Combobox(form_card, textvariable=self.teacher_var,
                     values=list(self._teacher_map.keys()), width=18, state="readonly").grid(
            row=1, column=5, padx=(0, 16))

        tk.Button(form_card, text="Save", font=FONTS["body_bold"],
                  bg=COLORS["primary"], fg="white", relief="flat",
                  cursor="hand2", padx=14, pady=4,
                  command=self._save).grid(row=1, column=6, padx=4)
        tk.Button(form_card, text="Clear", font=FONTS["body"],
                  bg=COLORS["bg_light"], fg=COLORS["text_primary"],
                  relief="flat", cursor="hand2", padx=14, pady=4,
                  command=self._clear).grid(row=1, column=7, padx=4)

        toolbar = tk.Frame(self, bg=COLORS["bg_medium"], pady=6)
        toolbar.pack(fill="x")
        tk.Button(toolbar, text="Delete Selected", font=FONTS["body"],
                  bg=COLORS["danger"], fg="white", relief="flat",
                  cursor="hand2", padx=10, command=self._delete).pack(side="right")

        cols = ("id", "name", "class_", "teacher")
        headings = ("ID", "Subject Name", "Class", "Teacher")
        frame, self.tree = scrollable_treeview(self, cols, headings, height=18)
        frame.pack(fill="both", expand=True, pady=6)
        widths = [40, 200, 140, 160]
        for col, w in zip(cols, widths):
            self.tree.column(col, width=w, minwidth=w)
        self.tree.tag_configure("odd", background=COLORS["table_odd"])
        self.tree.tag_configure("even", background=COLORS["table_even"])
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(self.subject_svc.get_all()):
            class_name = s.class_.class_name if s.class_ else "—"
            teacher_name = s.teacher.full_name if s.teacher else "—"
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=str(s.id), tags=(tag,), values=(
                s.id, s.subject_name, class_name, teacher_name,
            ))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if sel:
            self._selected_id = int(sel[0])
            s = self.subject_svc.get_by_id(self._selected_id)
            if s:
                self.name_var.set(s.subject_name)
                for lbl, cid in self._class_map.items():
                    if cid == s.class_id:
                        self.class_var.set(lbl)
                        break
                for lbl, tid in self._teacher_map.items():
                    if tid == s.teacher_id:
                        self.teacher_var.set(lbl)
                        break

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            show_error("Validation", "Subject name is required.")
            return
        class_id = self._class_map.get(self.class_var.get())
        teacher_id = self._teacher_map.get(self.teacher_var.get())
        try:
            if self._selected_id:
                self.subject_svc.update(self._selected_id, name, class_id, teacher_id)
                show_success("Updated", "Subject updated.")
            else:
                self.subject_svc.create(name, class_id, teacher_id)
                show_success("Added", "Subject added.")
            self._clear()
            self._load()
        except Exception as e:
            show_error("Error", str(e))

    def _clear(self):
        self._selected_id = None
        self.name_var.set("")
        self.class_var.set("—")
        self.teacher_var.set("—")
        self.tree.selection_remove(self.tree.selection())

    def _delete(self):
        if not self._selected_id:
            show_info("Select", "Please select a subject.")
            return
        s = self.subject_svc.get_by_id(self._selected_id)
        if s and confirm_delete(s.subject_name):
            try:
                self.subject_svc.delete(self._selected_id)
                self._clear()
                self._load()
            except Exception as e:
                show_error("Error", str(e))
