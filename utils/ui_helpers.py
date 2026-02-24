"""
utils/ui_helpers.py - Reusable UI components and helper functions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS


def apply_treeview_style(style: ttk.Style):
    """Apply dark theme styles to ttk widgets."""
    style.theme_use("clam")

    # Treeview
    style.configure(
        "Custom.Treeview",
        background=COLORS["table_odd"],
        foreground=COLORS["text_primary"],
        fieldbackground=COLORS["table_odd"],
        rowheight=28,
        borderwidth=0,
        font=FONTS["body"],
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=COLORS["table_header"],
        foreground=COLORS["white"],
        font=FONTS["body_bold"],
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", COLORS["primary_light"])],
        foreground=[("selected", COLORS["white"])],
    )

    # Buttons
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground=COLORS["white"],
        font=FONTS["body_bold"],
        borderwidth=0,
        focuscolor="none",
        padding=(12, 6),
    )
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_light"]), ("pressed", COLORS["primary"])])

    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground=COLORS["white"],
        font=FONTS["body_bold"],
        borderwidth=0,
        focuscolor="none",
        padding=(12, 6),
    )
    style.map("Danger.TButton",
              background=[("active", "#e53935"), ("pressed", COLORS["danger"])])

    style.configure(
        "Success.TButton",
        background=COLORS["success"],
        foreground=COLORS["white"],
        font=FONTS["body_bold"],
        borderwidth=0,
        focuscolor="none",
        padding=(12, 6),
    )
    style.map("Success.TButton",
              background=[("active", "#388e3c"), ("pressed", COLORS["success"])])

    style.configure(
        "Secondary.TButton",
        background=COLORS["bg_light"],
        foreground=COLORS["text_primary"],
        font=FONTS["body"],
        borderwidth=1,
        focuscolor="none",
        padding=(12, 6),
    )
    style.map("Secondary.TButton",
              background=[("active", COLORS["hover"])])

    # Entry, Combobox, Label
    style.configure(
        "TEntry",
        fieldbackground=COLORS["bg_light"],
        foreground=COLORS["text_primary"],
        bordercolor=COLORS["border"],
        insertcolor=COLORS["text_primary"],
        font=FONTS["body"],
    )
    style.configure(
        "TCombobox",
        fieldbackground=COLORS["bg_light"],
        background=COLORS["bg_light"],
        foreground=COLORS["text_primary"],
        selectbackground=COLORS["primary"],
        font=FONTS["body"],
    )
    style.configure(
        "TLabel",
        background=COLORS["bg_medium"],
        foreground=COLORS["text_primary"],
        font=FONTS["body"],
    )
    style.configure(
        "TFrame",
        background=COLORS["bg_medium"],
    )
    style.configure(
        "Card.TFrame",
        background=COLORS["card"],
    )
    style.configure(
        "Sidebar.TFrame",
        background=COLORS["sidebar"],
    )
    style.configure(
        "TScrollbar",
        background=COLORS["bg_light"],
        troughcolor=COLORS["bg_dark"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["text_secondary"],
    )
    style.configure("TNotebook", background=COLORS["bg_medium"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=COLORS["bg_light"],
        foreground=COLORS["text_secondary"],
        font=FONTS["body"],
        padding=(14, 6),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["primary"])],
        foreground=[("selected", COLORS["white"])],
    )


def make_label(parent, text, style="heading", fg=None, bg=None, **kwargs):
    color = fg or COLORS["text_primary"]
    background = bg or COLORS["bg_medium"]
    font = FONTS.get(style, FONTS["body"])
    lbl = tk.Label(parent, text=text, font=font, fg=color, bg=background, **kwargs)
    return lbl


def make_entry(parent, textvariable=None, width=30, show=None):
    bg = COLORS["bg_light"]
    fg = COLORS["text_primary"]
    entry = tk.Entry(
        parent, textvariable=textvariable, width=width,
        bg=bg, fg=fg, insertbackground=fg,
        relief="flat", font=FONTS["body"],
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["primary"],
        show=show or "",
    )
    return entry


def make_combobox(parent, textvariable, values, width=28):
    cb = ttk.Combobox(
        parent, textvariable=textvariable,
        values=values, width=width, state="readonly",
    )
    return cb


def scrollable_treeview(parent, columns, headings, show_scrollbar=True, height=18):
    """Create a Treeview with optional scrollbars."""
    frame = ttk.Frame(parent, style="Card.TFrame")
    tree = ttk.Treeview(
        frame, columns=columns, show="headings",
        style="Custom.Treeview", height=height,
    )
    for col, heading in zip(columns, headings):
        tree.heading(col, text=heading)
        tree.column(col, anchor="center", minwidth=60)

    if show_scrollbar:
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
    else:
        tree.grid(row=0, column=0, sticky="nsew")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    return frame, tree


def confirm_delete(item_name: str = "this item") -> bool:
    return messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete {item_name}?\nThis action cannot be undone.",
        icon="warning",
    )


def show_error(title, message):
    messagebox.showerror(title, message)


def show_success(title, message):
    messagebox.showinfo(title, message)


def show_info(title, message):
    messagebox.showinfo(title, message)


def center_window(win, width, height):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")
