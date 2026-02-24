"""
views/login_view.py - Secure login screen with separate registration pages
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, APP_TITLE, SessionLocal
from utils.ui_helpers import make_label, make_entry, center_window, show_error
from services.auth_service import AuthService
from services.student_service import StudentService


class LoginView(tk.Toplevel):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.title("Login — " + APP_TITLE)
        self.resizable(True, True)
        self.configure(bg=COLORS["bg_dark"])
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        
        # Set window size and allow resizing
        self.geometry("500x650")
        self.minsize(450, 550)
        center_window(self, 500, 650)
        
        self._build()
        self.grab_set()

    def _build(self):
        bg = COLORS["bg_dark"]
        
        # Main container
        self.outer = tk.Frame(self, bg=bg, padx=40, pady=30)
        self.outer.pack(fill="both", expand=True)

        # Logo / title area
        tk.Label(self.outer, text="🎓", font=("Segoe UI Emoji", 48), bg=bg,
                 fg=COLORS["primary_light"]).pack(pady=(10, 5))
        tk.Label(self.outer, text="School Examination Results",
                 font=FONTS["heading"], bg=bg, fg=COLORS["white"]).pack()
        tk.Label(self.outer, text="Management System",
                 font=FONTS["subheading"], bg=bg, fg=COLORS["text_secondary"]).pack(pady=(0, 20))

        # Show welcome card initially
        self._show_welcome_card()

    def _clear_outer(self):
        """Clear content inside outer frame"""
        for widget in self.outer.winfo_children():
            widget.destroy()

    def _show_welcome_card(self):
        """Show welcome card with options"""
        self._clear_outer()
        
        bg = COLORS["bg_dark"]
        
        # Welcome card
        card = tk.Frame(self.outer, bg=COLORS["card"], padx=30, pady=25,
                       highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", pady=20)
        
        tk.Label(card, text="Welcome to S.E.R.M.S",
                 font=FONTS["subheading"], bg=COLORS["card"],
                 fg=COLORS["primary"]).pack(anchor="w", pady=(0, 10))
        
        tk.Label(card, 
                 text="Manage student results efficiently, track academic performance, and generate detailed reports.",
                 font=FONTS["body"], bg=COLORS["card"],
                 fg=COLORS["text_secondary"], justify="left", wraplength=380).pack(anchor="w")
        
        # Buttons
        btn_frame = tk.Frame(card, bg=COLORS["card"])
        btn_frame.pack(fill="x", pady=(20, 0))
        
        login_btn = tk.Button(
            btn_frame, text="Login", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["white"],
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=10,
            command=self._show_login_form,
        )
        login_btn.pack(fill="x", pady=(0, 10))
        
        # Registration section
        tk.Label(card, text="New User? Register below:",
                 font=FONTS["body"], bg=COLORS["card"],
                 fg=COLORS["text_secondary"]).pack(anchor="w", pady=(15, 8))
        
        # Registration type selector
        reg_frame = tk.Frame(card, bg=COLORS["card"])
        reg_frame.pack(fill="x")
        
        tk.Button(
            reg_frame, text="Register as Admin", font=FONTS["body_bold"],
            bg=COLORS["warning"], fg="white",
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=8,
            command=self._show_admin_register_form,
        ).pack(fill="x", pady=(0, 8))
        
        tk.Button(
            reg_frame, text="Register as Teacher", font=FONTS["body_bold"],
            bg=COLORS["secondary"], fg="white",
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=8,
            command=self._show_teacher_register_form,
        ).pack(fill="x", pady=(0, 8))
        
        tk.Button(
            reg_frame, text="Register as Student", font=FONTS["body_bold"],
            bg=COLORS["success"], fg="white",
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=8,
            command=self._show_student_register_form,
        ).pack(fill="x")

    def _show_login_form(self):
        """Show login form"""
        self._clear_outer()
        
        bg = COLORS["bg_dark"]
        
        # Login card
        card = tk.Frame(self.outer, bg=COLORS["card"], padx=30, pady=25,
                       highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x")
        
        # Back button
        tk.Button(card, text="← Back to Welcome", font=FONTS["small"],
                  bg=COLORS["card"], fg=COLORS["text_secondary"],
                  relief="flat", cursor="hand2",
                  command=self._show_welcome_card).pack(anchor="w", pady=(0, 15))
        
        # Login type selector
        tk.Label(card, text="Login Type", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.login_type_var = tk.StringVar(value="email")
        type_frame = tk.Frame(card, bg=card["bg"])
        type_frame.pack(fill="x", pady=(4, 14))
        tk.Radiobutton(type_frame, text="Email", variable=self.login_type_var, 
                       value="email", bg=card["bg"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["bg_medium"],
                       command=self._update_login_placeholder).pack(side="left")
        tk.Radiobutton(type_frame, text="Admission No", variable=self.login_type_var,
                       value="admission", bg=card["bg"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["bg_medium"],
                       command=self._update_login_placeholder).pack(side="left", padx=10)
        
        # Username
        self.user_label = tk.Label(card, text="Email Address", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"])
        self.user_label.pack(anchor="w")
        self.user_var = tk.StringVar()
        self.user_entry = make_entry(card, textvariable=self.user_var, width=35)
        self.user_entry.configure(bg=COLORS["bg_medium"])
        self.user_entry.pack(fill="x", pady=(4, 14))

        # Password
        tk.Label(card, text="Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.pass_var = tk.StringVar()
        pass_entry = make_entry(card, textvariable=self.pass_var, width=35, show="•")
        pass_entry.configure(bg=COLORS["bg_medium"])
        pass_entry.pack(fill="x", pady=(4, 20))

        # Login button
        login_btn = tk.Button(
            card, text="Sign In", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["white"],
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=10,
            command=self._do_login,
        )
        login_btn.pack(fill="x")

        self.bind("<Return>", lambda e: self._do_login())
        self.user_entry.focus_set()

    def _update_login_placeholder(self):
        login_type = self.login_type_var.get()
        if login_type == "email":
            self.user_label.config(text="Email Address")
            self.user_entry.delete(0, tk.END)
            self.user_var.set("")
        else:
            self.user_label.config(text="Admission Number")
            self.user_entry.delete(0, tk.END)
            self.user_var.set("")

    def _show_admin_register_form(self):
        """Show admin registration form"""
        self._build_registration_form("Admin", COLORS["warning"])

    def _show_teacher_register_form(self):
        """Show teacher registration form"""
        self._build_registration_form("Teacher", COLORS["secondary"])

    def _show_student_register_form(self):
        """Show student registration form"""
        self._build_registration_form("Student", COLORS["success"])

    def _build_registration_form(self, user_type, color):
        """Build a registration form for the given user type"""
        self._clear_outer()
        
        bg = COLORS["bg_dark"]
        card_bg = COLORS["card"]
        
        # Registration card
        card = tk.Frame(self.outer, bg=card_bg, padx=30, pady=25,
                       highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x")
        
        # Back button
        tk.Button(card, text="← Back to Welcome", font=FONTS["small"],
                  bg=card_bg, fg=COLORS["text_secondary"],
                  relief="flat", cursor="hand2",
                  command=self._show_welcome_card).pack(anchor="w", pady=(0, 15))

        if user_type == "Student":
            self._build_student_fields(card, color)
        else:
            self._build_user_fields(card, user_type, color)

    def _build_user_fields(self, card, user_type, color):
        """Build fields for admin/teacher registration"""
        # Full Name
        tk.Label(card, text="Full Name", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        name_var = tk.StringVar()
        name_entry = make_entry(card, textvariable=name_var, width=35)
        name_entry.configure(bg=COLORS["bg_medium"])
        name_entry.pack(fill="x", pady=(4, 14))

        # Email
        tk.Label(card, text="Email Address", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        email_var = tk.StringVar()
        email_entry = make_entry(card, textvariable=email_var, width=35)
        email_entry.configure(bg=COLORS["bg_medium"])
        email_entry.pack(fill="x", pady=(4, 14))

        # Password
        tk.Label(card, text="Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        pass_var = tk.StringVar()
        pass_entry = make_entry(card, textvariable=pass_var, width=35, show="•")
        pass_entry.configure(bg=COLORS["bg_medium"])
        pass_entry.pack(fill="x", pady=(4, 14))

        # Confirm Password
        tk.Label(card, text="Confirm Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        confirm_var = tk.StringVar()
        confirm_entry = make_entry(card, textvariable=confirm_var, width=35, show="•")
        confirm_entry.configure(bg=COLORS["bg_medium"])
        confirm_entry.pack(fill="x", pady=(4, 20))

        # Register button
        register_btn = tk.Button(
            card, text=f"Register as {user_type}", font=FONTS["body_bold"],
            bg=color, fg="white",
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=10,
            command=lambda: self._do_register(user_type, name_var, email_var, pass_var, confirm_var),
        )
        register_btn.pack(fill="x")

    def _build_student_fields(self, card, color):
        """Build fields for student registration"""
        # Admission Number
        tk.Label(card, text="Admission Number", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        adm_var = tk.StringVar()
        adm_entry = make_entry(card, textvariable=adm_var, width=35)
        adm_entry.configure(bg=COLORS["bg_medium"])
        adm_entry.pack(fill="x", pady=(4, 14))

        # First Name
        tk.Label(card, text="First Name", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        first_var = tk.StringVar()
        first_entry = make_entry(card, textvariable=first_var, width=35)
        first_entry.configure(bg=COLORS["bg_medium"])
        first_entry.pack(fill="x", pady=(4, 14))

        # Last Name
        tk.Label(card, text="Last Name", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        last_var = tk.StringVar()
        last_entry = make_entry(card, textvariable=last_var, width=35)
        last_entry.configure(bg=COLORS["bg_medium"])
        last_entry.pack(fill="x", pady=(4, 14))

        # Gender
        tk.Label(card, text="Gender", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(card, textvariable=gender_var, width=32)
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo['state'] = 'readonly'
        gender_combo.configure(background=COLORS["bg_medium"])
        gender_combo.pack(fill="x", pady=(4, 14))

        # Password
        tk.Label(card, text="Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        pass_var = tk.StringVar()
        pass_entry = make_entry(card, textvariable=pass_var, width=35, show="•")
        pass_entry.configure(bg=COLORS["bg_medium"])
        pass_entry.pack(fill="x", pady=(4, 14))

        # Confirm Password
        tk.Label(card, text="Confirm Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        confirm_var = tk.StringVar()
        confirm_entry = make_entry(card, textvariable=confirm_var, width=35, show="•")
        confirm_entry.configure(bg=COLORS["bg_medium"])
        confirm_entry.pack(fill="x", pady=(4, 20))

        # Register button
        register_btn = tk.Button(
            card, text="Register as Student", font=FONTS["body_bold"],
            bg=color, fg="white",
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=10,
            command=lambda: self._do_student_register(adm_var, first_var, last_var, gender_var, pass_var, confirm_var),
        )
        register_btn.pack(fill="x")

    def _do_login(self):
        user_input = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        
        if not user_input or not password:
            show_error("Validation", "Please enter both credentials.")
            return
        
        login_type = self.login_type_var.get()
        
        if login_type == "admission":
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
            messagebox.showinfo("Success", f"{user_type} registered successfully! Please login.")
            self._show_welcome_card()
            
        except Exception as e:
            show_error("Registration Error", str(e))
        finally:
            db.close()

    def _do_student_register(self, adm_var, first_var, last_var, gender_var, pass_var, confirm_var):
        adm_number = adm_var.get().strip()
        first_name = first_var.get().strip()
        last_name = last_var.get().strip()
        gender = gender_var.get().strip()
        password = pass_var.get().strip()
        confirm = confirm_var.get().strip()

        if not adm_number or not first_name or not last_name or not gender or not password:
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
                admission_number=adm_number,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                class_id=None,
                password_hash=password_hash
            )
            
            from tkinter import messagebox
            messagebox.showinfo("Success", "Student registered successfully! Please login with your admission number.")
            self._show_welcome_card()
            
        except Exception as e:
            show_error("Registration Error", str(e))
        finally:
            db.close()
