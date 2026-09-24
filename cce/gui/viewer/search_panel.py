import customtkinter as ctk
from cce.utils.i18n import _

class SearchPanel(ctk.CTkFrame):
    def __init__(self, master, project, on_search, **kwargs):
        super().__init__(master, **kwargs)
        self.project = project
        self.on_search = on_search

        self.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(self, placeholder_text=_("Search events..."))
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.search_btn = ctk.CTkButton(self, text=_("Search"), width=60, command=self.do_search)
        self.search_btn.grid(row=0, column=1, padx=5, pady=5)

    def do_search(self):
        query = self.search_entry.get()
        self.on_search(query)
