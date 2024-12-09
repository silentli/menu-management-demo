from dataclasses import dataclass

@dataclass
class MenuItem:
    id: int
    category: str
    name: str
    price: float

