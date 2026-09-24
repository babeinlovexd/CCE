import customtkinter as ctk
from cce.models.calendar_model import Planet
from cce.utils.i18n import _
from cce.gui.utils.tooltip import Tooltip

class TabPlanets(ctk.CTkFrame):
    def __init__(self, master, project, **kwargs):
        super().__init__(master, **kwargs)
        self.project = project

        self.card = ctk.CTkFrame(self, corner_radius=10)
        self.card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.card, text="🪐 " + _("Planets & Orbit"), font=("Arial", 16, "bold")).pack(pady=(15, 5), padx=15, anchor="w")

        self.list_frame = ctk.CTkScrollableFrame(self.card)
        self.list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.planet_rows = []
        self.load_planets()

        self.btn_add = ctk.CTkButton(self.card, text=_("Add Planet"), command=self.add_planet_row)
        self.btn_add.pack(pady=(10, 15))

    def load_planets(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        self.planet_rows.clear()

        if not self.project.calendar_model.planets:
            # Default planet
            self.project.calendar_model.planets.append(Planet.create("Primary", 86400, 31536000))

        for p in self.project.calendar_model.planets:
            self.add_planet_row(p)

    def add_planet_row(self, planet=None):
        row_frame = ctk.CTkFrame(self.list_frame)
        row_frame.pack(fill="x", pady=2)

        name_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Name (e.g. Earth)"), width=150)
        name_ent.pack(side="left", padx=5)

        day_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Day length (ticks)"), width=120)
        day_ent.pack(side="left", padx=5)

        year_ent = ctk.CTkEntry(row_frame, placeholder_text=_("Year length (ticks)"), width=120)
        year_ent.pack(side="left", padx=5)

        prim_var = ctk.BooleanVar()
        prim_check = ctk.CTkCheckBox(row_frame, text=_("Primary"), variable=prim_var, width=60)
        prim_check.pack(side="left", padx=10)
        Tooltip(prim_check, _("The primary planet serves as the main reference frame for the calendar grid."))

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_planet_row(f))
        btn_del.pack(side="right", padx=5)

        if planet:
            name_ent.insert(0, planet.name)
            day_ent.insert(0, str(planet.day_length_ticks))
            year_ent.insert(0, str(planet.year_length_ticks))
            if planet.id == self.project.calendar_model.primary_planet_id:
                prim_var.set(True)

        self.planet_rows.append((row_frame, name_ent, day_ent, year_ent, prim_var, planet))

    def remove_planet_row(self, row_frame):
        self.planet_rows = [r for r in self.planet_rows if r[0] != row_frame]
        row_frame.destroy()

    def save_data(self):
        new_planets = []
        new_primary = None
        for _, name_ent, day_ent, year_ent, prim_var, orig_planet in self.planet_rows:
            name = name_ent.get()
            try:
                day = int(day_ent.get())
                year = int(year_ent.get())
                if day <= 0: day = 1000
                if year < day: year = day
            except:
                continue
            if name:
                p_id = orig_planet.id if orig_planet else None
                new_p = Planet(id=p_id, name=name, day_length_ticks=day, year_length_ticks=year) if p_id else Planet.create(name=name, day_length_ticks=day, year_length_ticks=year)
                new_planets.append(new_p)
                if prim_var.get() and not new_primary:
                    new_primary = new_p.id

        self.project.calendar_model.planets = new_planets
        if new_planets:
            if new_primary:
                self.project.calendar_model.primary_planet_id = new_primary
            else:
                self.project.calendar_model.primary_planet_id = new_planets[0].id
        else:
            self.project.calendar_model.primary_planet_id = None
