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

        self.filter_var = ctk.StringVar(value=_("Filter: None"))
        self.filter_menu = ctk.CTkOptionMenu(self, variable=self.filter_var, values=[_("Filter: None")], command=self.on_filter_change, width=120)
        self.filter_menu.grid(row=0, column=2, padx=5, pady=5)

    def populate_filters(self):
        chars = set()
        locs = set()
        for e in self.project.event_store.events:
            if e.location: locs.add(e.location)
            for c in e.characters:
                chars.add(c)

        vals = [_("Filter: None")]
        if chars:
            vals.append("--- " + _("Characters") + " ---")
            vals.extend(sorted(list(chars)))
        if locs:
            vals.append("--- " + _("Locations") + " ---")
            vals.extend(sorted(list(locs)))

        self.filter_menu.configure(values=vals)
        if self.filter_var.get() not in vals:
            self.filter_var.set(_("Filter: None"))

    def do_search(self):
        query = self.search_entry.get()
        filter_val = self.filter_var.get()
        if filter_val == _("Filter: None") or filter_val.startswith("---"):
            filter_val = ""
        self.on_search(query, filter_val)

    def on_filter_change(self, choice):
        self.do_search()
