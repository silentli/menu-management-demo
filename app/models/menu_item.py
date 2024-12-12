import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class MenuItem:
    id: int
    category: str
    name: str
    price: float
    _quantity: Optional[int] = field(init=False, default=None)

    @property
    def sold_out(self) -> bool:
        if self._quantity < 0:
            logger.debug(f"Negative quantity detected for item {self.name}: {self._quantity}")
        return self._quantity <= 0

    def set_quantity(self, quantity: int) -> None:
        self._quantity = quantity
