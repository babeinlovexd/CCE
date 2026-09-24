import customtkinter as ctk
from cce.models.calendar_model import Holiday, LeapRule

class TabHolidays(ctk.CTkFrame):
    def __init__(self, master, project, **kwargs):
        super().__init__(master, **kwargs)
        self.project = project

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Holidays
        self.holidays_frame = ctk.CTkFrame(self)
        self.holidays_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.holidays_frame, text="Holidays", font=("Arial", 14, "bold")).pack(pady=5)
        self.holidays_list = ctk.CTkScrollableFrame(self.holidays_frame, height=300)
        self.holidays_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.btn_add_holiday = ctk.CTkButton(self.holidays_frame, text="Add Holiday", command=self.add_holiday_row)
        self.btn_add_holiday.pack(pady=5)

        # Leap Rules
        self.leap_frame = ctk.CTkFrame(self)
        self.leap_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.leap_frame, text="Leap Rules", font=("Arial", 14, "bold")).pack(pady=5)
        self.leap_list = ctk.CTkScrollableFrame(self.leap_frame, height=300)
        self.leap_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.btn_add_leap = ctk.CTkButton(self.leap_frame, text="Add Leap Rule", command=self.add_leap_row)
        self.btn_add_leap.pack(pady=5)

        self.holiday_rows = []
        self.leap_rows = []

        self.load_data()

    def load_data(self):
        for w in self.holidays_list.winfo_children(): w.destroy()
        for w in self.leap_list.winfo_children(): w.destroy()
        self.holiday_rows.clear()
        self.leap_rows.clear()

        for h in self.project.calendar_model.holidays:
            self.add_holiday_row(h)

        for lr in self.project.calendar_model.leap_rules:
            self.add_leap_row(lr)

    def add_holiday_row(self, holiday=None):
        row_frame = ctk.CTkFrame(self.holidays_list)
        row_frame.pack(fill="x", pady=2)

        name_ent = ctk.CTkEntry(row_frame, placeholder_text="Name", width=100)
        name_ent.pack(side="left", padx=2)

        month_vals = ["(None - Abs Day)"] + [m.name for m in self.project.calendar_model.months]
        month_menu = ctk.CTkOptionMenu(row_frame, values=month_vals, width=120)
        month_menu.pack(side="left", padx=2)

        day_ent = ctk.CTkEntry(row_frame, placeholder_text="Day Num", width=70)
        day_ent.pack(side="left", padx=2)

        wd_var = ctk.BooleanVar()
        wd_check = ctk.CTkCheckBox(row_frame, text="Is Weekday", variable=wd_var, width=50)
        wd_check.pack(side="left", padx=5)

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_row(f, self.holiday_rows))
        btn_del.pack(side="right", padx=2)

        if holiday:
            name_ent.insert(0, holiday.name)
            wd_var.set(holiday.counts_as_weekday)
            if holiday.month_id:
                m_name = next((m.name for m in self.project.calendar_model.months if m.id == holiday.month_id), None)
                if m_name:
                    month_menu.set(m_name)
                    day_ent.insert(0, str(holiday.day_in_month))
            elif holiday.absolute_day_in_year:
                month_menu.set("(None - Abs Day)")
                day_ent.insert(0, str(holiday.absolute_day_in_year))

        self.holiday_rows.append((row_frame, name_ent, month_menu, day_ent, wd_var))

    def add_leap_row(self, rule=None):
        row_frame = ctk.CTkFrame(self.leap_list)
        row_frame.pack(fill="x", pady=2)

        desc_ent = ctk.CTkEntry(row_frame, placeholder_text="Description", width=90)
        desc_ent.pack(side="left", padx=2)

        freq_ent = ctk.CTkEntry(row_frame, placeholder_text="Every X Years", width=80)
        freq_ent.pack(side="left", padx=2)

        days_ent = ctk.CTkEntry(row_frame, placeholder_text="Days to add", width=70)
        days_ent.pack(side="left", padx=2)

        month_vals = ["(None)"] + [m.name for m in self.project.calendar_model.months]
        month_menu = ctk.CTkOptionMenu(row_frame, values=month_vals, width=120)
        month_menu.pack(side="left", padx=2)

        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=lambda f=row_frame: self.remove_row(f, self.leap_rows))
        btn_del.pack(side="right", padx=2)

        if rule:
            desc_ent.insert(0, rule.description)
            freq_ent.insert(0, str(rule.every_x_years))
            days_ent.insert(0, str(rule.days_to_add))
            if rule.target_month_id:
                m_name = next((m.name for m in self.project.calendar_model.months if m.id == rule.target_month_id), None)
                if m_name: month_menu.set(m_name)

        self.leap_rows.append((row_frame, desc_ent, freq_ent, days_ent, month_menu))


    def remove_row(self, row_frame, row_list):
        row_list[:] = [r for r in row_list if r[0] != row_frame]
        row_frame.destroy()

    def save_data(self):
        new_holidays = []
        for _, name_ent, month_menu, day_ent, wd_var in self.holiday_rows:
            name = name_ent.get()
            if not name: continue

            sel_month = month_menu.get()
            is_wd = wd_var.get()

            try:
                day_val = int(day_ent.get())
            except:
                continue

            if sel_month == "(None - Abs Day)":
                new_holidays.append(Holiday.create(name=name, absolute_day_in_year=day_val, counts_as_weekday=is_wd))
            else:
                m_id = next((m.id for m in self.project.calendar_model.months if m.name == sel_month), None)
                if m_id:
                    new_holidays.append(Holiday.create(name=name, month_id=m_id, day_in_month=day_val, counts_as_weekday=is_wd))

        new_leap_rules = []
        for _, desc_ent, freq_ent, days_ent, month_menu in self.leap_rows:
            desc = desc_ent.get()
            try:
                freq = int(freq_ent.get())
                days = int(days_ent.get())
            except:
                continue

            if desc and freq > 0:
                sel_month = month_menu.get()
                t_m_id = None
                if sel_month != "(None)":
                    t_m_id = next((m.id for m in self.project.calendar_model.months if m.name == sel_month), None)
                new_leap_rules.append(LeapRule.create(description=desc, every_x_years=freq, target_month_id=t_m_id, days_to_add=days))

        self.project.calendar_model.holidays = new_holidays
        self.project.calendar_model.leap_rules = new_leap_rules
