import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

from cce.models.project import Project
from cce.gui.editor.editor_view import EditorView
from cce.gui.viewer.viewer_main import ViewerView

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Custom Calendar Engine (CCE)")
        self.geometry("1200x800")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.project = Project()

        # Menu bar (using a top frame as customtk doesn't have native menus)
        self.menu_frame = ctk.CTkFrame(self, height=40)
        self.menu_frame.pack(fill="x", side="top")

        self.btn_export = ctk.CTkButton(self.menu_frame, text="📄 Export Timeline (MD)", width=120, command=self.export_timeline)
        self.btn_export.pack(side="right", padx=10, pady=5)

        # Initialize Views
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        self.editor_view = EditorView(self.main_container, self, self.project)
        self.viewer_view = ViewerView(self.main_container, self, self.project)

        # Start with Editor
        self.current_view = None
        self.switch_to_editor()

    def switch_to_editor(self):
        if self.current_view:
            self.current_view.pack_forget()
        self.current_view = self.editor_view
        self.current_view.pack(fill="both", expand=True)

    def switch_to_viewer(self):
        if self.current_view:
            self.current_view.pack_forget()

        self.current_view = self.viewer_view
        self.current_view.pack(fill="both", expand=True)
        self.viewer_view.on_show()

    def save_project(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".worldcal",
            filetypes=[("World Calendar Files", "*.worldcal"), ("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                self.project.save_to_file(filepath)
                messagebox.showinfo("Success", f"Project saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save project:\n{e}")

    def load_project(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("World Calendar Files", "*.worldcal"), ("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                self.project = Project.load_from_file(filepath)
                # Re-initialize views with new project
                self.editor_view.destroy()
                self.viewer_view.destroy()

                self.editor_view = EditorView(self.main_container, self, self.project)
                self.viewer_view = ViewerView(self.main_container, self, self.project)

                self.switch_to_editor()

                messagebox.showinfo("Success", f"Project loaded from {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load project:\n{e}")

    def export_timeline(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Story Timeline"
        )
        if not filepath:
            return

        try:
            sorted_events = sorted(self.project.event_store.events, key=lambda e: e.start_tick)

            prim = self.project.calendar_model.get_primary_planet()
            ticks_per_day = prim.day_length_ticks if prim else 1000

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Timeline for {self.project.name}\n\n")

                if not sorted_events:
                    f.write("*No events recorded yet.*\n")

                for ev in sorted_events:
                    # Reverse-calculate tick to Year and day in year
                    total_days = ev.start_tick // ticks_per_day
                    time_ticks_in_day = ev.start_tick % ticks_per_day

                    # Very naive year finder by iterating
                    # Optimization possible, but for export it's fast enough
                    y = 1
                    e0 = self.project.calendar_model.get_epoch_for_year(0)
                    has_yr_0 = e0 and getattr(e0, 'includes_year_zero', False)
                    if has_yr_0:
                        y = 0

                    if total_days >= 0:
                        while True:
                            diy = self.project.calendar_model.get_days_in_year(y)
                            if diy <= 0 or total_days < diy: break
                            total_days -= diy
                            y += 1
                            if y == 0 and not has_yr_0: y += 1
                    else:
                        while total_days < 0:
                            y -= 1
                            if y == 0 and not has_yr_0: y -= 1
                            diy = self.project.calendar_model.get_days_in_year(y)
                            if diy <= 0: break
                            total_days += diy

                    # Now total_days is the day index within year `y`
                    day_in_year = total_days + 1

                    # Find exact month and date by generating the calendar matrix for that year
                    matrix = self.project.calendar_model.generate_calendar_matrix(y)

                    date_str = f"Year {y}, Day {day_in_year}"
                    if 0 <= total_days < len(matrix):
                        d_info = matrix[total_days]
                        epoch = self.project.calendar_model.get_epoch_for_year(y)
                        e_str = f"{epoch.name} " if epoch else ""
                        m_name = d_info["month"].name if d_info["month"] else "Standalone"
                        d_name = d_info["day_in_month"] or d_info["absolute_day"]
                        wd_name = d_info["weekday"].name
                        date_str = f"{e_str}Year {y} - {m_name}, Day {d_name} ({wd_name})"

                    time_str = self.project.time_engine.format_ticks_to_time(time_ticks_in_day, ticks_per_day)

                    f.write(f"## {ev.title}  \n")
                    f.write(f"**Date:** {date_str} at {time_str}  \n")
                    if ev.location or ev.plotline:
                        f.write(f"**Location:** {ev.location} | **Plot:** {ev.plotline}  \n")
                    if ev.characters:
                        f.write(f"**Characters:** {', '.join(ev.characters)}  \n")
                    f.write(f"\n{ev.description}\n\n")
                    f.write("---\n\n")

            messagebox.showinfo("Success", f"Timeline exported to {filepath}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to export timeline:\n{e}")

def run():
    app = Application()
    app.mainloop()
