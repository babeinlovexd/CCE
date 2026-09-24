from dataclasses import dataclass, field
from typing import List, Optional, Dict
import uuid

@dataclass
class Planet:
    id: str
    name: str
    day_length_ticks: int # Ticks per day
    year_length_ticks: int # Ticks per year (orbit)

    @classmethod
    def create(cls, name: str, day_length_ticks: int, year_length_ticks: int):
        return cls(id=str(uuid.uuid4()), name=name, day_length_ticks=day_length_ticks, year_length_ticks=year_length_ticks)

@dataclass
class Epoch:
    id: str
    name: str
    abbr: str
    start_year: int
    includes_year_zero: bool

    @classmethod
    def create(cls, name: str, abbr: str, start_year: int = 0, includes_year_zero: bool = False):
        return cls(id=str(uuid.uuid4()), name=name, abbr=abbr, start_year=start_year, includes_year_zero=includes_year_zero)

@dataclass
class Month:
    id: str
    name: str
    days: int
    color: str = "#444444"

    @classmethod
    def create(cls, name: str, days: int, color: str = "#444444"):
        return cls(id=str(uuid.uuid4()), name=name, days=days, color=color)

@dataclass
class Weekday:
    id: str
    name: str

    @classmethod
    def create(cls, name: str):
        return cls(id=str(uuid.uuid4()), name=name)

@dataclass
class Holiday:
    id: str
    name: str
    month_id: Optional[str] # If None, it's outside of regular months
    day_in_month: Optional[int] # Which day it falls on (if tied to a month)
    absolute_day_in_year: Optional[int] # Or absolute day in the year
    counts_as_weekday: bool = True
    color: str = "#FFD700"

    @classmethod
    def create(cls, name: str, month_id: Optional[str] = None, day_in_month: Optional[int] = None,
               absolute_day_in_year: Optional[int] = None, counts_as_weekday: bool = True, color: str = "#FFD700"):
        return cls(id=str(uuid.uuid4()), name=name, month_id=month_id, day_in_month=day_in_month,
                   absolute_day_in_year=absolute_day_in_year, counts_as_weekday=counts_as_weekday, color=color)

@dataclass
class LeapRule:
    id: str
    description: str
    every_x_years: int
    target_month_id: Optional[str] # if None, adds an extra day not in any month
    days_to_add: int

    @classmethod
    def create(cls, description: str, every_x_years: int, target_month_id: Optional[str], days_to_add: int):
        return cls(id=str(uuid.uuid4()), description=description, every_x_years=every_x_years,
                   target_month_id=target_month_id, days_to_add=days_to_add)

