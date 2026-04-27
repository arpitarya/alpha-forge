"""Abstract broker interface — all broker integrations implement this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class BrokerName(str, Enum):
    ZERODHA = "zerodha"
    ANGEL_ONE = "angel_one"
    # Future brokers
    GROWW = "groww"
    UPSTOX = "upstox"


@dataclass
class BrokerOrder:
    order_id: str
    status: str
    symbol: str
    side: str
    quantity: int
    price: float | None
    message: str = ""


@dataclass
class BrokerPosition:
    symbol: str
    exchange: str
    quantity: int
    avg_price: float
    last_price: float
    pnl: float
    product: str


class BaseBroker(ABC):
    """Interface every broker adapter must implement."""

    @abstractmethod
    async def authenticate(self, credentials: dict) -> bool:
        ...

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        exchange: str,
        side: str,
        order_type: str,
        product: str,
        quantity: int,
        price: float | None = None,
        trigger_price: float | None = None,
    ) -> BrokerOrder:
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        ...

    @abstractmethod
    async def get_positions(self) -> list[BrokerPosition]:
        ...

    @abstractmethod
    async def get_holdings(self) -> list[BrokerPosition]:
        ...

    @abstractmethod
    async def get_order_history(self) -> list[BrokerOrder]:
        ...

    @abstractmethod
    async def get_quote(self, symbol: str, exchange: str) -> dict:
        ...
