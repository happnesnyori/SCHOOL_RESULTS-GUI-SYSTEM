"""
views/reports_panel.py - Report generation panel (PDF / CSV)
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog
from config import COLORS, FONTS
from utils.ui_helpers import make_label, show_error, show_success, show_info


class ReportsPanel(tk.Frame):
    def __init__(self, parent, report_svc, student_svc, class_svc):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.report_svc = report_svc
        self.student_svc = student_svc
        self.class_svc = class_svc
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        make_label(self, "Report Generation", "subheading").pack(
            anchor="w", padx=20, pady=(14, 6))

        # Cards row
        cards = tk.Frame(self, bg=COLORS["bg_medium"])
        cards.pack(fill="x", padx=16, pady=8)

        self._report_card(
            cards,
            "Student Report Card",
            "Generate a full PDF report card for an individual student.",
            self._gen_student_report,
        ).grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        self._report_card(
            cards,
            "Class Report PDF",
            "Generate a PDF report listing all students in a class with averages.",
            self._gen_class_report,
        ).grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        self._report_card(
            cards,
            "Export All Results (CSV)",
            "Export the entire results database to a CSV file.",
            self._export_csv,
        ).grid(row=0, column=2, padx=8, pady=8, sticky="nsew")

        for i in range(3):
            cards.columnconfigure(i, weight=1)

        # Student selector for report card
        sel_frame = tk.Frame(self, bg=COLORS["card"], padx=20, pady=16)
        sel_frame.pack(fill="x", padx=16, pady=8)
        make_label(sel_frame, "Student Report Card — Select Student", "body_bold").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        tk.Label(sel_frame, text="Search Student:", font=FONTS["body_bold"],
                 bg=COLORS["card"], fg=COLORS["text_secondary"]).grid(row=1, column=0, padx=(0, 8))
        self.student_search_var = tk.StringVar()
        from utils.ui_helpers import make_entry
        e = make_entry(sel_frame, textvariable=self.student_search_var, width=28)
        e.configure(bg=COLORS["bg_medium"])
        e.grid(row=1, column=1, padx=(0, 12))
        tk.Button(sel_frame, text="Search", font=FONTS["body"],
                  bg=COLORS["secondary"], fg="white", relief="flat",
                  cursor="hand2", padx=12,
                  command=self._search_students).grid(row=1, column=2, padx=4)

        from utils.ui_helpers import scrollable_treeview
        cols = ("id", "adm", "name", "class_")
        headings = ("ID", "Adm No", "Name", "Class")
        frame, self.stree = scrollable_treeview(sel_frame, cols, headings, height=8)
        frame.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=8)
        sel_frame.rowconfigure(2, weight=1)
        sel_frame.columnconfigure(3, weight=1)
        widths = [40, 100, 180, 120]
        for col, w in zip(cols, widths):
            self.stree.column(col, width=w, minwidth=w)
        self.stree.tag_configure("odd", background=COLORS["table_odd"])
        self.stree.tag_configure("even", background=COLORS["table_even"])

        tk.Button(sel_frame, text="Generate Report Card PDF",
                  font=FONTS["body_bold"], bg=COLORS["primary"],
                  fg="white", relief="flat", cursor="hand2", padx=16, pady=6,
                  command=self._gen_student_report).grid(row=3, column=0, columnspan=4, sticky="w", pady=4)

        self._search_students()

        # Class selector
        cls_frame = tk.Frame(self, bg=COLORS["card"], padx=20, pady=16)
        cls_frame.pack(fill="x", padx=16, pady=8)
        make_label(cls_frame, "Class Report PDF — Select Class", "body_bold").pack(anchor="w", pady=(0, 8))
        classes = self.class_svc.get_all()
        self._class_map = {f"{c.class_name} ({c.academic_year})": c.id for c in classes}
        self.cls_var = tk.StringVar(value=list(self._class_map.keys())[0] if self._class_map else "")
        ttk.Combobox(cls_frame, textvariable=self.cls_var,
                     values=list(self._class_map.keys()), width=30, state="readonly").pack(side="left", padx=(0, 12))
        tk.Button(cls_frame, text="Generate Class PDF",
                  font=FONTS["body_bold"], bg=COLORS["primary"],
                  fg="white", relief="flat", cursor="hand2", padx=16, pady=6,
                  command=self._gen_class_report).pack(side="left")

    def _report_card(self, parent, title, desc, cmd):
        card = tk.Frame(parent, bg=COLORS["card"], padx=16, pady=18,
                        highlightbackground=COLORS["border"], highlightthickness=1)
        tk.Label(card, text=title, font=FONTS["body_bold"],
                 bg=COLORS["card"], fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(card, text=desc, font=FONTS["small"],
                 bg=COLORS["card"], fg=COLORS["text_secondary"],
                 wraplength=220, justify="left").pack(anchor="w", pady=(4, 12))
        tk.Button(card, text="Generate", font=FONTS["body_bold"],
                  bg=COLORS["secondary"], fg="white", relief="flat",
                  cursor="hand2", padx=12, pady=4, command=cmd).pack(anchor="w")
        return card

    def _search_students(self):
        query = self.student_search_var.get().strip()
        students, _ = self.student_svc.search(query, page=1, page_size=50)
        self.stree.delete(*self.stree.get_children())
        for i, s in enumerate(students):
            class_name = s.class_.class_name if s.class_ else "—"
            tag = "odd" if i % 2 else "even"
            self.stree.insert("", "end", iid=str(s.id), tags=(tag,), values=(
                s.id, s.admission_number, s.full_name, class_name))

    def _gen_student_report(self):
        sel = self.stree.selection()
        if not sel:
            show_info("Select", "Please select a student from the table.")
            return
        student_id = int(sel[0])
        student = self.student_svc.get_by_id(student_id)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"report_card_{student.admission_number}.pdf",
        )
        if not filepath:
            return
        try:
            self.report_svc.generate_student_report_card(student_id, filepath)
            show_success("Generated", f"Report card saved to:\n{filepath}")
        except Exception as e:
            show_error("Error", str(e))

    def _gen_class_report(self):
        class_label = self.cls_var.get()
        class_id = self._class_map.get(class_label)
        if not class_id:
            show_info("Select", "Please select a class.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"class_report_{class_label.replace(' ', '_')}.pdf",
        )
        if not filepath:
            return
        try:
            self.report_svc.generate_class_report_pdf(class_id, filepath)
            show_success("Generated", f"Class report saved to:\n{filepath}")
        except Exception as e:
            show_error("Error", str(e))

    def _export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="results_export.csv",
        )
        if not filepath:
            return
        try:
            self.report_svc.export_results_csv(filepath)
            show_success("Exported", f"Results exported to:\n{filepath}")
        except Exception as e:
            show_error("Error", str(e))