@dataclass
class CalendarModel:
    planets: List[Planet] = field(default_factory=list)
    primary_planet_id: Optional[str] = None
    epochs: List[Epoch] = field(default_factory=list)
    months: List[Month] = field(default_factory=list)
    weekdays: List[Weekday] = field(default_factory=list)
    holidays: List[Holiday] = field(default_factory=list)
    leap_rules: List[LeapRule] = field(default_factory=list)

    def get_primary_planet(self) -> Optional[Planet]:
        for p in self.planets:
            if p.id == self.primary_planet_id:
                return p
        return self.planets[0] if self.planets else None

    def get_epoch_for_year(self, year: int) -> Optional[Epoch]:
        if not self.epochs:
            return None
        # Assuming epochs are sorted by start_year implicitly or we just find the closest one
        valid_epochs = [e for e in self.epochs if year >= e.start_year]
        if valid_epochs:
            # Get the one with the highest start_year that is <= year
            return max(valid_epochs, key=lambda e: e.start_year)
        # If year is before the first epoch
        return min(self.epochs, key=lambda e: e.start_year)

    def get_days_in_year(self, year: int) -> int:
        base_days = sum(m.days for m in self.months)

        # Add holidays that are absolute days (not inside a month)
        standalone_holidays = sum(1 for h in self.holidays if h.month_id is None)
        base_days += standalone_holidays

        # Apply leap rules
        leap_days = 0
        for rule in self.leap_rules:
            if rule.every_x_years > 0 and year % rule.every_x_years == 0:
                leap_days += rule.days_to_add

        total = base_days + leap_days

        # Fallback if no months or holidays are defined
        if total == 0:
            prim = self.get_primary_planet()
            if prim and prim.day_length_ticks > 0:
                total = max(1, prim.year_length_ticks // prim.day_length_ticks)
            else:
                total = 1

        return total

    def get_total_days_since_zero(self, year: int) -> int:
        """Calculate exact total days elapsed from Year 0 up to (but not including) the given year."""
        total_days = 0
        if year > 0:
            for y in range(0, year):
                # Only add if y is not 0 OR y is 0 and year 0 is included
                if y != 0 or (y == 0 and self.get_epoch_for_year(0) and getattr(self.get_epoch_for_year(0), 'includes_year_zero', False)):
                    total_days += self.get_days_in_year(y)
        elif year < 0:
            for y in range(year, 0):
                total_days -= self.get_days_in_year(y)
        return total_days

    def get_weekday_counting_days_in_year(self, year: int) -> int:
        # Number of days that advance the weekday counter
        total_days = self.get_days_in_year(year)
        # Subtract holidays that are NOT counted as weekdays
        non_wd_hols = sum(1 for h in self.holidays if not h.counts_as_weekday)

        # Assuming leap rules don't count as holidays and do advance weekdays by default
        return total_days - non_wd_hols

    def get_total_weekday_counting_days_since_zero(self, year: int) -> int:
        total = 0
        if year > 0:
            for y in range(0, year):
                if y != 0 or (y == 0 and self.get_epoch_for_year(0) and getattr(self.get_epoch_for_year(0), 'includes_year_zero', False)):
                    total += self.get_weekday_counting_days_in_year(y)
        elif year < 0:
            for y in range(year, 0):
                total -= self.get_weekday_counting_days_in_year(y)
        return total

    def generate_calendar_matrix(self, year: int):
        """
        Generates a flat list of days for a given year.
        Each day contains information like absolute day number, month, day in month, weekday, and holidays.
        """
        days = []

        weeklen = len(self.weekdays)
        if weeklen == 0:
            weeklen = 1
            dummy_weekday = Weekday(id="dummy", name="Day")
            self.weekdays = [dummy_weekday]

        # Determine continuous weekday index at the start of this year
        total_wcd = self.get_total_weekday_counting_days_since_zero(year)
        current_weekday_idx = total_wcd % weeklen

        leap_days_by_month = {}
        standalone_leap_days = 0
        for rule in self.leap_rules:
            if rule.every_x_years > 0 and year % rule.every_x_years == 0:
                if rule.target_month_id:
                    leap_days_by_month[rule.target_month_id] = leap_days_by_month.get(rule.target_month_id, 0) + rule.days_to_add
                else:
                    standalone_leap_days += rule.days_to_add

        # Build a queue of absolute standalone holidays
        # Sort them by absolute day
        standalone_holidays = sorted([h for h in self.holidays if h.month_id is None and h.absolute_day_in_year is not None], key=lambda h: h.absolute_day_in_year)

        total_days = self.get_days_in_year(year)

        month_idx = 0
        day_in_month = 1

        for absolute_day in range(1, total_days + 1):
            is_standalone_holiday = False
            holiday_matches = []

            # Check if this exact absolute day is a standalone holiday
            if standalone_holidays and standalone_holidays[0].absolute_day_in_year == absolute_day:
                holiday_matches.append(standalone_holidays.pop(0))
                is_standalone_holiday = True

            month = None
            d = None
            is_leap = False

            if is_standalone_holiday:
                # Standalone holidays pause the month progression
                pass
            elif month_idx < len(self.months):
                month = self.months[month_idx]
                d = day_in_month

                # Check for holidays specific to this month and day
                m_hols = [h for h in self.holidays if h.month_id == month.id and h.day_in_month == d]
                holiday_matches.extend(m_hols)

                month_days_total = month.days + leap_days_by_month.get(month.id, 0)
                is_leap = d > month.days

                day_in_month += 1
                if day_in_month > month_days_total:
                    day_in_month = 1
                    month_idx += 1
            elif standalone_leap_days > 0:
                # Appended at the end if there are no more months
                is_leap = True
                standalone_leap_days -= 1
            else:
                # Month-less calendar fallback
                d = absolute_day

            counts_as_weekday = True
            if holiday_matches:
                counts_as_weekday = all(h.counts_as_weekday for h in holiday_matches)

            days.append({
                "absolute_day": absolute_day,
                "month": month,
                "day_in_month": d,
                "weekday": self.weekdays[current_weekday_idx],
                "holidays": holiday_matches,
                "is_leap_day": is_leap
            })

            if counts_as_weekday:
                current_weekday_idx = (current_weekday_idx + 1) % weeklen

        return days
