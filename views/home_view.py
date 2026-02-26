"""
views/home_view.py - Welcoming home/landing page
School Examination Results Management System
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, APP_TITLE
from utils.ui_helpers import center_window, bind_hover, make_divider


class HomePage(tk.Toplevel):
    """Welcoming home page — landing screen before login/register."""

    def __init__(self, master, on_login_click, on_register_click):
        super().__init__(master)
        self.on_login_click = on_login_click
        self.on_register_click = on_register_click

        self.title("Welcome — " + APP_TITLE)
        self.resizable(True, True)
        self.configure(bg=COLORS["bg_dark"])
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.geometry("860x720")
        self.minsize(680, 600)
        center_window(self, 860, 720)
        self._build()
        self.grab_set()

    # ── Main build ────────────────────────────────────────────────────────────

    def _build(self):
        bg = COLORS["bg_dark"]

        # Coloured accent strip at the very top
        tk.Frame(self, bg=COLORS["primary"], height=4).pack(fill="x")

        # Fixed hero + actions (always visible)
        fixed = tk.Frame(self, bg=bg)
        fixed.pack(fill="x", padx=32, pady=(20, 0))
        self._build_hero(fixed, bg)
        self._build_actions(fixed, bg)

        make_divider(self, padx=32, pady=0)

        # Scrollable features area
        scroll_host = tk.Frame(self, bg=bg)
        scroll_host.pack(fill="both", expand=True, padx=0, pady=0)

        canvas = tk.Canvas(scroll_host, bg=bg, highlightthickness=0)
        vscroll = ttk.Scrollbar(scroll_host, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(canvas, bg=bg)
        win_id = canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._build_features(self._inner, bg)
        self._build_roles(self._inner, bg)
        self._build_footer(self._inner, bg)

        self._inner.bind("<Configure>",
                         lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # ── Hero ──────────────────────────────────────────────────────────────────

    def _build_hero(self, parent, bg):
        hero = tk.Frame(parent, bg=bg)
        hero.pack(fill="x", pady=(0, 16))

        left = tk.Frame(hero, bg=bg)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="\U0001f393",
                 font=("Segoe UI Emoji", 56),
                 bg=bg, fg=COLORS["primary_light"]).pack(anchor="w")

        tk.Label(left, text="School Examination Results",
                 font=("Segoe UI", 26, "bold"),
                 bg=bg, fg=COLORS["white"]).pack(anchor="w", pady=(8, 0))
        tk.Label(left, text="Management System",
                 font=("Segoe UI", 16),
                 bg=bg, fg=COLORS["text_secondary"]).pack(anchor="w")

        tk.Label(left,
                 text="Empowering Education Through Data-Driven Insights",
                 font=("Segoe UI", 10, "italic"),
                 bg=bg, fg=COLORS["accent"]).pack(anchor="w", pady=(6, 0))

    # ── Action buttons ────────────────────────────────────────────────────────

    def _build_actions(self, parent, bg):
        actions = tk.Frame(parent, bg=bg)
        actions.pack(fill="x", pady=(0, 20))

        btn_row = tk.Frame(actions, bg=bg)
        btn_row.pack(anchor="w")

        login_btn = tk.Button(
            btn_row,
            text="  \U0001f510  Sign In to Your Account  ",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["primary"], fg=COLORS["white"],
            activebackground=COLORS["primary_light"],
            activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=10, padx=6,
            command=self.on_login_click,
        )
        login_btn.pack(side="left", padx=(0, 12))
        bind_hover(login_btn, COLORS["primary"], COLORS["primary_light"])

        reg_btn = tk.Button(
            btn_row,
            text="  \U0001f4dd  Create New Account  ",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["bg_light"], fg=COLORS["text_primary"],
            activebackground=COLORS["hover"],
            activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=10, padx=6,
            highlightbackground=COLORS["border"], highlightthickness=1,
            command=self.on_register_click,
        )
        reg_btn.pack(side="left")
        bind_hover(reg_btn, COLORS["bg_light"], COLORS["hover"])

        tk.Label(actions,
                 text="Register as Admin, Teacher, or Student using the Create Account button.",
                 font=FONTS["small"], bg=bg, fg=COLORS["text_secondary"]).pack(anchor="w", pady=(8, 0))

    # ── Feature cards ─────────────────────────────────────────────────────────

    def _build_features(self, parent, bg):
        section = tk.Frame(parent, bg=bg)
        section.pack(fill="x", padx=32, pady=(24, 0))

        tk.Label(section, text="Everything You Need to Manage School Results",
                 font=FONTS["subheading"], bg=bg, fg=COLORS["white"]).pack(anchor="w")
        tk.Label(section, text="A complete toolkit for modern school administration.",
                 font=FONTS["body"], bg=bg, fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 16))

        features = [
            ("\U0001f4ca", "Performance Tracking",
             "Monitor academic progress across all subjects and terms."),
            ("\U0001f4dd", "Results Management",
             "Enter, update, and manage examination results with ease."),
            ("\U0001f4c4", "Report Generation",
             "Create professional PDF report cards and class summaries."),
            ("\U0001f4c8", "Analytics & Insights",
             "Visualise trends with interactive charts and graphs."),
            ("\U0001f465", "Student Management",
             "Manage student profiles, enrolments, and class assignments."),
            ("\U0001f512", "Secure Access Control",
             "Role-based access for Admins, Teachers, and Students."),
        ]

        grid = tk.Frame(section, bg=bg)
        grid.pack(fill="x")

        for i, (icon, title, desc) in enumerate(features):
            col = i % 3
            row = i // 3

            # Card with coloured top accent
            accent_colors = [
                COLORS["primary"], COLORS["secondary"], COLORS["accent"],
                COLORS["success"], COLORS["warning"], COLORS["primary_light"],
            ]
            card_color = accent_colors[i % len(accent_colors)]

            card_wrap = tk.Frame(grid, bg=card_color)
            card_wrap.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

            top_bar = tk.Frame(card_wrap, bg=card_color, height=4)
            top_bar.pack(fill="x")

            card_inner = tk.Frame(card_wrap, bg=COLORS["card"], padx=16, pady=14,
                                  highlightbackground=COLORS["border"], highlightthickness=1)
            card_inner.pack(fill="both", expand=True)

            tk.Label(card_inner, text=icon, font=("Segoe UI Emoji", 22),
                     bg=COLORS["card"], fg=card_color).pack(anchor="w")
            tk.Label(card_inner, text=title, font=FONTS["body_bold"],
                     bg=COLORS["card"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(4, 2))
            tk.Label(card_inner, text=desc, font=FONTS["small"],
                     bg=COLORS["card"], fg=COLORS["text_secondary"],
                     wraplength=200, justify="left").pack(anchor="w")

            grid.columnconfigure(col, weight=1)
            grid.rowconfigure(row, weight=1)

    # ── Role cards ────────────────────────────────────────────────────────────

    def _build_roles(self, parent, bg):
        section = tk.Frame(parent, bg=bg)
        section.pack(fill="x", padx=32, pady=(28, 0))

        make_divider(section, pady=(0, 20))

        tk.Label(section, text="Who Uses S.E.R.M.S?",
                 font=FONTS["subheading"], bg=bg, fg=COLORS["white"]).pack(anchor="w")
        tk.Label(section,
                 text="Three distinct roles, each with tailored access and capabilities.",
                 font=FONTS["body"], bg=bg,
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 14))

        roles = [
            ("\U0001f6e1\ufe0f", "Administrator",
             "Full system control: manage students, teachers, results, classes, and reports.",
             COLORS["primary"]),
            ("\U0001f9d1\u200d\U0001f3eb", "Teacher",
             "Enter marks for assigned subjects and monitor class-level performance.",
             COLORS["secondary"]),
            ("\U0001f393", "Student",
             "View personal results, grades, and academic report cards.",
             COLORS["success"]),
        ]

        role_row = tk.Frame(section, bg=bg)
        role_row.pack(fill="x")

        for i, (icon, role_name, desc, color) in enumerate(roles):
            card = tk.Frame(role_row, bg=COLORS["card"], padx=20, pady=18,
                            highlightbackground=color, highlightthickness=2)
            card.grid(row=0, column=i, padx=6, sticky="nsew")

            circle = tk.Label(card, text=icon, font=("Segoe UI Emoji", 28),
                              bg=color, fg="white", padx=10, pady=6)
            circle.pack(anchor="w")

            tk.Label(card, text=role_name, font=FONTS["body_bold"],
                     bg=COLORS["card"], fg=color).pack(anchor="w", pady=(10, 2))
            tk.Label(card, text=desc, font=FONTS["small"],
                     bg=COLORS["card"], fg=COLORS["text_secondary"],
                     wraplength=210, justify="left").pack(anchor="w")

            role_row.columnconfigure(i, weight=1)

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self, parent, bg):
        footer = tk.Frame(parent, bg=bg)
        footer.pack(fill="x", padx=32, pady=(28, 16))

        make_divider(footer, pady=(0, 10))

        tk.Label(footer,
                 text="\u00a9 2025 School Examination Results Management System  \u2022  All Rights Reserved",
                 font=FONTS["small"], bg=bg, fg=COLORS["text_secondary"]).pack()
        tk.Label(footer,
                 text="For support, please contact your system administrator.",
                 font=("Segoe UI", 8), bg=bg, fg=COLORS["text_secondary"]).pack()
