import customtkinter as ctk
from cce.models.calendar_model import Epoch, Month, Weekday

class TabCalendar(ctk.CTkFrame):
    def __init__(self, master, project, **kwargs):
        super().__init__(master, **kwargs)
        self.project = project

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Left Column: Epochs
        self.epochs_frame = ctk.CTkFrame(self)
        self.epochs_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.epochs_frame, text="Epochs / Eras", font=("Arial", 14, "bold")).pack(pady=5)
        self.epochs_list = ctk.CTkScrollableFrame(self.epochs_frame)
        self.epochs_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.btn_add_epoch = ctk.CTkButton(self.epochs_frame, text="Add Epoch", command=self.add_epoch_row)
        self.btn_add_epoch.pack(pady=5)

        # Middle Column: Months
        self.months_frame = ctk.CTkFrame(self)
        self.months_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.months_frame, text="Months / Seasons", font=("Arial", 14, "bold")).pack(pady=5)
        self.months_list = ctk.CTkScrollableFrame(self.months_frame)
        self.months_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.btn_add_month = ctk.CTkButton(self.months_frame, text="Add Month", command=self.add_month_row)
        self.btn_add_month.pack(pady=5)

        # Right Column: Weekdays
        self.weekdays_frame = ctk.CTkFrame(self)
        self.weekdays_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.weekdays_frame, text="Weekdays", font=("Arial", 14, "bold")).pack(pady=5)
        self.weekdays_list = ctk.CTkScrollableFrame(self.weekdays_frame)
        self.weekdays_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.btn_add_weekday = ctk.CTkButton(self.weekdays_frame, text="Add Weekday", command=self.add_weekday_row)
        self.btn_add_weekday.pack(pady=5)

        self.epoch_rows = []
        self.month_rows = []
        self.weekday_rows = []

        self.load_data()

    def load_data(self):
        for w in self.epochs_list.winfo_children(): w.destroy()
        for w in self.months_list.winfo_children(): w.destroy()
        for w in self.weekdays_list.winfo_children(): w.destroy()

        self.epoch_rows.clear()
        self.month_rows.clear()
        self.weekday_rows.clear()

        for e in self.project.calendar_model.epochs:
            self.add_epoch_row(e)

        for m in self.project.calendar_model.months:
            self.add_month_row(m)

        for w in self.project.calendar_model.weekdays:
            self.add_weekday_row(w)

    def add_epoch_row(self, epoch=None):
        row_frame = ctk.CTkFrame(self.epochs_list)
        row_frame.pack(fill="x", pady=2)

        name_ent = ctk.CTkEntry(row_frame, placeholder_text="Name", width=100)
        name_ent.pack(side="left", padx=5)

        start_ent = ctk.CTkEntry(row_frame, placeholder_text="Start Year", width=70)
        start_ent.pack(side="left", padx=5)

        y0_var = ctk.BooleanVar()
        y0_check = ctk.CTkCheckBox(row_frame, text="Yr 0", variable=y0_var, width=50)
        y0_check.pack(side="left", padx=5)

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_row(f, self.epoch_rows))
        btn_del.pack(side="right", padx=5)

        if epoch:
            name_ent.insert(0, epoch.name)
            start_ent.insert(0, str(epoch.start_year))
            y0_var.set(epoch.includes_year_zero)

        self.epoch_rows.append((row_frame, name_ent, start_ent, y0_var))

    def add_month_row(self, month=None):
        row_frame = ctk.CTkFrame(self.months_list)
        row_frame.pack(fill="x", pady=2)

        name_ent = ctk.CTkEntry(row_frame, placeholder_text="Name", width=90)
        name_ent.pack(side="left", padx=5)

        days_ent = ctk.CTkEntry(row_frame, placeholder_text="Days", width=50)
        days_ent.pack(side="left", padx=5)

        col_ent = ctk.CTkEntry(row_frame, placeholder_text="Color (#HEX)", width=80)
        col_ent.pack(side="left", padx=5)

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_row(f, self.month_rows))
        btn_del.pack(side="right", padx=5)

        m_id = None
        if month:
            name_ent.insert(0, month.name)
            days_ent.insert(0, str(month.days))
            col_ent.insert(0, month.color)
            m_id = month.id

        self.month_rows.append((row_frame, name_ent, days_ent, col_ent, m_id))

    def add_weekday_row(self, weekday=None):
        row_frame = ctk.CTkFrame(self.weekdays_list)
        row_frame.pack(fill="x", pady=2)

        name_ent = ctk.CTkEntry(row_frame, placeholder_text="Name", width=150)
        name_ent.pack(side="left", padx=5)

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_row(f, self.weekday_rows))
        btn_del.pack(side="right", padx=5)

        if weekday:
            name_ent.insert(0, weekday.name)

        self.weekday_rows.append((row_frame, name_ent))

    def remove_row(self, row_frame, row_list):
        row_list[:] = [r for r in row_list if r[0] != row_frame]
        row_frame.destroy()

    def save_data(self):
        new_epochs = []
        for _, name_ent, start_ent, y0_var in self.epoch_rows:
            name = name_ent.get()
            try:
                start = int(start_ent.get())
            except:
                start = 0
            if name:
                new_epochs.append(Epoch.create(name=name, abbr=name[:3], start_year=start, includes_year_zero=y0_var.get()))

        new_months = []
        for _, name_ent, days_ent, col_ent, orig_id in self.month_rows:
            name = name_ent.get()
            col = col_ent.get() or "#444444"
            try:
                days = int(days_ent.get())
            except:
                continue
            if name:
                if orig_id:
                    new_months.append(Month(id=orig_id, name=name, days=days, color=col))
                else:
                    new_months.append(Month.create(name=name, days=days, color=col))

        new_weekdays = []
        for _, name_ent in self.weekday_rows:
            name = name_ent.get()
            if name:
                new_weekdays.append(Weekday.create(name=name))

        self.project.calendar_model.epochs = new_epochs
        self.project.calendar_model.months = new_months
        self.project.calendar_model.weekdays = new_weekdays
