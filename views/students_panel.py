"""
views/students_panel.py - Student Management CRUD panel
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import COLORS, FONTS
from utils.ui_helpers import (
    scrollable_treeview, make_entry, make_label,
    confirm_delete, show_error, show_success, show_info
)


class StudentsPanel(tk.Frame):
    PAGE_SIZE = 20

    def __init__(self, parent, student_svc, class_svc):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.student_svc = student_svc
        self.class_svc = class_svc
        self._page = 1
        self._total = 0
        self._selected_id = None
        self.pack(fill="both", expand=True)
        self._build()
        self._load()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build(self):
        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS["bg_medium"], pady=10)
        toolbar.pack(fill="x", padx=16)

        make_label(toolbar, "Student Management", "subheading").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._on_search())
        search_entry = make_entry(toolbar, textvariable=self.search_var, width=26)
        search_entry.configure(bg=COLORS["bg_light"])
        search_entry.pack(side="left", padx=(24, 6))
        make_label(toolbar, "Search:", "body").pack(side="left", padx=(0, 2))

        # Class filter
        make_label(toolbar, "Class:", "body").pack(side="left", padx=(16, 4))
        self.class_var = tk.StringVar(value="All")
        self.class_filter = ttk.Combobox(
            toolbar, textvariable=self.class_var, width=16, state="readonly")
        self.class_filter.pack(side="left")
        self.class_filter.bind("<<ComboboxSelected>>", lambda e: self._on_search())

        # Buttons
        for (text, style_bg, cmd) in [
            ("+ Add Student", COLORS["primary"], self._open_add),
            ("Edit", COLORS["secondary"], self._open_edit),
            ("Delete", COLORS["danger"], self._do_delete),
        ]:
            tk.Button(toolbar, text=text, font=FONTS["body_bold"],
                      bg=style_bg, fg="white", activebackground=style_bg,
                      relief="flat", cursor="hand2", padx=12, pady=5,
                      command=cmd).pack(side="right", padx=4)

        # Table
        cols = ("adm_no", "name", "gender", "dob", "class", "results")
        headings = ("Adm No", "Full Name", "Gender", "Date of Birth", "Class", "Results")
        frame, self.tree = scrollable_treeview(self, cols, headings, height=20)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # Configure column widths
        widths = [100, 180, 70, 100, 120, 60]
        for col, w in zip(cols, widths):
            self.tree.column(col, width=w, minwidth=w)

        # Row colour tags
        self.tree.tag_configure("odd", background=COLORS["table_odd"])
        self.tree.tag_configure("even", background=COLORS["table_even"])
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Pagination bar
        pag = tk.Frame(self, bg=COLORS["bg_medium"])
        pag.pack(fill="x", padx=16, pady=4)
        self.page_lbl = tk.Label(pag, text="", font=FONTS["small"],
                                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"])
        self.page_lbl.pack(side="left")

        tk.Button(pag, text="Prev", font=FONTS["small"],
                  bg=COLORS["bg_light"], fg=COLORS["text_primary"],
                  relief="flat", cursor="hand2", padx=8,
                  command=self._prev_page).pack(side="right", padx=2)
        tk.Button(pag, text="Next", font=FONTS["small"],
                  bg=COLORS["bg_light"], fg=COLORS["text_primary"],
                  relief="flat", cursor="hand2", padx=8,
                  command=self._next_page).pack(side="right", padx=2)

        self._refresh_class_filter()

    # ── Data ─────────────────────────────────────────────────────────────────

    def _refresh_class_filter(self):
        classes = self.class_svc.get_all()
        self._class_map = {c.class_name: c.id for c in classes}
        values = ["All"] + list(self._class_map.keys())
        self.class_filter["values"] = values
        if self.class_var.get() not in values:
            self.class_var.set("All")

    def _load(self):
        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        class_name = self.class_var.get() if hasattr(self, "class_var") else "All"
        class_id = self._class_map.get(class_name) if class_name != "All" else None
        students, total = self.student_svc.search(query, class_id, self._page, self.PAGE_SIZE)
        self._total = total
        self._populate(students)
        pages = max(1, (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.page_lbl.configure(
            text=f"Showing {len(students)} of {total}  |  Page {self._page}/{pages}")

    def _populate(self, students):
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(students):
            class_name = s.class_.class_name if s.class_ else "—"
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=str(s.id), tags=(tag,), values=(
                s.admission_number, s.full_name, s.gender,
                str(s.date_of_birth or "—"), class_name, len(s.results),
            ))

    def _on_select(self, _event):
        sel = self.tree.selection()
        self._selected_id = int(sel[0]) if sel else None

    def _on_search(self):
        self._page = 1
        self._load()

    def _prev_page(self):
        if self._page > 1:
            self._page -= 1
            self._load()

    def _next_page(self):
        pages = max(1, (self._total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        if self._page < pages:
            self._page += 1
            self._load()

    # ── CRUD dialogs ──────────────────────────────────────────────────────────

    def _open_add(self):
        StudentFormDialog(self, self.student_svc, self.class_svc,
                          on_save=self._load)

    def _open_edit(self):
        if not self._selected_id:
            show_info("Select", "Please select a student to edit.")
            return
        student = self.student_svc.get_by_id(self._selected_id)
        if not student:
            show_error("Not Found", "Student not found.")
            return
        StudentFormDialog(self, self.student_svc, self.class_svc,
                          student=student, on_save=self._load)

    def _do_delete(self):
        if not self._selected_id:
            show_info("Select", "Please select a student to delete.")
            return
        student = self.student_svc.get_by_id(self._selected_id)
        if not student:
            return
        if confirm_delete(student.full_name):
            try:
                self.student_svc.delete(self._selected_id)
                self._selected_id = None
                self._load()
                show_success("Deleted", "Student deleted successfully.")
            except Exception as e:
                show_error("Error", str(e))


class StudentFormDialog(tk.Toplevel):
    def __init__(self, parent, student_svc, class_svc, student=None, on_save=None):
        super().__init__(parent)
        self.student_svc = student_svc
        self.class_svc = class_svc
        self.student = student
        self.on_save = on_save
        self.title("Edit Student" if student else "Add Student")
        self.configure(bg=COLORS["bg_medium"])
        self.resizable(False, False)
        self.grab_set()
        self._build()
        if student:
            self._fill(student)

    def _build(self):
        pad = dict(padx=20, pady=8)
        form = tk.Frame(self, bg=COLORS["bg_medium"], padx=30, pady=20)
        form.pack()

        fields = [
            ("Admission Number", "adm_var"),
            ("First Name", "fname_var"),
            ("Last Name", "lname_var"),
            ("Date of Birth (YYYY-MM-DD)", "dob_var"),
        ]
        for label, attr in fields:
            tk.Label(form, text=label, font=FONTS["body_bold"],
                     bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]).pack(anchor="w")
            var = tk.StringVar()
            setattr(self, attr, var)
            make_entry(form, textvariable=var, width=38).pack(fill="x", **pad)

        # Gender
        tk.Label(form, text="Gender", font=FONTS["body_bold"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.gender_var = tk.StringVar(value="Male")
        ttk.Combobox(form, textvariable=self.gender_var,
                     values=["Male", "Female", "Other"],
                     width=36, state="readonly").pack(fill="x", **pad)

        # Class
        classes = self.class_svc.get_all()
        self._class_map = {f"{c.class_name} ({c.academic_year})": c.id for c in classes}
        tk.Label(form, text="Class", font=FONTS["body_bold"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.class_var = tk.StringVar(value="")
        ttk.Combobox(form, textvariable=self.class_var,
                     values=list(self._class_map.keys()),
                     width=36, state="readonly").pack(fill="x", **pad)

        # Buttons
        btn_row = tk.Frame(form, bg=COLORS["bg_medium"])
        btn_row.pack(fill="x", pady=(12, 0))
        tk.Button(btn_row, text="Save", font=FONTS["body_bold"],
                  bg=COLORS["primary"], fg="white", relief="flat",
                  cursor="hand2", padx=20, pady=6,
                  command=self._save).pack(side="right", padx=6)
        tk.Button(btn_row, text="Cancel", font=FONTS["body"],
                  bg=COLORS["bg_light"], fg=COLORS["text_primary"],
                  relief="flat", cursor="hand2", padx=20, pady=6,
                  command=self.destroy).pack(side="right")

    def _fill(self, s):
        self.adm_var.set(s.admission_number)
        self.fname_var.set(s.first_name)
        self.lname_var.set(s.last_name)
        self.dob_var.set(str(s.date_of_birth or ""))
        self.gender_var.set(s.gender)
        # Find class label
        for label, cid in self._class_map.items():
            if cid == s.class_id:
                self.class_var.set(label)
                break

    def _save(self):
        adm = self.adm_var.get().strip()
        fname = self.fname_var.get().strip()
        lname = self.lname_var.get().strip()
        dob_str = self.dob_var.get().strip()
        gender = self.gender_var.get()
        class_label = self.class_var.get()
        class_id = self._class_map.get(class_label)

        if not all([adm, fname, lname, gender]):
            show_error("Validation", "Admission number, first name, last name and gender are required.")
            return

        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                show_error("Validation", "Date of birth must be in YYYY-MM-DD format.")
                return

        try:
            if self.student:
                self.student_svc.update(
                    self.student.id, adm, fname, lname, gender, dob, class_id)
                show_success("Updated", "Student updated successfully.")
            else:
                self.student_svc.create(adm, fname, lname, gender, dob, class_id)
                show_success("Added", "Student added successfully.")
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            show_error("Error", str(e))
