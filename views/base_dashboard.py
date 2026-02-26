"""
views/base_dashboard.py - Base dashboard layout with polished sidebar navigation
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, APP_TITLE, NAV_ICONS, ROLE_COLORS


class BaseDashboard(tk.Frame):
    """
    Base class providing a two-pane layout:
    - Left sidebar  : branding, nav items with icon + left-accent indicator,
                      user-avatar panel, logout button
    - Right area    : topbar (title + role badge) + swappable content frame
    """

    NAV_ITEMS = []  # Override in subclasses: list of (label, callback)

    def __init__(self, master, user, role, logout_callback):
        super().__init__(master, bg=COLORS["bg_medium"])
        self.user = user
        self.role = role
        self.logout_callback = logout_callback
        self._current_section = None
        self.nav_buttons = {}
        self.nav_accents = {}
        self.pack(fill="both", expand=True)
        self._build_layout()
        self._build_sidebar()
        self._build_topbar()

    # ── Layout skeleton ──────────────────────────────────────────────────────

    def _build_layout(self):
        self.sidebar_frame = tk.Frame(self, bg=COLORS["sidebar"], width=228)
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
        sb = self.sidebar_frame

        # ── Brand header ────────────────────────────────────────────────────
        brand = tk.Frame(sb, bg=COLORS["primary"], pady=16)
        brand.pack(fill="x")
        tk.Label(brand, text="\U0001f393", font=("Segoe UI Emoji", 26),
                 bg=COLORS["primary"], fg="white").pack()
        tk.Label(brand, text="S.E.R.M.S", font=FONTS["subheading"],
                 bg=COLORS["primary"], fg="white").pack(pady=(4, 0))
        tk.Label(brand, text="Results Management", font=("Segoe UI", 8),
                 bg=COLORS["primary"], fg="#b3bce0").pack()

        tk.Frame(sb, bg=COLORS["border"], height=1).pack(fill="x")

        # ── "MENU" label ────────────────────────────────────────────────────
        tk.Label(sb, text="MENU", font=("Segoe UI", 7, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["text_secondary"],
                 anchor="w").pack(fill="x", padx=16, pady=(12, 4))

        # ── Nav items ───────────────────────────────────────────────────────
        nav_container = tk.Frame(sb, bg=COLORS["sidebar"])
        nav_container.pack(fill="x", pady=(0, 4))

        for label, callback in self.NAV_ITEMS:
            icon = NAV_ICONS.get(label, "\u25b8")
            item_frame = tk.Frame(nav_container, bg=COLORS["sidebar"])
            item_frame.pack(fill="x", padx=4, pady=1)

            # Left accent indicator bar (3 px wide)
            accent = tk.Frame(item_frame, bg=COLORS["sidebar"], width=3)
            accent.pack(side="left", fill="y")

            btn = tk.Button(
                item_frame,
                text=f"  {icon}  {label}",
                font=FONTS["body"],
                bg=COLORS["sidebar"],
                fg=COLORS["text_secondary"],
                activebackground=COLORS["hover"],
                activeforeground=COLORS["white"],
                relief="flat", anchor="w",
                cursor="hand2", pady=9,
                command=lambda cb=callback, lbl=label: self._nav_click(lbl, cb),
            )
            btn.pack(side="left", fill="x", expand=True)

            # Hover bindings (skip if item is currently active)
            def _make_hover(b, a):
                def _enter(e):
                    if a["bg"] == COLORS["sidebar"]:
                        b.configure(bg=COLORS["hover"], fg=COLORS["white"])
                def _leave(e):
                    if a["bg"] == COLORS["sidebar"]:
                        b.configure(bg=COLORS["sidebar"], fg=COLORS["text_secondary"])
                b.bind("<Enter>", _enter)
                b.bind("<Leave>", _leave)
            _make_hover(btn, accent)

            self.nav_buttons[label] = btn
            self.nav_accents[label] = accent

        # ── Bottom section (packed from bottom up) ───────────────────────────

        # Logout
        tk.Frame(sb, bg=COLORS["border"], height=1).pack(
            side="bottom", fill="x")

        logout_wrap = tk.Frame(sb, bg=COLORS["sidebar"])
        logout_wrap.pack(side="bottom", fill="x", padx=4)

        lo_accent = tk.Frame(logout_wrap, bg=COLORS["sidebar"], width=3)
        lo_accent.pack(side="left", fill="y")

        lo_btn = tk.Button(
            logout_wrap,
            text="  \U0001f6aa  Sign Out",
            font=FONTS["body"], bg=COLORS["sidebar"],
            fg=COLORS["danger"],
            activebackground=COLORS["hover"],
            activeforeground=COLORS["danger"],
            relief="flat", anchor="w", cursor="hand2", pady=10,
            command=self.logout_callback,
        )
        lo_btn.pack(side="left", fill="x", expand=True)

        def _lo_enter(e):
            lo_btn.configure(bg=COLORS["hover"])
            lo_accent.configure(bg=COLORS["danger"])
        def _lo_leave(e):
            lo_btn.configure(bg=COLORS["sidebar"])
            lo_accent.configure(bg=COLORS["sidebar"])
        lo_btn.bind("<Enter>", _lo_enter)
        lo_btn.bind("<Leave>", _lo_leave)

        # Divider above user info
        tk.Frame(sb, bg=COLORS["border"], height=1).pack(
            side="bottom", fill="x")

        # User info panel
        user_panel = tk.Frame(sb, bg=COLORS["sidebar"], pady=10, padx=10)
        user_panel.pack(side="bottom", fill="x")

        # Avatar (initials circle)
        name = getattr(self.user, "full_name", "User")
        initials = "".join(w[0].upper() for w in name.split()[:2]) or "U"
        role_color = ROLE_COLORS.get(self.role, COLORS["primary_light"])

        avatar = tk.Label(user_panel, text=initials, font=FONTS["body_bold"],
                          bg=role_color, fg="white", width=3, pady=5)
        avatar.pack(side="left")

        info = tk.Frame(user_panel, bg=COLORS["sidebar"])
        info.pack(side="left", padx=(8, 0), fill="x", expand=True)

        display_name = name[:20] + ("\u2026" if len(name) > 20 else "")
        tk.Label(info, text=display_name, font=("Segoe UI", 9, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["text_primary"],
                 anchor="w").pack(anchor="w")
        tk.Label(info, text=self.role, font=("Segoe UI", 8),
                 bg=COLORS["sidebar"], fg=role_color,
                 anchor="w").pack(anchor="w")

    # ── Nav click ─────────────────────────────────────────────────────────────

    def _nav_click(self, label, callback):
        # Deactivate all
        for lbl, btn in self.nav_buttons.items():
            btn.configure(bg=COLORS["sidebar"], fg=COLORS["text_secondary"])
            self.nav_accents[lbl].configure(bg=COLORS["sidebar"])
        # Activate selected
        self.nav_buttons[label].configure(bg=COLORS["hover"], fg=COLORS["white"])
        self.nav_accents[label].configure(bg=COLORS["primary_light"])
        self._current_section = label
        # Swap content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        callback()

    # ── Topbar ────────────────────────────────────────────────────────────────

    def _build_topbar(self):
        tb = self.topbar_frame

        # Bottom separator
        tk.Frame(tb, bg=COLORS["border"], height=1).pack(side="bottom", fill="x")

        # Left: section title
        left = tk.Frame(tb, bg=COLORS["bg_dark"])
        left.pack(side="left", fill="y", padx=(20, 0))

        self.section_title_lbl = tk.Label(
            left, text="Dashboard",
            font=FONTS["subheading"], bg=COLORS["bg_dark"],
            fg=COLORS["white"])
        self.section_title_lbl.pack(side="left")

        # Right: user name + role badge
        right = tk.Frame(tb, bg=COLORS["bg_dark"])
        right.pack(side="right", fill="y", padx=16)

        role_color = ROLE_COLORS.get(self.role, COLORS["primary"])
        role_badge = tk.Label(right, text=f" {self.role} ",
                              font=("Segoe UI", 8, "bold"),
                              bg=role_color, fg="white", pady=2, padx=6)
        role_badge.pack(side="right", pady=17)

        tk.Frame(right, bg=COLORS["border"], width=1).pack(
            side="right", fill="y", padx=10, pady=14)

        tk.Label(right, text=getattr(self.user, "full_name", ""),
                 font=FONTS["body_bold"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_primary"]).pack(side="right")

    def update_section_title(self, title: str):
        self.section_title_lbl.configure(text=title)

    def get_content_frame(self):
        return self.content_frame
