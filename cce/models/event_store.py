from dataclasses import dataclass, field
from typing import List, Optional
import uuid

@dataclass
class StoryEvent:
    id: str
    title: str
    start_tick: int
    end_tick: int
    characters: List[str] = field(default_factory=list)
    location: str = ""
    plotline: str = ""
    description: str = ""

    @classmethod
    def create(cls, title: str, start_tick: int, end_tick: int, characters: Optional[List[str]] = None,
               location: str = "", plotline: str = "", description: str = ""):
        return cls(
            id=str(uuid.uuid4()),
            title=title,
            start_tick=start_tick,
            end_tick=end_tick,
            characters=characters or [],
            location=location,
            plotline=plotline,
            description=description
        )

@dataclass
class EventStore:
    events: List[StoryEvent] = field(default_factory=list)
