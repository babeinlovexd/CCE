import json
import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict

from cce.models.time_engine import TimeEngine, TimeUnit
from cce.models.calendar_model import CalendarModel, Planet, Epoch, Month, Weekday, Holiday, LeapRule
from cce.models.astronomy import AstronomyModel, Sun, Moon
from cce.models.event_store import EventStore, StoryEvent

class DataclassEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

@dataclass
class Project:
    name: str = "New World"
    time_engine: TimeEngine = field(default_factory=TimeEngine)
    calendar_model: CalendarModel = field(default_factory=CalendarModel)
    astronomy_model: AstronomyModel = field(default_factory=AstronomyModel)
    event_store: EventStore = field(default_factory=EventStore)

    def save_to_file(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self, f, cls=DataclassEncoder, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Project':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Reconstruct TimeEngine
        te_data = data.get("time_engine", {})
        time_units = [TimeUnit(**tu) for tu in te_data.get("time_units", [])]
        time_engine = TimeEngine(
            base_tick_name=te_data.get("base_tick_name", "Tick"),
            base_tick_desc=te_data.get("base_tick_desc", ""),
            time_units=time_units,
            smallest_unit_ticks=te_data.get("smallest_unit_ticks", 1)
        )

        # Reconstruct CalendarModel
        cm_data = data.get("calendar_model", {})
        calendar_model = CalendarModel(
            planets=[Planet(**p) for p in cm_data.get("planets", [])],
            primary_planet_id=cm_data.get("primary_planet_id"),
            epochs=[Epoch(**e) for e in cm_data.get("epochs", [])],
            months=[Month(**m) for m in cm_data.get("months", [])],
            weekdays=[Weekday(**w) for w in cm_data.get("weekdays", [])],
            holidays=[Holiday(**h) for h in cm_data.get("holidays", [])],
            leap_rules=[LeapRule(**lr) for lr in cm_data.get("leap_rules", [])]
        )

        # Reconstruct AstronomyModel
        am_data = data.get("astronomy_model", {})
        astronomy_model = AstronomyModel(
            suns=[Sun(**s) for s in am_data.get("suns", [])],
            moons=[Moon(**m) for m in am_data.get("moons", [])]
        )

        # Reconstruct EventStore
        es_data = data.get("event_store", {})
        event_store = EventStore(
            events=[StoryEvent(**e) for e in es_data.get("events", [])]
        )

        return cls(
            name=data.get("name", "New World"),
            time_engine=time_engine,
            calendar_model=calendar_model,
            astronomy_model=astronomy_model,
            event_store=event_store
        )
