"""
views/home_view.py - Welcoming home/landing page
School Examination Results Management System
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, APP_TITLE
from utils.ui_helpers import center_window


class HomePage(tk.Toplevel):
    """
    Welcoming home page that serves as the landing page.
    Allows users to navigate to login or registration screens.
    """

    def __init__(self, master, on_login_click, on_register_click):
        super().__init__(master)
        self.on_login_click = on_login_click
        self.on_register_click = on_register_click
        
        self.title("Welcome — " + APP_TITLE)
        self.resizable(True, True)
        self.configure(bg=COLORS["bg_dark"])
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        
        # Set window size
        self.geometry("800x700")
        self.minsize(650, 600)
        center_window(self, 800, 700)
        
        self._build()
        self.grab_set()

    def _build(self):
        """Build the home page UI"""
        bg = COLORS["bg_dark"]
        # Main container with padding
        main_container = tk.Frame(self, bg=bg)
        main_container.pack(fill="both", expand=True, padx=24, pady=24)

        # Build header and top actions (kept visible at top)
        header_container = tk.Frame(main_container, bg=bg)
        header_container.pack(fill="x")
        self._build_header(header_container, bg)
        self._build_actions(header_container, bg)

        # Create scrollable content area for the rest of the page
        content_container = tk.Frame(main_container, bg=bg)
        content_container.pack(fill="both", expand=True, pady=(12, 0))

        # Canvas + scrollbar
        canvas = tk.Canvas(content_container, bg=bg, highlightthickness=0)
        v_scroll = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Inner frame that will hold the actual content
        self._inner = tk.Frame(canvas, bg=bg)
        window_id = canvas.create_window((0, 0), window=self._inner, anchor="nw")

        # Populate scrollable content
        self._build_content(self._inner, bg)
        self._build_footer(self._inner, bg)

        # Configure scrolling region
        def _on_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        self._inner.bind("<Configure>", _on_frame_config)

        # Make canvas width adapt to inner frame
        def _on_canvas_config(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", _on_canvas_config)

        # Mousewheel support (Windows)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _build_header(self, parent, bg):
        """Build header with logo and title"""
        header = tk.Frame(parent, bg=bg)
        header.pack(fill="x", pady=(0, 30))

        # Logo emoji
        tk.Label(
            header,
            text="🎓",
            font=("Segoe UI Emoji", 64),
            bg=bg,
            fg=COLORS["primary_light"]
        ).pack()

        # Main title
        tk.Label(
            header,
            text="School Examination Results",
            font=("Segoe UI", 28, "bold"),
            bg=bg,
            fg=COLORS["white"]
        ).pack(pady=(15, 5))

        # Subtitle
        tk.Label(
            header,
            text="Management System",
            font=("Segoe UI", 18),
            bg=bg,
            fg=COLORS["text_secondary"]
        ).pack(pady=(0, 20))

        # Tagline
        tk.Label(
            header,
            text="Empowering Education Through Data-Driven Insights",
            font=("Segoe UI", 11, "italic"),
            bg=bg,
            fg=COLORS["primary"]
        ).pack()

    def _build_content(self, parent, bg):
        """Build content section with features"""
        content = tk.Frame(parent, bg=bg)
        content.pack(fill="both", expand=True, pady=30)

        # Welcome message
        welcome_card = tk.Frame(
            content,
            bg=COLORS["card"],
            padx=25,
            pady=25,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        welcome_card.pack(fill="both", expand=True, pady=(0, 20))

        tk.Label(
            welcome_card,
            text="Welcome!",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["card"],
            fg=COLORS["primary"]
        ).pack(anchor="w", pady=(0, 10))

        welcome_text = (
            "Welcome to S.E.R.M.S - Your comprehensive solution for managing "
            "school examination results and academic performance.\n\n"
            "Our system provides educators and administration with powerful tools to:\n"
        )
        
        tk.Label(
            welcome_card,
            text=welcome_text,
            font=FONTS["body"],
            bg=COLORS["card"],
            fg=COLORS["text_secondary"],
            justify="left",
            wraplength=500
        ).pack(anchor="w", pady=(0, 12))

        # Features list
        features = [
            "✓ Track Student Academic Performance",
            "✓ Manage Results & Examinations",
            "✓ Generate Detailed Reports",
            "✓ Analyze Class Analytics",
            "✓ Secure Data Management"
        ]

        features_frame = tk.Frame(welcome_card, bg=COLORS["card"])
        features_frame.pack(anchor="w", fill="x", padx=(20, 0))

        for feature in features:
            tk.Label(
                features_frame,
                text=feature,
                font=("Segoe UI", 10),
                bg=COLORS["card"],
                fg=COLORS["success"]
            ).pack(anchor="w", pady=4)

    def _build_actions(self, parent, bg):
        """Build action buttons for login and registration"""
        actions = tk.Frame(parent, bg=bg)
        actions.pack(fill="x", pady=20)

        # Login button
        login_btn = tk.Button(
            actions,
            text="🔐 Sign In to Your Account",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"],
            activebackground=COLORS["primary_light"],
            activeforeground=COLORS["white"],
            relief="flat",
            cursor="hand2",
            pady=12,
            command=self._handle_login
        )
        login_btn.pack(fill="x", pady=(0, 12))

        # Register button
        register_btn = tk.Button(
            actions,
            text="📝 Create New Account",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["secondary"],
            fg=COLORS["white"],
            activebackground=COLORS["primary_light"],
            activeforeground=COLORS["white"],
            relief="flat",
            cursor="hand2",
            pady=12,
            command=self._handle_register
        )
        register_btn.pack(fill="x")

        # Info text
        info_text = tk.Label(
            actions,
            text="New here? Click 'Create New Account' to register as Admin, Teacher, or Student",
            font=("Segoe UI", 9),
            bg=bg,
            fg=COLORS["text_secondary"],
            justify="center"
        )
        info_text.pack(pady=(12, 0))

    def _build_footer(self, parent, bg):
        """Build footer with additional info"""
        footer = tk.Frame(parent, bg=bg)
        footer.pack(fill="x", side="bottom")

        # Separator
        tk.Frame(footer, bg=COLORS["border"], height=1).pack(fill="x", pady=(20, 10))

        # Footer text
        tk.Label(
            footer,
            text="© 2025 School Examination Results Management System | All Rights Reserved",
            font=("Segoe UI", 9),
            bg=bg,
            fg=COLORS["text_secondary"]
        ).pack()

        tk.Label(
            footer,
            text="For support, contact your system administrator",
            font=("Segoe UI", 8),
            bg=bg,
            fg=COLORS["text_secondary"]
        ).pack()

    def _handle_login(self):
        """Handle login button click"""
        self.on_login_click()

    def _handle_register(self):
        """Handle register button click"""
        self.on_register_click()
