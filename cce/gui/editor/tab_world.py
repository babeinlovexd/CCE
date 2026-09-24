import customtkinter as ctk
from cce.models.time_engine import TimeUnit

class TabWorld(ctk.CTkFrame):
    def __init__(self, master, project, **kwargs):
        super().__init__(master, **kwargs)
        self.project = project

        self.grid_columnconfigure(1, weight=1)

        # World Name
        ctk.CTkLabel(self, text="World Name:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.world_name_entry = ctk.CTkEntry(self)
        self.world_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.world_name_entry.insert(0, self.project.name)

        # Base Tick
        ctk.CTkLabel(self, text="Base Tick Name:", font=("Arial", 14, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.tick_name_entry = ctk.CTkEntry(self)
        self.tick_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.tick_name_entry.insert(0, self.project.time_engine.base_tick_name)

        # Time units hierarchy
        ctk.CTkLabel(self, text="Time Units (Day -> Smaller Units):", font=("Arial", 14, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.units_frame = ctk.CTkScrollableFrame(self, height=200)
        self.units_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.unit_rows = []
        self.load_units()

        # Add unit button
        self.btn_add = ctk.CTkButton(self, text="Add Time Unit", command=self.add_unit_row)
        self.btn_add.grid(row=4, column=0, columnspan=2, pady=10)

        # Smallest unit to tick ratio
        ctk.CTkLabel(self, text="Smallest Unit Ticks:", font=("Arial", 14, "bold")).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.smallest_tick_entry = ctk.CTkEntry(self)
        self.smallest_tick_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")
        self.smallest_tick_entry.insert(0, str(self.project.time_engine.smallest_unit_ticks))

    def load_units(self):
        for widget in self.units_frame.winfo_children():
            widget.destroy()
        self.unit_rows.clear()

        for unit in self.project.time_engine.time_units:
            self.add_unit_row(unit)

    def add_unit_row(self, unit=None):
        row_frame = ctk.CTkFrame(self.units_frame)
        row_frame.pack(fill="x", pady=2)

        name_ent = ctk.CTkEntry(row_frame, placeholder_text="Name (e.g. Hour)", width=150)
        name_ent.pack(side="left", padx=5)

        abbr_ent = ctk.CTkEntry(row_frame, placeholder_text="Abbr (e.g. h)", width=80)
        abbr_ent.pack(side="left", padx=5)

        count_ent = ctk.CTkEntry(row_frame, placeholder_text="Count in parent (e.g. 24)", width=120)
        count_ent.pack(side="left", padx=5)

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_unit_row(f))
        btn_del.pack(side="right", padx=5)

        if unit:
            name_ent.insert(0, unit.name)
            abbr_ent.insert(0, unit.abbr)
            count_ent.insert(0, str(unit.count_in_parent))

        self.unit_rows.append((row_frame, name_ent, abbr_ent, count_ent))

    def remove_unit_row(self, row_frame):
        self.unit_rows = [r for r in self.unit_rows if r[0] != row_frame]
        row_frame.destroy()

    def save_data(self):
        self.project.name = self.world_name_entry.get()
        self.project.time_engine.base_tick_name = self.tick_name_entry.get()
        try:
            st = int(self.smallest_tick_entry.get())
            self.project.time_engine.smallest_unit_ticks = st if st > 0 else 1
        except:
            self.project.time_engine.smallest_unit_ticks = 1

        new_units = []
        for _, name_ent, abbr_ent, count_ent in self.unit_rows:
            name = name_ent.get()
            abbr = abbr_ent.get()
            try:
                count = int(count_ent.get())
                if count <= 0: count = 1
            except:
                count = 1
            if name:
                new_units.append(TimeUnit.create(name=name, abbr=abbr, count_in_parent=count))

        self.project.time_engine.time_units = new_units
