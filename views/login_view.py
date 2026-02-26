"""
views/login_view.py - Secure login screen with separate registration pages
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, APP_TITLE, SessionLocal
from utils.ui_helpers import make_entry, center_window, show_error, make_divider, bind_hover
from services.auth_service import AuthService
from services.student_service import StudentService


class LoginView(tk.Toplevel):
    def __init__(self, master, on_login_success, on_back_home=None):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.on_back_home = on_back_home
        self.title("Sign In — " + APP_TITLE)
        self.resizable(True, True)
        self.configure(bg=COLORS["bg_dark"])
        # handle window close by returning to home if callback exists
        self.protocol("WM_DELETE_WINDOW", self._handle_close)
        self.geometry("520x680")
        self.minsize(460, 560)
        center_window(self, 520, 680)
        self._build()
        self.grab_set()

    # ── Scaffold ──────────────────────────────────────────────────────────────

    def _build(self):
        bg = COLORS["bg_dark"]

        # window close handler helpers
    
    def _handle_close(self):
        # when the user closes the window, navigate back to home if possible
        if self.on_back_home:
            self.on_back_home()
        else:
            self.master.destroy()

    def _go_home(self):
        if self.on_back_home:
            self.on_back_home()

    def _build(self):
        bg = COLORS["bg_dark"]

        # Coloured top accent
        tk.Frame(self, bg=COLORS["primary"], height=4).pack(fill="x")

        # Outer scroll-safe container
        self.outer = tk.Frame(self, bg=bg, padx=44, pady=20)
        self.outer.pack(fill="both", expand=True)

        # ── Fixed logo section ───────────────────────────────────────────────
        self._logo_frame = tk.Frame(self.outer, bg=bg)
        self._logo_frame.pack(fill="x")

        # optional home button
        if self.on_back_home:
            home_btn = tk.Button(
                self._logo_frame,
                text="🏠 Home",
                font=FONTS["small"],
                bg=bg,
                fg=COLORS["text_secondary"],
                relief="flat",
                cursor="hand2",
                command=self._go_home
            )
            home_btn.pack(side="right", padx=(0, 4))

        tk.Label(self._logo_frame, text="\U0001f393",
                 font=("Segoe UI Emoji", 44),
                 bg=bg, fg=COLORS["primary_light"]).pack()
        tk.Label(self._logo_frame, text="S.E.R.M.S",
                 font=FONTS["heading"], bg=bg, fg=COLORS["white"]).pack()
        tk.Label(self._logo_frame, text="School Examination Results Management System",
                 font=FONTS["small"], bg=bg, fg=COLORS["text_secondary"]).pack(pady=(2, 0))

        make_divider(self._logo_frame, pady=(12, 0))

        # ── Dynamic content area ─────────────────────────────────────────────
        self.content = tk.Frame(self.outer, bg=bg)
        self.content.pack(fill="both", expand=True, pady=(12, 0))

        self._show_welcome_card()

    def _clear_content(self):
        """Clear only the dynamic content area (logo persists)."""
        for w in self.content.winfo_children():
            w.destroy()

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _make_card(self, bg_card=None):
        """Return a styled card frame packed into content."""
        bg_card = bg_card or COLORS["card"]
        card = tk.Frame(self.content, bg=bg_card, padx=28, pady=22,
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", pady=(4, 0))
        return card

    def _back_btn(self, card):
        tk.Button(card, text="\u2190 Back to Welcome",
                  font=FONTS["small"], bg=card["bg"],
                  fg=COLORS["text_secondary"], relief="flat",
                  cursor="hand2",
                  command=self._show_welcome_card).pack(anchor="w", pady=(0, 14))

    def _field(self, card, label_text, attr_name, show=None):
        """Build a label + entry and store the StringVar as self.<attr_name>."""
        tk.Label(card, text=label_text, font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        var = tk.StringVar()
        setattr(self, attr_name, var)
        e = make_entry(card, textvariable=var, width=36, show=show)
        e.pack(fill="x", pady=(4, 12))
        return var

    def _primary_btn(self, card, text, color, cmd):
        btn = tk.Button(card, text=text, font=FONTS["body_bold"],
                        bg=color, fg="white",
                        activebackground=COLORS["primary_light"],
                        activeforeground="white",
                        relief="flat", cursor="hand2", pady=10,
                        command=cmd)
        btn.pack(fill="x", pady=(4, 0))
        bind_hover(btn, color, COLORS["primary_light"])
        return btn

    # ── Welcome card ──────────────────────────────────────────────────────────

    def _show_welcome_card(self):
        self._clear_content()

        card = self._make_card()

        # Title
        tk.Label(card, text="Welcome to S.E.R.M.S",
                 font=FONTS["subheading"], bg=card["bg"],
                 fg=COLORS["primary"]).pack(anchor="w", pady=(0, 6))
        tk.Label(card,
                 text="Manage results, track performance, and generate reports — all in one place.",
                 font=FONTS["body"], bg=card["bg"],
                 fg=COLORS["text_secondary"], justify="left", wraplength=400).pack(anchor="w")

        make_divider(card, pady=(14, 12))

        # Login button (prominent)
        self._primary_btn(card, "\U0001f510  Sign In to Your Account",
                          COLORS["primary"], self._show_login_form)

        # Register section
        tk.Label(card, text="New User? Register below:",
                 font=FONTS["body_bold"], bg=card["bg"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(18, 8))

        reg_frame = tk.Frame(card, bg=card["bg"])
        reg_frame.pack(fill="x")

        reg_items = [
            ("Register as Admin",   COLORS["warning"],   self._show_admin_register_form),
            ("Register as Teacher", COLORS["secondary"], self._show_teacher_register_form),
            ("Register as Student", COLORS["success"],   self._show_student_register_form),
        ]
        for text, color, cmd in reg_items:
            btn = tk.Button(reg_frame, text=text, font=FONTS["body_bold"],
                            bg=color, fg="white",
                            activebackground=COLORS["primary_light"],
                            activeforeground="white",
                            relief="flat", cursor="hand2", pady=8,
                            command=cmd)
            btn.pack(fill="x", pady=(0, 6))
            bind_hover(btn, color, COLORS["primary_light"])

    # ── Login form ────────────────────────────────────────────────────────────

    def _show_login_form(self):
        self._clear_content()
        card = self._make_card()
        self._back_btn(card)

        # Login type
        tk.Label(card, text="Login Type", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.login_type_var = tk.StringVar(value="email")
        type_frame = tk.Frame(card, bg=card["bg"])
        type_frame.pack(fill="x", pady=(4, 12))
        for txt, val in [("Email", "email"), ("Admission Number", "admission")]:
            tk.Radiobutton(
                type_frame, text=txt, variable=self.login_type_var, value=val,
                bg=card["bg"], fg=COLORS["text_primary"],
                selectcolor=COLORS["bg_medium"], activebackground=card["bg"],
                font=FONTS["body"],
                command=self._update_login_placeholder,
            ).pack(side="left", padx=(0, 16))

        # Identifier field
        self.user_label_widget = tk.Label(card, text="Email Address",
                                          font=FONTS["body_bold"],
                                          bg=card["bg"], fg=COLORS["text_secondary"])
        self.user_label_widget.pack(anchor="w")
        self.user_var = tk.StringVar()
        self.user_entry = make_entry(card, textvariable=self.user_var, width=36)
        self.user_entry.pack(fill="x", pady=(4, 12))

        # Password
        tk.Label(card, text="Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.pass_var = tk.StringVar()
        make_entry(card, textvariable=self.pass_var, width=36, show="\u2022").pack(
            fill="x", pady=(4, 18))

        self._primary_btn(card, "\U0001f510  Sign In", COLORS["primary"], self._do_login)
        self.bind("<Return>", lambda e: self._do_login())
        self.user_entry.focus_set()

    def _update_login_placeholder(self):
        if self.login_type_var.get() == "email":
            self.user_label_widget.config(text="Email Address")
        else:
            self.user_label_widget.config(text="Admission Number")
        self.user_var.set("")
        self.user_entry.delete(0, tk.END)

    # ── Registration forms ────────────────────────────────────────────────────

    def _show_admin_register_form(self):
        self._build_registration_form("Admin", COLORS["warning"])

    def _show_teacher_register_form(self):
        self._build_registration_form("Teacher", COLORS["secondary"])

    def _show_student_register_form(self):
        self._build_registration_form("Student", COLORS["success"])

    def _build_registration_form(self, user_type, color):
        self._clear_content()
        card = self._make_card()
        self._back_btn(card)

        # Coloured header strip
        hdr = tk.Frame(card, bg=color, padx=12, pady=8)
        hdr.pack(fill="x", pady=(0, 14))
        tk.Label(hdr, text=f"Register as {user_type}",
                 font=FONTS["body_bold"], bg=color, fg="white").pack(anchor="w")

        if user_type == "Student":
            self._build_student_fields(card, color)
        else:
            self._build_user_fields(card, user_type, color)

    def _build_user_fields(self, card, user_type, color):
        self._field(card, "Full Name", "_reg_name")
        self._field(card, "Email Address", "_reg_email")
        self._field(card, "Password", "_reg_pass", show="\u2022")
        self._field(card, "Confirm Password", "_reg_confirm", show="\u2022")
        self._primary_btn(card, f"Create {user_type} Account", color,
                          lambda: self._do_register(user_type,
                                                    self._reg_name, self._reg_email,
                                                    self._reg_pass, self._reg_confirm))

    def _build_student_fields(self, card, color):
        self._field(card, "Admission Number", "_reg_adm")
        self._field(card, "First Name", "_reg_first")
        self._field(card, "Last Name", "_reg_last")

        tk.Label(card, text="Gender", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self._reg_gender = tk.StringVar()
        ttk.Combobox(card, textvariable=self._reg_gender,
                     values=["Male", "Female", "Other"],
                     width=34, state="readonly").pack(fill="x", pady=(4, 12))

        self._field(card, "Password", "_reg_pass", show="\u2022")
        self._field(card, "Confirm Password", "_reg_confirm", show="\u2022")

        self._primary_btn(card, "Create Student Account", color,
                          lambda: self._do_student_register(
                              self._reg_adm, self._reg_first, self._reg_last,
                              self._reg_gender, self._reg_pass, self._reg_confirm))

    # ── Auth actions ──────────────────────────────────────────────────────────

    def _do_login(self):
        user_input = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        if not user_input or not password:
            show_error("Validation", "Please enter both credentials.")
            return
        if self.login_type_var.get() == "admission":
            self.on_login_success("", password, admission_number=user_input)
        else:
            self.on_login_success(user_input, password)

    def _do_register(self, user_type, name_var, email_var, pass_var, confirm_var):
        name = name_var.get().strip()
        email = email_var.get().strip()
        password = pass_var.get().strip()
        confirm = confirm_var.get().strip()
        if not name or not email or not password:
            show_error("Validation", "All fields are required.")
            return
        if password != confirm:
            show_error("Validation", "Passwords do not match.")
            return
        if len(password) < 6:
            show_error("Validation", "Password must be at least 6 characters.")
            return
        db = SessionLocal()
        try:
            auth_svc = AuthService(db)
            if user_type == "Admin":
                auth_svc.create_admin(name, email, password)
            else:
                auth_svc.create_teacher(name, email, password)
            from tkinter import messagebox
            messagebox.showinfo("Success", f"{user_type} registered successfully! Please log in.")
            self._show_welcome_card()
        except Exception as e:
            show_error("Registration Error", str(e))
        finally:
            db.close()

    def _do_student_register(self, adm_var, first_var, last_var,
                              gender_var, pass_var, confirm_var):
        adm = adm_var.get().strip()
        first = first_var.get().strip()
        last = last_var.get().strip()
        gender = gender_var.get().strip()
        password = pass_var.get().strip()
        confirm = confirm_var.get().strip()
        if not all([adm, first, last, gender, password]):
            show_error("Validation", "All fields are required.")
            return
        if password != confirm:
            show_error("Validation", "Passwords do not match.")
            return
        if len(password) < 6:
            show_error("Validation", "Password must be at least 6 characters.")
            return
        db = SessionLocal()
        try:
            student_svc = StudentService(db)
            password_hash = AuthService.hash_password(password)
            student_svc.create(
                admission_number=adm, first_name=first, last_name=last,
                gender=gender, class_id=None, password_hash=password_hash)
            from tkinter import messagebox
            messagebox.showinfo("Success",
                                "Student registered successfully!\nPlease log in with your admission number.")
            self._show_welcome_card()
        except Exception as e:
            show_error("Registration Error", str(e))
        finally:
            db.close()
