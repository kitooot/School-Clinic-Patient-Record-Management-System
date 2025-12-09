"""Analytics window separated from the main system module."""
from __future__ import annotations # Ensure compatibility with future Python versions

from typing import Callable, Optional # 

import customtkinter as ctk # For custom Tkinter widgets
from tkinter import BOTH, messagebox # For message boxes

from system_configs.config import ACCENT, CARD_BG, PRIMARY, SECONDARY, TEXT # Import color constants

# Module-level variables to hold dependencies
_compute_analytics: Optional[Callable[[], dict]] = None 
_create_analytics_figures: Optional[Callable[[dict], dict]] = None
_root = None
_figure_cls = None
_figure_canvas_cls = None

# Configure module-level analytics dependencies.
def configure(
    *,
    compute_analytics: Callable[[], dict],
    create_analytics_figures: Callable[[dict], dict],
    root,
    figure_cls,
    figure_canvas_cls,
) -> None:
    """Configure module-level analytics dependencies."""
    global _compute_analytics, _create_analytics_figures, _root, _figure_cls, _figure_canvas_cls
    _compute_analytics = compute_analytics
    _create_analytics_figures = create_analytics_figures
    _root = root
    _figure_cls = figure_cls
    _figure_canvas_cls = figure_canvas_cls

# Show the analytics window with charts and summaries.
def show_analytics_window():  # pragma: no cover - UI callback
    if _compute_analytics is None or _create_analytics_figures is None:
        return

    analytics = _compute_analytics()

    if analytics.get("total", 0) == 0:
        messagebox.showinfo("Patient Analytics", "No patient records available to analyze yet.")
        return

    if _figure_cls is None or _figure_canvas_cls is None:
        messagebox.showerror(
            "Missing Dependency",
            'Analytics charts require the "matplotlib" package. Install it with "pip install matplotlib" and try again.',
        )
        return

    analytics_window = ctk.CTkToplevel()
    analytics_window.title("Patient Analytics")
    analytics_window.grab_set()
    analytics_window.configure(fg_color=ACCENT)
    analytics_window.transient(_root)
    analytics_window.resizable(True, True)
    analytics_window.grid_rowconfigure(0, weight=1)
    analytics_window.grid_columnconfigure(0, weight=1)

    screen_w = analytics_window.winfo_screenwidth()
    screen_h = analytics_window.winfo_screenheight()
    min_width = min(960, screen_w)
    min_height = min(700, screen_h)
    win_w = min(max(int(screen_w * 0.75), min_width), screen_w)
    win_h = min(max(int(screen_h * 0.75), min_height), screen_h)
    pos_x = max((screen_w - win_w) // 2, 0)
    pos_y = max((screen_h - win_h) // 2, 0)
    analytics_window.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
    analytics_window.minsize(min_width, min_height)

    container = ctk.CTkFrame(analytics_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24, sticky="nsew")
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(2, weight=1)

    #   Make matplotlib canvases responsive to frame size changes.
    def _make_canvas_responsive(target_frame, fig, canvas):
        """Resize matplotlib canvases when their parent frames change size."""

        def _on_resize(event):
            if event.width <= 1 or event.height <= 1:
                return
            dpi = fig.dpi or 100
            fig.set_size_inches(max(event.width / dpi, 1), max(event.height / dpi, 1))
            canvas.draw_idle()

        target_frame.bind("<Configure>", _on_resize)

    ctk.CTkLabel(container, text="Patient Analytics Overview", font=("Segoe UI", 18, "bold"), text_color=TEXT).grid(
        row=0, column=0, padx=18, pady=(10, 6), sticky="ew"
    )

    summary_frame = ctk.CTkFrame(container, fg_color="transparent")
    summary_frame.grid(row=1, column=0, padx=18, pady=(4, 10), sticky="ew")
    summary_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        summary_frame,
        text=f"Total Patients: {analytics['total']}",
        font=("Segoe UI", 14, "bold"),
        text_color=TEXT,
    ).grid(row=0, column=0, sticky="w")

    ctk.CTkLabel(
        summary_frame,
        text=f"Most Recent Visit: {analytics['latest_visit']}",
        font=("Segoe UI", 13),
        text_color=TEXT,
    ).grid(row=1, column=0, pady=(2, 0), sticky="w")

    chart_frame = ctk.CTkFrame(container, fg_color="transparent")
    chart_frame.grid(row=2, column=0, padx=18, pady=(4, 10), sticky="nsew")
    chart_frame.grid_columnconfigure((0, 1), weight=1)
    chart_frame.grid_rowconfigure((0, 1), weight=1)

    pie_frame = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=16)
    pie_frame.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="nsew")
    bar_frame = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=16)
    bar_frame.grid(row=0, column=1, padx=(8, 0), pady=(0, 8), sticky="nsew")
    municipality_frame = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=16)
    municipality_frame.grid(row=1, column=0, padx=(0, 8), pady=(8, 0), sticky="nsew")
    line_frame = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=16)
    line_frame.grid(row=1, column=1, padx=(8, 0), pady=(8, 0), sticky="nsew")

    chart_canvases = []
    figures = _create_analytics_figures(analytics)

    chart_specs = [
        ("gender", "No gender data available.", pie_frame),
        ("diagnosis", "No diagnosis data available.", bar_frame),
        ("municipality", "No municipality data available.", municipality_frame),
        ("visits", "No visit history available.", line_frame),
    ]

    for key, empty_text, frame in chart_specs:
        fig = figures.get(key)
        if fig is None:
            ctk.CTkLabel(frame, text=empty_text, font=("Segoe UI", 12), text_color=TEXT).pack(
                expand=True, padx=18, pady=18
            )
            continue

        canvas = _figure_canvas_cls(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        chart_canvases.append(canvas)
        _make_canvas_responsive(frame, fig, canvas)

    analytics_window._chart_canvases = chart_canvases  # keep references

    close_button = ctk.CTkButton(
        container,
        text="Close",
        command=analytics_window.destroy,
        fg_color=SECONDARY,
        hover_color=PRIMARY,
        corner_radius=14,
        font=("Segoe UI", 13, "bold"),
    )
    close_button.grid(row=3, column=0, padx=18, pady=(6, 4), sticky="ew")


__all__ = [
    "configure",
    "show_analytics_window",
]
