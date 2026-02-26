"""
views/teacher_dashboard.py - Teacher dashboard (restricted view)
"""
import tkinter as tk
from config import COLORS, FONTS
from views.base_dashboard import BaseDashboard
from views.results_panel import ResultsPanel
from services import StudentService, SubjectService, ResultService, ClassService
from config import SessionLocal


class TeacherDashboard(BaseDashboard):
    def __init__(self, master, user, logout_callback):
        self._db = SessionLocal()
        self._init_services(user)
        self.NAV_ITEMS = [
            ("My Subjects & Marks", self._show_results),
            ("My Class Performance", self._show_class_perf),
        ]
        super().__init__(master, user, "TEACHER", logout_callback)
        self._nav_click("My Subjects & Marks", self._show_results)

    def _init_services(self, user):
        db = self._db
        self.student_svc = StudentService(db)
        self.subject_svc = SubjectService(db)
        self.result_svc = ResultService(db)
        self.class_svc = ClassService(db)

    def _show_results(self):
        self.update_section_title("Enter Student Marks")
        ResultsPanel(
            self.get_content_frame(),
            self.result_svc, self.student_svc, self.subject_svc, self.class_svc,
            teacher=self.user,
        )

    def _show_class_perf(self):
        self.update_section_title("Class Performance")
        f = self.get_content_frame()
        from utils.ui_helpers import make_divider, make_stat_card
        subjects = self.subject_svc.get_by_teacher(self.user.id)

        # Header
        header = tk.Frame(f, bg=COLORS["bg_medium"], pady=20)
        header.pack(fill="x", padx=24)
        tk.Label(header, text="\U0001f4c8  Class Performance",
                 font=FONTS["heading"], bg=COLORS["bg_medium"],
                 fg=COLORS["white"]).pack(anchor="w")
        tk.Label(header, text="Overview of your assigned subjects and student performance.",
                 font=FONTS["body"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))
        make_divider(f, padx=24, pady=(0, 8))

        if not subjects:
            empty = tk.Frame(f, bg=COLORS["bg_medium"])
            empty.pack(fill="both", expand=True)
            tk.Label(empty, text="\U0001f4da",
                     font=("Segoe UI Emoji", 48),
                     bg=COLORS["bg_medium"], fg=COLORS["border"]).pack(pady=(60, 8))
            tk.Label(empty, text="No subjects assigned yet.",
                     font=FONTS["subheading"], bg=COLORS["bg_medium"],
                     fg=COLORS["text_secondary"]).pack()
            return

        # Scrollable subject cards
        cards_host = tk.Frame(f, bg=COLORS["bg_medium"])
        cards_host.pack(fill="both", expand=True, padx=24)

        accent_cycle = [
            COLORS["primary"], COLORS["secondary"], COLORS["accent"],
            COLORS["success"], COLORS["warning"],
        ]

        for idx, subject in enumerate(subjects):
            results = self.result_svc.get_by_subject(subject.id)
            class_name = subject.class_.class_name if subject.class_ else "\u2014"
            color = accent_cycle[idx % len(accent_cycle)]

            # Card with left accent bar
            card_wrap = tk.Frame(cards_host, bg=color)
            card_wrap.pack(fill="x", pady=6)
            tk.Frame(card_wrap, bg=color, width=5).pack(side="left", fill="y")

            card = tk.Frame(card_wrap, bg=COLORS["card"], padx=18, pady=14,
                            highlightbackground=COLORS["border"], highlightthickness=1)
            card.pack(side="left", fill="both", expand=True)

            # Subject name + class row
            top = tk.Frame(card, bg=COLORS["card"])
            top.pack(fill="x")
            tk.Label(top, text=f"\U0001f4da  {subject.subject_name}",
                     font=FONTS["body_bold"], bg=COLORS["card"],
                     fg=color).pack(side="left")
            tk.Label(top, text=f"Class: {class_name}",
                     font=FONTS["small"], bg=COLORS["card"],
                     fg=COLORS["text_secondary"]).pack(side="right")

            if results:
                avg = sum(r.marks for r in results) / len(results)
                pass_c = sum(1 for r in results if r.marks >= 50)
                fail_c = len(results) - pass_c

                # Mini stat row
                stats_row = tk.Frame(card, bg=COLORS["card"])
                stats_row.pack(fill="x", pady=(10, 0))

                for s_text, s_val, s_fg in [
                    ("Students",    len(results),           COLORS["text_primary"]),
                    ("Avg Score",   f"{avg:.1f}%",          COLORS["accent"]),
                    ("Passed",      f"{pass_c}",            COLORS["success"]),
                    ("Failed",      f"{fail_c}",            COLORS["danger"]),
                ]:
                    box = tk.Frame(stats_row, bg=COLORS["bg_light"],
                                   highlightbackground=COLORS["border"],
                                   highlightthickness=1, padx=12, pady=6)
                    box.pack(side="left", padx=(0, 8))
                    tk.Label(box, text=str(s_val), font=("Segoe UI", 12, "bold"),
                             bg=COLORS["bg_light"], fg=s_fg).pack()
                    tk.Label(box, text=s_text, font=("Segoe UI", 8),
                             bg=COLORS["bg_light"], fg=COLORS["text_secondary"]).pack()
            else:
                tk.Label(card, text="No marks entered yet.",
                         font=FONTS["small"], bg=COLORS["card"],
                         fg=COLORS["text_secondary"]).pack(anchor="w", pady=(8, 0))
