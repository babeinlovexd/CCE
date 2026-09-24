import customtkinter as ctk
from cce.models.astronomy import Sun, Moon
from cce.utils.i18n import _
from cce.gui.utils.tooltip import Tooltip

class TabAstronomy(ctk.CTkFrame):
    def __init__(self, master, project, **kwargs):
        super().__init__(master, **kwargs)
        self.project = project

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Suns
        self.suns_frame = ctk.CTkFrame(self, corner_radius=10)
        self.suns_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        ctk.CTkLabel(self.suns_frame, text="☀️ " + _("Suns"), font=("Arial", 16, "bold")).pack(pady=(15, 5))
        self.suns_list = ctk.CTkScrollableFrame(self.suns_frame)
        self.suns_list.pack(fill="both", expand=True, padx=15, pady=5)
        self.btn_add_sun = ctk.CTkButton(self.suns_frame, text=_("Add Sun"), command=self.add_sun_row)
        self.btn_add_sun.pack(pady=(10, 15))

        # Moons
        self.moons_frame = ctk.CTkFrame(self, corner_radius=10)
        self.moons_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)

        ctk.CTkLabel(self.moons_frame, text="🌙 " + _("Moons"), font=("Arial", 16, "bold")).pack(pady=(15, 5))
        self.moons_list = ctk.CTkScrollableFrame(self.moons_frame)
        self.moons_list.pack(fill="both", expand=True, padx=15, pady=5)
        self.btn_add_moon = ctk.CTkButton(self.moons_frame, text=_("Add Moon"), command=self.add_moon_row)
        self.btn_add_moon.pack(pady=(10, 15))

        self.sun_rows = []
        self.moon_rows = []

        self.load_data()

    def load_data(self):
        for w in self.suns_list.winfo_children(): w.destroy()
        for w in self.moons_list.winfo_children(): w.destroy()
        self.sun_rows.clear()
        self.moon_rows.clear()

        for s in self.project.astronomy_model.suns:
            self.add_sun_row(s)

        for m in self.project.astronomy_model.moons:
            self.add_moon_row(m)

    def add_sun_row(self, sun=None):
        row_frame = ctk.CTkFrame(self.suns_list)
        row_frame.pack(fill="x", pady=2)

        name_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Name"), width=100)
        name_ent.pack(side="left", padx=2)

        dawn_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Dawn (tick)"), width=70)
        dawn_ent.pack(side="left", padx=2)

        zenith_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Zenith"), width=70)
        zenith_ent.pack(side="left", padx=2)

        dusk_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Dusk"), width=70)
        dusk_ent.pack(side="left", padx=2)

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_row(f, self.sun_rows))
        btn_del.pack(side="right", padx=2)

        if sun:
            name_ent.insert(0, sun.name)
            dawn_ent.insert(0, str(sun.dawn_tick))
            zenith_ent.insert(0, str(sun.zenith_tick))
            dusk_ent.insert(0, str(sun.dusk_tick))

        self.sun_rows.append((row_frame, name_ent, dawn_ent, zenith_ent, dusk_ent))

    def add_moon_row(self, moon=None):
        row_frame = ctk.CTkFrame(self.moons_list)
        row_frame.pack(fill="x", pady=2)

        name_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Name"), width=100)
        name_ent.pack(side="left", padx=5)

        cycle_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Cycle (days)"), width=80)
        cycle_ent.pack(side="left", padx=5)

        offset_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Offset"), width=50)
        offset_ent.pack(side="left", padx=5)
        Tooltip(offset_ent, _("Starting phase offset in days at absolute day 1."))

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_row(f, self.moon_rows))
        btn_del.pack(side="right", padx=5)

        if moon:
            name_ent.insert(0, moon.name)
            cycle_ent.insert(0, str(moon.cycle_days))
            offset_ent.insert(0, str(moon.phase_offset))

        self.moon_rows.append((row_frame, name_ent, cycle_ent, offset_ent))

    def remove_row(self, row_frame, row_list):
        from tkinter import messagebox
        from cce.utils.i18n import _
        if not messagebox.askyesno(_("Confirm Delete"), _("Are you sure you want to delete this item?")):
            return
        row_list[:] = [r for r in row_list if r[0] != row_frame]
        row_frame.destroy()
        self.master.master.master.app.mark_dirty()

    def save_data(self):
        self.master.master.master.app.mark_dirty()
        new_suns = []
        for _, name_ent, dawn_ent, zenith_ent, dusk_ent in self.sun_rows:
            name = name_ent.get()
            if name:
                try: dawn = int(dawn_ent.get())
                except: dawn = 0
                try: zenith = int(zenith_ent.get())
                except: zenith = 0
                try: dusk = int(dusk_ent.get())
                except: dusk = 0
                new_suns.append(Sun.create(name=name, dawn_tick=dawn, zenith_tick=zenith, dusk_tick=dusk))

        new_moons = []
        for _, name_ent, cycle_ent, offset_ent in self.moon_rows:
            name = name_ent.get()
            try:
                cycle = float(cycle_ent.get())
                offset = float(offset_ent.get())
            except:
                continue
            if name:
                new_moons.append(Moon.create(name=name, cycle_days=cycle, phase_offset=offset))

        self.project.astronomy_model.suns = new_suns
        self.project.astronomy_model.moons = new_moons
