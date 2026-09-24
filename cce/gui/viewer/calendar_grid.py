import customtkinter as ctk
from cce.utils.i18n import _

class CalendarGrid(ctk.CTkFrame):
    def __init__(self, master, project, on_day_click, **kwargs):
        super().__init__(master, **kwargs)
        self.project = project
        self.on_day_click = on_day_click

        self.grid_scroll = ctk.CTkScrollableFrame(self)
        self.grid_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.current_year = 1
        self.current_month_index = 0 # -1 means show all, or index in months
        self.search_highlight_ticks = set()

    def set_search_highlights(self, start_ticks: set):
        self.search_highlight_ticks = start_ticks

    def render_year(self, year: int, month_index: int = -1):
        self.current_year = year
        self.current_month_index = month_index
        for widget in self.grid_scroll.winfo_children():
            widget.destroy()

        days = self.project.calendar_model.generate_calendar_matrix(year)
        if not days:
            ctk.CTkLabel(self.grid_scroll, text=_("No calendar configured.")).pack(pady=20)
            return

        # Simple grouping by Month
        current_month = None
        month_frame = None
        row_idx = 0
        col_idx = 0

        target_month_id = None
        if 0 <= month_index < len(self.project.calendar_model.months):
            target_month_id = self.project.calendar_model.months[month_index].id

        for day in days:
            m = day["month"]
            m_name = m.name if m else "Standalone"

            if target_month_id and m and m.id != target_month_id:
                continue # Skip if we are filtering by a specific month

            if m_name != current_month:
                current_month = m_name
                # New month section
                month_frame = ctk.CTkFrame(self.grid_scroll, corner_radius=10)
                month_frame.pack(fill="x", pady=15, padx=10)

                ctk.CTkLabel(month_frame, text=m_name, font=("Arial", 18, "bold"), text_color=m.color if m else "white").pack(anchor="center", pady=(10, 5))

                # Weekday headers
                header_frame = ctk.CTkFrame(month_frame, fg_color="transparent")
                header_frame.pack(fill="x", padx=10)
                for i, wd in enumerate(self.project.calendar_model.weekdays):
                    lbl = ctk.CTkLabel(header_frame, text=wd.name[:3], width=60, font=("Arial", 12, "bold"), text_color="gray70")
                    lbl.grid(row=0, column=i, padx=4, pady=5)

                self.days_grid = ctk.CTkFrame(month_frame, fg_color="transparent")
                self.days_grid.pack(fill="x")

                # find start col index for the first day of month based on its weekday
                wd_id = day["weekday"].id
                col_idx = 0
                for i, w in enumerate(self.project.calendar_model.weekdays):
                    if w.id == wd_id:
                        col_idx = i
                        break
                row_idx = 0

                # Fill preceding empty grid cells for visual alignment
                for i in range(col_idx):
                    empty_lbl = ctk.CTkLabel(self.days_grid, text="", width=60, height=60)
                    empty_lbl.grid(row=row_idx, column=i, padx=2, pady=2)

            # Determine colors and badges
            bg_color = m.color if m else "gray20"
            if day["holidays"]:
                bg_color = day["holidays"][0].color
            elif day["is_leap_day"]:
                bg_color = "darkred"

            # Compute ticks strictly avoiding year * day_in_year multiplication
            primary_planet = self.project.calendar_model.get_primary_planet()
            ticks_per_day = primary_planet.day_length_ticks if primary_planet else 1000

            days_since_zero = self.project.calendar_model.get_total_days_since_zero(year)
            # absolute_day is 1-indexed, so we subtract 1 for math
            total_absolute_days = days_since_zero + (day["absolute_day"] - 1)
            day_start_tick = total_absolute_days * ticks_per_day

            border_color = "green" if any(t >= day_start_tick and t < day_start_tick + ticks_per_day for t in self.search_highlight_ticks) else "gray50"
            border_width = 2 if border_color == "green" else 1

            # Count events for badge
            event_count = sum(1 for e in self.project.event_store.events if e.start_tick >= day_start_tick and e.start_tick < day_start_tick + ticks_per_day)

            # Moon phase rough indicator (first moon)
            moon_indicator = ""
            if self.project.astronomy_model.moons:
                moon = self.project.astronomy_model.moons[0]
                if moon.cycle_days > 0:
                    phase = ((total_absolute_days + moon.phase_offset) % moon.cycle_days) / moon.cycle_days
                    if phase < 0.1 or phase > 0.9: moon_indicator = "🌑"
                    elif phase < 0.4: moon_indicator = "🌓"
                    elif phase < 0.6: moon_indicator = "🌕"
                    else: moon_indicator = "🌗"

            tile_text = str(day["absolute_day"] if day["day_in_month"] is None else day["day_in_month"])
            if event_count > 0:
                tile_text += f"\nEvents: {event_count}"
            if moon_indicator:
                tile_text += f"\n{moon_indicator}"

            tile = ctk.CTkButton(self.days_grid, text=tile_text,
                                 width=60, height=60, fg_color=bg_color, border_width=border_width, border_color=border_color,
                                 command=lambda d=day, ds=day_start_tick: self.on_day_click(d, year, ds))
            tile.grid(row=row_idx, column=col_idx, padx=2, pady=2)

            col_idx += 1
            if col_idx >= len(self.project.calendar_model.weekdays):
                col_idx = 0
                row_idx += 1
