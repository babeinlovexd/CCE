import customtkinter as ctk

from cce.gui.editor.tab_world import TabWorld
from cce.gui.editor.tab_planets import TabPlanets
from cce.gui.editor.tab_calendar import TabCalendar
from cce.gui.editor.tab_holidays import TabHolidays
from cce.gui.editor.tab_astronomy import TabAstronomy
from cce.utils.i18n import _

class EditorView(ctk.CTkFrame):
    def __init__(self, master, app, project, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.project = project

        # Notebook (Tabview)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add(_("World & Base"))
        self.tabview.add(_("Planets"))
        self.tabview.add(_("Calendar"))
        self.tabview.add(_("Holidays"))
        self.tabview.add(_("Astronomy"))

        self.tab_world = TabWorld(self.tabview.tab(_("World & Base")), self.project)
        self.tab_world.pack(fill="both", expand=True)

        self.tab_planets = TabPlanets(self.tabview.tab(_("Planets")), self.project)
        self.tab_planets.pack(fill="both", expand=True)

        self.tab_calendar = TabCalendar(self.tabview.tab(_("Calendar")), self.project)
        self.tab_calendar.pack(fill="both", expand=True)

        self.tab_holidays = TabHolidays(self.tabview.tab(_("Holidays")), self.project)
        self.tab_holidays.pack(fill="both", expand=True)

        self.tab_astronomy = TabAstronomy(self.tabview.tab(_("Astronomy")), self.project)
        self.tab_astronomy.pack(fill="both", expand=True)

        # Bottom Bar
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(fill="x", side="bottom", padx=10, pady=10)

        self.btn_save = ctk.CTkButton(self.bottom_frame, text=_("Save Project"), command=self.save_project)
        self.btn_save.pack(side="left", padx=10)

        self.btn_save_as = ctk.CTkButton(self.bottom_frame, text=_("Save As..."), command=self.save_project_as)
        self.btn_save_as.pack(side="left", padx=10)

        self.btn_load = ctk.CTkButton(self.bottom_frame, text=_("Load Project"), command=self.app.load_project)
        self.btn_load.pack(side="left", padx=10)

        self.btn_generate = ctk.CTkButton(self.bottom_frame, text=_("🚀 Generate & Open Calendar"), fg_color="green", command=self.generate_calendar)
        self.btn_generate.pack(side="right", padx=10)

    def save_project(self):
        # Notify all tabs to save data to the project model
        self.tab_world.save_data()
        self.tab_planets.save_data()
        self.tab_calendar.save_data()
        self.tab_holidays.save_data()
        self.tab_astronomy.save_data()

        self.app.save_project()

    def generate_calendar(self):
        self.save_project()
        self.app.switch_to_viewer()
