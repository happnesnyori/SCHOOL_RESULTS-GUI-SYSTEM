"""
views/results_panel.py - Results entry and display with real-time refresh
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from utils.ui_helpers import (
    scrollable_treeview, make_entry, make_label,
    show_error, show_success, show_info, confirm_delete
)


class ResultsPanel(tk.Frame):
    def __init__(self, parent, result_svc, student_svc, subject_svc, class_svc,
                 teacher=None):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.result_svc = result_svc
        self.student_svc = student_svc
        self.subject_svc = subject_svc
        self.class_svc = class_svc
        self.teacher = teacher  # If set, restrict to teacher's subjects
        self.pack(fill="both", expand=True)
        self._build()
        self._load()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        # Top: entry form
        form_card = tk.Frame(self, bg=COLORS["card"], padx=20, pady=16,
                             highlightbackground=COLORS["border"], highlightthickness=1)
        form_card.pack(fill="x", padx=16, pady=(12, 6))

        make_label(form_card, "Enter / Update Marks", "subheading").grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 12))

        labels = ["Student Adm No", "Subject", "Marks (0–100)"]
        for col, lbl in enumerate(labels):
            tk.Label(form_card, text=lbl, font=FONTS["body_bold"],
                     bg=COLORS["card"], fg=COLORS["text_secondary"]).grid(
                row=1, column=col * 2, sticky="w", padx=(0 if col == 0 else 16, 4))

        self.adm_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.marks_var = tk.StringVar()

        adm_entry = make_entry(form_card, textvariable=self.adm_var, width=20)
        adm_entry.configure(bg=COLORS["bg_medium"])
        adm_entry.grid(row=1, column=1, padx=(0, 8), pady=6)

        # Subjects
        subjects = self._get_available_subjects()
        self._subject_map = {s.subject_name: s.id for s in subjects}
        self.subject_cb = ttk.Combobox(
            form_card, textvariable=self.subject_var,
            values=list(self._subject_map.keys()), width=22, state="readonly")
        self.subject_cb.grid(row=1, column=3, padx=(0, 8))

        marks_entry = make_entry(form_card, textvariable=self.marks_var, width=12)
        marks_entry.configure(bg=COLORS["bg_medium"])
        marks_entry.grid(row=1, column=5, padx=(0, 8))

        btn_frame = tk.Frame(form_card, bg=COLORS["card"])
        btn_frame.grid(row=1, column=6, padx=(16, 0))

        tk.Button(btn_frame, text="Submit", font=FONTS["body_bold"],
                  bg=COLORS["success"], fg="white", relief="flat",
                  cursor="hand2", padx=14, pady=5,
                  command=self._submit_marks).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Update", font=FONTS["body_bold"],
                  bg=COLORS["secondary"], fg="white", relief="flat",
                  cursor="hand2", padx=14, pady=5,
                  command=self._update_marks).pack(side="left", padx=2)

        # Toolbar / filter
        toolbar = tk.Frame(self, bg=COLORS["bg_medium"], pady=6)
        toolbar.pack(fill="x", padx=16)
        make_label(toolbar, "Results Table", "subheading").pack(side="left")

        # Class filter for admin
        make_label(toolbar, "Filter Class:", "body").pack(side="left", padx=(20, 4))
        self.filter_class_var = tk.StringVar(value="All")
        classes = self.class_svc.get_all()
        self._class_map_filter = {c.class_name: c.id for c in classes}
        filter_values = ["All"] + list(self._class_map_filter.keys())
        ttk.Combobox(toolbar, textvariable=self.filter_class_var,
                     values=filter_values, width=18, state="readonly").pack(side="left")
        tk.Button(toolbar, text="Apply", font=FONTS["body"],
                  bg=COLORS["primary"], fg="white", relief="flat",
                  cursor="hand2", padx=10, command=self._load).pack(side="left", padx=6)

        tk.Button(toolbar, text="Delete Selected", font=FONTS["body"],
                  bg=COLORS["danger"], fg="white", relief="flat",
                  cursor="hand2", padx=10,
                  command=self._delete_result).pack(side="right")

        # Table
        cols = ("id", "adm", "student", "class_", "subject", "marks", "grade", "gpa", "remarks")
        headings = ("ID", "Adm No", "Student", "Class", "Subject", "Marks", "Grade", "GPA", "Remarks")
        frame, self.tree = scrollable_treeview(self, cols, headings, height=22)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        widths = [40, 90, 160, 110, 130, 60, 60, 60, 100]
        for col, w in zip(cols, widths):
            self.tree.column(col, width=w, minwidth=w)

        self.tree.tag_configure("A", foreground="#66bb6a")
        self.tree.tag_configure("B", foreground="#42a5f5")
        self.tree.tag_configure("C", foreground="#ffa726")
        self.tree.tag_configure("D", foreground="#ef5350")
        self.tree.tag_configure("F", foreground=COLORS["danger"])
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self._selected_result_id = None

    def _get_available_subjects(self):
        if self.teacher:
            return self.subject_svc.get_by_teacher(self.teacher.id)
        return self.subject_svc.get_all()

    # ── Data ─────────────────────────────────────────────────────────────────

    def _load(self):
        class_name = self.filter_class_var.get() if hasattr(self, "filter_class_var") else "All"
        if class_name != "All":
            class_id = self._class_map_filter.get(class_name)
            results = self.result_svc.get_class_results(class_id)
        else:
            results = self.result_svc.get_all()
        self._populate(results)

    def _populate(self, results):
        self.tree.delete(*self.tree.get_children())
        for r in results:
            student = r.student
            class_name = student.class_.class_name if student and student.class_ else "—"
            subject_name = r.subject.subject_name if r.subject else "—"
            self.tree.insert("", "end", iid=str(r.id), tags=(r.grade,), values=(
                r.id,
                student.admission_number if student else "—",
                student.full_name if student else "—",
                class_name,
                subject_name,
                f"{r.marks:.1f}",
                r.grade,
                f"{r.gpa:.1f}",
                r.remarks,
            ))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            self._selected_result_id = None
            return
        iid = int(sel[0])
        self._selected_result_id = iid
        # Auto-fill marks
        result = self.result_svc.get_by_id(iid)
        if result:
            self.marks_var.set(str(result.marks))
            self.adm_var.set(result.student.admission_number)
            for name, sid in self._subject_map.items():
                if sid == result.subject_id:
                    self.subject_var.set(name)
                    break

    # ── Actions ───────────────────────────────────────────────────────────────

    def _submit_marks(self):
        try:
            adm = self.adm_var.get().strip()
            marks = float(self.marks_var.get().strip())
            subject_name = self.subject_var.get()
            if not adm or not subject_name:
                show_error("Validation", "Admission number and subject are required.")
                return
            student = self.student_svc.get_by_admission(adm)
            if not student:
                show_error("Not Found", f"No student with admission number '{adm}'.")
                return
            subject_id = self._subject_map.get(subject_name)
            result = self.result_svc.add_result(student.id, subject_id, marks)
            show_success("Saved", f"Marks saved: {result.marks} — Grade {result.grade}")
            # Real-time append to tree
            class_name = student.class_.class_name if student.class_ else "—"
            self.tree.insert("", 0, iid=str(result.id), tags=(result.grade,), values=(
                result.id, student.admission_number, student.full_name,
                class_name, subject_name, f"{result.marks:.1f}",
                result.grade, f"{result.gpa:.1f}", result.remarks,
            ))
        except ValueError as e:
            show_error("Error", str(e))
        except Exception as e:
            show_error("Error", str(e))

    def _update_marks(self):
        if not self._selected_result_id:
            show_info("Select", "Please select a result row to update.")
            return
        try:
            marks = float(self.marks_var.get().strip())
            result = self.result_svc.update_result(self._selected_result_id, marks)
            show_success("Updated", f"Marks updated: {result.marks} — Grade {result.grade}")
            # Update row in-place
            student = result.student
            subject_name = result.subject.subject_name if result.subject else "—"
            class_name = student.class_.class_name if student and student.class_ else "—"
            self.tree.item(str(result.id), tags=(result.grade,), values=(
                result.id, student.admission_number, student.full_name,
                class_name, subject_name, f"{result.marks:.1f}",
                result.grade, f"{result.gpa:.1f}", result.remarks,
            ))
        except Exception as e:
            show_error("Error", str(e))

    def _delete_result(self):
        if not self._selected_result_id:
            show_info("Select", "Please select a result to delete.")
            return
        if confirm_delete("this result"):
            try:
                self.result_svc.delete_result(self._selected_result_id)
                self.tree.delete(str(self._selected_result_id))
                self._selected_result_id = None
                show_success("Deleted", "Result deleted.")
            except Exception as e:
                show_error("Error", str(e))
