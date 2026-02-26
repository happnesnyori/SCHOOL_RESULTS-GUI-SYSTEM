"""
views/student_dashboard.py - Student dashboard (restricted view)
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from views.base_dashboard import BaseDashboard
from services import ResultService, SubjectService, ClassService
from config import SessionLocal


class StudentDashboard(BaseDashboard):
    def __init__(self, master, user, logout_callback):
        self._db = SessionLocal()
        self._init_services(user)
        self.NAV_ITEMS = [
            ("My Results", self._show_results),
            ("My Profile", self._show_profile),
        ]
        super().__init__(master, user, "STUDENT", logout_callback)
        self._nav_click("My Results", self._show_results)

    def _init_services(self, user):
        db = self._db
        self.result_svc = ResultService(db)
        self.subject_svc = SubjectService(db)
        self.class_svc = ClassService(db)

    def _show_results(self):
        self.update_section_title("My Results")
        f = self.get_content_frame()
        from utils.ui_helpers import make_stat_card, make_divider

        results = self.result_svc.get_by_student(self.user.id)

        # ── Welcome header ───────────────────────────────────────────────────
        header = tk.Frame(f, bg=COLORS["bg_medium"], pady=20)
        header.pack(fill="x", padx=24)
        tk.Label(header, text=f"\U0001f393  {self.user.full_name}",
                 font=FONTS["heading"], bg=COLORS["bg_medium"],
                 fg=COLORS["white"]).pack(anchor="w")
        tk.Label(header, text=f"Admission No: {self.user.admission_number}",
                 font=FONTS["body"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))

        make_divider(f, padx=24, pady=(0, 4))

        if not results:
            empty = tk.Frame(f, bg=COLORS["bg_medium"])
            empty.pack(fill="both", expand=True)
            tk.Label(empty, text="\U0001f4cb",
                     font=("Segoe UI Emoji", 48),
                     bg=COLORS["bg_medium"], fg=COLORS["border"]).pack(pady=(60, 8))
            tk.Label(empty, text="No results available yet.",
                     font=FONTS["subheading"], bg=COLORS["bg_medium"],
                     fg=COLORS["text_secondary"]).pack()
            tk.Label(empty, text="Results will appear here once your teacher enters your marks.",
                     font=FONTS["body"], bg=COLORS["bg_medium"],
                     fg=COLORS["text_secondary"]).pack(pady=(4, 0))
            return

        total_marks = sum(r.marks for r in results)
        avg_marks = total_marks / len(results) if results else 0
        passed = sum(1 for r in results if r.marks >= 50)

        # ── Stat cards ───────────────────────────────────────────────────────
        cards_row = tk.Frame(f, bg=COLORS["bg_medium"])
        cards_row.pack(fill="x", padx=24, pady=16)
        stat_items = [
            ("\U0001f4da", len(results),          "Total Subjects",  COLORS["primary"]),
            ("\u2b50",     f"{avg_marks:.1f}%",   "Average Score",   COLORS["secondary"]),
            ("\u2705",     f"{passed}/{len(results)}", "Passed",     COLORS["success"]),
        ]
        for i, (icon, val, label, color) in enumerate(stat_items):
            card = make_stat_card(cards_row, icon, val, label, color)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            cards_row.columnconfigure(i, weight=1)

        make_divider(f, padx=24, pady=(4, 0))

        # ── Section header ───────────────────────────────────────────────────
        hdr = tk.Frame(f, bg=COLORS["bg_medium"])
        hdr.pack(fill="x", padx=24, pady=(14, 8))
        tk.Label(hdr, text="Subject Results", font=FONTS["subheading"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_primary"]).pack(anchor="w")

        cols = ("subject", "class", "marks", "grade", "remarks")
        headings = ("Subject", "Class", "Marks", "Grade", "Remarks")
        tree_frame = tk.Frame(f, bg=COLORS["bg_medium"])
        tree_frame.pack(fill="both", expand=True, padx=20, pady=8)
        
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=10)
        for col, head in zip(cols, headings):
            tree.heading(col, text=head)
            tree.column(col, width=150 if col != "remarks" else 200)
        tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Grade scale
        grade_scale = [
            (80, 100, "A", "Distinction"),
            (70, 79, "B", "Credit"),
            (60, 69, "C", "Merit"),
            (50, 59, "D", "Pass"),
            (0, 49, "F", "Fail"),
        ]

        for r in results:
            subject = r.subject.subject_name if r.subject else "N/A"
            class_name = r.subject.class_.class_name if r.subject and r.subject.class_ else "N/A"
            marks = r.marks
            
            # Determine grade
            grade = "F"
            remarks = "Fail"
            for min_val, max_val, g, rem in grade_scale:
                if min_val <= marks <= max_val:
                    grade = g
                    remarks = rem
                    break
            
            tree.insert("", "end", values=(subject, class_name, f"{marks}", grade, remarks))

    def _show_profile(self):
        self.update_section_title("My Profile")
        f = self.get_content_frame()
        from utils.ui_helpers import make_divider

        # ── Page header ──────────────────────────────────────────────────────
        header = tk.Frame(f, bg=COLORS["bg_medium"], pady=20)
        header.pack(fill="x", padx=24)
        tk.Label(header, text="\U0001f464  My Profile",
                 font=FONTS["heading"], bg=COLORS["bg_medium"],
                 fg=COLORS["white"]).pack(anchor="w")
        make_divider(f, padx=24, pady=(0, 4))

        # ── Avatar + info card ────────────────────────────────────────────────
        name = self.user.full_name or "Student"
        initials = "".join(w[0].upper() for w in name.split()[:2]) or "S"

        card = tk.Frame(f, bg=COLORS["card"], padx=28, pady=24,
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", padx=24, pady=16)

        # Avatar circle row
        avatar_row = tk.Frame(card, bg=COLORS["card"])
        avatar_row.pack(fill="x", pady=(0, 16))
        tk.Label(avatar_row, text=initials,
                 font=("Segoe UI", 20, "bold"),
                 bg=COLORS["success"], fg="white",
                 padx=16, pady=10).pack(side="left")
        name_col = tk.Frame(avatar_row, bg=COLORS["card"])
        name_col.pack(side="left", padx=(14, 0))
        tk.Label(name_col, text=name,
                 font=FONTS["subheading"], bg=COLORS["card"],
                 fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(name_col, text="Student", font=FONTS["small"],
                 bg=COLORS["card"], fg=COLORS["success"]).pack(anchor="w")

        make_divider(card, pady=(0, 14))

        # Info fields in 2-column grid
        info_items = [
            ("Admission Number", self.user.admission_number),
            ("Full Name",        self.user.full_name),
            ("Gender",           self.user.gender),
            ("Date of Birth",    str(self.user.date_of_birth) if self.user.date_of_birth else "Not set"),
            ("Class",            self.user.class_.class_name if self.user.class_ else "Not assigned"),
        ]

        grid = tk.Frame(card, bg=COLORS["card"])
        grid.pack(fill="x")
        for i, (label, value) in enumerate(info_items):
            col = (i % 2) * 2
            row = i // 2
            tk.Label(grid, text=label, font=FONTS["small_bold"],
                     bg=COLORS["card"], fg=COLORS["text_secondary"],
                     anchor="w").grid(row=row, column=col, sticky="w", padx=(0, 8), pady=5)
            tk.Label(grid, text=str(value), font=FONTS["body"],
                     bg=COLORS["card"], fg=COLORS["text_primary"],
                     anchor="w").grid(row=row, column=col + 1, sticky="w", padx=(0, 40), pady=5)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)
