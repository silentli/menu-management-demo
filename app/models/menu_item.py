from dataclasses import dataclass, field
from typing import Optional

@dataclass
class MenuItem:
    id: int
    category: str
    name: str
    price: float
    sold_out: Optional[bool] = field(default=None)

