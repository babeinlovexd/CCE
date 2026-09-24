from dataclasses import dataclass, field
from typing import List, Dict
import uuid

@dataclass
class TimeUnit:
    id: str
    name: str
    abbr: str
    count_in_parent: int  # How many of this unit fit in its parent

    @classmethod
    def create(cls, name: str, abbr: str, count_in_parent: int):
        return cls(id=str(uuid.uuid4()), name=name, abbr=abbr, count_in_parent=count_in_parent)

@dataclass
class TimeEngine:
    base_tick_name: str = "Tick"
    base_tick_desc: str = "1 standard physical unit"

    # Hierarchy of time units.
    # Index 0 is the largest unit (e.g., "Hour"), directly below a "Day".
    # Index -1 is the smallest unit (e.g., "Second"), directly above a "Tick".
    time_units: List[TimeUnit] = field(default_factory=list)
    smallest_unit_ticks: int = 1  # How many ticks in the smallest time unit

    def get_ticks_per_day(self) -> int:
        """Returns the total number of ticks in one standard day on the primary planet.
           Wait, day length might be planet-specific in ticks.
           This method assumes the base hierarchy defines a standard day.
        """
        ticks = self.smallest_unit_ticks
        for unit in reversed(self.time_units):
            ticks *= unit.count_in_parent
        return ticks

    def convert_time_to_ticks(self, time_values: Dict[str, int]) -> int:
        """Converts a dictionary of unit_id -> value to total ticks."""
        ticks = 0
        current_multiplier = self.smallest_unit_ticks

        for unit in reversed(self.time_units):
            val = time_values.get(unit.id, 0)
            ticks += val * current_multiplier
            current_multiplier *= unit.count_in_parent

        return ticks

    def format_ticks_to_time(self, ticks: int, day_length_ticks: int = None) -> str:
        """Formats ticks into a readable time string."""
        if not self.time_units:
            return f"{ticks} {self.base_tick_name}"

        # If day_length_ticks is provided, we might wrap around
        tpd = self.get_ticks_per_day()
        if tpd <= 0: tpd = 1

        if day_length_ticks and day_length_ticks > 0:
            remainder = ticks % day_length_ticks
        else:
            remainder = ticks % tpd

        parts = []
        current_multiplier = self.smallest_unit_ticks
        multipliers = {}
        for unit in reversed(self.time_units):
            multipliers[unit.id] = current_multiplier
            current_multiplier *= unit.count_in_parent

        for unit in self.time_units:
            mult = multipliers[unit.id]
            val = remainder // mult
            remainder = remainder % mult
            parts.append(f"{val}{unit.abbr}")

        if remainder > 0 or not parts:
            parts.append(f"{remainder} {self.base_tick_name}")

        return " ".join(parts)

    def parse_time_string_to_ticks(self, time_str: str) -> int:
        """Parses a string like '2h 30m' or '500 Tick' into total ticks."""
        import re
        ticks = 0

        # Build a mapping of abbr to multiplier
        multipliers = {}
        current_multiplier = self.smallest_unit_ticks
        for unit in reversed(self.time_units):
            multipliers[unit.abbr] = current_multiplier
            current_multiplier *= unit.count_in_parent

        # Also map base tick name
        multipliers[self.base_tick_name] = 1

        # Regex to find number followed by string
        matches = re.findall(r"(\d+)\s*([a-zA-Z]+)", time_str)
        for val_str, abbr in matches:
            val = int(val_str)
            if abbr in multipliers:
                ticks += val * multipliers[abbr]
            # Try lowercase matching just in case
            else:
                for k, v in multipliers.items():
                    if k.lower() == abbr.lower():
                        ticks += val * v
                        break
        return ticks
