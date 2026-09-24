import customtkinter as ctk
from cce.models.event_store import StoryEvent

class DayPanel(ctk.CTkFrame):
    def __init__(self, master, project, on_events_changed, **kwargs):
        super().__init__(master, **kwargs)
        self.project = project
        self.on_events_changed = on_events_changed
        self.current_day_start_tick = 0
        self.current_day_end_tick = 0
        self.current_year = 0

        ctk.CTkLabel(self, text="Day Details & Events", font=("Arial", 16, "bold")).pack(pady=10)

        # Selected Date Label
        self.date_label = ctk.CTkLabel(self, text="Select a date", font=("Arial", 14))
        self.date_label.pack(pady=10)

        # Sky Panel
        self.sky_panel = ctk.CTkFrame(self, height=80)
        self.sky_panel.pack(fill="x", padx=10, pady=5)
        self.sky_label = ctk.CTkLabel(self.sky_panel, text="Sky Panel (Suns & Moons)")
        self.sky_label.pack(pady=10)

        # Event List
        self.events_list_frame = ctk.CTkScrollableFrame(self, height=150)
        self.events_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(self.events_list_frame, text="Events for this day").pack(pady=2)

        self.events_container = ctk.CTkFrame(self.events_list_frame, fg_color="transparent")
        self.events_container.pack(fill="both", expand=True)

        # Event Editor
        self.event_editor_frame = ctk.CTkScrollableFrame(self, height=250)
        self.event_editor_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.event_editor_frame, text="Add/Edit Event", font=("Arial", 12, "bold")).pack(pady=5)

        self.event_id_var = ctk.StringVar(value="")

        self.event_title = ctk.CTkEntry(self.event_editor_frame, placeholder_text="Event Title")
        self.event_title.pack(fill="x", padx=10, pady=2)

        time_frame = ctk.CTkFrame(self.event_editor_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=10, pady=2)
        self.event_start_time = ctk.CTkEntry(time_frame, placeholder_text="Start Time (e.g. 2h 30m)", width=120)
        self.event_start_time.pack(side="left", padx=(0,5), expand=True, fill="x")
        self.event_end_time = ctk.CTkEntry(time_frame, placeholder_text="End Time", width=120)
        self.event_end_time.pack(side="left", padx=(5,0), expand=True, fill="x")

        self.event_loc = ctk.CTkEntry(self.event_editor_frame, placeholder_text="Location")
        self.event_loc.pack(fill="x", padx=10, pady=2)

        self.event_plot = ctk.CTkEntry(self.event_editor_frame, placeholder_text="Plotline / Category")
        self.event_plot.pack(fill="x", padx=10, pady=2)

        self.event_chars = ctk.CTkEntry(self.event_editor_frame, placeholder_text="Characters (comma separated)")
        self.event_chars.pack(fill="x", padx=10, pady=2)

        self.event_desc = ctk.CTkEntry(self.event_editor_frame, placeholder_text="Description / Notes")
        self.event_desc.pack(fill="x", padx=10, pady=2)

        btn_frame = ctk.CTkFrame(self.event_editor_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(btn_frame, text="Save Event", command=self.save_event).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="Clear", fg_color="gray", command=self.clear_editor).pack(side="right", expand=True, padx=5)

    def set_day(self, day, year, day_start_tick):
        epoch = self.project.calendar_model.get_epoch_for_year(year)
        epoch_str = f"{epoch.name}, " if epoch else ""
        m_name = day['month'].name if day['month'] else "Standalone"
        d_name = f"Day {day['day_in_month']}" if day['day_in_month'] else f"Abs Day {day['absolute_day']}"
        holidays = ", ".join([h.name for h in day['holidays']])
        holiday_str = f" [{holidays}]" if holidays else ""

        # Adjusted for requested format string
        # "[Epoch], [Month] Day X [Holidays], [Time]" -> time is dynamic, so we just show the date here
        title = f"{epoch_str}Yr {year} - {m_name}, {d_name} - {day['weekday'].name}{holiday_str}"
        self.date_label.configure(text=title)

        # Calculate ticks
        prim = self.project.calendar_model.get_primary_planet()
        ticks_per_day = prim.day_length_ticks if prim else 1000
        self.current_day_start_tick = day_start_tick
        self.current_day_end_tick = day_start_tick + ticks_per_day
        self.current_year = year

        # Moon & Sun info
        sky_texts = []
        for sun in self.project.astronomy_model.suns:
            dawn_str = self.project.time_engine.format_ticks_to_time(sun.dawn_tick, ticks_per_day)
            zenith_str = self.project.time_engine.format_ticks_to_time(sun.zenith_tick, ticks_per_day)
            dusk_str = self.project.time_engine.format_ticks_to_time(sun.dusk_tick, ticks_per_day)
            sky_texts.append(f"☀️ {sun.name} (↑{dawn_str} / ↓{dusk_str})")

        for moon in self.project.astronomy_model.moons:
            if moon.cycle_days > 0:
                # Need to resolve total_absolute_days for accurate phase
                dsz = self.project.calendar_model.get_total_days_since_zero(year)
                tot_abs_day = dsz + (day['absolute_day'] - 1)
                phase = ((tot_abs_day + moon.phase_offset) % moon.cycle_days) / moon.cycle_days
                sky_texts.append(f"🌙 {moon.name}: {phase*100:.1f}%")
            else:
                sky_texts.append(f"🌙 {moon.name}: N/A")

        self.sky_label.configure(text=" | ".join(sky_texts) if sky_texts else "No Astronomy Data")

        self.load_events()
        self.clear_editor()

    def load_events(self):
        for w in self.events_container.winfo_children():
            w.destroy()

        day_events = [e for e in self.project.event_store.events if e.start_tick >= self.current_day_start_tick and e.start_tick < self.current_day_end_tick]

        if not day_events:
            ctk.CTkLabel(self.events_container, text="No events on this day.").pack(pady=10)
            return

        # sort by start_tick
        day_events.sort(key=lambda x: x.start_tick)

        for ev in day_events:
            f = ctk.CTkFrame(self.events_container)
            f.pack(fill="x", pady=2)

            # format time
            rel_tick = ev.start_tick - self.current_day_start_tick
            prim = self.project.calendar_model.get_primary_planet()
            dl = prim.day_length_ticks if prim else 1000
            t_str = self.project.time_engine.format_ticks_to_time(rel_tick, dl)

            lbl = ctk.CTkLabel(f, text=f"[{t_str}] {ev.title}\n{ev.location} | {ev.plotline}", justify="left")
            lbl.pack(side="left", padx=10, pady=5)

            btn_del = ctk.CTkButton(f, text="Del", width=40, fg_color="red", command=lambda e=ev: self.delete_event(e))
            btn_del.pack(side="right", padx=5, pady=5)

            btn_edit = ctk.CTkButton(f, text="Edit", width=40, command=lambda e=ev: self.edit_event(e))
            btn_edit.pack(side="right", padx=5, pady=5)

    def save_event(self):
        title = self.event_title.get().strip()
        if not title:
            return

        desc = self.event_desc.get().strip()
        loc = self.event_loc.get().strip()
        plot = self.event_plot.get().strip()
        chars = [c.strip() for c in self.event_chars.get().split(',') if c.strip()]

        # Parse times
        st_str = self.event_start_time.get().strip()
        et_str = self.event_end_time.get().strip()

        st_ticks = self.project.time_engine.parse_time_string_to_ticks(st_str) if st_str else 0
        et_ticks = self.project.time_engine.parse_time_string_to_ticks(et_str) if et_str else st_ticks

        abs_start = self.current_day_start_tick + st_ticks
        abs_end = self.current_day_start_tick + et_ticks

        eid = self.event_id_var.get()

        if eid:
            # Edit existing
            for e in self.project.event_store.events:
                if e.id == eid:
                    e.title = title
                    e.start_tick = abs_start
                    e.end_tick = abs_end
                    e.location = loc
                    e.plotline = plot
                    e.description = desc
                    e.characters = chars
                    break
        else:
            # New event
            ev = StoryEvent.create(title=title, start_tick=abs_start, end_tick=abs_end,
                                   location=loc, plotline=plot, description=desc, characters=chars)
            self.project.event_store.events.append(ev)

        self.load_events()
        self.clear_editor()
        self.on_events_changed()

    def edit_event(self, ev: StoryEvent):
        self.clear_editor()
        self.event_id_var.set(ev.id)
        self.event_title.insert(0, ev.title)

        prim = self.project.calendar_model.get_primary_planet()
        dl = prim.day_length_ticks if prim else 1000

        s_rel = ev.start_tick - self.current_day_start_tick
        e_rel = ev.end_tick - self.current_day_start_tick

        self.event_start_time.insert(0, self.project.time_engine.format_ticks_to_time(s_rel, dl))
        self.event_end_time.insert(0, self.project.time_engine.format_ticks_to_time(e_rel, dl))

        self.event_loc.insert(0, ev.location)
        self.event_plot.insert(0, ev.plotline)
        self.event_desc.insert(0, ev.description)
        self.event_chars.insert(0, ", ".join(ev.characters))

    def delete_event(self, ev: StoryEvent):
        self.project.event_store.events = [e for e in self.project.event_store.events if e.id != ev.id]
        self.load_events()
        self.on_events_changed()

    def clear_editor(self):
        self.event_id_var.set("")
        self.event_title.delete(0, 'end')
        self.event_start_time.delete(0, 'end')
        self.event_end_time.delete(0, 'end')
        self.event_loc.delete(0, 'end')
        self.event_plot.delete(0, 'end')
        self.event_desc.delete(0, 'end')
        self.event_chars.delete(0, 'end')
