from dataclasses import dataclass, field
from typing import List, Optional
import uuid

@dataclass
class Sun:
    id: str
    name: str
    dawn_tick: int = 0
    zenith_tick: int = 500
    dusk_tick: int = 1000
    color: str = "#FFD700"

    @classmethod
    def create(cls, name: str, dawn_tick: int = 0, zenith_tick: int = 500, dusk_tick: int = 1000, color: str = "#FFD700"):
        return cls(id=str(uuid.uuid4()), name=name, dawn_tick=dawn_tick, zenith_tick=zenith_tick, dusk_tick=dusk_tick, color=color)

@dataclass
class Moon:
    id: str
    name: str
    cycle_days: float # synodic period in days
    phase_offset: float # phase offset at day 0
    color: str = "#CCCCCC"

    @classmethod
    def create(cls, name: str, cycle_days: float, phase_offset: float = 0.0, color: str = "#CCCCCC"):
        return cls(id=str(uuid.uuid4()), name=name, cycle_days=cycle_days, phase_offset=phase_offset, color=color)

@dataclass
class AstronomyModel:
    suns: List[Sun] = field(default_factory=list)
    moons: List[Moon] = field(default_factory=list)
