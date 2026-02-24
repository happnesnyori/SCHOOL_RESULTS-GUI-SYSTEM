"""
views/analytics_panel.py - Analytics dashboard with embedded matplotlib charts
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from utils.ui_helpers import make_label

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class AnalyticsPanel(tk.Frame):
    def __init__(self, parent, analytics_svc):
        super().__init__(parent, bg=COLORS["bg_medium"])
        self.analytics_svc = analytics_svc
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_medium"], pady=10)
        header.pack(fill="x", padx=16)
        make_label(header, "Analytics Dashboard", "subheading").pack(side="left")
        tk.Button(header, text="Refresh", font=FONTS["body"],
                  bg=COLORS["primary"], fg="white", relief="flat",
                  cursor="hand2", padx=12,
                  command=self._refresh).pack(side="right")

        # Stats cards row
        self.stats_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        self.stats_frame.pack(fill="x", padx=16, pady=(0, 8))

        # Charts area (scrollable)
        canvas_outer = tk.Canvas(self, bg=COLORS["bg_medium"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas_outer.yview)
        self.charts_frame = tk.Frame(canvas_outer, bg=COLORS["bg_medium"])
        self.charts_frame.bind(
            "<Configure>",
            lambda e: canvas_outer.configure(scrollregion=canvas_outer.bbox("all"))
        )
        canvas_outer.create_window((0, 0), window=self.charts_frame, anchor="nw")
        canvas_outer.configure(yscrollcommand=scrollbar.set)
        canvas_outer.pack(side="left", fill="both", expand=True, padx=16)
        scrollbar.pack(side="right", fill="y")

        self._refresh()

    def _refresh(self):
        # Clear old
        for w in self.stats_frame.winfo_children():
            w.destroy()
        for w in self.charts_frame.winfo_children():
            w.destroy()

        stats = self.analytics_svc.total_stats()
        self._build_stat_cards(stats)
        self._build_charts()

    def _build_stat_cards(self, stats):
        card_data = [
            ("Total Students", stats["total_students"], COLORS["primary"]),
            ("Total Results", stats["total_results"], COLORS["secondary"]),
            ("Average Marks", f"{stats['avg_marks']}%", COLORS["success"]),
        ]
        for i, (title, value, color) in enumerate(card_data):
            card = tk.Frame(self.stats_frame, bg=color, padx=20, pady=16)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            self.stats_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=str(value), font=("Segoe UI", 28, "bold"),
                     bg=color, fg="white").pack()
            tk.Label(card, text=title, font=FONTS["body"],
                     bg=color, fg="#e0e0e0").pack()

    def _build_charts(self):
        dark_bg = COLORS["bg_medium"]
        text_color = COLORS["text_primary"]
        chart_configs = [
            (self._plot_class_avg, "Class Average Performance"),
            (self._plot_subject_avg, "Subject Average Marks"),
            (self._plot_top_students, "Top 5 Students"),
            (self._plot_pass_fail, "Pass / Fail Rate"),
            (self._plot_gpa_dist, "GPA Grade Distribution"),
        ]

        for row, (plot_fn, title) in enumerate(chart_configs):
            card = tk.Frame(self.charts_frame, bg=COLORS["card"],
                            highlightbackground=COLORS["border"], highlightthickness=1)
            card.pack(fill="x", pady=8, padx=4)
            tk.Label(card, text=title, font=FONTS["body_bold"],
                     bg=COLORS["card"], fg=COLORS["text_primary"]).pack(anchor="w", padx=12, pady=6)
            try:
                fig = Figure(figsize=(10, 3.2), facecolor=dark_bg)
                ax = fig.add_subplot(111, facecolor=dark_bg)
                ax.tick_params(colors=text_color, labelsize=8)
                for spine in ax.spines.values():
                    spine.set_edgecolor(COLORS["border"])
                plot_fn(ax, text_color)
                fig.tight_layout(pad=1.5)
                canvas = FigureCanvasTkAgg(fig, master=card)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="x", padx=8, pady=(0, 8))
            except Exception as e:
                tk.Label(card, text=f"No data: {e}", font=FONTS["small"],
                         bg=COLORS["card"], fg=COLORS["text_secondary"]).pack(pady=10)

    def _plot_class_avg(self, ax, tc):
        data = self.analytics_svc.class_average()
        if not data:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", color=tc)
            return
        names, vals = zip(*data)
        bars = ax.bar(names, vals, color=COLORS["primary_light"], edgecolor=COLORS["border"])
        ax.set_ylabel("Avg Marks", color=tc)
        ax.set_ylim(0, 100)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f"{val:.1f}", ha="center", va="bottom", color=tc, fontsize=8)

    def _plot_subject_avg(self, ax, tc):
        data = self.analytics_svc.subject_average()
        if not data:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", color=tc)
            return
        names, vals = zip(*data)
        ax.barh(names, vals, color=COLORS["accent"], edgecolor=COLORS["border"])
        ax.set_xlabel("Avg Marks", color=tc)
        ax.set_xlim(0, 100)

    def _plot_top_students(self, ax, tc):
        data = self.analytics_svc.top_students(5)
        if not data:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", color=tc)
            return
        names, vals = zip(*data)
        colors_list = ["#ffd700", "#c0c0c0", "#cd7f32", "#42a5f5", "#66bb6a"][:len(names)]
        bars = ax.bar(names, vals, color=colors_list, edgecolor=COLORS["border"])
        ax.set_ylabel("Avg Marks", color=tc)
        ax.set_ylim(0, 100)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f"{val:.1f}", ha="center", va="bottom", color=tc, fontsize=8)

    def _plot_pass_fail(self, ax, tc):
        pass_c, fail_c = self.analytics_svc.pass_fail_rate()
        if pass_c + fail_c == 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", color=tc)
            return
        ax.pie(
            [pass_c, fail_c],
            labels=[f"Pass ({pass_c})", f"Fail ({fail_c})"],
            colors=[COLORS["success"], COLORS["danger"]],
            autopct="%1.1f%%",
            textprops={"color": tc, "fontsize": 9},
            startangle=90,
        )

    def _plot_gpa_dist(self, ax, tc):
        data = self.analytics_svc.gpa_distribution()
        if not data:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", color=tc)
            return
        grade_colors = {"A": "#66bb6a", "B": "#42a5f5", "C": "#ffa726", "D": "#ef5350", "F": "#b71c1c"}
        grades = sorted(data.keys())
        counts = [data[g] for g in grades]
        bar_colors = [grade_colors.get(g, COLORS["accent"]) for g in grades]
        bars = ax.bar(grades, counts, color=bar_colors, edgecolor=COLORS["border"])
        ax.set_ylabel("Count", color=tc)
        for bar, val in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    str(val), ha="center", va="bottom", color=tc, fontsize=9)
