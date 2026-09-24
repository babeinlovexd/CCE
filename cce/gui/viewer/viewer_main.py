import customtkinter as ctk

from cce.gui.viewer.calendar_grid import CalendarGrid
from cce.gui.viewer.day_panel import DayPanel
from cce.gui.viewer.search_panel import SearchPanel
from cce.utils.i18n import _

class ViewerView(ctk.CTkFrame):
    def __init__(self, master, app, project, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.project = project

        self.current_year = 1
        self.current_month_idx = 0 # -1 for all year

        # Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=10)
        self.header_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_back = ctk.CTkButton(self.header_frame, text=_("🔙 Editor"), width=60, command=self.app.switch_to_editor, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray40"), text_color=("black", "white"))
        self.btn_back.pack(side="left", padx=15, pady=15)

        # Navigation Controls
        nav_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        nav_frame.pack(side="left", padx=10, pady=10)

        self.btn_prev_year = ctk.CTkButton(nav_frame, text=_("<< Year"), width=60, command=self.prev_year)
        self.btn_prev_year.pack(side="left", padx=2)

        self.btn_prev_month = ctk.CTkButton(nav_frame, text=_("< Month"), width=60, command=self.prev_month)
        self.btn_prev_month.pack(side="left", padx=2)

        self.date_label = ctk.CTkLabel(nav_frame, text=self.get_date_label_text(), font=("Arial", 16, "bold"), width=150)
        self.date_label.pack(side="left", padx=10)

        self.btn_next_month = ctk.CTkButton(nav_frame, text=_("Month >"), width=60, command=self.next_month)
        self.btn_next_month.pack(side="left", padx=2)

        self.btn_next_year = ctk.CTkButton(nav_frame, text=_("Year >>"), width=60, command=self.next_year)
        self.btn_next_year.pack(side="left", padx=2)

        self.btn_all_year = ctk.CTkButton(nav_frame, text=_("Show All Year"), width=80, command=self.show_all_year, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.btn_all_year.pack(side="left", padx=10)

        self.jump_entry = ctk.CTkEntry(nav_frame, placeholder_text=_("Year"), width=60)
        self.jump_entry.pack(side="left", padx=2)

        self.btn_jump = ctk.CTkButton(nav_frame, text=_("Jump"), width=40, command=self.jump_year)
        self.btn_jump.pack(side="left", padx=2)

        # Search Panel
        self.search_panel = SearchPanel(self.header_frame, self.project, on_search=self.on_search, fg_color="transparent")
        self.search_panel.pack(side="right", padx=15, pady=10)

        # Sync Planet display
        self.sync_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.sync_frame.pack(side="right", padx=10, pady=10)

        self.sync_planet_var = ctk.StringVar(value="None")
        self.sync_planet_menu = ctk.CTkOptionMenu(self.sync_frame, variable=self.sync_planet_var, values=["None"], width=100, command=self.on_sync_planet_change)
        self.sync_planet_menu.pack(side="left", padx=5)

        self.sync_label = ctk.CTkLabel(self.sync_frame, text=_("Select a day"), font=("Arial", 11), text_color=("gray30", "gray70"))
        self.sync_label.pack(side="left", padx=5)

        self.current_selected_day_start_tick = None

        # Main Area (Two Panes)
        self.main_pane = ctk.CTkFrame(self, fg_color="transparent")
        self.main_pane.pack(fill="both", expand=True, padx=10, pady=0)

        self.main_pane.grid_columnconfigure(0, weight=2)
        self.main_pane.grid_columnconfigure(1, weight=1)

        # Left: Calendar Grid
        self.calendar_grid = CalendarGrid(self.main_pane, self.project, self.on_day_click)
        self.calendar_grid.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Right: Day Details
        self.day_panel = DayPanel(self.main_pane, self.project, on_events_changed=self.on_events_changed)
        self.day_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    def get_date_label_text(self):
        m_text = _("All Year")
        if 0 <= self.current_month_idx < len(self.project.calendar_model.months):
            m_text = self.project.calendar_model.months[self.current_month_idx].name
        return f"{_('Year')} {self.current_year} - {m_text}"

    def on_show(self):
        # Update planet options
        p_names = [p.name for p in self.project.calendar_model.planets if p.id != self.project.calendar_model.primary_planet_id]
        if not p_names:
            p_names = [_("(None)")]
        self.sync_planet_menu.configure(values=p_names)
        if self.sync_planet_var.get() not in p_names:
            self.sync_planet_var.set(p_names[0])

        self.search_panel.populate_filters()

        self.date_label.configure(text=self.get_date_label_text())
        self.calendar_grid.render_year(self.current_year, self.current_month_idx)
        self.update_sync_display()

    def on_sync_planet_change(self, choice):
        self.update_sync_display()

    def update_sync_display(self):
        if self.current_selected_day_start_tick is None:
            self.sync_label.configure(text=_("Select a day"))
            return

        target_name = self.sync_planet_var.get()
        if target_name in ["None", _("(None)")]:
            self.sync_label.configure(text="")
            return

        sec = next((p for p in self.project.calendar_model.planets if p.name == target_name), None)
        if sec and sec.day_length_ticks > 0:
            sec_days_per_year = max(1, sec.year_length_ticks // sec.day_length_ticks)
            sec_days_total = self.current_selected_day_start_tick // sec.day_length_ticks
            sec_year = sec_days_total // sec_days_per_year
            sec_day_in_year = (sec_days_total % sec_days_per_year) + 1
            sec_time_str = self.project.time_engine.format_ticks_to_time(self.current_selected_day_start_tick, sec.day_length_ticks)
            self.sync_label.configure(text=f"{_('Year')} {sec_year}, {_('Day')} {sec_day_in_year} | Time: {sec_time_str}")
        else:
            self.sync_label.configure(text="Invalid settings")

    def on_day_click(self, day, year, day_start_tick):
        self.day_panel.set_day(day, year, day_start_tick)
        self.current_selected_day_start_tick = day_start_tick
        self.update_sync_display()

    def prev_year(self):
        self.current_year -= 1
        if self.current_year == 0:
            e0 = self.project.calendar_model.get_epoch_for_year(0)
            if not e0 or not e0.includes_year_zero:
                self.current_year = -1
        self.on_show()

    def next_year(self):
        self.current_year += 1
        if self.current_year == 0:
            e0 = self.project.calendar_model.get_epoch_for_year(0)
            if not e0 or not e0.includes_year_zero:
                self.current_year = 1
        self.on_show()

    def prev_month(self):
        if self.current_month_idx > 0:
            self.current_month_idx -= 1
        elif self.current_month_idx == 0:
            self.current_year -= 1
            self.current_month_idx = max(0, len(self.project.calendar_model.months) - 1)
        self.on_show()

    def next_month(self):
        if self.current_month_idx < len(self.project.calendar_model.months) - 1:
            self.current_month_idx += 1
        else:
            self.current_year += 1
            self.current_month_idx = 0
        self.on_show()

    def show_all_year(self):
        self.current_month_idx = -1
        self.on_show()

    def jump_year(self):
        try:
            y = int(self.jump_entry.get())
            self.current_year = y
            self.on_show()
        except ValueError:
            pass

    def on_search(self, query, filter_val=""):
        highlights = set()
        query = query.lower()

        for e in self.project.event_store.events:
            match_q = True
            if query:
                match_q = query in e.title.lower() or query in e.description.lower() or any(query in c.lower() for c in e.characters)

            match_f = True
            if filter_val:
                match_f = (filter_val == e.location) or (filter_val in e.characters)

            if match_q and match_f and (query or filter_val):
                highlights.add(e.start_tick)

        self.calendar_grid.set_search_highlights(highlights)
        self.calendar_grid.render_year(self.current_year, self.current_month_idx)

    def on_events_changed(self):
        self.on_show() # refresh grid badges
