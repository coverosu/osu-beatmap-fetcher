from dataclasses import dataclass
from typing import Optional

from ossapi.models import Score


@dataclass
class Player:
    user_name: str
    id: int
    most_recent_scores: Optional[list[Score]]
