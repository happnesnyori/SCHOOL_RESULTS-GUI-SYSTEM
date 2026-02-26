"""
views/admin_dashboard.py - Full admin dashboard
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from views.base_dashboard import BaseDashboard
from views.students_panel import StudentsPanel
from views.teachers_panel import TeachersPanel
from views.classes_subjects_panel import ClassesSubjectsPanel
from views.results_panel import ResultsPanel
from views.analytics_panel import AnalyticsPanel
from views.reports_panel import ReportsPanel
from services import (
    StudentService, TeacherService, ClassService,
    SubjectService, ResultService, ReportService, AnalyticsService
)
from config import SessionLocal


class AdminDashboard(BaseDashboard):
    def __init__(self, master, user, logout_callback):
        self._db = SessionLocal()
        self._init_services()
        self.NAV_ITEMS = [
            ("Dashboard",   self._show_overview),
            ("Students",    self._show_students),
            ("Teachers",    self._show_teachers),
            ("Classes & Subjects", self._show_classes),
            ("Results",     self._show_results),
            ("Analytics",   self._show_analytics),
            ("Reports",     self._show_reports),
        ]
        super().__init__(master, user, "ADMIN", logout_callback)
        # Auto-load overview
        self._nav_click("Dashboard", self._show_overview)

    def _init_services(self):
        db = self._db
        self.student_svc = StudentService(db)
        self.teacher_svc = TeacherService(db)
        self.class_svc = ClassService(db)
        self.subject_svc = SubjectService(db)
        self.result_svc = ResultService(db)
        self.report_svc = ReportService(db)
        self.analytics_svc = AnalyticsService(db)

    def _show_overview(self):
        self.update_section_title("Dashboard Overview")
        f = self.get_content_frame()
        stats = self.analytics_svc.total_stats()
        from utils.ui_helpers import make_stat_card, make_divider, bind_hover

        # ── Welcome header ───────────────────────────────────────────────────
        header = tk.Frame(f, bg=COLORS["bg_medium"], pady=20)
        header.pack(fill="x", padx=24)
        tk.Label(header, text=f"Welcome back, {self.user.full_name} \U0001f44b",
                 font=FONTS["heading"], bg=COLORS["bg_medium"],
                 fg=COLORS["white"]).pack(anchor="w")
        tk.Label(header,
                 text="Here's an overview of your school's examination results.",
                 font=FONTS["body"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))

        make_divider(f, padx=24, pady=(0, 4))

        # ── Stat cards ───────────────────────────────────────────────────────
        cards_row = tk.Frame(f, bg=COLORS["bg_medium"])
        cards_row.pack(fill="x", padx=24, pady=16)

        stat_items = [
            ("\U0001f465", stats["total_students"], "Total Students",  COLORS["primary"]),
            ("\U0001f4dd", stats["total_results"],  "Total Results",   COLORS["secondary"]),
            ("\u2b50",     f"{stats['avg_marks']}%", "Average Score",  COLORS["success"]),
        ]
        for i, (icon, val, label, color) in enumerate(stat_items):
            card = make_stat_card(cards_row, icon, val, label, color)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            cards_row.columnconfigure(i, weight=1)

        make_divider(f, padx=24, pady=(4, 0))

        # ── Quick actions ────────────────────────────────────────────────────
        quick = tk.Frame(f, bg=COLORS["bg_medium"])
        quick.pack(fill="x", padx=24, pady=16)
        tk.Label(quick, text="Quick Actions", font=FONTS["subheading"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 12))

        btn_row = tk.Frame(quick, bg=COLORS["bg_medium"])
        btn_row.pack(fill="x")

        actions = [
            ("\U0001f465", "Manage Students",  "Students",  self._show_students,  COLORS["primary"]),
            ("\U0001f4dd", "Enter Marks",       "Results",   self._show_results,   COLORS["secondary"]),
            ("\U0001f4c8", "View Analytics",    "Analytics", self._show_analytics, COLORS["accent"]),
            ("\U0001f4c4", "Generate Reports",  "Reports",   self._show_reports,   COLORS["success"]),
        ]
        for i, (icon, text, section, callback, color) in enumerate(actions):
            btn = tk.Button(
                btn_row,
                text=f"{icon}\n{text}",
                font=FONTS["body_bold"],
                bg=COLORS["card"], fg=color,
                activebackground=COLORS["hover"],
                activeforeground=COLORS["white"],
                relief="flat", cursor="hand2",
                padx=20, pady=20,
                justify="center",
                highlightbackground=color, highlightthickness=1,
                command=lambda s=section, cb=callback: self._nav_click(s, cb),
            )
            btn.grid(row=0, column=i, padx=6, sticky="ew")
            btn_row.columnconfigure(i, weight=1)
            bind_hover(btn, COLORS["card"], COLORS["hover"],
                       normal_fg=color, hover_fg=COLORS["white"])

    def _show_students(self):
        self.update_section_title("Student Management")
        StudentsPanel(self.get_content_frame(), self.student_svc, self.class_svc)

    def _show_teachers(self):
        self.update_section_title("Teacher Management")
        TeachersPanel(self.get_content_frame(), self.teacher_svc, self.subject_svc)

    def _show_classes(self):
        self.update_section_title("Classes & Subjects")
        ClassesSubjectsPanel(self.get_content_frame(), self.class_svc,
                             self.subject_svc, self.teacher_svc)

    def _show_results(self):
        self.update_section_title("Results Management")
        ResultsPanel(self.get_content_frame(), self.result_svc,
                     self.student_svc, self.subject_svc, self.class_svc)

    def _show_analytics(self):
        self.update_section_title("Analytics Dashboard")
        AnalyticsPanel(self.get_content_frame(), self.analytics_svc)

    def _show_reports(self):
        self.update_section_title("Report Generation")
        ReportsPanel(self.get_content_frame(), self.report_svc,
                     self.student_svc, self.class_svc)
