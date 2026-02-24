"""
views/base_dashboard.py - Base dashboard layout with sidebar navigation
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, APP_TITLE


class BaseDashboard(tk.Frame):
    """
    Base class providing a two-pane layout:
    - Left sidebar with navigation buttons
    - Right content area where sub-frames are swapped
    """

    NAV_ITEMS = []  # To be overridden by subclasses: list of (label, callback)

    def __init__(self, master, user, role, logout_callback):
        super().__init__(master, bg=COLORS["bg_medium"])
        self.user = user
        self.role = role
        self.logout_callback = logout_callback
        self._current_section = None
        self.pack(fill="both", expand=True)
        self._build_layout()
        self._build_sidebar()
        self._build_topbar()

    # ── Layout skeleton ──────────────────────────────────────────────────────

    def _build_layout(self):
        self.sidebar_frame = tk.Frame(self, bg=COLORS["sidebar"], width=220)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.main_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.topbar_frame = tk.Frame(self.main_frame, bg=COLORS["bg_dark"], height=54)
        self.topbar_frame.pack(side="top", fill="x")
        self.topbar_frame.pack_propagate(False)

        self.content_frame = tk.Frame(self.main_frame, bg=COLORS["bg_medium"])
        self.content_frame.pack(side="top", fill="both", expand=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        # Branding
        brand = tk.Frame(self.sidebar_frame, bg=COLORS["primary"], pady=14)
        brand.pack(fill="x")
        tk.Label(brand, text="School Results", font=FONTS["subheading"],
                 bg=COLORS["primary"], fg=COLORS["white"]).pack()
        tk.Label(brand, text=f"• {self.role} Panel", font=FONTS["small"],
                 bg=COLORS["primary"], fg="#b3bce0").pack()

        # Separator
        tk.Frame(self.sidebar_frame, bg=COLORS["border"], height=1).pack(fill="x")

        # Nav items
        self.nav_buttons = {}
        nav_container = tk.Frame(self.sidebar_frame, bg=COLORS["sidebar"])
        nav_container.pack(fill="x", pady=8)

        for label, callback in self.NAV_ITEMS:
            btn = tk.Button(
                nav_container, text=f"  {label}",
                font=FONTS["body"], bg=COLORS["sidebar"],
                fg=COLORS["text_secondary"],
                activebackground=COLORS["hover"],
                activeforeground=COLORS["white"],
                relief="flat", anchor="w",
                cursor="hand2", pady=10,
                command=lambda cb=callback, lbl=label: self._nav_click(lbl, cb),
            )
            btn.pack(fill="x", padx=6, pady=1)
            self.nav_buttons[label] = btn

        # Logout at bottom
        tk.Frame(self.sidebar_frame, bg=COLORS["border"], height=1).pack(
            fill="x", side="bottom", pady=4)
        tk.Button(
            self.sidebar_frame, text="  Logout",
            font=FONTS["body"], bg=COLORS["sidebar"],
            fg=COLORS["danger"], activebackground=COLORS["hover"],
            activeforeground=COLORS["danger"],
            relief="flat", anchor="w", cursor="hand2", pady=10,
            command=self.logout_callback,
        ).pack(fill="x", padx=6, side="bottom")

    def _nav_click(self, label, callback):
        # Reset all button styles
        for lbl, btn in self.nav_buttons.items():
            btn.configure(bg=COLORS["sidebar"], fg=COLORS["text_secondary"])
        # Highlight active
        self.nav_buttons[label].configure(
            bg=COLORS["primary"], fg=COLORS["white"])
        self._current_section = label
        # Clear content and call the section builder
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        callback()

    # ── Topbar ───────────────────────────────────────────────────────────────

    def _build_topbar(self):
        # Section title (updated dynamically)
        self.section_title_lbl = tk.Label(
            self.topbar_frame, text="Dashboard",
            font=FONTS["subheading"], bg=COLORS["bg_dark"],
            fg=COLORS["white"],
        )
        self.section_title_lbl.pack(side="left", padx=20)

        # User badge
        user_badge = tk.Frame(self.topbar_frame, bg=COLORS["bg_dark"])
        user_badge.pack(side="right", padx=16)
        tk.Label(
            user_badge, text=self.user.full_name,
            font=FONTS["body_bold"], bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(side="right")

    def update_section_title(self, title: str):
        self.section_title_lbl.configure(text=title)

    def get_content_frame(self):
        return self.content_frame
