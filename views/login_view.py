"""
views/login_view.py - Secure login screen
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, APP_TITLE
from utils.ui_helpers import make_label, make_entry, center_window, show_error


class LoginView(tk.Toplevel):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.title("Login — " + APP_TITLE)
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_dark"])
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        center_window(self, 440, 520)
        self._build()
        self.grab_set()

    def _build(self):
        bg = COLORS["bg_dark"]
        card_bg = COLORS["card"]
        # Outer padding
        outer = tk.Frame(self, bg=bg, padx=40, pady=40)
        outer.pack(fill="both", expand=True)

        # Logo / title area
        tk.Label(outer, text="🎓", font=("Segoe UI Emoji", 42), bg=bg,
                 fg=COLORS["primary_light"]).pack(pady=(0, 8))
        tk.Label(outer, text="School Results System",
                 font=FONTS["heading"], bg=bg, fg=COLORS["white"]).pack()
        tk.Label(outer, text="Sign in to your account",
                 font=FONTS["small"], bg=bg, fg=COLORS["text_secondary"]).pack(pady=(4, 24))

        # Card
        card = tk.Frame(outer, bg=card_bg, padx=30, pady=28,
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x")

        # Email
        tk.Label(card, text="Email Address", font=FONTS["body_bold"],
                 bg=card_bg, fg=COLORS["text_secondary"]).pack(anchor="w")
        self.email_var = tk.StringVar()
        email_entry = make_entry(card, textvariable=self.email_var, width=35)
        email_entry.configure(bg=COLORS["bg_medium"])
        email_entry.pack(fill="x", pady=(4, 14))

        # Password
        tk.Label(card, text="Password", font=FONTS["body_bold"],
                 bg=card_bg, fg=COLORS["text_secondary"]).pack(anchor="w")
        self.pass_var = tk.StringVar()
        pass_entry = make_entry(card, textvariable=self.pass_var, width=35, show="•")
        pass_entry.configure(bg=COLORS["bg_medium"])
        pass_entry.pack(fill="x", pady=(4, 20))

        # Login button
        login_btn = tk.Button(
            card, text="Sign In", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["white"],
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=8,
            command=self._do_login,
        )
        login_btn.pack(fill="x")

        # Bind Enter key
        self.bind("<Return>", lambda e: self._do_login())
        email_entry.focus_set()

        # Footer hint
        tk.Label(outer, text="Default admin: admin@school.edu / Admin@1234",
                 font=FONTS["small"], bg=bg, fg=COLORS["text_secondary"]).pack(pady=(16, 0))

    def _do_login(self):
        email = self.email_var.get().strip()
        password = self.pass_var.get().strip()
        if not email or not password:
            show_error("Validation", "Please enter both email and password.")
            return
        self.on_login_success(email, password)
